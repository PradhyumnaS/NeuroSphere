import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
import random
import time
import requests
import streamlit as st
import time
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv
from reinforcement import PromptOptimizationRL

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = 'gemini-2.0-flash'

if 'rl_agent' not in st.session_state:
    st.session_state.rl_agent = PromptOptimizationRL()

def init_styles():
    st.set_page_config(
        page_title="NeuroSphere",
        page_icon="🧠",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    page_bg_style = """
    <style>
     .stButton button {
        background-color: #236860;
        color: white;
        padding: 15px 30px;
        border-radius: 25px;
        width: 100%;
    }
    .stTab {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
    }
    .css-1d391kg {
        padding: 1rem;
    }
    </style>
    """
    
    st.markdown(page_bg_style, unsafe_allow_html=True)

def generate_response(user_message):
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
        
        optimized_prompt = st.session_state.rl_agent.generate_optimized_prompt(user_message)
        
        response = model.generate_content(optimized_prompt)
        response_text = response.text
        
        return response_text
        
    except Exception as e:
        st.error(f"Error generating response: {e}")
        print(f"Detailed error: {str(e)}")
        return "I apologize, but I'm having trouble processing your request at the moment. Please try again."

def record_and_transcribe():
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            with st.spinner("Adjusting for ambient noise..."):
                recognizer.adjust_for_ambient_noise(source, duration=1)
            
            st.info("🎤 Listening... Please speak now.")
            
            audio_data = recognizer.listen(
                source,
                timeout=None,
                phrase_time_limit=None
            )
            
            with st.spinner("Transcribing..."):
                try:
                    transcription = recognizer.recognize_google(audio_data)
                    return transcription
                except sr.UnknownValueError:
                    st.error("Could not understand the audio. Please try again.")
                except sr.RequestError:
                    st.error("Could not connect to speech recognition service.")
    except Exception as e:
        st.error(f"Error accessing microphone: {e}")
    
    return None

def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        audio_file = "response.mp3"
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None

def chatbot_page():
    st.header("💭 Chat with Me")
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    st.write("### Choose Input Method")
    input_method = st.radio(
        "Input method selection",
        ["Text Input", "Voice Recording (5-10 seconds recommended)"],
        label_visibility="collapsed"
    )
    
    if input_method == "Text Input":
        user_text = st.text_input("Type your message:", key="text_input")
        if st.button("Send"):
            if user_text:
                process_message(user_text)
    
    else:
        if st.button("🎤 Start Recording"):
            transcription = record_and_transcribe()
            if transcription:
                st.success(f"You said: {transcription}")
                process_message(transcription)
    
    st.write("### Chat History")
    message_pairs = []
    for i in range(0, len(st.session_state.messages), 2):
        if i+1 < len(st.session_state.messages):
            message_pairs.append((st.session_state.messages[i], st.session_state.messages[i+1], i))
    
    for user_msg, assistant_msg, msg_idx in reversed(message_pairs):
        with st.chat_message(user_msg["role"]):
            st.write(user_msg["content"])
        
        with st.chat_message(assistant_msg["role"]):
            st.write(assistant_msg["content"])
            
            st.markdown("""
            <style>
            .feedback-button {
                width: 100% !important;
                min-width: 100% !important;
                padding: 0.5rem !important;
                text-align: center !important;
                margin: 0 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            feedback_col1, feedback_col2, feedback_col3, feedback_col4 = st.columns(4)
            
            with feedback_col1:
                if st.button("Helpful", key=f"helpful_{msg_idx}", use_container_width=True):
                    st.session_state.rl_agent.process_feedback("helpful")
                    st.success("Thanks for your feedback!")
                    st.rerun()
            
            with feedback_col2:
                if st.button("More Empathy", key=f"empathy_{msg_idx}", use_container_width=True):
                    st.session_state.rl_agent.process_feedback("more_empathy")
                    st.info("I'll be more empathetic next time.")
                    st.rerun()
            
            with feedback_col3:
                if st.button("More Practical", key=f"practical_{msg_idx}", use_container_width=True):
                    st.session_state.rl_agent.process_feedback("more_practical")
                    st.info("I'll provide more practical advice next time.")
                    st.rerun()
            
            with feedback_col4:
                if st.button("Not Helpful", key=f"not_helpful_{msg_idx}", use_container_width=True):
                    st.session_state.rl_agent.process_feedback("not_helpful")
                    st.info("I'll improve my responses next time.")
                    st.rerun()

def process_message(message_text):
    response = generate_response(message_text)
    if response:
        st.session_state.messages.append({"role": "user", "content": message_text})
        st.session_state.messages.append({"role": "assistant", "content": response})
        audio_file = speak(response)
        if audio_file:
            st.audio(audio_file)

def game_center_page():
    tab1, tab2 = st.tabs(["Memory Matcher", "Rock Paper Scissors"])

    with tab1:
        st.title("🧠 Memory Matcher")
        
        if 'game_state' not in st.session_state:
            emojis = ['🍎', '🍌', '🍇', '🍊', '🍉', '🍓', 
                      '🚗', '🚀', '🎈', '🏀', '🐶', '🐱']
            board = emojis * 2
            random.shuffle(board)
            
            st.session_state.game_state = {
                'board': board,
                'flipped': [],
                'matched': [],
                'attempts': 0,
                'game_over': False
            }
        
        game = st.session_state.game_state
        
        cols = st.columns(4)
        for i in range(12):
            with cols[i % 4]:
                if i not in game['matched']:
                    if i in game['flipped']:
                        st.button(game['board'][i], disabled=True, key=f"flipped_{i}")
                    else:
                        if st.button(f"Card {i+1}", key=f"card_{i}"):
                            game['flipped'].append(i)
                            
                            if len(game['flipped']) == 2:
                                game['attempts'] += 1
                                first, second = game['flipped']
                                if game['board'][first] == game['board'][second]:
                                    game['matched'].extend(game['flipped'])
                                else:
                                    time.sleep(1)
                                
                                game['flipped'] = []
                else:
                    st.button(game['board'][i], disabled=True, key=f"matched_{i}")
        
        st.write(f"Attempts: {game['attempts']}")
        
        if len(game['matched']) == 12:
            st.balloons()
            st.success("Congratulations! You found all pairs! 🎉")
            game['game_over'] = True
        
        if game.get('game_over'):
            if st.button("New Game", key="new_game"):
                del st.session_state.game_state

    with tab2:
        st.title("✊ Rock Paper Scissors Showdown!")

        st.markdown("""
        <style>
        .hand-container {
            display: flex;
            justify-content: space-between;
            font-size: 100px;
            margin: 20px 0;
            transition: transform 0.3s ease;
        }
        .hand-move {
            animation: shake 0.5s;
        }
        @keyframes shake {
            0% { transform: rotate(0deg); }
            25% { transform: rotate(15deg); }
            50% { transform: rotate(-15deg); }
            75% { transform: rotate(15deg); }
            100% { transform: rotate(0deg); }
        }
        </style>
        """, unsafe_allow_html=True)

        choices = ['Rock ✊', 'Paper ✋', 'Scissors ✌️']

        player_choice = st.radio(
        "Player selection",
        choices,
        label_visibility="collapsed"
)

        if st.button("Play"):
            computer_choice = random.choice(choices)

            with st.spinner('Battling it out...'):
                time.sleep(1)

            col1, col2 = st.columns(2)

            with col1:
                st.write("### Your Choice")
                st.markdown(f"## {player_choice}")

            with col2:
                st.write("### Computer's Choice")
                st.markdown(f"## {computer_choice}")

            if player_choice == computer_choice:
                st.balloons()
                st.info("### It's a tie! 🤝")
            elif (
                (player_choice == 'Rock ✊' and computer_choice == 'Scissors ✌️') or
                (player_choice == 'Paper ✋' and computer_choice == 'Rock ✊') or
                (player_choice == 'Scissors ✌️' and computer_choice == 'Paper ✋')
            ):
                st.snow()
                st.success("### You win! 🎉🏆")
            else:
                st.error("### Computer wins! That's always OK, TRY AGAIN! 😢🤖")

def breathing_center_page():
    st.header("🫁 Breathing Center")
    
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
                audio_file = open('assets/audio/meditation.mp3', 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
            
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

def journal_page():
    st.title("📝 Personal Journal")
    
    if 'journal_entries' not in st.session_state:
        st.session_state.journal_entries = []
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            journal_entry = st.text_area(
                "Write your journal entry here:", 
                height=200, 
                placeholder="What's on your mind today?"
            )
            
            char_count = len(journal_entry)
            if char_count > 0:
                color = "green" if char_count <= 500 else "red"
                st.markdown(f"<p style='color:{color}'>Character Count: {char_count}</p>", 
                            unsafe_allow_html=True)
        
        with col2:
            st.write("### Journal Actions")
            
            if st.button("💾 Save Entry", use_container_width=True):
                if journal_entry.strip():
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.journal_entries.append((current_time, journal_entry))
                    st.success("Entry saved successfully!")
                else:
                    st.error("Please write something before submitting!")
            
            if st.button("🗑️ Clear All Entries", use_container_width=True):
                 if st.session_state.journal_entries:
                     if st.checkbox("Are you sure you want to clear all entries?"):
                            st.session_state.journal_entries = []
                            st.success("All entries have been cleared!")
                            st.rerun()
                 else:
                     st.warning("No entries to clear.")

           
    
    with st.container():
        st.write("### Search Entries")
        search_term = st.text_input("Search your journal entries:")
        
        if st.session_state.journal_entries:
            filtered_entries = [
                entry for entry in st.session_state.journal_entries 
                if search_term.lower() in entry[1].lower()
            ]
            
            if filtered_entries:
                st.write("### Your Journal Entries")
                for time_sent, message in reversed(filtered_entries):
                    with st.expander(f"Entry from {time_sent}"):
                        st.write(message)
            else:
                st.info("No entries match your search term.")
        else:
            st.info("No journal entries yet. Start writing your first entry!")

def stress_burster():
    st.title("🧘 Stress Burster")
    
    st.markdown("""
    <style>
    
    .spline-container {
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        overflow: hidden;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### Take a Moment to Unwind 
    Interact with our BlueBall and let your stress melt away.
    """)
    
    st.markdown("""
    <div class="spline-container">
    <iframe 
        src='https://my.spline.design/aitherapist-e7816283ccca0cc7f2e74c543a304ec1/' 
        frameborder='0' 
        width='100%' 
        height='500px'>
    </iframe>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Quick Stress Relief Tips")
    tips = [
        "Take deep, slow breaths",
        "Practice mindfulness",
        "Stretch or do light exercise",
        "Listen to calming music"
    ]
    
    for tip in tips:
        st.markdown(f"• {tip}")

def mood_tracker_page():
    st.title("📊 Mood Tracker")
    
    if 'mood_history' not in st.session_state:
        st.session_state.mood_history = []
    
    st.subheader("How are you feeling today?")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mood_scale = st.slider("Rate your mood (1-10):", 1, 10, 5)
        mood_notes = st.text_area("Any notes about your mood?", placeholder="What's affecting your mood today?")
    
    with col2:
        mood_emojis = {
            1: "😢", 2: "😔", 3: "😕", 4: "😐",
            5: "😊", 6: "😄", 7: "😃", 8: "😁",
            9: "🤗", 10: "🥳"
        }
        st.markdown(f"### {mood_emojis[mood_scale]}")
        if st.button("Save Mood"):
            current_time = datetime.now()
            st.session_state.mood_history.append({
                'date': current_time,
                'mood': mood_scale,
                'notes': mood_notes
            })
            st.success("Mood recorded!")
    
    if st.session_state.mood_history:
        st.subheader("Your Mood History")
        
        df = pd.DataFrame(st.session_state.mood_history)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['mood'],
            mode='lines+markers',
            name='Mood',
            line=dict(color='#236860'),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Mood Over Time',
            xaxis_title='Date',
            yaxis_title='Mood Level',
            yaxis_range=[0, 11],
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Recent Entries")
        for entry in reversed(st.session_state.mood_history[-5:]):
            with st.expander(f"Entry from {entry['date'].strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"Mood: {entry['mood']}/10 {mood_emojis[entry['mood']]}")
                st.write(f"Notes: {entry['notes']}")

def gratitude_journal_page():
    st.title("🙏 Gratitude Journal")
    
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

def sleep_tracker_page():
    st.title("😴 Sleep Tracker")
    
    if 'sleep_data' not in st.session_state:
        st.session_state.sleep_data = []
    
    st.subheader("Log Your Sleep")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sleep_date = st.date_input("Date:")
        sleep_duration = st.number_input("Hours of sleep:", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
    
    with col2:
        sleep_quality = st.select_slider(
            "Sleep quality:",
            options=["Poor", "Fair", "Good", "Very Good", "Excellent"],
            value="Good"
        )
        
        factors = st.multiselect(
            "Factors affecting sleep:",
            ["Stress", "Exercise", "Caffeine", "Screen Time", "Noise", "Temperature","ECE Department"]
        )
    
    if st.button("Save Sleep Log"):
        st.session_state.sleep_data.append({
            'date': sleep_date,
            'duration': sleep_duration,
            'quality': sleep_quality,
            'factors': factors
        })
        st.success("Sleep log saved!")
    
    if st.session_state.sleep_data:
        st.subheader("Sleep Statistics")
        
        df = pd.DataFrame(st.session_state.sleep_data)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['duration'],
            name='Sleep Duration',
            marker_color='#236860'
        ))
        
        fig.update_layout(
            title='Sleep Duration Over Time',
            xaxis_title='Date',
            yaxis_title='Hours of Sleep',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Sleep Duration", f"{df['duration'].mean():.1f} hours")
        with col2:
            st.metric("Most Common Quality", df['quality'].mode()[0])

def resources_page():
    st.title("🆘 Mental Health Resources")
    
    st.header("Emergency Contacts")
    
    emergency_contacts = {
        "National Crisis Hotline": "1-800-273-8255",
        "Crisis Text Line": "Text HOME to 741741",
        "Emergency Services": "911"
    }
    
    for service, contact in emergency_contacts.items():
        st.markdown(f"**{service}**: {contact}")
    
    st.header("Self-Help Resources")
    
    with st.expander("Meditation Apps"):
        st.markdown("""
        - Headspace
        - Calm
        - Insight Timer
        - Simple Habit
        """)
    
    with st.expander("Educational Resources"):
        st.markdown("""
        - National Institute of Mental Health
        - Mental Health America
        - Psychology Today
        - Mind.org
        """)
    
    with st.expander("Support Groups"):
        st.markdown("""
        - NAMI Support Groups
        - Depression and Bipolar Support Alliance
        - Anxiety and Depression Association of America
        """)
    
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

def brainrot_corner_page():
    st.header("🎮 Brainrot Corner")

    if 'meme_counter' not in st.session_state:
        st.session_state.meme_counter = 0

    def fetch_random_meme():
        try:
            response = requests.get("https://meme-api.com/gimme", timeout=10)
            response.raise_for_status()
            meme_data = response.json()
            image_url = meme_data.get('url', "https://via.placeholder.com/800x600")
            meme_text = meme_data.get('title', "No caption available.")
            return image_url, meme_text
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching meme: {e}")
            return "https://via.placeholder.com/800x600", "Error fetching meme! Try again."

    if st.button("Generate New Meme"):
        st.session_state.meme_counter += 1
        image_url, meme_text = fetch_random_meme()

        st.markdown(f"""
            <div style="text-align: center; background-color: #1a1a1a; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h2 style="color: white; font-size: 24px; margin-bottom: 20px;">{meme_text}</h2>
                <img src="{image_url}" style="max-width: 100%; border-radius: 8px;" alt="Random Meme">
                <p style="color: #888; margin-top: 15px;">Meme #{st.session_state.meme_counter}</p>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.meme_counter % 5 == 0:
            st.balloons()
            st.markdown("""
                <div style="text-align: center; color: #236860; font-size: 20px; margin: 20px 0;">
                    🎉 Milestone reached! Keep the memes flowing! 🎉
                </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="text-align: center; margin-top: 20px; color: #888;">
            Memes Generated: {st.session_state.meme_counter} 🎭
            <br>Keep clicking for infinite entertainment!
        </div>
    """, unsafe_allow_html=True)

def therapeutic_activities_page():


    assets_dir = Path(__file__).parent / "assets"
    audio_dir = assets_dir / "audio"

    st.title("🎨 Therapeutic Activities")
    
    st.markdown("""
    <style>
    .activity-card {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .activity-card:hover {
        transform: translateY(-5px);
    }
    .canvas-container {
        background: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
    }
    .visualization-text {
        font-size: 1.2em;
        line-height: 1.6;
        padding: 20px;
        background: rgba(255,255,255,0.9);
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    activity = st.selectbox(
        "Choose an Activity:",
        ["Art Therapy", "Sound Therapy",]
    )

    if activity == "Art Therapy":
        st.subheader("🎨 Express Yourself Through Art")
        
        if 'drawing_mode' not in st.session_state:
            st.session_state.drawing_mode = "freedraw"
        if 'stroke_width' not in st.session_state:
            st.session_state.stroke_width = 2
        if 'stroke_color' not in st.session_state:
            st.session_state.stroke_color = "#000000"
        
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.session_state.drawing_mode = st.selectbox(
                "Drawing Tool:",
                ("freedraw", "line", "rect", "circle")
            )
        with col2:
            st.session_state.stroke_width = st.slider("Brush Size:", 1, 25, 2)
        with col3:
            st.session_state.stroke_color = st.color_picker("Color:", "#000000")
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=st.session_state.stroke_width,
            stroke_color=st.session_state.stroke_color,
            background_color="#FFFFFF",
            background_image=None,
            update_streamlit=True,
            height=400,
            drawing_mode=st.session_state.drawing_mode,
            key="canvas",
        )

    
    elif activity == "Sound Therapy":
        st.subheader("🎵 Therapeutic Sounds")
        
        sounds = {
            "Ocean Waves": audio_dir / "ocean.mp3",
            "Forest Birds": audio_dir / "forest.mp3",
            "Rainfall": audio_dir / "rain.mp3"
        }
        
        col1, col2 = st.columns(2)
        with col1:
            selected_sound = st.selectbox("Choose a sound:", list(sounds.keys()))
            
        with col2:
            st.markdown("### Sound Settings")
            volume = st.slider("Volume:", 0.0, 1.0, 0.5)
            
        if st.button("Play Sound"):
            try:
                with open(sounds[selected_sound], "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3")
            except FileNotFoundError:
                st.error(f"Audio file for {selected_sound} not found. Please ensure it exists in the assets directory.")

def main():
    init_styles()

    col1, col2 = st.columns([1.5, 10])

    with col1:
        st.image('logo.jpg', width=100)

    with col2:
        st.title("NeuroSphere")
        st.markdown("*Your Safe Space for Healing: Chat, Journal, Grow.*")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "Chatbot", "Breathing Center", "Therapeutic Activities",
        "Sleep Tracker", "Mood Tracker", "Journal Center", 
        "BrainRot Memes", "Stress Buster", "Game Center"
    ])

    with tab1:
        chatbot_page()
    with tab2:
        breathing_center_page()
    with tab3:
        therapeutic_activities_page()
    with tab4:
        sleep_tracker_page()
    with tab5:  
        mood_tracker_page()
    with tab6:
        journal_page()
    with tab7:
        brainrot_corner_page()
    with tab8:
        stress_burster()
    with tab9:
        game_center_page()


    with st.sidebar:
        st.title("Additional Resources")
        if st.button("View Mental Health Resources"):
            resources_page()

    st.markdown("""
Created with ❤ for mental health awareness

For support, email: neurosphere_support@gmail.com  
For Queries, dm on <a href="https://www.instagram.com/NeuroSphere">NeuroSphere</a>
""", unsafe_allow_html=True)

if __name__=="__main__":
        main()
