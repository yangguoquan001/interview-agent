import random
import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from config import prompts
from src.schemas.enums import DifficultyLevel
from src.schemas.states import KnowledgeAgentState
from src.utils.llm_fatory import get_chat_model
from src.utils.logger import logger


def generate_questions_node(state: KnowledgeAgentState):
    if not state["files_to_read"]:
        return {"question": "未知题目", "topic": "未知主题", "files_to_read": []}

    difficulty_level = random.choice(list(DifficultyLevel.__members__.values()))
    # difficulty_level = DifficultyLevel.EASY.value
    difficulty_desc = {
        DifficultyLevel.EASY.value: "侧重于基础概念的理解、基本用法及核心流程。考察候选人是否掌握了该技术点的‘是什么’和‘怎么用’。",
        DifficultyLevel.MEDIUM.value: "侧重于实战应用、性能优化或常见坑点。要求结合业务场景，考察候选人解决实际问题的能力。",
        DifficultyLevel.HARD.value: "侧重于底层原理、架构设计、极端边界情况的处理或与其他系统的复杂交互。考察技术深度和设计思维。",
    }
    file_path = state["files_to_read"][0]
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    llm = get_chat_model(streaming=True)
    system_prompt = f"""
    你是一个资深面试官。请基于提供的文档内容和指定难度出一道面试题。
    [内容要求]:
    - 题目必须与文档内容紧密相关。
    - 题目要清晰明确。
    - 不要给出参考答案和考察要点，只需要给出题目内容。
    [格式要求]:
    - 第一行固定输出：知识点来源：{file_path} 
    - 第二行必须是以二级标题开头的主题，格式为：## 主题：[核心考点名称]
    - 第三行开始是以二级标题开头的题目，格式为：## 面试题：
    - 第四行开始是题目内容。
    """
    prompt = prompts.QUESTIONER_PROMPT_TEMPLATE.format(
        difficulty_level=difficulty_level,
        difficulty_desc=difficulty_desc,
        content=content,
    )
    response = llm.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
    )

    # 解析输出
    raw_text = response.content

    topic_match = re.search(r"^## 主题：\s*(.*)", raw_text, re.MULTILINE)
    topic = topic_match.group(1).strip() if topic_match else "未知主题"
    logger.debug(f"raw_text: {raw_text}")
    question_match = re.search(r"## 面试题：\s*\n?(.*)", raw_text, re.DOTALL)
    question = question_match.group(1).strip() if question_match else "未知题目"

    logger.info(f"🌟 难度: [{difficulty_level}] | 主题: {topic} | 来源: {file_path}")

    remaining = state["files_to_read"][1:]
    return {
        "question": question,
        "topic": topic,
        "current_file": file_path,
        "files_to_read": remaining,
        "messages": [SystemMessage(content=system_prompt), AIMessage(content=question)],
        "difficulty": difficulty_level,
    }
