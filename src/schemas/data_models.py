from pydantic import BaseModel


class InterviewQuestion(BaseModel):  
    """面试问题"""  
      
    topic: str  # 面试主题
    question: str  # 面试问题
    