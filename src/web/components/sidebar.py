import streamlit as st
from src.web.services.records import RecordService


def render_sidebar():
    with st.sidebar:
        st.title("📚 历史记录")

        record_service = RecordService()
        all_records = record_service.get_all_records()

        if not all_records:
            st.info("暂无面试记录")
            return

        records_by_source: dict[str, dict[str, list]] = {}
        for date_str, records in all_records.items():
            for record in records:
                source = record.source
                if source not in records_by_source:
                    records_by_source[source] = {}
                if date_str not in records_by_source[source]:
                    records_by_source[source][date_str] = []
                records_by_source[source][date_str].append(record)

        for source, records_by_date in records_by_source.items():
            source_label = "💬 知识面试" if source == "records" else "📄 简历面试"
            with st.expander(source_label, expanded=True):
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
                                    st.session_state["selected_record"] = str(
                                        record.file_path
                                    )
                                    st.session_state["last_interview_mode"] = (
                                        st.session_state.get(
                                            "interview_mode", "knowledge"
                                        )
                                    )
                                    st.session_state["view_mode"] = "record"
                                    st.rerun()
                            with col2:
                                if st.button(
                                    "🗑️",
                                    key=f"delete_{record.file_path}",
                                    use_container_width=True,
                                    type="secondary",
                                ):
                                    if record_service.delete_record(
                                        str(record.file_path)
                                    ):
                                        st.success("已删除")
                                        st.rerun()
                                    else:
                                        st.error("删除失败")
