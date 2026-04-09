import streamlit as st
import time

st.title("Streamlit Old Content Becomes Gray")

# 1. Initialize simulated data
if "data_items" not in st.session_state:
    st.session_state.data_items = ["Data Record A", "Data Record B", "Data Record C"]

if "is_loading" not in st.session_state:
    st.session_state.is_loading = False

# 2. Render data items
# Expected behavior: When is_loading is True, data_items is an empty list [], 
# so nothing should be displayed here.
for item in st.session_state.data_items:
    with st.chat_message("user"):
        st.write(item)

# 3. Trigger logic
if not st.session_state.is_loading:
    if st.button("Load Next Batch"):
        st.session_state.data_items = []  # Clear the data
        st.session_state.is_loading = True # Set loading flag
        st.rerun() # Force script restart to enter the "empty data" state
else:
    # --- Critical Reproduction Point ---
    # At this point, the script has rerun, and data_items is now an empty list [].
    # Logically, the loop above should not render any messages.
    # However, because the sleep below simulates a time-consuming task,
    # Streamlit "grays out" the UI from the previous run and keeps it on screen.
    with st.spinner("Fetching new data (Simulating 3-second task)..."):
        time.sleep(3) 
    
    st.session_state.data_items = ["New Fetched Record ✨"]
    st.session_state.is_loading = False
    st.rerun()