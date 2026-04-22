import json
from typing import Dict, Any

from langchain_core.messages import AIMessage, HumanMessage

from config import prompts
from src.utils.llm_fatory import get_chat_model
from src.schemas.states import ResumeAgentState



def generate_final_report(summaries: list) -> str:
    """生成综合评估报告"""
    # 如果summaries中每一项都为空，返回空字符串
    if all(not summary for summary in summaries):
        return ""
    
    llm = get_chat_model(temperature=0.3, streaming=True)
    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_REPORTER_PROMPT.format(
                    summaries=summaries
                )
            )
        ]
    )

    return response.content


def resume_reporter_node(state: ResumeAgentState) -> Dict[str, Any]:
    """综合报告节点"""
    question_records = state.get("question_records", [])
    summaries = [q.summary for q in question_records]

    final_report = generate_final_report(summaries)
    return {
        "final_report": final_report,
        "messages": [
            AIMessage(content=final_report)
        ]
    }

