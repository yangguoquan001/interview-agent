import json
from typing import Dict, Any

from langchain_core.messages import HumanMessage

from config import prompts
from src.utils.llm_fatory import get_chat_model
from src.schemas.states import ResumeAgentState


def decide_end(questions: list) -> dict:
    """决定是否结束面试"""
    llm = get_chat_model(temperature=0.3)

    questions_summary = ""
    for i, q in enumerate(questions):
        questions_summary += f"{i + 1}. {q.question} (评分: {q.score})\n"

    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_END_DECISION_PROMPT.format(
                    question_count=len(questions), questions_summary=questions_summary
                )
            )
        ]
    )

    return json.loads(response.content)


def generate_final_report(candidate_name: str, job_title: str, questions: list) -> str:
    """生成综合评估报告"""
    llm = get_chat_model(temperature=0.3)

    questions_evaluation = ""
    for i, q in enumerate(questions):
        questions_evaluation += f"""
### 问题{i + 1}: {q.question}
- 回答: {q.answer}
- 追问次数: {len(q.follow_ups)}
- 评分: {q.score}/10
- 总结: {q.summary}
"""

    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_FINAL_REPORT_PROMPT.format(
                    candidate_name=candidate_name or "候选人",
                    job_title=job_title or "未知职位",
                    questions_evaluation=questions_evaluation,
                )
            )
        ]
    )

    return response.content


def resume_reporter_node(state: ResumeAgentState) -> Dict[str, Any]:
    """综合报告节点"""
    questions = state.get("questions", [])
    resume_info = state.get("resume_info")
    job_description = state.get("job_description")

    decision = decide_end(questions)

    if decision.get("should_end", False):
        candidate_name = resume_info.candidate_name if resume_info else "候选人"
        job_title = job_description.job_title if job_description else "未知职位"

        final_report = generate_final_report(candidate_name, job_title, questions)

        return {
            "is_end": True,
            "final_report": final_report,
        }
    else:
        next_question = decision.get("next_question", "")
        if (
            not next_question
            and len(questions) > state.get("current_question_index", 0) + 1
        ):
            next_question = questions[
                state.get("current_question_index", 0) + 1
            ].question

        return {
            "is_end": False,
            "question": next_question,
            "current_question_index": state.get("current_question_index", 0) + 1,
            "follow_up_count": 0,
        }
