from langchain_core.messages import AIMessage, HumanMessage
from typing import Dict, Any

from config import prompts
from src.schemas.states import ResumeAgentState
from src.utils.llm_fatory import get_chat_model


def generate_summary(
    questions: list, answers: list
) -> str:
    """生成问题总结"""
    llm = get_chat_model(temperature=0.3, streaming=True)
    question_answer_pairs = []
    for i in range(len(questions)):
        question = questions[i]
        answer = answers[i]
        question_answer_pairs.append({"role": "assistant", "content": question})
        question_answer_pairs.append({"role": "user", "content": answer})

    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_SUMMARY_PROMPT.format(
                    chat_history=question_answer_pairs
                )
            )
        ]
    )

    return response.content


def resume_summary_node(state: ResumeAgentState) -> Dict[str, Any]:
    """问题总结节点"""
    current_index = state.get("current_question_index", 0)
    question_records = state["question_records"]
    curr_question_record = question_records[current_index]
    current_questions = curr_question_record.questions
    current_answers = curr_question_record.answers

    summary = generate_summary(
        current_questions,
        current_answers
    )

    curr_question_record.summary = summary

    return {
        "question_records": question_records,
        "current_question_index": current_index+1,
        "last_answer": "",
        "messages": [
            AIMessage(content=summary)
        ]
    }
