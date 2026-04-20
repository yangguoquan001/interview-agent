from langchain_core.messages import HumanMessage
import json
from typing import Dict, Any

from config import prompts
from src.utils.llm_fatory import get_chat_model
from src.schemas.states import ResumeAgentState


def decide_followup(questions: list, answers: list, follow_up_count: int) -> dict:
    """决定是否继续追问"""
    llm = get_chat_model(temperature=0.3)

    # 拼装问答记录
    question_answer_pairs = list(zip(questions, answers))

    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_FOLLOWUP_DECISION_PROMPT.format(
                    chat_history=question_answer_pairs, follow_up_count=follow_up_count
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
    current_questions = curr_question_record.questions
    current_answers = curr_question_record.answers
    last_answer = current_answers[-1] if current_answers else ""

    # --- 情况 A: 开启新题 (此时 answer 为空) ---
    # 场景：从 questioner 刚进来，或者从 summary 刚跳过来
    if not last_answer:
        return {}

    # --- 情况 B: 处理用户的回答 (此时 answer 有内容) ---
    
    # 1. 判定是否“不知道”或达到追问上限
    is_unknown = "不知道" in last_answer or "不清楚" in last_answer or "不了解" in last_answer
    if is_unknown or follow_up_count >= 3:
        curr_question_record.answers.append(last_answer)
        curr_question_record.is_terminated = True
        return {
            "question_records": question_records,
            "current_question_index": current_index+1,
        }

    decision = decide_followup(current_questions, current_answers, follow_up_count)

    next_question = decision.get("next_question", "")
    if next_question:
        current_questions.append(next_question)
        follow_up_count += 1
        curr_question_record.follow_up_count = follow_up_count
        curr_question_record.questions = current_questions
        return {
            "question_records": question_records,
        }
    else:
        curr_question_record.is_terminated = True
        return {
            "question_records": question_records,
        }
