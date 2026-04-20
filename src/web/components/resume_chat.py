import streamlit as st
from pathlib import Path
from src.web.services.interview import InterviewService


def write_on_screen(
    service: InterviewService, input: dict | None, save_message: bool = True
):
    generator = service.stream_out_tokens(input)
    response = st.write_stream(generator)
    if save_message:
        st.session_state["resume"].append({"role": "assistant", "content": response})

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
    """初始化简历面试（第一阶段：解析）"""
    resume_path = save_uploaded_file(resume_file)
    jd_path = save_uploaded_file(jd_file)

    service = InterviewService(mode="resume")
    result, config = service.start_resume_interview(str(resume_path), str(jd_path))

    st.session_state["parsing_status"] = "parsed"
    st.session_state["interview_service"] = service
    st.session_state["interview_config"] = config
    st.session_state["interview_mode"] = "resume"


def generate_interview_questions():
    """生成面试问题（第二阶段）"""
    service = st.session_state.get("interview_service")
    config = st.session_state.get("interview_config")
    if not service or not config:
        return None

    result = service.generate_questions(config)
    question = result.get("question", "") if result else ""
    st.session_state["current_question"] = question
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


def  render_resume_interview_page(mode):
    # 1. 初始化面试服务单例
    if "interview_service" not in st.session_state[mode]:
        st.session_state[mode]["interview_service"] = InterviewService(mode=mode)
    
    # 2. 渲染历史消息
    if "messages" not in st.session_state[mode]:
        st.session_state[mode]["messages"] = []

    # 3. 面试开始标记（控制界面显示"开始按钮"或"聊天窗口"）
    if "interview_started" not in st.session_state[mode]:
        st.session_state[mode]["interview_started"] = False
    
    # === 渲染已有消息历史 ===
    for msg in st.session_state[mode]["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # === 阶段 1: 面试开始前 ===
    # === 渲染初始页面 ===
    # 显示上传简历和JD组件，以及"开始面试"按钮，点击后启动 LangGraph Workflow
    if not st.session_state[mode]["interview_started"]:
        resume_file, jd_file = render_file_uploader()
        if st.button("开始面试"):
            if resume_file and jd_file:
                st.session_state[mode]["interview_started"] = True
                st.session_state[mode]["messages"] = []
                st.session_state[mode]["resume_file"] = resume_file
                st.session_state[mode]["jd_file"] = jd_file
                st.rerun()
            else:
                st.error("请同时上传简历和JD文件")
    
    container = st.empty()
    # === 阶段 2: 面试进行中 ===
    # 根据 LangGraph 返回的 current_node 判断当前应该做什么
    if st.session_state[mode]["interview_started"]:
        state = st.session_state[mode]["interview_service"].get_current_state()
        if not state.next:
            # 先解析简历和JD文件，设置解析状态为 parsed，再生成面试问题
            service = st.session_state[mode]["interview_service"]
            config = service.get_config()
            resume_file = st.session_state[mode]["resume_file"]
            jd_file = st.session_state[mode]["jd_file"]
            resume_path = save_uploaded_file(resume_file)
            jd_path = save_uploaded_file(jd_file)
            initial_input = {
                "resume_file": str(resume_path),
                "jd_file": str(jd_path),
                "messages": [],
                "interview_mode": "resume",
                "resume_info": None,
                "job_description": None,
                "questions": [],
                "current_question_index": 0,
                "follow_up_count": 0,
                "question_summary": "",
                "session": None,
                "final_report": "",
                "should_ask_next": False,
            }
            with st.status("🧐 面试官正在阅读您的简历，请稍候...") as status:
                for event in service.app.stream(initial_input, config=config):
                    if "parser" in event:
                        status.update(label="🤔 面试官正在思考问题...")  
                    if "questioner" in event:
                        status.update(label="🚀 面试准备就绪！", state="complete")
            service = st.session_state[mode]["interview_service"]
            state = service.get_current_state()
            question_records = state.values["question_records"]
            current_question_index = state.values["current_question_index"]
            current_question_record = question_records[current_question_index]
            st.session_state[mode]["messages"].append({
                "role": "assistant",
                "content": current_question_record.questions[0],
            })
            st.rerun()
        else:
            current_node = state.next[0]
            with container.container():
                input_col, end_col = st.columns(
                    [7, 1], vertical_alignment="center"
                )
                with input_col:
                    input_prompt = "请输入你的回答..."
                    prompt = st.chat_input(input_prompt)
                with end_col:
                    end_clicked = st.button(
                        "结束面试",
                        use_container_width=True,
                        type="primary",
                        icon="🚪",
                        key="resume_inteview_end_button"
                    )
            
            if end_clicked:
                container.empty()

                service = st.session_state[mode]["interview_service"]
                config = service.get_config()
                service.app.update_state(
                    config,
                    {
                        "is_end": True,
                    },
                )

                write_on_screen(service, None, False)
                st.session_state[mode]["messages"] = []
                st.session_state[mode]["interview_started"] = False

                st.rerun()
            
            if prompt:
                container.empty()
                with st.chat_message("user"):
                    st.markdown(prompt)


