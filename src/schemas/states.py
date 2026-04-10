from langgraph.graph import MessagesState
from pathlib import Path
from typing import List, Optional


class AgentState(MessagesState):
    files_to_read: List[Path]    # 选中的文件路径
    current_file: Optional[Path]
    question: str
    answer: str
    feedback: str
    topic: str  # Agent 总结的面试主题
    difficulty: str  # 难度分级：简单/中等/困难
    thread_id: str  # 线程ID，用于唯一标识每次面试
    is_end: bool = False  # 是否结束面试