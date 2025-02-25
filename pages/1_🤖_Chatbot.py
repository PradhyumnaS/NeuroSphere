import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import os
from dotenv import load_dotenv

load_dotenv()
if 'rl_agent' not in st.session_state:
    from reinforcement import PromptOptimizationRL
    st.session_state.rl_agent = PromptOptimizationRL()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = 'gemini-2.0-flash'

st.title("💭 Chat with Me")

def generate_response(user_message):
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
        
        optimized_prompt, action = st.session_state.rl_agent.generate_optimized_prompt(user_message)
        
        st.session_state.rl_agent.last_action = action

        response = model.generate_content(optimized_prompt)
        response_text = response.text
        
        return response_text
        
    except Exception as e:
        st.error(f"Error generating response: {e}")
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

def process_message(message_text):
    response = generate_response(message_text)
    if response:
        st.session_state.messages.append({"role": "user", "content": message_text})
        st.session_state.messages.append({"role": "assistant", "content": response})
        audio_file = speak(response)
        if audio_file:
            st.audio(audio_file)

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
            if st.button("👍 Helpful", key=f"helpful_{msg_idx}", use_container_width=True):
                reward = st.session_state.rl_agent.give_feedback("helpful")
                st.session_state.rl_agent.process_feedback(reward)
                st.success("Thanks for your feedback!")
                st.rerun()

        with feedback_col2:
            if st.button("❤️ Empathy", key=f"empathy_{msg_idx}", use_container_width=True):
                reward = st.session_state.rl_agent.give_feedback("more_empathy")
                st.session_state.rl_agent.process_feedback(reward)
                st.info("I'll be more empathetic next time.")
                st.rerun()

        with feedback_col3:
            if st.button("🛠️ Practical", key=f"practical_{msg_idx}", use_container_width=True):
                reward = st.session_state.rl_agent.give_feedback("more_practical")
                st.session_state.rl_agent.process_feedback(reward)
                st.info("I'll provide more practical advice next time.")
                st.rerun()

        with feedback_col4:
            if st.button("👎 Not Helpful", key=f"not_helpful_{msg_idx}", use_container_width=True):
                reward = st.session_state.rl_agent.give_feedback("not_helpful")
                st.session_state.rl_agent.process_feedback(reward)
                st.info("I'll improve my responses next time.")
                st.rerun()