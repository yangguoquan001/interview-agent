from langchain_core.messages import HumanMessage
from typing import Dict, Any

from config import prompts
from src.utils.llm_fatory import get_chat_model
from src.schemas.states import AgentState


def generate_summary(
    question: str, answer: str, follow_up_count: int, score: int
) -> str:
    """生成问题总结"""
    llm = get_chat_model(temperature=0.3)

    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_SUMMARY_PROMPT.format(
                    question=question,
                    answer=answer,
                    follow_up_count=follow_up_count,
                    score=score,
                )
            )
        ]
    )

    return response.content


def resume_summary_node(state: AgentState) -> Dict[str, Any]:
    """问题总结节点"""
    questions = state.get("questions", [])
    current_index = state.get("current_question_index", 0)

    if current_index >= len(questions):
        return {"error": "没有更多问题"}

    current_question = questions[current_index]

    summary = generate_summary(
        current_question.question,
        current_question.answer,
        len(current_question.follow_ups),
        current_question.score,
    )

    questions[current_index].summary = summary

    return {
        "questions": questions,
        "question_summary": summary,
    }
