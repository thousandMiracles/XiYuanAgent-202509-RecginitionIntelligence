import logging
import os
import time
from typing import Optional, List
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .base import POI, TravelInfo
from .session_manager import session_manager
from .agents.travel_info_agent import TravelInfoAgent

app = FastAPI()

# 加载环境变量（优先 .env.local，其次 .env）
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 先加载 .env（不覆盖已有环境变量）
load_dotenv(os.path.join(PROJECT_ROOT, '.env'), override=False)
# 再加载 .env.local（允许覆盖，便于本地开发）
load_dotenv(os.path.join(PROJECT_ROOT, '.env.local'), override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定具体域名，如 "http://localhost:5173"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 从环境变量获取API密钥（延迟初始化，避免无密钥时阻塞服务启动）
KIMI_API_KEY = os.getenv("KIMI_API_KEY")
KIMI_BASE_URL = os.getenv("KIMI_BASE_URL")

travel_agent: Optional[TravelInfoAgent] = None

def get_travel_agent() -> TravelInfoAgent:
    global travel_agent
    if travel_agent is not None:
        return travel_agent
    api_key = os.getenv("KIMI_API_KEY")
    api_base = os.getenv("KIMI_BASE_URL")
    model_name = os.getenv("KIMI_MODEL", "kimi-k2-0905")
    if not api_key or not api_base:
        raise HTTPException(status_code=503, detail="Kimi API 未配置，请设置 KIMI_API_KEY 和 KIMI_BASE_URL")
    travel_agent = TravelInfoAgent(api_key=api_key, api_base=api_base, model_name=model_name)
    return travel_agent


def _mask_key(key: Optional[str]) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "****"
    return f"{key[:3]}...{key[-4:]}"


def _mask_url(url: Optional[str]) -> str:
    if not url:
        return ""
    try:
        p = urlparse(url)
        # 仅展示协议+域名，避免泄露路径和查询
        base = f"{p.scheme}://{p.netloc}"
        return base or url
    except Exception:
        return url


# 请求/响应模型
class ChatRequest(BaseModel):
    """聊天请求模型"""
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    """聊天响应模型"""
    session_id: str
    response: str
    travel_info: TravelInfo
    is_complete: bool


class SessionResponse(BaseModel):
    """会话响应模型"""
    session_id: str


class NormalizeDestinationRequest(BaseModel):
    """地名补全请求"""
    name: str
    city_hint: Optional[str] = None


class NormalizeDestinationResponse(BaseModel):
    """地名补全响应"""
    raw: str
    suggestion: str
    alternatives: List[str] = []


class ConfirmDestinationRequest(BaseModel):
    destination: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    处理用户聊天消息，收集旅行信息

    Args:
        request: 包含session_id和用户消息的请求

    Returns:
        ChatResponse: 包含回复、旅行信息和完成状态
    """
    try:
        # 如果没有session_id，创建新会话
        if not request.session_id or not session_manager.session_exists(request.session_id):
            session_id = session_manager.create_session()
            logger.info(f"Created new session: {session_id}")
        else:
            session_id = request.session_id

        # 获取会话
        session = session_manager.get_session(session_id)

        # 添加用户消息到历史
        session.conversation_history.append({
            "role": "user",
            "content": request.message
        })

        # 使用Agent处理消息（懒加载）
        agent = get_travel_agent()
        result = agent.process_message(
            user_message=request.message,
            current_info=session.travel_info
        )

        # 更新旅行信息
        if "extracted_info" in result and result["extracted_info"]:
            session.travel_info = agent.update_travel_info(
                current_info=session.travel_info,
                extracted_info=result["extracted_info"]
            )

        # 获取回复
        agent_response = result.get("response", "抱歉，我没有理解您的意思，能否再说一遍？")
        is_complete = result.get("is_complete", False)

        # 添加Agent回复到历史
        session.conversation_history.append({
            "role": "assistant",
            "content": agent_response
        })

        # 更新会话
        session_manager.update_session(session_id, session)

        logger.info(f"Session {session_id}: User: {request.message[:50]}...")
        logger.info(f"Session {session_id}: Info complete: {is_complete}")

        return ChatResponse(
            session_id=session_id,
            response=agent_response,
            travel_info=session.travel_info,
            is_complete=is_complete
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/normalize_destination", response_model=NormalizeDestinationResponse)
async def normalize_destination(req: NormalizeDestinationRequest):
    """
    使用 Kimi 对目的地名称进行补全/规范化（不调用高德），返回一个建议名称和若干候选项。

    输入：粗略名称 + 可选城市提示
    输出：标准化建议 + 备用候选
    """
    try:
        agent = get_travel_agent()
        sys_prompt = (
            "你是一名地点标准化助手。任务：将用户给出的中文目的地名称补全为更完整、常用、官方的称谓，"
            "尽量包含城市和区县信息（如能确定），但不要编造不存在的信息。"
            "每次补全时，只能根据本次输入的 name 字段独立判断，不要参考历史、会话、已确认目的地或任何缓存。"
            "请只返回 JSON，字段：suggestion (字符串，最佳补全)、alternatives (字符串数组，最多5条不同的合理补全，不包含suggestion)；"
            "如果无法确定更完整名称，请将 suggestion 设为原始输入。"
        )
        human = (
            f"原始名称: {req.name}\n"
            f"城市提示: {req.city_hint or '无'}\n"
            "请输出JSON。示例：{\"suggestion\": \"上海市黄浦区外滩\", \"alternatives\":[\"上海外滩\", \"上海黄浦外滩\"]}"
        )

        from langchain_core.messages import SystemMessage, HumanMessage
        res = agent.llm.invoke([SystemMessage(content=sys_prompt), HumanMessage(content=human)])
        content = getattr(res, "content", "") or ""

        # 解析 JSON（容错提取）
        import json, re
        data = None
        try:
            # 直接解析
            data = json.loads(content)
        except Exception:
            # 从文本中提取第一个花括号JSON片段
            try:
                m = re.search(r"\{[\s\S]*\}", content)
                if m:
                    data = json.loads(m.group(0))
            except Exception:
                data = None

        suggestion = req.name
        alternatives: List[str] = []
        if isinstance(data, dict):
            s = data.get("suggestion")
            if isinstance(s, str) and s.strip():
                suggestion = s.strip()
            alts = data.get("alternatives", [])
            if isinstance(alts, list):
                alternatives = [str(a).strip() for a in alts if str(a).strip()]

        return NormalizeDestinationResponse(
            raw=req.name,
            suggestion=suggestion,
            alternatives=alternatives[:5]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"normalize_destination error: {e}")
        # 失败兜底：直接返回原始名称
        return NormalizeDestinationResponse(
            raw=req.name,
            suggestion=req.name,
            alternatives=[]
        )


@app.post("/api/session/{session_id}/confirm_destination")
async def confirm_destination(session_id: str, req: ConfirmDestinationRequest):
    """
    将用户确认后的目的地写入会话，并标记为已确认，避免模型重复询问。
    """
    try:
        if not session_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        session = session_manager.get_session(session_id)
        # 更新 travel_info
        ti = session.travel_info
        ti.destination = req.destination
        # 兼容旧会话没有该字段
        try:
            setattr(ti, 'destination_confirmed', True)
        except Exception:
            pass
        session.travel_info = ti
        session_manager.update_session(session_id, session)
        return {"ok": True, "destination": req.destination}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"confirm_destination error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/kimi/health")
async def kimi_health():
    """Kimi API 健康检查：尝试最小调用来验证联通性"""
    from langchain_core.messages import HumanMessage
    t0 = time.perf_counter()
    try:
        msg = HumanMessage(content="ping")
        # 若未配置密钥，直接返回失败但不抛异常
        if not os.getenv("KIMI_API_KEY") or not os.getenv("KIMI_BASE_URL"):
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            return {
                "ok": False,
                "elapsed_ms": elapsed_ms,
                "error": "KIMI_API_KEY 或 KIMI_BASE_URL 未配置",
                "env": {
                    "base_url": _mask_url(os.getenv("KIMI_BASE_URL")),
                    "key_hint": _mask_key(os.getenv("KIMI_API_KEY"))
                }
            }
        agent = get_travel_agent()
        res = agent.llm.invoke([msg])
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        content = getattr(res, "content", "")
        model = getattr(agent.llm, "model", os.getenv("KIMI_MODEL", "unknown"))
        return {
            "ok": True,
            "elapsed_ms": elapsed_ms,
            "model": model,
            "preview": str(content)[:120],
            "env": {
                "base_url": _mask_url(os.getenv("KIMI_BASE_URL"))
            }
        }
    except Exception as e:
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        logger.error(f"Kimi health check failed: {e}")
        return {
            "ok": False,
            "elapsed_ms": elapsed_ms,
            "error": str(e)
        }


@app.post("/api/session/new", response_model=SessionResponse)
async def create_new_session():
    """
    创建新的会话

    Returns:
        SessionResponse: 包含新创建的session_id
    """
    try:
        session_id = session_manager.create_session()
        logger.info(f"Created new session: {session_id}")
        return SessionResponse(session_id=session_id)
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}", response_model=ChatResponse)
async def get_session_info(session_id: str):
    """
    获取会话信息

    Args:
        session_id: 会话ID

    Returns:
        ChatResponse: 包含当前会话的旅行信息和完成状态
    """
    try:
        if not session_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        session = session_manager.get_session(session_id)
        is_complete = session.travel_info.is_complete()

        return ChatResponse(
            session_id=session_id,
            response="",  # 空回复
            travel_info=session.travel_info,
            is_complete=is_complete
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    删除会话

    Args:
        session_id: 会话ID

    Returns:
        成功消息
    """
    try:
        if not session_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        session_manager.delete_session(session_id)
        logger.info(f"Deleted session: {session_id}")
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/api/gaode_poi")
# async def gaode_poi_retrival(user_input: str):
#     pass


@app.get("/")
async def root():
    """健康检查端点"""
    return {"status": "ok", "message": "Travel Agent API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
