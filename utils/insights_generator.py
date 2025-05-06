import streamlit as st
import google.generativeai as genai

def configure_genai():
    """Configure the Google GenerativeAI with API key from secrets"""
    if not hasattr(st.session_state, 'genai_configured'):
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            st.session_state.genai_configured = True
        except Exception as e:
            st.error(f"Error configuring GenerativeAI: {e}")
            return False
    return True

def generate_sleep_insights(sleep_data):
    """
    Generate AI-driven textual insights about sleep data
    
    Args:
        sleep_data: Dictionary or list containing sleep metrics
        
    Returns:
        str: Text insights about sleep patterns
    """
    if not configure_genai():
        return "Unable to generate insights due to API configuration issues."
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create a prompt with the sleep data
        prompt = f"""
        Based on the following sleep data, provide helpful insights and recommendations:
        {sleep_data}
        
        Please analyze sleep duration, quality, and patterns. Provide 3-5 concise, actionable insights 
        about improving sleep health. Focus on identifying patterns and suggesting practical steps.
        Keep the response under 200 words and easy to understand.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating sleep insights: {e}")
        return "Could not generate insights at this time. Please try again later."

def generate_mood_insights(mood_data):
    """
    Generate AI-driven textual insights about mood data
    
    Args:
        mood_data: Dictionary or list containing mood metrics
        
    Returns:
        str: Text insights about mood patterns
    """
    if not configure_genai():
        return "Unable to generate insights due to API configuration issues."
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create a prompt with the mood data
        prompt = f"""
        Based on the following mood tracking data, provide helpful insights and recommendations:
        {mood_data}
        
        Please analyze mood patterns, triggers, and trends. Provide 3-5 concise, actionable insights 
        about understanding and improving emotional well-being. Focus on identifying patterns and suggesting 
        practical steps. Keep the response under 200 words and easy to understand.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating mood insights: {e}")
        return "Could not generate insights at this time. Please try again later."
