import logging
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from base import POI, TravelInfo
from session_manager import session_manager
from agents.travel_info_agent import TravelInfoAgent

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定具体域名，如 "http://localhost:5173"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 从环境变量获取API密钥
KIMI_API_KEY = os.getenv("KIMI_API_KEY")
KIMI_BASE_URL= os.getenv("KIMI_BASE_URL")

# 初始化TravelInfoAgent
travel_agent = TravelInfoAgent(api_key=KIMI_API_KEY, api_base=KIMI_BASE_URL)


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

        # 使用Agent处理消息
        result = travel_agent.process_message(
            user_message=request.message,
            current_info=session.travel_info
        )

        # 更新旅行信息
        if "extracted_info" in result and result["extracted_info"]:
            session.travel_info = travel_agent.update_travel_info(
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
