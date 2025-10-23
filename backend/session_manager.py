import uuid
from typing import Dict
from base import TravelInfo, ChatSession


class SessionManager:
    """会话管理器，用于管理多个用户的对话会话"""

    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}

    def create_session(self) -> str:
        """
        创建新的会话

        Returns:
            会话ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ChatSession(
            session_id=session_id,
            travel_info=TravelInfo(),
            conversation_history=[]
        )
        return session_id

    def get_session(self, session_id: str) -> ChatSession:
        """
        获取会话

        Args:
            session_id: 会话ID

        Returns:
            ChatSession对象

        Raises:
            KeyError: 如果会话不存在
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
        return self.sessions[session_id]

    def update_session(self, session_id: str, session: ChatSession):
        """
        更新会话

        Args:
            session_id: 会话ID
            session: 更新后的ChatSession对象
        """
        self.sessions[session_id] = session

    def delete_session(self, session_id: str):
        """
        删除会话

        Args:
            session_id: 会话ID
        """
        if session_id in self.sessions:
            del self.sessions[session_id]

    def session_exists(self, session_id: str) -> bool:
        """
        检查会话是否存在

        Args:
            session_id: 会话ID

        Returns:
            会话是否存在
        """
        return session_id in self.sessions


# 全局会话管理器实例
session_manager = SessionManager()
