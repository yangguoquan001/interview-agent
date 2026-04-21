from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from config import prompts
from src.schemas.states import KnowledgeAgentState
from src.utils.llm_fatory import get_chat_model


def evaluate_node(state: KnowledgeAgentState):
    if state["is_end"]:
        return state
    
    """评价用户的回答"""
    # 获取刚才的文件内容
    with open(state["current_file"], "r", encoding="utf-8") as f:
        content = f.read()
    
    llm = get_chat_model(streaming=True)
    system_prompt = prompts.EVALUATOR_SYSTEM_PROMPT
    prompt = prompts.EVALUATOR_PROMPT_TEMPLATE.format(
        difficulty_level=state["difficulty"],
        question=state["question"],
        answer=state["answer"],
        content=content
    )
    
    feedback = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)]).content
    print(f"\n📝 评估反馈:\n{feedback}\n" + "="*50)
    
    return {
        "feedback": feedback, 
        "messages": [
            SystemMessage(content=prompts.EVALUATOR_PROMPT_TO_MESSAGES), 
            AIMessage(content=feedback)
        ]
    }
