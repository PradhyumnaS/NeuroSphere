import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import redis
import json
import uuid
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv

@st.cache_resource
def get_redis_connection():
    try:
        r = redis.Redis(
            host=st.secrets.get("REDIS_HOST", "localhost"),
            port=st.secrets.get("REDIS_PORT", 6379),
            db=st.secrets.get("REDIS_DB", 0),
            password=st.secrets.get("REDIS_PASSWORD", None),
            decode_responses=True
        )
        r.ping()
        return r
    except redis.exceptions.ConnectionError as e:
        st.error(f"Failed to connect to Redis: {e}. Context history will not be saved/loaded.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred during Redis connection: {e}")
        return None

@st.cache_resource
def load_knowledge_base():
    try:
        df = pd.read_csv("./assets/knowledge_base/kb.csv")
        if 'question' in df.columns and 'answer' in df.columns:
            vectorizer = TfidfVectorizer(stop_words='english')
            question_vectors = vectorizer.fit_transform(df['question'])
            
            return {
                'df': df,
                'vectorizer': vectorizer,
                'question_vectors': question_vectors
            }
        else:
            print(f"Knowledge base failed to load cuz of the columns")
            st.warning("CSV file doesn't have the expected columns (question, answer).")
            return None
    except Exception as e:
        print(f"Knowledge base failed to load")
        st.error(f"Error loading knowledge base: {e}")
        return None
    
def get_relevant_knowledge(user_message, knowledge_base, top_n=3):
    if not knowledge_base:
        return []
    
    user_vector = knowledge_base['vectorizer'].transform([user_message])
    
    similarities = cosine_similarity(user_vector, knowledge_base['question_vectors']).flatten()
    
    top_indices = similarities.argsort()[-top_n:][::-1]
    
    relevant_entries = []
    for idx in top_indices:
        similarity = similarities[idx]
        if similarity > 0.2:
            relevant_entries.append({
                'question': knowledge_base['df']['question'].iloc[idx],
                'answer': knowledge_base['df']['answer'].iloc[idx],
                'similarity': similarity
            })
    return relevant_entries

def summarize_knowledge_entries(kb_entries):
    if not kb_entries:
        return ""
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        content_to_summarize = "Summarize these expert answers concisely within 100 words:\n\n"
        for entry in kb_entries:
            content_to_summarize += f"EXPERT ANSWER: {entry['answer']}\n\n"
            
        content_to_summarize += "Format as bullet points focusing on key advice and therapeutic approaches."
        
        response = model.generate_content(content_to_summarize)
        summary = response.text
        
        return summary
    except Exception as e:
        print(f"Error generating knowledge summary: {e}")
        
        return summary

