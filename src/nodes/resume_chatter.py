from langchain_core.messages import AIMessage, HumanMessage
from typing import Dict, Any

from config import prompts
from src.schemas.states import ResumeAgentState
from src.utils.llm_fatory import get_chat_model
from src.utils.logger import logger


def decide_followup(questions: list, answers: list, follow_up_count: int) -> dict:
    """决定是否继续追问"""
    llm = get_chat_model(temperature=0.3, streaming=True)

    # 格式化拼装问答记录
    question_answer_pairs = []
    for i in range(len(questions)):
        question = questions[i]
        answer = answers[i]
        question_answer_pairs.append({"role": "assistant", "content": question})
        question_answer_pairs.append({"role": "user", "content": answer})

    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_FOLLOWUP_DECISION_PROMPT.format(
                    chat_history=question_answer_pairs, follow_up_count=follow_up_count
                )
            )
        ]
    )

    return response.content


def resume_chatter_node(state: ResumeAgentState) -> Dict[str, Any]:
    """
    追问与对话核心节点
    职责：
    1. 如果没有当前回答，说明是新题目开始，抛出主问题。
    2. 如果有回答，判断是否需要追问。
    3. 如果满足结束条件，标记 is_question_finished = True 引导至 summary 节点。
    """
    question_list = state.get("question_list", [])
    current_index = state.get("current_question_index", 0)
    # 判断是否满足终止条件
    if current_index >= len(question_list):
        return {"is_end": True}

    question_records = state["question_records"]
    curr_question_record = question_records[current_index]
    follow_up_count = curr_question_record.follow_up_count
    current_questions = curr_question_record.questions
    current_answers = curr_question_record.answers
    last_answer = state.get("last_answer", "")
    if last_answer:
        current_answers.append(last_answer)
    # --- 情况 A: 开启新题 (此时 answer 为空) ---
    # 场景：从 questioner 刚进来，或者从 summary 刚跳过来
    if not last_answer:
        return {"messages": [AIMessage(content=current_questions[0])]}

    # --- 情况 B: 处理用户的回答 (此时 answer 有内容) ---

    next_question = decide_followup(current_questions, current_answers, follow_up_count)
    logger.info(f"原始追问: {next_question}")
    if current_index == len(question_list) - 1:
        next_question = next_question.replace("好的，今天就到此为止吧。", "")
    else:
        next_question = next_question.replace("好的，下一个问题。", "")

    if next_question:
        current_questions.append(next_question)
        follow_up_count += 1
        curr_question_record.follow_up_count = follow_up_count
        curr_question_record.questions = current_questions
        return {
            "question_records": question_records,
            "messages": [
                HumanMessage(content=last_answer),
                AIMessage(content=next_question),
            ],
        }
    else:
        curr_question_record.is_terminated = True
        logger.info(f"结束当前题目: {current_index}")
        return {
            "question_records": question_records,
        }
