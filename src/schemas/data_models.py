from pydantic import BaseModel
from enum import Enum


class InterviewMode(Enum):
    """面试模式"""

    KNOWLEDGE = "knowledge"  # 知识点面试
    RESUME = "resume"  # 简历面试


class InterviewQuestion(BaseModel):
    """面试问题"""

    topic: str  # 面试主题
    question: str  # 面试问题


class StStatusConfig(BaseModel):
    """st.status配置，用于控制在graph执行的不同阶段显示不同的状态"""
    initial: str = ""
    config: dict | None = {}
