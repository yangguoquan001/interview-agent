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
                    col1, col2 = st.columns([3, 1], vertical_alignment="center")
                    with col1:
                        if st.button(
                            record.topic,
                            key=f"record_{record.file_path}",
                            use_container_width=True,
                        ):
                            st.session_state["selected_record"] = str(record.file_path)
                            st.session_state["view_mode"] = "record"
                            st.rerun()
                    with col2:
                        if st.button(
                            "🗑️",
                            key=f"delete_{record.file_path}",
                            use_container_width=True,
                            type="secondary"
                        ):
                            if record_service.delete_record(str(record.file_path)):
                                st.success("已删除")
                                st.rerun()
                            else:
                                st.error("删除失败")
