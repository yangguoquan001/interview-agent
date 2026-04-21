import streamlit as st

from langchain_core.messages import AIMessage, AIMessageChunk
from pathlib import Path


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


def  render_resume_interview_page(session_state: dict | None):
    for msg in session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not session_state["interview_started"]:
        resume_file, jd_file = render_file_uploader()
        if st.button("开始面试"):
            if resume_file and jd_file:
                session_state["interview_started"] = True
                session_state["messages"] = []
                session_state["resume_file"] = resume_file
                session_state["jd_file"] = jd_file
                st.rerun()
            else:
                st.error("请同时上传简历和JD文件")
    
    container = st.empty()

    if session_state["interview_started"]:
        graph_state = session_state["interview_service"].get_current_state()
        if not graph_state.next and not graph_state.values.get("is_end", False):
            # 先解析简历和JD文件，设置解析状态为 parsed，再生成面试问题
            service = session_state["interview_service"]
            config = service.get_config()
            resume_file = session_state["resume_file"]
            jd_file = session_state["jd_file"]
            resume_path = save_uploaded_file(resume_file)
            jd_path = save_uploaded_file(jd_file)
            initial_input = {
                "resume_file": str(resume_path),
                "jd_file": str(jd_path),
                "messages": [],
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
            service = session_state["interview_service"]
            graph_state = service.get_current_state()
            question_records = graph_state.values["question_records"]
            current_question_index = graph_state.values["current_question_index"]
            current_question_record = question_records[current_question_index]
            session_state["messages"].append({
                "role": "assistant",
                "content": current_question_record.questions[0],
            })
            st.rerun()
        else:
            if not graph_state.next:
                with st.chat_message("assistant"):
                    st.markdown(f"面试已结束，可前往{graph_state.values['save_file_path']}中查看面试过程及总结和评价")
                _, center, _ = st.columns(3)
                with center:
                    if st.button("重新面试", type="primary"):
                        session_state["interview_started"] = False
                        session_state["messages"] = []
                        st.rerun()  # 立刻刷新页面！这样按钮和窄列布局就会瞬间消失
            else:
                current_node = graph_state.next[0]
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

                    service = session_state["interview_service"]
                    config = service.get_config()
                    service.app.update_state(
                        config,
                        {
                            "is_end": True,
                        },
                    )

                    config = service.get_config()
                    full_content = ""
                    for msg_chunk, metadata in service.app.stream(
                        None, config, stream_mode="messages"
                    ):  
                        if hasattr(msg_chunk, "content") and msg_chunk.content:
                            full_content += msg_chunk.content
                    if full_content:
                        session_state["messages"].append({"role": "assistant", "content": full_content}) 
                    session_state["messages"] = []
                    session_state["interview_started"] = False

                    st.rerun()
                
                if prompt:
                    container.empty()
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    session_state["messages"].append(
                        {"role": "user", "content": prompt}
                    )

                    service = session_state["interview_service"]
                    config = service.get_config()
                    service.app.update_state(
                        config,
                        {
                            "last_answer": prompt,
                        },
                    )

                    last_node = None
                    full_content = ""
                    placeholder = None

                    # 获取流式输出
                    for msg_chunk, metadata in service.app.stream(None, config, stream_mode="messages"):
                        node_name = metadata.get("langgraph_node")
                        
                        if isinstance(msg_chunk, (AIMessage, AIMessageChunk)): #TODO 删除AIMessage
                            
                            # 检测节点切换，开启新气泡
                            if node_name != last_node:
                                # 如果上一个气泡有内容，先存档
                                if last_node and full_content:
                                    session_state["messages"].append({"role": "assistant", "content": full_content, "node": last_node})
                                
                                last_node = node_name
                                full_content = ""
                                label = "正在总结..." if current_node == "summary" else "正在思考问题..."
                                
                                # 开启新气泡并显示状态
                                with st.chat_message("assistant"):
                                    placeholder = st.empty()
                                    placeholder.markdown(f"*{label}* ⏳")

                            if msg_chunk.content:
                                full_content += msg_chunk.content
                                placeholder.markdown(full_content + "▌")

                    # 整个循环结束后，存入最后一个节点的 AI 输出
                    if full_content:
                        session_state["messages"].append({"role": "assistant", "content": full_content, "node": last_node})

                    st.rerun()
                
                            

