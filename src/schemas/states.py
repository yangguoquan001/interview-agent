from langgraph.graph import MessagesState
from pathlib import Path
from typing import List, Optional

from .data_models import ResumeInfo, JobDescription, QuestionRecord


class ResumeAgentState(MessagesState):
    # 文档相关
    resume_file: Optional[str] = None
    jd_file: Optional[str] = None
    resume_info: Optional[ResumeInfo] = None
    job_description: Optional[JobDescription] = None

    # 问题相关
    question_list: List[str] = []
    question_records: List[QuestionRecord] = []
    current_question_index: int = 0

    # 最近一条回答
    last_answer: Optional[str] = None

    final_report: str = ""  # 综合评估报告、
    save_file_path: Optional[str] = None  # 保存的文件路径
    is_end: bool = False  # 是否结束面试


class KnowledgeAgentState(MessagesState):
    files_to_read: List[Path]  # 选中的文件路径
    current_file: Optional[Path]
    question: str
    answer: str
    feedback: str
    topic: str  # Agent 总结的面试主题
    difficulty: str  # 难度分级：简单/中等/困难
    thread_id: str  # 线程ID，用于唯一标识每次面试
    is_end: bool = False  # 是否结束面试
