import streamlit as st
import time

st.title("Streamlit Old Content Becomes Gray")

if "data_items" not in st.session_state:
    st.session_state.data_items = ["Data Record A", "Data Record B", "Data Record C"]

if "is_loading" not in st.session_state:
    st.session_state.is_loading = False

# Use a container so we can clear it
content_area = st.empty()

if not st.session_state.is_loading:
    with content_area.container():
        for item in st.session_state.data_items:
            with st.chat_message("user"):
                st.write(item)

        if st.button("Load Next Batch"):
            st.session_state.data_items = []
            st.session_state.is_loading = True
            st.rerun()
else:
    # Clear previous content immediately
    content_area.empty()

    with st.spinner("Fetching new data (Simulating 3-second task)..."):
        time.sleep(3)

    st.session_state.data_items = ["New Fetched Record ✨"]
    st.session_state.is_loading = False
    st.rerun()