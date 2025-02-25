import streamlit as st
from streamlit_drawable_canvas import st_canvas
import pandas as pd
import time

st.title("🎨 Therapeutic Activities")

st.markdown("""
<style>
    .activity-card {
        background: linear-gradient(to right bottom, #ffffff, #f5f7f9);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .activity-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }
    .activity-title {
        color: #236860;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    .stButton > button {
        background-color: #236860;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

activities = {
    "Mindful Drawing": {
        "description": "Express your emotions through free-form drawing. No artistic skills required!",
        "icon": "🖌️"
    },
    "Gratitude Practice": {
        "description": "Write down three things you're grateful for today.",
        "icon": "🙏"
    },
    "Sound Bath": {
        "description": "Immerse yourself in calming sounds to promote relaxation and healing.",
        "icon": "🔊"
    },
    "Positive Affirmations": {
        "description": "Practice repeating positive statements to shift your mindset.",
        "icon": "✨"
    }
}

activity_names = list(activities.keys())
selected_activity = st.selectbox("Choose an activity:", activity_names)

st.markdown(f"""
<div class="activity-card">
    <div class="activity-title">{activities[selected_activity]['icon']} {selected_activity}</div>
    <p>{activities[selected_activity]['description']}</p>
</div>
""", unsafe_allow_html=True)

if selected_activity == "Mindful Drawing":
    st.write("Use the canvas below to express how you're feeling right now. Focus on the process, not the result.")
    
    drawing_mode = st.selectbox(
        "Drawing tool:",
        ("freedraw", "line", "rect", "circle", "transform")
    )
    
    stroke_width = st.slider("Stroke width: ", 1, 25, 3)
    stroke_color = st.color_picker("Stroke color: ", "#236860")
    bg_color = st.color_picker("Background color: ", "#FFFFFF")
    
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=400,
        drawing_mode=drawing_mode,
        key="canvas",
    )
    
    if st.button("💾 Save Your Creation"):
        st.success("Your artwork has been saved to your profile!")
        
elif selected_activity == "Gratitude Practice":
    st.write("Take a moment to reflect on what you're thankful for today.")
    
    gratitude_1 = st.text_area("I am grateful for...", "", key="gratitude1")
    gratitude_2 = st.text_area("I appreciate...", "", key="gratitude2")
    gratitude_3 = st.text_area("I'm thankful for...", "", key="gratitude3")
    
    if st.button("📝 Save Gratitude Journal"):
        if gratitude_1 or gratitude_2 or gratitude_3:
            if 'gratitude_entries' not in st.session_state:
                st.session_state.gratitude_entries = []
                
            entry = {
                'date': pd.Timestamp.now().strftime("%Y-%m-%d"),
                'entries': [gratitude_1, gratitude_2, gratitude_3]
            }
            
            st.session_state.gratitude_entries.append(entry)
            st.success("Your gratitude journal has been saved!")
        else:
            st.warning("Please enter at least one gratitude note.")

elif selected_activity == "Sound Bath":
    st.write("Choose a calming sound and allow yourself to be present with it.")
    
    sound_options = {
        "Ocean Waves": "ocean.mp3",
        "Forest Ambience": "forest.mp3",
        "Rain Sounds": "rain.mp3",
        "Meditation Bell": "meditation.mp3"
    }
    
    selected_sound = st.selectbox("Select a sound:", list(sound_options.keys()))
    
    if st.button("▶️ Play Sound Bath"):
        st.audio(f"assets/audio/{sound_options[selected_sound]}", format='audio/mp3', loop=True)
        
        with st.spinner("Sound bath in progress..."):
            duration = 60
            progress_bar = st.progress(0)
            
            for i in range(duration):
                progress_bar.progress((i + 1) / duration)
                time.sleep(1)
                
            st.success("Sound bath complete. How do you feel now?")
            
elif selected_activity == "Positive Affirmations":
    st.write("Repeat these affirmations to yourself, or create your own.")
    
    affirmations = [
        "I am worthy of love and respect",
        "I am capable of handling life's challenges",
        "My feelings are valid and important",
        "I am growing and learning every day",
        "I choose peace over worry",
        "I am exactly where I need to be"
    ]
    
    custom_affirmation = st.text_input("Create your own affirmation:")
    
    if custom_affirmation:
        affirmations.append(custom_affirmation)
    
    st.markdown("### Today's Affirmations")
    
    for i, affirmation in enumerate(affirmations):
        st.markdown(f"""
        <div class="activity-card" style="background: linear-gradient(45deg, rgba(35, 104, 96, 0.1), rgba(35, 104, 96, 0.05));">
            <p style="font-size: 1.2rem; text-align: center; font-style: italic;">"{affirmation}"</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 Practice Daily"):
        st.balloons()
        st.success("Remember to practice these affirmations throughout your day!")