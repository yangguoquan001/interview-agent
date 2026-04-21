import datetime
import re

from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage, SystemMessage
from pathlib import Path

from src.schemas.states import ResumeAgentState


def resume_save_node(state: ResumeAgentState):
    """
    持久化当前面试记录的节点
    """
    # 1. 准备目录 (例如: records/20260401)
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    folder_path = Path("resume_records") / date_str
    folder_path.mkdir(parents=True, exist_ok=True)

    time_str = datetime.datetime.now().strftime("%H%M%S")
    file_path = folder_path / f"{time_str}.md"

    # 3. 构造 Markdown 内容
    md_lines = [
        f"- **日期**: {datetime.datetime.now().isoformat()}", 
        "---"
    ]
    
    for msg in state["messages"]:
        if isinstance(msg, SystemMessage):
            # 这里的 System Prompt 可以选存或不存，建议存一下背景
            # md_lines.append(f"> **系统指令**: {msg.content}\n")
            continue
        elif isinstance(msg, HumanMessage):
            # 过滤掉控制指令如 "next"
            if msg.content.lower().strip() not in ["next", "n", "下一题"]:
                md_lines.append(f"### 👤 候选人\n{msg.content}\n")
        elif isinstance(msg, AIMessage):
            md_lines.append(f"### 🤖 Agent\n{msg.content}\n")

    # 4. 写入文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    
    print(f"💾 [系统]: 当前简历面试已保存至 {file_path}")
    
    delete_msgs = [RemoveMessage(id=m.id) for m in state["messages"]]
    return {"messages": delete_msgs, "save_file_path": str(file_path) if file_path else None, "is_end": True}
