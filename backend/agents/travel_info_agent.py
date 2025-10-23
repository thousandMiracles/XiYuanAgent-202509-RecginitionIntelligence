import os
import json
from typing import Dict, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from base import TravelInfo

os.environ["KIMI_API_KEY"] = "your API KEY"


class ExtractedInfo(BaseModel):
    """提取的旅行信息模型"""
    destination: Optional[str] = Field(None, description="提取到的目的地")
    start_date: Optional[str] = Field(None, description="提取到的开始日期(YYYY-MM-DD格式)")
    end_date: Optional[str] = Field(None, description="提取到的结束日期(YYYY-MM-DD格式)")
    num_people: Optional[int] = Field(None, description="提取到的人数")
    budget: Optional[float] = Field(None, description="提取到的预算(元)")
    preferences: Optional[str] = Field(None, description="提取到的旅行偏好")


class AgentResponse(BaseModel):
    """Agent响应模型"""
    extracted_info: ExtractedInfo = Field(description="从用户消息中提取的信息")
    response: str = Field(description="对用户的友好回复")
    is_complete: bool = Field(description="所有必要信息是否已收集完成")


class TravelInfoAgent:
    """旅行信息采集Agent，用于多轮对话收集用户旅行需求 - 使用LangChain框架"""

    def __init__(
            self,
            api_key: str,
            api_base: str,
            model_name: str = "kimi-k2-0905",
            temperature: float = 0
        ):
        """
        初始化TravelInfoAgent

        Args:
            api_base: API基础URL
            api_key: Moonshot API密钥
            model_name: 模型名称
            temperature: 温度参数
        """
        # 初始化LangChain ChatOpenAI模型（兼容Moonshot API）
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
            base_url=api_base
        )

        # 创建结构化输出模型
        self.structured_llm = self.llm.with_structured_output(AgentResponse)

        # 获取系统指令
        self.system_message = self._get_instructions()

    def _get_instructions(self) -> str:
        """获取Agent的系统指令"""
        return """你是一个专业的旅行规划助手，负责收集用户的旅行需求信息。

你需要收集以下必要信息：
1. destination（目的地）：用户想去哪里旅行
2. start_date（开始日期）：旅行开始日期（格式：YYYY-MM-DD）
3. end_date（结束日期）：旅行结束日期（格式：YYYY-MM-DD）
4. num_people（人数）：参加旅行的人数
5. budget（预算）：旅行预算（单位：元）

可选信息：
- preferences（偏好）：旅行偏好，如美食、文化、自然风光、购物等

任务规则：
1. 从用户的自然语言输入中提取已有信息
2. 识别缺失的信息
3. 用友好、自然的方式询问缺失的信息（一次询问1-2个相关问题）
4. 如果用户提供了新信息，要确认理解并继续询问其他缺失信息
5. 当所有必要信息收集完成后，总结所有信息并询问用户是否确认

注意：
- 日期格式要转换为YYYY-MM-DD格式
- 人数要转换为数字
- 预算要转换为数字（去掉"元"、"块"等单位）
- 如果用户说"下周"、"下个月"等相对时间，要询问具体日期"""

    def process_message(
        self,
        user_message: str,
        current_info: TravelInfo
    ) -> Dict:
        """
        处理用户消息，提取信息并生成回复

        Args:
            user_message: 用户输入的消息
            current_info: 当前已收集的旅行信息

        Returns:
            包含提取信息、回复内容和完成状态的字典
        """
        # 构建上下文提示
        context = self._build_context(current_info)

        # 构建完整提示
        user_prompt = f"""{context}

用户新消息：{user_message}

请分析用户消息，提取新信息，并根据当前已有信息和缺失信息生成合适的回复。"""

        # 使用LangChain调用模型
        messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=user_prompt)
        ]

        try:
            # 调用结构化输出模型
            result: AgentResponse = self.structured_llm.invoke(messages)

            # 转换为字典格式
            return {
                "extracted_info": result.extracted_info.model_dump(),
                "response": result.response,
                "is_complete": result.is_complete
            }

        except Exception as e:
            # 如果结构化输出失败，尝试使用普通模型并返回默认响应
            try:
                response = self.llm.invoke(messages)
                return {
                    "extracted_info": {},
                    "response": response.content,
                    "is_complete": False
                }
            except Exception as inner_e:
                return {
                    "extracted_info": {},
                    "response": f"抱歉，处理您的消息时出现了错误。请重试。",
                    "is_complete": False
                }

    def _build_context(self, current_info: TravelInfo) -> str:
        """
        构建当前信息上下文

        Args:
            current_info: 当前已收集的旅行信息

        Returns:
            上下文字符串
        """
        context_parts = ["当前已收集的信息："]

        if current_info.destination:
            context_parts.append(f"- 目的地：{current_info.destination}")
        if current_info.start_date:
            context_parts.append(f"- 开始日期：{current_info.start_date}")
        if current_info.end_date:
            context_parts.append(f"- 结束日期：{current_info.end_date}")
        if current_info.num_people:
            context_parts.append(f"- 人数：{current_info.num_people}人")
        if current_info.budget:
            context_parts.append(f"- 预算：{current_info.budget}元")
        if current_info.preferences:
            context_parts.append(f"- 偏好：{current_info.preferences}")

        if len(context_parts) == 1:
            context_parts.append("（暂无）")

        # 添加缺失信息
        missing = current_info.get_missing_fields()
        if missing:
            context_parts.append(f"\n缺失的必要信息：{', '.join(missing)}")
        else:
            context_parts.append("\n✓ 所有必要信息已收集完成")

        return "\n".join(context_parts)

    def update_travel_info(
        self,
        current_info: TravelInfo,
        extracted_info: Dict
    ) -> TravelInfo:
        """
        更新旅行信息

        Args:
            current_info: 当前旅行信息
            extracted_info: 从用户消息中提取的新信息

        Returns:
            更新后的旅行信息
        """
        # 创建新的信息对象，保留旧信息
        updated_data = current_info.model_dump()

        # 更新提取到的新信息（只更新非空值）
        for key, value in extracted_info.items():
            if value is not None and value != "":
                updated_data[key] = value

        return TravelInfo(**updated_data)

# 便捷函数
def create_travel_info_agent(api_key: Optional[str] = None) -> TravelInfoAgent:
    """
    创建TravelInfoAgent实例

    Args:
        api_key: Moonshot API密钥

    Returns:
        TravelInfoAgent实例
    """
    return TravelInfoAgent(api_key=api_key)
