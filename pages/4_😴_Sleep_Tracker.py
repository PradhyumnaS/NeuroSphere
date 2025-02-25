import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

st.title("😴 Sleep Tracker")

if 'sleep_data' not in st.session_state:
    dates = pd.date_range(end=datetime.today(), periods=7).tolist()
    sample_data = []
    
    for date in dates:
        sample_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'hours': round(np.random.uniform(5.5, 8.5), 1),
            'quality': int(np.random.uniform(1, 5)),
            'notes': ""
        })
    
    st.session_state.sleep_data = sample_data

st.markdown("""
<style>
    .card {
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0px;
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .metrics-container {
        display: flex;
        justify-content: space-between;
        text-align: center;
        margin: 20px 0;
    }
    .metric {
        border-radius: 10px;
        padding: 15px;
        background: #f8f9fa;
        width: 30%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #236860;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #777;
    }
    .rating-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .rating-star {
        font-size: 2rem;
        cursor: pointer;
        transition: all 0.2s;
    }
</style>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Log Sleep", "Sleep Insights"])

with tab1:
    st.header("Record Last Night's Sleep")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sleep_date = st.date_input(
            "Date",
            value=datetime.now().date() - timedelta(days=1),
            max_value=datetime.now().date()
        )
    
    with col2:
        sleep_hours = st.number_input(
            "Hours Slept",
            min_value=0.0,
            max_value=24.0,
            value=7.5,
            step=0.5
        )
    
    st.markdown("##### How would you rate your sleep quality?")
    
    rating_col1, rating_col2, rating_col3, rating_col4, rating_col5 = st.columns(5)
    quality_rating = 0
    
    if 'temp_rating' not in st.session_state:
        st.session_state.temp_rating = 0
    
    with rating_col1:
        if st.button("⭐", key="star1"):
            st.session_state.temp_rating = 1
    with rating_col2:
        if st.button("⭐", key="star2"):
            st.session_state.temp_rating = 2
    with rating_col3:
        if st.button("⭐", key="star3"):
            st.session_state.temp_rating = 3
    with rating_col4:
        if st.button("⭐", key="star4"):
            st.session_state.temp_rating = 4
    with rating_col5:
        if st.button("⭐", key="star5"):
            st.session_state.temp_rating = 5
    
    quality_rating = st.session_state.temp_rating
    st.write(f"Current rating: {quality_rating}/5")
    
    sleep_notes = st.text_area("Notes (optional)", 
                              placeholder="Any factors affecting your sleep? (stress, caffeine, exercise, etc.)")
    
    if st.button("Save Sleep Log"):
        date_str = sleep_date.strftime('%Y-%m-%d')
        existing_entry_index = None
        
        for i, entry in enumerate(st.session_state.sleep_data):
            if entry['date'] == date_str:
                existing_entry_index = i
                break
        
        new_entry = {
            'date': date_str,
            'hours': sleep_hours,
            'quality': quality_rating,
            'notes': sleep_notes
        }
        
        if existing_entry_index is not None:
            st.session_state.sleep_data[existing_entry_index] = new_entry
            st.success(f"Updated sleep log for {date_str}")
        else:
            st.session_state.sleep_data.append(new_entry)
            st.success(f"Added new sleep log for {date_str}")
        
        st.session_state.temp_rating = 0
        st.experimental_rerun()

with tab2:
    st.header("Your Sleep Patterns")
    
    df = pd.DataFrame(st.session_state.sleep_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    avg_sleep = df['hours'].mean()
    avg_quality = df['quality'].mean()
    consistency = 100 - (df['hours'].std() / df['hours'].mean() * 100)
    
    st.markdown("""
    <div class="metrics-container">
        <div class="metric">
            <div class="metric-value">{:.1f}h</div>
            <div class="metric-label">Average Sleep</div>
        </div>
        <div class="metric">
            <div class="metric-value">{:.1f}/5</div>
            <div class="metric-label">Average Quality</div>
        </div>
        <div class="metric">
            <div class="metric-value">{:.1f}%</div>
            <div class="metric-label">Consistency</div>
        </div>
    </div>
    """.format(avg_sleep, avg_quality, consistency), unsafe_allow_html=True)
    
    fig1 = go.Figure()
    
    fig1.add_trace(go.Bar(
        x=df['date'],
        y=df['hours'],
        name='Hours Slept',
        marker_color='#236860'
    ))
    
    fig1.add_trace(go.Scatter(
        x=df['date'],
        y=[7] * len(df),
        mode='lines',
        name='Recommended',
        line=dict(color='rgba(235, 52, 52, 0.7)', width=2, dash='dash')
    ))
    
    fig1.update_layout(
        title='Sleep Duration Over Time',
        xaxis_title='Date',
        yaxis_title='Hours',
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=df['date'],
        y=df['quality'],
        mode='lines+markers',
        name='Sleep Quality',
        marker=dict(size=10, color='#2E7D32')
    ))
    
    fig2.update_layout(
        title='Sleep Quality Over Time',
        xaxis_title='Date',
        yaxis_title='Quality (1-5)',
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        yaxis=dict(range=[0, 5.5]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    st.header("Sleep Log")
    
    display_df = df.copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df['quality'] = display_df['quality'].apply(lambda x: '⭐' * int(x))
    display_df.columns = ['Date', 'Hours', 'Quality', 'Notes']
    
    st.dataframe(display_df.sort_values('Date', ascending=False), use_container_width=True)