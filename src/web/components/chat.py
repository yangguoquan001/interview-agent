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

from langchain_core.messages import HumanMessage

from src.web.services.interview import InterviewService
from src.web.services.records import RecordService


def write_on_screen(
    service: InterviewService, input: dict | None, save_message: bool = True
):
    generator = service.stream_out_tokens(input)
    response = st.write_stream(generator)
    if save_message:
        st.session_state["messages"].append({"role": "assistant", "content": response})


def render_record_viewer():
    """
    渲染历史记录查看器

    产品功能：让用户查看已保存的面试记录
    界面逻辑：
    1. 从 session_state 获取用户选中的记录路径
    2. 如果没有选中，显示提示信息
    3. 否则读取 Markdown 文件内容并渲染
    4. 提供"返回"按钮切回面试或记录列表
    """
    selected_file = st.session_state.get("selected_record")
    if not selected_file:
        st.info("请从左侧选择一条历史记录")
        return

    record_service = RecordService()
    content = record_service.get_record_by_path(selected_file)

    col_back, _ = st.columns([1, 5])
    with col_back:
        if st.button("← 返回", use_container_width=True):
            st.session_state["view_mode"] = "chat"
            st.session_state.pop("selected_record", None)
            st.rerun()

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
                st.session_state["messages"] = []
                st.session_state["generating_question"] = True
                st.rerun()  # 立刻刷新页面！这样按钮和窄列布局就会瞬间消失

    container = st.empty()

    if st.session_state["interview_started"]:
        if st.session_state.get("generating_question", False):
            with st.chat_message("assistant"):
                with st.spinner("🔍 正在根据知识库生成面试题..."):
                    service = st.session_state["interview_service"]
                    initial_input = service.get_initial_input()
                    write_on_screen(service, initial_input)

                st.session_state["generating_question"] = False
            st.rerun()

        # === 阶段 2: 面试进行中 ===
        # 根据 LangGraph 返回的 current_node 判断当前应该做什么
        else:
            # 获取当前 Agent 状态（包含 next 字段，表示下一个要执行的节点）
            state = st.session_state["interview_service"].get_current_state()

            if state and state.next:
                current_node = state.next[0]
                with container.container():
                    input_col, end_col, next_col = st.columns(
                        [8, 1, 1], vertical_alignment="center"
                    )
                    with input_col:
                        input_prompt = (
                            "请输入你的回答..."
                            if current_node == "evaluator"
                            else "请输入你的追问..."
                        )
                        prompt = st.chat_input(input_prompt)
                    with end_col:
                        end_clicked = st.button(
                            "结束面试",
                            use_container_width=True,
                            type="primary",
                            icon="🚪",
                        )
                    with next_col:
                        next_clicked = st.button(
                            "下一题", use_container_width=True, icon="➡️"
                        )

                if end_clicked:
                    container.empty()

                    service = st.session_state["interview_service"]
                    config = service.get_config()
                    service.app.update_state(
                        config,
                        {
                            "is_end": True,
                        },
                    )

                    write_on_screen(service, None, False)
                    st.session_state["messages"] = []
                    st.session_state["interview_started"] = False

                    st.rerun()

                if next_clicked:
                    container.empty()

                    service = st.session_state["interview_service"]
                    config = service.get_config()
                    service.app.update_state(
                        config,
                        {
                            "is_end": True,
                        },
                    )

                    write_on_screen(service, None, False)
                    st.session_state["messages"] = []
                    st.session_state["generating_question"] = True
                    st.rerun()

                if prompt:
                    container.empty()
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    st.session_state["messages"].append(
                        {"role": "user", "content": prompt}
                    )

                    service = st.session_state["interview_service"]
                    config = service.get_config()
                    service.app.update_state(
                        config,
                        {
                            "messages": [HumanMessage(content=prompt)],
                            "user_answer": prompt,
                            "is_end": False,
                        },
                    )

                    with st.chat_message("assistant"):
                        loading_text = (
                            "📝 面试官正在评估回答"
                            if current_node == "evaluator"
                            else "🧠 面试官正在思考你的问题"
                        )
                        with st.spinner(loading_text):
                            write_on_screen(service, None)

                    st.rerun()
