from langchain_core.messages import HumanMessage
import json
from typing import Dict, Any

from config import prompts
from src.utils.llm_fatory import get_chat_model
from src.schemas.states import AgentState


def decide_followup(question: str, answer: str, follow_up_count: int) -> dict:
    """决定是否继续追问"""
    llm = get_chat_model(temperature=0.3)

    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_FOLLOWUP_DECISION_PROMPT.format(
                    question=question, answer=answer, follow_up_count=follow_up_count
                )
            )
        ]
    )

    return json.loads(response.content)


def generate_followup(question: str, answer: str) -> str:
    """生成追问问题"""
    llm = get_chat_model(temperature=0.7)

    prompt = f"""
你是一个面试官。候选人刚回答了一个问题，现在需要深入追问。

[原问题]: {question}
[候选人回答]: {answer}

请提出一个深入追问的问题，要求能够考察候选人的深度理解。
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def resume_chatter_node(state: AgentState) -> Dict[str, Any]:
    """追问节点"""
    questions = state.get("questions", [])
    current_index = state.get("current_question_index", 0)
    answer = state.get("answer", "")
    follow_up_count = state.get("follow_up_count", 0)

    if current_index >= len(questions):
        return {"is_end": True}

    current_question = questions[current_index]

    is_unknown = "不知道" in answer or "不清楚" in answer or "不了解" in answer

    if is_unknown or follow_up_count >= 3:
        questions[current_index].is_terminated = is_unknown
        return {
            "questions": questions,
            "follow_up_count": 0,
            "should_ask_next": True,
        }

    decision = decide_followup(current_question.question, answer, follow_up_count)

    if decision.get("should_continue", False):
        next_follow_up = decision.get("next_follow_up", "")
        if not next_follow_up:
            next_follow_up = generate_followup(current_question.question, answer)

        questions[current_index].follow_ups.append(answer)
        follow_up_count += 1
        questions[current_index].follow_up_count = follow_up_count

        return {
            "questions": questions,
            "follow_up_count": follow_up_count,
            "question": next_follow_up,
            "should_ask_next": False,
        }
    else:
        return {
            "questions": questions,
            "follow_up_count": 0,
            "should_ask_next": True,
        }
