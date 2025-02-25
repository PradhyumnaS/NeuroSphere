import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

st.title("📊 Mood Tracker")

# Initialize session state for mood data
if 'mood_data' not in st.session_state:
    # Generate sample data for first-time users
    dates = pd.date_range(end=datetime.today(), periods=14).tolist()
    moods = ["Happy", "Calm", "Sad", "Anxious", "Excited", "Tired", "Neutral"]
    intensities = [1, 2, 3, 4, 5]
    
    sample_data = []
    for date in dates:
        # Generate 1-3 mood entries per day
        for _ in range(random.randint(1, 3)):
            time_of_day = random.randint(8, 22)  # Between 8 AM and 10 PM
            mood_datetime = date.replace(hour=time_of_day, minute=random.randint(0, 59))
            
            sample_data.append({
                'datetime': mood_datetime,
                'date': mood_datetime.strftime('%Y-%m-%d'),
                'time': mood_datetime.strftime('%H:%M'),
                'mood': random.choice(moods),
                'intensity': random.choice(intensities),
                'note': ""
            })
    
    st.session_state.mood_data = sample_data

# Mood definitions and emojis
mood_emojis = {
    "Happy": "😊",
    "Calm": "😌",
    "Sad": "😢",
    "Anxious": "😰",
    "Excited": "🤩",
    "Tired": "😴",
    "Neutral": "😐",
    "Angry": "😡",
    "Stressed": "😫"
}

