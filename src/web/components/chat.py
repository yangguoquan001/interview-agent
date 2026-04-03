import streamlit as st
from src.web.services.interview import InterviewService
from src.web.services.records import RecordService


def render_record_viewer():
    selected_file = st.session_state.get("selected_record")
    if not selected_file:
        st.info("请从左侧选择一条历史记录")
        return

    record_service = RecordService()
    content = record_service.get_record_by_path(selected_file)
    st.markdown(content)


def stream_response(generator):
    response_placeholder = st.empty()
    full_response = ""
    for chunk in generator:
        full_response += chunk
        response_placeholder.markdown(full_response + "▌")
    response_placeholder.markdown(full_response)
    return full_response


def render_chat_window():
    if "interview_service" not in st.session_state:
        st.session_state["interview_service"] = InterviewService()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "interview_started" not in st.session_state:
        st.session_state["interview_started"] = False

    st.title("🎯 AI 模拟面试")

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state["interview_started"]:
        if st.button("开始面试"):
            st.session_state["interview_started"] = True
            st.session_state["messages"] = []
            st.rerun()

    if st.session_state["interview_started"]:
        state = st.session_state["interview_service"].get_current_state()

        if state and state.next:
            current_node = state.next[0]

            if current_node == "evaluator":
                prompt = st.chat_input("请输入你的回答...")
                if prompt:
                    st.session_state["messages"].append(
                        {"role": "user", "content": prompt}
                    )
                    service = st.session_state["interview_service"]
                    full_response = stream_response(service.submit_answer(prompt))
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": full_response}
                    )
                    st.rerun()

            elif current_node == "chat_node":
                prompt = st.chat_input("输入 'next' 进入下一题，或输入你的追问...")
                if prompt:
                    st.session_state["messages"].append(
                        {"role": "user", "content": prompt}
                    )
                    service = st.session_state["interview_service"]

                    if prompt.lower().strip() in ["next", "n", "下一题"]:
                        full_response = stream_response(service.next_question())
                    else:
                        full_response = stream_response(
                            service.continue_interview(prompt)
                        )

                    st.session_state["messages"].append(
                        {"role": "assistant", "content": full_response}
                    )
                    st.rerun()

        else:
            st.success("🎉 本轮面试已完成！")
            if st.button("重新开始"):
                st.session_state["interview_started"] = False
                st.session_state["messages"] = []
                st.rerun()
