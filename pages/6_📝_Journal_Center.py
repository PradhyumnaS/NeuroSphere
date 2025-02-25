import streamlit as st
from datetime import datetime

st.markdown("<h1 style='text-align: center;'>📝 Journal Center</h1>", unsafe_allow_html=True)
    
if 'gratitude_entries' not in st.session_state:
    st.session_state.gratitude_entries = []

st.markdown("""
### Daily Gratitude Practice
Taking time to appreciate the good things in life can improve mental well-being.
""")

gratitude_text = st.text_area(
    "What are you grateful for today?",
    placeholder="List 3 things you're thankful for..."
)

if st.button("Save Gratitude Entry"):
    if gratitude_text.strip():
        current_time = datetime.now()
        st.session_state.gratitude_entries.append({
            'date': current_time,
            'entry': gratitude_text
        })
        st.success("Gratitude entry saved! 🌟")

if st.session_state.gratitude_entries:
    st.subheader("Your Gratitude Journey")
    for entry in reversed(st.session_state.gratitude_entries):
        with st.expander(f"Entry from {entry['date'].strftime('%Y-%m-%d %H:%M')}"):
            st.write(entry['entry'])