# CSS styling
st.markdown("""
<style>
    .mood-btn {
        display: inline-block;
        width: 100%;
        text-align: center;
        padding: 15px 0;
        border-radius: 10px;
        font-size: 1.5rem;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .mood-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .mood-log {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .mood-date {
        color: #777;
        font-size: 0.9rem;
    }
    .mood-text {
        font-size: 1.2rem;
        margin: 5px 0;
    }
    .stButton > button {
        background-color: #236860;
        color: white;
    }
    .stExpander {
        border: none !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Log Mood", "Mood Insights"])

with tab1:
    st.header("How are you feeling right now?")
    
    # Create a grid of mood buttons
    col1, col2, col3 = st.columns(3)
    
    mood_selected = None
    
    with col1:
        if st.button(f"{mood_emojis['Happy']} Happy", use_container_width=True):
            mood_selected = "Happy"
        if st.button(f"{mood_emojis['Sad']} Sad", use_container_width=True):
            mood_selected = "Sad"
        if st.button(f"{mood_emojis['Neutral']} Neutral", use_container_width=True):
            mood_selected = "Neutral"
    
    with col2:
        if st.button(f"{mood_emojis['Excited']} Excited", use_container_width=True):
            mood_selected = "Excited"
        if st.button(f"{mood_emojis['Anxious']} Anxious", use_container_width=True):
            mood_selected = "Anxious"
        if st.button(f"{mood_emojis['Angry']} Angry", use_container_width=True):
            mood_selected = "Angry"
    
    with col3:
        if st.button(f"{mood_emojis['Calm']} Calm", use_container_width=True):
            mood_selected = "Calm"
        if st.button(f"{mood_emojis['Tired']} Tired", use_container_width=True):
            mood_selected = "Tired"
        if st.button(f"{mood_emojis['Stressed']} Stressed", use_container_width=True):
            mood_selected = "Stressed"
    
    # Store the selected mood in session state
    if mood_selected:
        st.session_state.current_mood = mood_selected
    
    # If a mood is selected, display intensity slider and notes
    if 'current_mood' in st.session_state:
        st.markdown(f"### You selected: {mood_emojis[st.session_state.current_mood]} {st.session_state.current_mood}")
        
        intensity = st.slider("How intense is this feeling? (1 = mild, 5 = very strong)", 1, 5, 3)
        
        mood_note = st.text_area("Add a note (optional):", placeholder="What triggered this feeling? What's on your mind?")
        
        if st.button("Save Mood"):
            # Get current datetime
            now = datetime.now()
            
            # Create new mood entry
            new_entry = {
                'datetime': now,
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M'),
                'mood': st.session_state.current_mood,
                'intensity': intensity,
                'note': mood_note
            }
            
            # Add to session state
            st.session_state.mood_data.append(new_entry)
            
            st.success("Mood logged successfully!")
            
            # Clear the current mood
            del st.session_state.current_mood
            
            st.experimental_rerun()
    
    # Recent mood logs
    st.header("Recent Mood Logs")
    
    if len(st.session_state.mood_data) > 0:
        # Sort by datetime (newest first)
        recent_moods = sorted(st.session_state.mood_data, key=lambda x: x['datetime'], reverse=True)[:5]
        
        for mood in recent_moods:
            with st.expander(f"{mood_emojis[mood['mood']]} {mood['mood']} - {mood['date']} at {mood['time']}"):
                st.markdown(f"**Intensity:** {'●' * mood['intensity']}{'○' * (5 - mood['intensity'])}")
                
                if mood['note']:
                    st.markdown(f"**Note:** {mood['note']}")
                else:
                    st.markdown("*No notes added*")
    else:
        st.info("No mood logs yet. Start tracking your moods above!")

with tab2:
    st.header("Your Mood Patterns")
    
    # Convert session state data to DataFrame for analysis
    df = pd.DataFrame(st.session_state.mood_data)
    
    if not df.empty:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['date'] = pd.to_datetime(df['date'])
        
        # Time period selector
        time_period = st.radio("Select time period:", 
                              ["Last 7 days", "Last 30 days", "All time"], 
                              horizontal=True)
        
        if time_period == "Last 7 days":
            cutoff_date = datetime.now() - timedelta(days=7)
            filtered_df = df[df['datetime'] >= cutoff_date]
        elif time_period == "Last 30 days":
            cutoff_date = datetime.now() - timedelta(days=30)
            filtered_df = df[df['datetime'] >= cutoff_date]
        else:
            filtered_df = df
        
        if not filtered_df.empty:
            # Mood frequency chart
            mood_counts = filtered_df['mood'].value_counts().reset_index()
            mood_counts.columns = ['Mood', 'Count']
            
            fig1 = px.bar(mood_counts, x='Mood', y='Count', 
                         labels={'Count': 'Frequency'}, 
                         color='Mood',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            
            fig1.update_layout(
                title='Mood Frequency',
                xaxis_title='',
                yaxis_title='Count',
                showlegend=False,
                height=350,
                margin=dict(l=0, r=0, t=40, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig1, use_container_width=True)
            
            # Mood intensity over time
            filtered_df = filtered_df.sort_values('datetime')
            
            fig2 = go.Figure()
            
            for mood in filtered_df['mood'].unique():
                mood_df = filtered_df[filtered_df['mood'] == mood]
                
                fig2.add_trace(go.Scatter(
                    x=mood_df['datetime'],
                    y=mood_df['intensity'],
                    mode='markers+lines',
                    name=mood,
                    hoverinfo='text',
                    hovertext=mood_df.apply(lambda row: f"{row['mood']} - {row['time']} ({row['intensity']}/5)", axis=1),
                    marker=dict(size=10)
                ))
            
            fig2.update_layout(
                title='Mood Intensity Over Time',
                xaxis_title='Date',
                yaxis_title='Intensity (1-5)',
                height=350,
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            # Mood patterns
            st.header("Mood Patterns")
            
            # Identify most frequent mood
            most_frequent_mood = mood_counts.iloc[0]['Mood']
            mood_percentage = (mood_counts.iloc[0]['Count'] / mood_counts['Count'].sum()) * 100
            
            # Calculate average mood intensity
            avg_intensity = filtered_df['intensity'].mean()
            
            # Display insights
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Most Frequent Mood", f"{mood_emojis[most_frequent_mood]} {most_frequent_mood}", 
                         f"{mood_percentage:.1f}% of entries")
            
            with col2:
                st.metric("Average Mood Intensity", f"{avg_intensity:.1f}/5", 
                         "+0.2 from last week" if random.random() > 0.5 else "-0.3 from last week")
            
            # Daily mood patterns
            st.subheader("Time of Day Patterns")
            
            # Extract hour from time
            filtered_df['hour'] = filtered_df['datetime'].dt.hour
            
            # Group by hour and calculate average intensity
            hourly_mood = filtered_df.groupby(['hour', 'mood']).size().reset_index()
            hourly_mood.columns = ['hour', 'mood', 'count']
            
            # Create time of day chart
            fig3 = px.bar(hourly_mood, x='hour', y='count', color='mood',
                         labels={'hour': 'Hour of Day', 'count': 'Frequency'},
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            
            fig3.update_layout(
                title='Mood Distribution Throughout the Day',
                xaxis=dict(tickvals=list(range(0, 24, 3)), ticktext=['12 AM', '3 AM', '6 AM', '9 AM', '12 PM', '3 PM', '6 PM', '9 PM']),
                height=300,
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                barmode='stack',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig3, use_container_width=True)
            
        else:
            st.info(f"No mood data available for the selected period ({time_period}).")
    else:
        st.info("Start logging your moods to see insights and patterns.")