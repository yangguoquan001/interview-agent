import random

from langchain_core.messages import AIMessage, ChatMessage, HumanMessage, SystemMessage
from langgraph.graph import END

from config.prompts import  QUESTIONER_PROMPT_TEMPLATE, QUESTIONER_SYSTEM_PROMPT
from src.schemas.data_models import InterviewQuestion
from src.schemas.enums import DifficultyLevel
from src.schemas.states import AgentState
from src.utils.llm_fatory import get_chat_model


def generate_questions_node(state: AgentState) -> str:
    if not state["files_to_read"]:
        return END

    difficulty_level = random.choice(list(DifficultyLevel.__members.values__()))
    difficulty_desc = {
        DifficultyLevel.EASY.value: "侧重于基础概念的理解、基本用法及核心流程。考察候选人是否掌握了该技术点的‘是什么’和‘怎么用’。",
        DifficultyLevel.MEDIUM.value: "侧重于实战应用、性能优化或常见坑点。要求结合业务场景，考察候选人解决实际问题的能力。",
        DifficultyLevel.HARD.value: "侧重于底层原理、架构设计、极端边界情况的处理或与其他系统的复杂交互。考察技术深度和设计思维。"
    }
    file_path = state["files_to_read"][0]
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    llm = get_chat_model(structured_output_schema=InterviewQuestion)
    system_prompt = QUESTIONER_SYSTEM_PROMPT
    prompt = QUESTIONER_PROMPT_TEMPLATE.format(
        difficulty_level=difficulty_level,
        difficulty_desc=difficulty_desc,
        content=content
    )

    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)])

    # 解析输出
    topic = response.topic
    question = response.question

    
    print(f"\n🌟 难度: [{difficulty_level}] | 主题: {topic} | 来源: {file_path}")
    
    remaining = state["files_to_read"][1:]
    return {
        "question": question, 
        "topic": topic,
        "current_file": file_path, 
        "files_to_read": remaining,
        "messages": [SystemMessage(content=system_prompt), AIMessage(content=question)],
        "difficulty": difficulty_level
    }
