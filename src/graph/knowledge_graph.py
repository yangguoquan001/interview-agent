from langgraph.graph import StateGraph, END

from src.nodes.knowledge_chatter import chat_node
from src.nodes.knowledge_evaluator import evaluate_node
from src.nodes.knowledge_saver import save_node
from src.nodes.knowledge_scanner import scan_repositories_node
from src.nodes.knowledge_questioner import generate_questions_node
from src.schemas.states import KnowledgeAgentState

def create_knowledge_graph(checkpointer):
    workflow = StateGraph(KnowledgeAgentState)
    workflow.add_node("scanner", scan_repositories_node)
    workflow.add_node("questioner", generate_questions_node)
    workflow.add_node("evaluator", evaluate_node)
    workflow.add_node("chat_node", chat_node)
    workflow.add_node("saver", save_node)

    workflow.set_entry_point("scanner")
    workflow.add_edge("scanner", "questioner")
    workflow.add_edge("questioner", "evaluator")

    def router(state: KnowledgeAgentState):
        if state.get("is_end"):
            return "go_save"

        return "chat_node"

    workflow.add_conditional_edges(
        "evaluator", router, {"go_save": "saver", "chat_node": "chat_node"}
    )

    workflow.add_conditional_edges(
        "chat_node", router, {"go_save": "saver", "chat_node": "chat_node"}
    )

    workflow.add_edge("saver", END)  # 直接跳转到 scanner 重新扫描

    # 在评估后和聊天前中断，等待用户输入
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["evaluator", "chat_node"],
        # interrupt_after=["evaluator", "chat_node"],
    )