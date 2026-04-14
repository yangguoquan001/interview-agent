import streamlit as st
from pathlib import Path
from src.web.services.interview import InterviewService


def render_file_uploader():
    """渲染文件上传组件"""
    col1, col2 = st.columns(2)

    with col1:
        resume_file = st.file_uploader("上传简历 (PDF/TXT)", type=["pdf", "txt"])

    with col2:
        jd_file = st.file_uploader("上传职位描述 (PDF/TXT)", type=["pdf", "txt"])

    return resume_file, jd_file


def save_uploaded_file(uploaded_file) -> Path:
    """保存上传的文件"""
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def init_resume_interview(resume_file, jd_file):
    """初始化简历面试"""
    resume_path = save_uploaded_file(resume_file)
    jd_path = save_uploaded_file(jd_file)

    service = InterviewService(mode="resume")
    result, config = service.start_resume_interview(str(resume_path), str(jd_path))

    st.session_state["interview_service"] = service
    st.session_state["interview_config"] = config
    st.session_state["interview_mode"] = "resume"

    return result


def render_resume_chat():
    """渲染简历面试聊天界面"""
    if (
        "interview_service" not in st.session_state
        or "interview_config" not in st.session_state
    ):
        st.warning("请先上传简历和JD文件")
        return

    service = st.session_state["interview_service"]
    config = st.session_state["interview_config"]

    state = service.get_current_state(config)
    current_question = state.values.get("question", "")
    is_ended = state.values.get("is_end", False)
    final_report = state.values.get("final_report", "")

    if is_ended and final_report:
        st.subheader("面试评估报告")
        st.markdown(final_report)
        return

    if current_question:
        st.markdown(f"**面试官:** {current_question}")

    if answer := st.chat_input("请输入你的回答..."):
        with st.spinner("面试官正在思考..."):
            result = service.submit_answer(answer, config)

            next_question = result.get("question", "")
            is_ended = result.get("is_end", False)

            if is_ended:
                final_report = result.get("final_report", "")
                st.session_state["is_interview_ended"] = True
                st.session_state["final_report"] = final_report
            else:
                st.session_state["current_question"] = next_question

        st.rerun()


def render_resume_interview_page():
    """渲染简历面试页面"""

    if "is_interview_ended" not in st.session_state:
        st.session_state["is_interview_ended"] = False

    if not st.session_state["is_interview_ended"]:
        resume_file, jd_file = render_file_uploader()

        if st.button("开始面试"):
            if resume_file and jd_file:
                with st.spinner("正在解析简历和JD..."):
                    init_resume_interview(resume_file, jd_file)
                st.rerun()
            else:
                st.error("请同时上传简历和JD文件")
    else:
        if st.button("重新开始面试"):
            for key in [
                "interview_service",
                "interview_config",
                "is_interview_ended",
                "final_report",
                "current_question",
            ]:
                st.session_state.pop(key, None)
            st.session_state["view_mode"] = "chat"
            st.rerun()

    if (
        "interview_service" in st.session_state
        and "interview_config" in st.session_state
    ):
        render_resume_chat()
