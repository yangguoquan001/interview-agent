from langgraph.graph import StateGraph, END

from src.nodes import (
    resume_parser,
    resume_questioner,
    resume_chatter,
    resume_summary,
    resume_reporter,
    resume_saver,
)
from src.schemas.states import ResumeAgentState

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
        is_end = state.get("is_end")
        if is_end:
            return "go_report"

        question_records = state["question_records"]
        current_question_index = state.get("current_question_index", 0)
        if question_records[current_question_index].is_terminated:
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
        if state.get("current_question_index") > len(state["question_list"]):
            return "go_report"
        
        if state.get("is_end"):
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