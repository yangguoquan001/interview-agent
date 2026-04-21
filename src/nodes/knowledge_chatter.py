from langchain_core.messages import AIMessage, SystemMessage

from config import prompts
from src.schemas.states import KnowledgeAgentState
from src.utils.llm_fatory import get_chat_model



def chat_node(state: KnowledgeAgentState):
    """处理用户评价后的追问"""
    llm = get_chat_model(streaming=True)
    messages = state["messages"]

    # 是否已经进入过chat_node
    new_messages = [messages[-1]]
    has_chat_started = any(isinstance(msg, SystemMessage) and msg.content == prompts.KNOWLEDGE_CHAT_PROMPT for msg in messages)
    if not has_chat_started:
        new_messages.append(SystemMessage(content=prompts.KNOWLEDGE_CHAT_PROMPT))
        messages.append(SystemMessage(content=prompts.KNOWLEDGE_CHAT_PROMPT))
        
    response = llm.invoke(messages).content
    new_messages.append(AIMessage(content=response))
    print(f"\n📝 回答:\n{response}\n" + "="*50)
    return {"messages": new_messages[1:]}
