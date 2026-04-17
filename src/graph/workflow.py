from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, END

from src.nodes.chatter import chat_node
from src.nodes.evaluator import evaluate_node
from src.nodes.saver import save_node
from src.nodes.scanner import scan_repositories_node
from src.nodes.questioner import generate_questions_node
from src.nodes import (
    resume_parser,
    resume_questioner,
    resume_evaluator,
    resume_chatter,
    resume_summary,
    resume_reporter,
    resume_saver,
)
from src.schemas.states import AgentState, ResumeAgentState


def create_graph(checkpointer):
    workflow = StateGraph(AgentState)
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
    def router(state: AgentState):
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


def create_resume_graph(checkpointer=None):
    """创建简历面试工作流"""

    workflow = StateGraph(ResumeAgentState)

    workflow.add_node("parser", resume_parser.resume_parser_node)
    workflow.add_node("questioner", resume_questioner.resume_questioner_node)
    workflow.add_node("chatter", resume_chatter.resume_chatter_node)
    workflow.add_node("user_input", lambda state: state)                      # 【新增】空节点，用于中断挂起
    workflow.add_node("summary", resume_summary.resume_summary_node)
    workflow.add_node("reporter", resume_reporter.resume_reporter_node)
    workflow.add_node("saver", resume_saver.resume_save_node)

    workflow.set_entry_point("parser")
    workflow.add_edge("parser", "questioner")
    workflow.add_edge("questioner", "chatter")

    def chatter_router(state: ResumeAgentState):
        """AI发言后的判断"""
        if state.get("is_end"):
            return "go_report"
        
        if state.get("is_question_finished"):
            return "go_summary"
        
        return "go_wait"
    
    workflow.add_conditional_edges(
        "chatter",
        chatter_router,
        {
            "go_report": "reporter",
            "go_summary": "summary",
            "go_wait": "user_input"
        }
    )
    workflow.add_edge("user_input", "chatter")

    def summary_router(state: ResumeAgentState):
        """总结完后的判断"""
        if state.get("is_end"):
            return "go_report"
        
        current_idx = state.get("current_question_index", 0)
        questions = state.get("questions", [])
        if current_idx >= len(questions):
            return "go_report"
        
        return "go_next_question"
    
    workflow.add_conditional_edges(
        "summary",
        summary_router,
        {
            "go_report": "reporter",
            "go_next_question": "chatter"
        }
    )
    workflow.add_edge("reporter", "saver")
    workflow.add_edge("saver", END)

    return workflow.compile(checkpointer=checkpointer, interrupt_before=["user_input"])
