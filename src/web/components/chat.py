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
from langchain_core.messages import AIMessage
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


def stream_response(generator):
    """
    流式响应渲染函数（打字机效果）

    产品需求：PRD 4.2 提到"流式输出打字机效果"
    界面效果：
    1. 使用 st.empty() 创建占位符，动态更新内容
    2. 每次收到一个 chunk（片段），立即追加显示
    3. 末尾添加 ▌ 光标符号，模拟打字进行中的视觉效果
    4. 全部完成后移除光标

    参数 generator: LLM 的流式输出生成器（yield chunk 的迭代器）
    返回: 完整的响应字符串
    """
    response_placeholder = st.empty()
    full_response = ""
    for chunk in generator:
        full_response += chunk
        response_placeholder.markdown(full_response + "▌")
    response_placeholder.markdown(full_response)
    return full_response


def render_chat_window():
    """
    渲染聊天窗口主函数

    这是整个面试 Web 界面的核心函数，处理完整的面试流程：

    面试流程（对应 PRD 4.2 Web 模式）:
    ┌─────────────────────────────────────────────────────────────┐
    │ 1. 初始状态: 显示"开始面试"按钮                               │
    │ 2. 用户点击开始 → scanner 扫描知识库 → questioner 生成问题    │
    │ 3. evaluator 节点: 用户输入回答 → AI 评估反馈              │
    │ 4. chat_node 节点: 用户选择"next"继续或追问                │
    │ 5. 面试完成: 显示完成提示，可重新开始                        │
    └─────────────────────────────────────────────────────────────┘

    状态管理（使用 Streamlit session_state）:
    - interview_service: InterviewService 单例，封装 LangGraph 调用
    - messages: 对话消息历史列表
    - interview_started: 布尔值，标记面试是否已启动
    """

    # === 初始化 Session State ===
    # Streamlit 每次 rerun 都会重新执行脚本，需要用 session_state 持久化状态

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

                service = st.session_state["interview_service"]

                # 显示加载动画（因为 LLM 调用需要较长时间）
                with st.spinner("正在初始化面试..."):
                    # 获取初始输入（启动 scanner 节点）
                    initial_input = service.get_initial_input()

                    # stream() 执行 LangGraph Workflow
                    # stream_mode="updates" 表示每次节点输出时 yield 一个 event
                    for event in service.app.stream(
                        initial_input, service.get_config(), stream_mode="updates"
                    ):
                        # event 结构: {node_name: {messages: [...], ...}}
                        for node_name, values in event.items():
                            if "messages" in values:
                                last_msg = values["messages"][-1]
                                # 只处理 AI 消息（Agent 的回复）
                                if isinstance(last_msg, AIMessage):
                                    st.session_state["messages"].append(
                                        {
                                            "role": "assistant",
                                            "content": last_msg.content,
                                        }
                                    )

                # 重新执行脚本，更新界面显示 Agent 生成的问题
                st.rerun()

    # === 阶段 2: 面试进行中 ===
    # 根据 LangGraph 返回的 current_node 判断当前应该做什么
    if st.session_state["interview_started"]:
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

                    # 2. 调用 Service 提交回答，获取流式响应
                    service = st.session_state["interview_service"]
                    full_response = stream_response(service.submit_answer(prompt))

                    # 3. 把 AI 评估结果加入消息历史
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": full_response}
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
                    # 1. 先把用户输入加入消息历史
                    st.session_state["messages"].append(
                        {"role": "user", "content": prompt}
                    )
                    service = st.session_state["interview_service"]

                    # 2. 判断用户意图：继续下一题 OR 追问
                    if prompt.lower().strip() in ["next", "n", "下一题"]:
                        # 进入下一题（触发 questioner 节点生成新问题）
                        full_response = stream_response(service.next_question())
                    else:
                        # 追问（触发 chat_node 处理技术问题）
                        full_response = stream_response(
                            service.continue_interview(prompt)
                        )

                    # 3. 把 AI 回复加入消息历史
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": full_response}
                    )

                    # 4. 触发 rerun，继续 Workflow
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
