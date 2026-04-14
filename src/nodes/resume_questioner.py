import json

from typing import Dict, Any

from langchain_core.messages import HumanMessage

from config import prompts
from src.schemas.states import AgentState
from src.schemas.resume_models import QuestionRecord
from src.utils.llm_fatory import get_chat_model


def generate_questions(
    resume_info: dict, job_description: dict
) -> list[QuestionRecord]:
    """根据简历和JD生成面试问题"""
    llm = get_chat_model(temperature=0.7)

    resume_str = f"姓名: {resume_info.get('candidate_name', '')}\n"
    resume_str += f"工作年限: {resume_info.get('years_experience', '')}\n"
    resume_str += f"技能: {', '.join(resume_info.get('skills', []))}\n"
    resume_str += f"项目经验: {'; '.join(resume_info.get('project_experience', []))}"

    jd_str = f"职位: {job_description.get('job_title', '')}\n"
    jd_str += f"必需技能: {', '.join(job_description.get('required_skills', []))}\n"
    jd_str += f"加分技能: {', '.join(job_description.get('preferred_skills', []))}\n"
    jd_str += f"岗位职责: {'; '.join(job_description.get('responsibilities', []))}"

    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_QUESTIONER_PROMPT_TEMPLATE.format(
                    resume_info=resume_str, job_description=jd_str
                )
            )
        ]
    )

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError as e:
        raise ValueError(f"解析LLM响应失败: {e}") from e

    questions = []
    for q in result.get("questions", []):
        questions.append(
            QuestionRecord(topic=q.get("topic", ""), question=q.get("question", ""))
        )
    return questions


def resume_questioner_node(state: AgentState) -> Dict[str, Any]:
    """生成面试问题节点"""
    resume_info = state.get("resume_info")
    job_description = state.get("job_description")

    if not resume_info or not job_description:
        return {"error": "缺少简历或JD信息"}

    questions = generate_questions(
        resume_info.model_dump() if hasattr(resume_info, "model_dump") else resume_info,
        job_description.model_dump()
        if hasattr(job_description, "model_dump")
        else job_description,
    )

    return {
        "questions": questions,
        "current_question_index": 0,
    }
