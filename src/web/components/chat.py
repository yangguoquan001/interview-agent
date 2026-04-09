"""
Chat.py 详细注释 - AI 模拟面试 Web 界面

本模块实现了 Interview Agent 的 Streamlit 聊天界面，负责：
1. 面试流程的 UI 展示（开始面试 → 出题 → 回答 → 评估 → 追问）
2. 与 LangGraph Agent 的交互（通过 InterviewService）
3. 消息历史的管理和渲染

核心概念：
- interview_started: 标记面试是否已经开始
- messages: 存储对话历史 [{role: "user"|"assistant", content: "..."}]
- current_node: 来自 AgentState.next，表示当前所在的 Workflow 节点
"""

import streamlit as st

from langchain_core.messages import BaseMessageChunk, HumanMessage

from src.web.services.interview import InterviewService
from src.web.services.records import RecordService


def render_record_viewer():
    """
    渲染历史记录查看器

    产品功能：让用户查看已保存的面试记录
    界面逻辑：
    1. 从 session_state 获取用户选中的记录路径
    2. 如果没有选中，显示提示信息
    3. 否则读取 Markdown 文件内容并渲染
    """
    selected_file = st.session_state.get("selected_record")
    if not selected_file:
        st.info("请从左侧选择一条历史记录")
        return

    record_service = RecordService()
    content = record_service.get_record_by_path(selected_file)
    st.markdown(content)


def render_chat_window():
    # 1. 面试服务单例（封装 LangGraph Workflow 调用）
    if "interview_service" not in st.session_state:
        st.session_state["interview_service"] = InterviewService()

    # 2. 消息历史（用户和助手的对话记录，用于渲染聊天界面）
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # 3. 面试开始标记（控制界面显示"开始按钮"或"聊天窗口"）
    if "interview_started" not in st.session_state:
        st.session_state["interview_started"] = False

    # === 界面标题 ===
    st.title("🎯 AI 模拟面试")

    # === 渲染已有消息历史 ===
    # 遍历 session_state 中的所有消息，用 st.chat_message 渲染
    # st.chat_message 会自动应用聊天气泡样式（user 右对齐，assistant 左对齐）
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # === 阶段 1: 面试开始前 ===
    # 显示"开始面试"按钮，点击后启动 LangGraph Workflow
    if not st.session_state["interview_started"]:
        _, center, _ = st.columns(3)
        with center:
            if st.button("开始面试", type="primary"):
                st.session_state["interview_started"] = True
                st.session_state["messages"] = []  # 清空旧消息
                st.session_state["generating_question"] = True
                st.rerun()  # 立刻刷新页面！这样按钮和窄列布局就会瞬间消失

    if st.session_state["interview_started"]:
        if st.session_state.get("generating_question", False):
            with st.spinner("🔍 正在根据知识库生成面试题..."):
                with st.chat_message("assistant"):
                    service = st.session_state["interview_service"]
                    initial_input = service.get_initial_input()
                    generator = service.stream_out_tokens(initial_input, ["questioner"])
                    response = st.write_stream(generator)
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": response}
                    )

                st.session_state["generating_question"] = False
            st.rerun()

        # === 阶段 2: 面试进行中 ===
        # 根据 LangGraph 返回的 current_node 判断当前应该做什么
        else:
            # 获取当前 Agent 状态（包含 next 字段，表示下一个要执行的节点）
            state = st.session_state["interview_service"].get_current_state()

            # state.next 是节点名称列表，如 ["evaluator"] 或 ["chat_node"]
            if state and state.next:
                current_node = state.next[0]

                # --- 分支 A: evaluator 节点 ---
                # Agent 状态要求评估用户回答，此时需要用户输入回答
                if current_node == "evaluator":
                    # st.chat_input 在底部显示输入框，placeholder 显示提示文字
                    prompt = st.chat_input("请输入你的回答...")
                    if prompt:
                        # 1. 先把用户回答加入消息历史
                        st.session_state["messages"].append(
                            {"role": "user", "content": prompt}
                        )
                        # 立即在界面上回显用户输入
                        with st.chat_message("user"):
                            st.markdown(prompt)

                        # 2. 调用 Service 提交回答，获取流式响应
                        service = st.session_state["interview_service"]
                        config = service.get_config()

                        # 这里的字典 key 必须和你定义的 AgentState 保持一致
                        service.app.update_state(
                            config,
                            {
                                "messages": [HumanMessage(content=prompt)],
                                "user_answer": prompt,
                            },
                        )
                        with st.chat_message("assistant"):
                            generator = service.stream_out_tokens(None, ["evaluator"])
                            response = st.write_stream(generator)
                            # 3. 把 AI 评估结果加入消息历史
                            st.session_state["messages"].append(
                                {"role": "assistant", "content": response}
                            )

                        # 4. 触发 rerun，让 Workflow 继续执行到下一个节点
                        st.rerun()

                # --- 分支 B: chat_node 节点 ---
                # 用户已提交回答，AI 已给出评估，此时用户可以选择：
                # - 输入"next/n/下一题"进入下一题
                # - 输入其他内容进行追问
                elif current_node == "chat_node":
                    prompt = st.chat_input("输入 'next' 进入下一题，或输入你的追问...")
                    if prompt:
                        # 判断是否是进入下一题
                        is_next = prompt.lower().strip() in ["next", "n", "下一题"]
                        
                        service = st.session_state["interview_service"]
                        config = service.get_config()
                        service.app.update_state(
                            config, 
                            {"messages": [HumanMessage(content=prompt)], "user_answer": prompt} 
                        )
                        
                        if is_next:
                            st.session_state["messages"] = []
                            st.session_state["generating_question"] = True
                            st.rerun()
                        else:
                            with st.chat_message("assistant"):
                                generator = service.stream_out_tokens(None, ["chat_node", "questioner"])
                                response = st.write_stream(generator)
                                st.session_state["messages"].append({"role": "assistant", "content": response})
                            st.rerun()

            # === 阶段 3: 面试完成 ===
            # state.next 为空，说明 Workflow 已完成所有节点
            else:
                st.success("🎉 本轮面试已完成！")
                if st.button("重新开始"):
                    # 重置状态，让用户可以开始新一轮面试
                    st.session_state["interview_started"] = False
                    st.session_state["messages"] = []
                    st.rerun()
