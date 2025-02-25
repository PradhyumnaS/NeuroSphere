import streamlit as st
import requests

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