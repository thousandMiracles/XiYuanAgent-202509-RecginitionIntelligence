from pydantic import BaseModel
from typing import List, Optional


class POI(BaseModel):
    name: str
    type: str
    location: List[float]
    distance: int


class TravelInfo(BaseModel):
    """旅行信息模型"""
    destination: Optional[str] = None  # 目的地
    destination_confirmed: Optional[bool] = False  # 目的地是否已确认
    start_date: Optional[str] = None  # 开始日期
    end_date: Optional[str] = None  # 结束日期
    num_people: Optional[int] = None  # 人数
    budget: Optional[float] = None  # 预算
    preferences: Optional[str] = None  # 偏好（如：美食、文化、自然风光等）

    def is_complete(self) -> bool:
        """检查必要信息是否完整"""
        return all([
            self.destination,
            self.start_date,
            self.end_date,
            self.num_people,
            self.budget
        ])

    def get_missing_fields(self) -> List[str]:
        """获取缺失的字段"""
        missing = []
        field_names = {
            'destination': '目的地',
            'start_date': '开始日期',
            'end_date': '结束日期',
            'num_people': '人数',
            'budget': '预算'
        }

        if not self.destination:
            missing.append(field_names['destination'])
        if not self.start_date:
            missing.append(field_names['start_date'])
        if not self.end_date:
            missing.append(field_names['end_date'])
        if not self.num_people:
            missing.append(field_names['num_people'])
        if not self.budget:
            missing.append(field_names['budget'])

        return missing


class ChatSession(BaseModel):
    """对话会话模型"""
    session_id: str
    travel_info: TravelInfo
    conversation_history: List[dict] = []
