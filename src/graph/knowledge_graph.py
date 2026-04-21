from langgraph.graph import StateGraph, END

from nodes.knowledge_chatter import chat_node
from nodes.knowledge_evaluator import evaluate_node
from nodes.knowledge_saver import save_node
from nodes.knowledge_scanner import scan_repositories_node
from nodes.knowledge_questioner import generate_questions_node
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

    # TODO：更加格式化的开始下一题
    # 评价后的循环：是继续聊天还是下一题？
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