import streamlit as st
from dotenv import load_dotenv

from src.schemas.enums import InterviewMode
from src.web.components.knowledge_chat import render_knowledge_interview_page, render_record_viewer
from src.web.components.resume_chat import render_resume_interview_page
from src.web.components.sidebar import render_sidebar
from src.web.services.interview import InterviewService

load_dotenv()


def initial_session_state(mode: InterviewMode):
    if mode not in st.session_state:
        st.session_state[mode] = {}

    # 面试服务单例
    if "interview_service" not in st.session_state[mode]:
        st.session_state[mode]["interview_service"] = InterviewService(mode=mode)

    # 消息历史（用户和助手的对话记录，用于渲染聊天界面）
    if "messages" not in st.session_state[mode]:
        st.session_state[mode]["messages"] = []

    # 面试开始标记（控制界面显示"开始按钮"或"聊天窗口"）
    if "interview_started" not in st.session_state[mode]:
        st.session_state[mode]["interview_started"] = False


def main():
    st.set_page_config(layout="wide", page_title="AI 模拟面试")

    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = "chat"

    render_sidebar()

    if st.session_state["view_mode"] == "record":
        render_record_viewer()
        return

    st.title("🎯 AI 模拟面试")

    tab_knowledge, tab_resume = st.tabs(["💬 知识面试", "📄 简历面试"])

    with tab_knowledge:
        mode = InterviewMode.KNOWLEDGE
        initial_session_state(mode)
        render_knowledge_interview_page(st.session_state[mode])

    with tab_resume:
        mode = InterviewMode.RESUME
        initial_session_state(mode)
        render_resume_interview_page(st.session_state[mode])


if __name__ == "__main__":
    main()
