from langgraph.graph import MessagesState
from pathlib import Path
from typing import List, Optional

from .resume_models import ResumeInfo, JobDescription, QuestionRecord, InterviewSession


class ResumeAgentState(MessagesState):
    resume_file: Optional[str] = None
    jd_file: Optional[str] = None
    interview_mode: str = "resume"  # knowledge/resume
    resume_info: Optional[ResumeInfo] = None
    job_description: Optional[JobDescription] = None
    questions: List[QuestionRecord] = []
    current_question_index: int = 0
    follow_up_count: int = 0  # 当前问题追问次数
    question_summary: str = ""  # 当前问题总结
    session: Optional[InterviewSession] = None
    final_report: str = ""  # 综合评估报告
    should_ask_next: bool = False


class AgentState(MessagesState):
    files_to_read: List[Path]  # 选中的文件路径
    current_file: Optional[Path]
    question: str
    answer: str
    feedback: str
    topic: str  # Agent 总结的面试主题
    difficulty: str  # 难度分级：简单/中等/困难
    thread_id: str  # 线程ID，用于唯一标识每次面试
    is_end: bool = False  # 是否结束面试

    interview_mode: str = "knowledge"  # knowledge/resume
    resume_info: Optional[ResumeInfo] = None
    job_description: Optional[JobDescription] = None
    questions: List[QuestionRecord] = []
    current_question_index: int = 0
    follow_up_count: int = 0  # 当前问题追问次数
    question_summary: str = ""  # 当前问题总结
    session: Optional[InterviewSession] = None
    final_report: str = ""  # 综合评估报告
