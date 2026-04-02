import time

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from src.graph.workflow import create_graph

load_dotenv()


def print_agent_output(event):
    """
    辅助函数：从 stream 事件中提取并打印 Agent 的最新回复
    """
    # event 的 key 是当前运行完的 node 名字
    for node_name, values in event.items():
        if "messages" in values:
            last_msg = values["messages"][-1]
            if isinstance(last_msg, AIMessage):
                # 打印内容，可以根据内容前缀判断是“题目”还是“反馈”
                print(f"\n[Agent]: {last_msg.content}")


def main():
    with SqliteSaver.from_conn_string("checkpoints.db") as saver:
        app = create_graph(saver)
        # thread_id 使用时间戳作为唯一标识
        config = {"configurable": {"thread_id": f"daily_study_{int(time.time())}"}}

        state = app.get_state(config)
        if not state.values:
            # 如果是第一次运行，初始化输入
            initial_input = {
                "files_to_read": [], # scanner 节点会填充这个
                "messages": [],
                "current_file": "",
                "question": "",
                "answer": "",
                "feedback": "",
                "topic": "",
                "difficulty": "",
                "thread_id": config["configurable"]["thread_id"],
            }
            print("\n--- 正在初始化面试流程 ---")
            for event in app.stream(initial_input, config, stream_mode="updates"):
                print_agent_output(event)
        else:
            print("\n--- 检测到已有进度，正在恢复 ---")

        while True:
            state = app.get_state(config)
            if not state.next:
                print("\n[系统]: 今日练习已全部完成，再见！")
                break

            current_node = state.next[0]
            # 1. 如果当前停在 evaluator 前，说明在等用户回答题目
            if current_node == "evaluator":
                user_input = input("\n[回答题目] (输入 'skip' 跳过): ")
                app.update_state(config, {"messages": [HumanMessage(content=user_input)], "answer": user_input})
                
            # 2. 如果停在 chat_node 前，说明刚评价完，等待用户追问或下一题
            elif state.next[0] == "chat_node":
                user_input = input("\n[评价已出] (输入 'next' 进入下一题，或输入你的追问): ")
                app.update_state(config, {"messages": [HumanMessage(content=user_input)]})
            # 执行下一步
            for event in app.stream(None, config, stream_mode="updates"):
                # 打印 feedback 或 question
                print_agent_output(event)

if __name__ == "__main__":
    main()
