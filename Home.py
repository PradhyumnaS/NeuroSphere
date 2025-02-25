import streamlit as st

st.set_page_config(
    page_title="NeuroSphere",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🧠 NeuroSphere")
st.markdown("*Your Safe Space for Healing: Chat, Journal, Grow.*")
st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.markdown("""
## Welcome to NeuroSphere

NeuroSphere is a comprehensive mental health support application that combines AI-powered chat therapy with interactive wellness tools. Navigate through our features using the sidebar.

### How to Use NeuroSphere

1. **Choose a Feature**: Select from our various tools in the sidebar
2. **Explore and Engage**: Each page offers unique mental wellness activities
3. **Track Your Progress**: Many features save your data between sessions

### Getting Started

We recommend starting with our AI Chatbot, which can provide personalized mental health guidance and support.
""")
st.markdown('</div>', unsafe_allow_html=True)

with st.expander("🆘 Mental Health Resources"):
    st.header("Emergency Contacts")
    
    emergency_contacts = {
        "National Crisis Hotline": "1-800-273-8255",
        "Crisis Text Line": "Text HOME to 741741",
        "Emergency Services": "911"
    }
    
    for service, contact in emergency_contacts.items():
        st.markdown(f"**{service}**: {contact}")
    
    st.header("Quick Mental Health Tips")
    tips = [
        "Practice deep breathing exercises",
        "Maintain a regular sleep schedule",
        "Exercise regularly",
        "Stay connected with loved ones",
        "Practice mindfulness",
        "Set realistic goals",
        "Take breaks when needed"
    ]
    
    for tip in tips:
        st.markdown(f"• {tip}")

