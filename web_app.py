import streamlit as st
from dotenv import load_dotenv

from src.web.components.sidebar import render_sidebar
from src.web.components.chat import render_chat_window, render_record_viewer
from src.web.components.resume_chat import render_resume_interview_page

load_dotenv()


def main():
    st.set_page_config(layout="wide", page_title="AI 模拟面试")

    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = "chat"

    if "interview_mode" not in st.session_state:
        st.session_state["interview_mode"] = "knowledge"

    render_sidebar()
    if st.session_state["view_mode"] == "record":
        render_record_viewer()

    st.title("🎯 AI 模拟面试")

    tab_knowledge, tab_resume = st.tabs(["💬 知识面试", "📄 简历面试"])

    with tab_knowledge:
        st.session_state["interview_mode"] = "knowledge"
        # if st.session_state["view_mode"] == "record":
        #     render_record_viewer()
        # else:
        #     render_chat_window()
        render_chat_window()

    with tab_resume:
        st.session_state["interview_mode"] = "resume"
        render_resume_interview_page()


if __name__ == "__main__":
    main()
