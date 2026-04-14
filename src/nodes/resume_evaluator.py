import re
from typing import Dict, Any

from langchain_core.messages import HumanMessage

from config import prompts
from src.schemas.resume_models import QuestionRecord
from src.schemas.states import ResumeAgentState
from src.utils.llm_fatory import get_chat_model


def evaluate_answer(
    question: str, answer: str, related_experience: str = ""
) -> Dict[str, Any]:
    """评估候选人回答"""
    llm = get_chat_model(temperature=0.3)

    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_EVALUATOR_PROMPT_TEMPLATE.format(
                    question=question,
                    answer=answer,
                    related_experience=related_experience,
                )
            )
        ]
    )

    content = response.content

    score_match = re.search(r"评分[：:]\s*(\d+)", content, re.MULTILINE)
    score = int(score_match.group(1)) if score_match else 0

    return {"score": score, "feedback": content}


def resume_evaluator_node(state: ResumeAgentState) -> Dict[str, Any]:
    questions = state.get("questions", [])
    current_index = state.get("current_question_index", 0)
    answer = state.get("answer", "")

    if current_index >= len(questions):
        return {"error": "没有更多问题"}

    current_question = questions[current_index]
    evaluation = evaluate_answer(
        current_question.question, answer, ", ".join(current_question.follow_ups)
    )

    questions[current_index].answer = answer
    questions[current_index].score = evaluation["score"]
    questions[current_index].feedback = evaluation["feedback"]

    return {
        "questions": questions,
        "feedback": evaluation["feedback"],
    }
