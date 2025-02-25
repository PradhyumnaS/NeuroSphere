import streamlit as st
import time

st.title("🫁 Breathing Center")

st.markdown("""
    <style>
    @keyframes breathe {
        0% { transform: scale(1); opacity: 0.3; }
        50% { transform: scale(1.5); opacity: 0.8; }
        100% { transform: scale(1); opacity: 0.3; }
    }
    .breathing-circle {
        width: 150px;
        height: 150px;
        background: radial-gradient(circle, #236860, #2E7D32);
        border-radius: 50%;
        margin: 40px auto;
        animation: breathe 8s infinite ease-in-out;
        box-shadow: 0 0 30px rgba(46, 125, 50, 0.3);
    }
    .exercise-card {
        background: linear-gradient(to right bottom, #ffffff, #f8f9fa);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        color: #1a1a1a;
        border: 1px solid rgba(46, 125, 50, 0.1);
    }
    .timer-text {
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        color: #2E7D32;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    div[data-testid="stSelectbox"] {
        width: 100%;
    }
    .stButton > button {
        width: 100%;
        padding: 0.5rem 1rem;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

container = st.container()

with container:
    st.markdown('<div class="breathing-circle"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        breathing_exercise = st.selectbox(
            "Select a breathing exercise:",
            ["Box Breathing", "4-7-8 Breathing", "Deep Breathing"],
            key="breathing_select"
        )
        
        descriptions = {
            "Box Breathing": """🔲 Box breathing is a powerful stress-relief technique used by Navy SEALs. 
            Perfect for maintaining calm and focus under pressure.""",
            "4-7-8 Breathing": """🌙 The 4-7-8 breathing technique helps reduce anxiety and aids better sleep. 
            Practiced twice daily, it becomes more effective over time.""",
            "Deep Breathing": """🌊 Deep breathing is a simple yet effective way to reduce stress and increase mindfulness. 
            It helps activate your body's natural relaxation response."""
        }
        
        st.markdown(
            f'<div class="exercise-card">{descriptions[breathing_exercise]}</div>', 
            unsafe_allow_html=True
        )
        
        controls_col1, controls_col2 = st.columns([2, 2])
        with controls_col1:
            start_button = st.button("Start Exercise 🎯", key="start_breathing", use_container_width=True)
        with controls_col2:
            play_music = st.checkbox("🎵 Play Meditation Music", key="play_music")
            
        if play_music:
            st.audio('assets/audio/meditation.mp3', format='audio/mpeg', loop=True)
        
        if start_button:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            if breathing_exercise == "Box Breathing":
                for cycle in range(4):
                    for phase, duration in [("Inhale", 4), ("Hold", 4), ("Exhale", 4), ("Hold", 4)]:
                        status_text.markdown(
                            f'<p class="timer-text">{phase}</p>', unsafe_allow_html=True)
                        for i in range(duration):
                            progress_bar.progress((i + 1) / duration)
                            time.sleep(1)
                        progress_bar.progress(0)
                        
            elif breathing_exercise == "4-7-8 Breathing":
                for cycle in range(4):
                    for phase, duration in [("Inhale", 4), ("Hold", 7), ("Exhale", 8)]:
                        status_text.markdown(
                            f'<p class="timer-text">{phase}</p>', unsafe_allow_html=True)
                        for i in range(duration):
                            progress_bar.progress((i + 1) / duration)
                            time.sleep(1)
                        progress_bar.progress(0)
                        
            elif breathing_exercise == "Deep Breathing":
                for cycle in range(4):
                    for phase, duration in [("Inhale Deeply", 4), ("Hold", 2), ("Exhale Slowly", 4), ("Rest", 2)]:
                        status_text.markdown(
                            f'<p class="timer-text">{phase}</p>', unsafe_allow_html=True)
                        for i in range(duration):
                            progress_bar.progress((i + 1) / duration)
                            time.sleep(1)
                        progress_bar.progress(0)
                        
            st.success("✨ Exercise completed! Take a moment to notice how you feel.")