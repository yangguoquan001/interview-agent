import streamlit as st
from dotenv import load_dotenv

from src.web.components.sidebar import render_sidebar
from src.web.components.chat import render_chat_window, render_record_viewer

load_dotenv()


def main():
    st.set_page_config(layout="wide", page_title="AI 模拟面试")

    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = "chat"

    render_sidebar()

    if st.session_state["view_mode"] == "record":
        render_record_viewer()
    else:
        render_chat_window()


if __name__ == "__main__":
    main()
