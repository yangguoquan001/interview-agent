from pydantic import BaseModel
from typing import List, TypedDict


class ResumeInfo(TypedDict):
    """简历解析结果"""

    candidate_name: str = ""
    years_experience: float = 0
    current_company: str = ""
    skills: List[str] = []
    project_experience: List[str] = []
    education: str = ""
    raw_text: str = ""


class JobDescription(TypedDict):
    """JD解析结果"""

    job_title: str = ""
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    responsibilities: List[str] = []
    requirements: List[str] = []
    raw_text: str = ""


class QuestionRecord(BaseModel):
    """单个问题记录"""

    questions: List[str] = []  # 单个问题的所有追问
    answers: List[str] = []
    summary: str = ""
    score: int = 0
    feedback: str = ""
    is_terminated: bool = False
    follow_up_count: int = 0


class QuestionsOutput(BaseModel):
    """LLM输出的问题列表"""

    question_list: List[str] = []