def save_conversation_to_knowledge_base(user_message, assistant_response, feedback_type):
    if feedback_type not in ["helpful"]:
        return False
    
    try:
        kb_path = "./assets/knowledge_base/kb.csv"
        
        if knowledge_base and 'df' in knowledge_base:
            similar_entries = get_relevant_knowledge(user_message, knowledge_base, top_n=1)
            
            if similar_entries and similar_entries[0]['similarity'] > 0.8:
                print(f"Similar question already exists with similarity {similar_entries[0]['similarity']}")
                return False
        
        with open(kb_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([user_message, assistant_response])
        
        print(f"Added new conversation to knowledge base: {user_message[:50]}...")
        
        return True
    
    except Exception as e:
        print(f"Error saving to knowledge base: {e}")
        return False

def reload_knowledge_base():
    st.cache_resource.clear()
    global knowledge_base
    knowledge_base = load_knowledge_base()

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

redis_conn = get_redis_connection()
SESSION_HISTORY_KEY = f"chat_history:{st.session_state.session_id}"
MAX_HISTORY_LENGTH = 10

if 'rl_agent' not in st.session_state:
    from reinforcement import PromptOptimizationRL
    st.session_state.rl_agent = PromptOptimizationRL()

knowledge_base = load_knowledge_base()

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
MODEL_NAME = 'gemini-2.0-flash'

st.title("💭 Chat with Me")

def get_conversation_history():
    """Retrieves the last N messages from Redis."""
    if not redis_conn:
        return []
    try:
        history_json = redis_conn.lrange(SESSION_HISTORY_KEY, -MAX_HISTORY_LENGTH * 2, -1)
        history = [json.loads(msg) for msg in history_json]
        return history
    except Exception as e:
        st.warning(f"Could not retrieve chat history from Redis: {e}")
        return []

def add_to_conversation_history(role, content):
    """Adds a message to Redis history for context management."""
    if not redis_conn:
        return
    try:
        redis_conn.rpush(SESSION_HISTORY_KEY, json.dumps({"role": role, "content": content}))
    except Exception as e:
        st.warning(f"Could not save chat history to Redis: {e}")

def generate_response(user_message):
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)

        history = get_conversation_history()
        context_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        
        kb_entries = get_relevant_knowledge(user_message, knowledge_base)
        knowledge_context = ""
        
        if kb_entries:
            knowledge_summary = summarize_knowledge_entries(kb_entries)
            knowledge_context = "\n\nRELEVANT EXPERT INSIGHTS:\n" + knowledge_summary
        
        full_user_message = (
            f"{context_prompt}\n\n"
            f"{knowledge_context}\n\n"
            f"user: {user_message}\n\n"
        )

        print(f"Full User Message: {full_user_message}")

        optimized_prompt, action = st.session_state.rl_agent.generate_optimized_prompt(full_user_message)
        st.session_state.rl_agent.last_action = action

        response = model.generate_content(optimized_prompt)
        response_text = response.text
        audio_file = speak(response_text)
        return response_text, audio_file

    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "I apologize, but I'm having trouble processing your request at the moment. Please try again.", None

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
    if message_text:
        st.session_state.messages.append({"role": "user", "content": message_text})
        st.chat_message("user").write(message_text)
        add_to_conversation_history("user", message_text)
        with st.chat_message("assistant"):
            with st.spinner("Consulting the archives of the mind..."):
                response_text, audio_file = generate_response(message_text)
                st.write(response_text)
                if audio_file:
                    st.audio(audio_file)
        st.session_state.messages.append({"role": "assistant", "content": response_text, "audio_file": audio_file})
        add_to_conversation_history("assistant", response_text)
        st.session_state.needs_rerun = True

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'needs_rerun' not in st.session_state:
    st.session_state.needs_rerun = False

st.write("### Choose Input Method")
input_method = st.radio(
    "Input method selection",
    ["Text Input", "Voice Recording (5-10 seconds recommended)"],
    label_visibility="collapsed"
)
    
if input_method == "Voice Recording (5-10 seconds recommended)":
    spoken_text = speech_to_text(
                    language='en',
                    start_prompt="Speak now...",
                    stop_prompt="Done",
                    use_container_width=True,
                    just_once=True,
                    key='STT',
                )

    if spoken_text:
        process_message(spoken_text)

if st.session_state.needs_rerun:
    st.session_state.needs_rerun = False
    st.rerun()

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if (
            msg["role"] == "assistant"
            and i == len(st.session_state.messages) - 1
            and "audio_file" in msg
            and msg["audio_file"]
        ):
            st.audio(msg["audio_file"])
        if msg["role"] == "assistant" and i != 0:
            feedback_col1, feedback_col2, feedback_col3, feedback_col4 = st.columns(4)
            with feedback_col1:
                if st.button("Helpful", key=f"helpful_{i}", use_container_width=True):
                    reward = st.session_state.rl_agent.give_feedback("helpful")
                    st.session_state.rl_agent.process_feedback(reward)
                    st.toast("Thanks for your feedback!")
                    save_conversation_to_knowledge_base(
                        st.session_state.messages[i-1]["content"],
                        msg["content"],
                        "helpful")
                    reload_knowledge_base()
            with feedback_col2:
                if st.button("Need Empathy", key=f"empathy_{i}", use_container_width=True):
                    reward = st.session_state.rl_agent.give_feedback("more_empathy")
                    st.session_state.rl_agent.process_feedback(reward)
                    st.toast("I'll be more empathetic next time.")
            with feedback_col3:
                if st.button("Need Practicality", key=f"practical_{i}", use_container_width=True):
                    reward = st.session_state.rl_agent.give_feedback("more_practical")
                    st.session_state.rl_agent.process_feedback(reward)
                    st.toast("I'll provide more practical advice next time.")
            with feedback_col4:
                if st.button("Not Helpful", key=f"not_helpful_{i}", use_container_width=True):
                    reward = st.session_state.rl_agent.give_feedback("not_helpful")
                    st.session_state.rl_agent.process_feedback(reward)
                    st.toast("I'll improve my responses next time.")

if prompt := st.chat_input("Type your message..."):
    process_message(prompt) 
if st.session_state.needs_rerun:
    st.session_state.needs_rerun = False
    st.rerun()