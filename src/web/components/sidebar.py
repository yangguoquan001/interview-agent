import streamlit as st
from src.web.services.records import RecordService


def render_sidebar():
    with st.sidebar:
        st.title("📚 历史记录")

        record_service = RecordService()
        records_by_date = record_service.get_all_records()

        if not records_by_date:
            st.info("暂无面试记录")
            return

        for date_str, records in records_by_date.items():
            with st.expander(f"📅 {date_str}", expanded=True):
                for record in records:
                    btn_label = f"{record.topic}"
                    if st.button(
                        btn_label,
                        key=f"record_{record.file_path}",
                        use_container_width=True,
                    ):
                        st.session_state["selected_record"] = str(record.file_path)
                        st.session_state["view_mode"] = "record"
                        st.rerun()
