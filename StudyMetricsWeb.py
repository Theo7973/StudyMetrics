import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from database import DatabaseManager
from api_service import WeatherService

# Page configuration
st.set_page_config(
    page_title="StudyMetrics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        margin: 0.5rem 0;
    }
    .timer-display {
        font-size: 4rem;
        text-align: center;
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize services
db = DatabaseManager()
weather_service = WeatherService()

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def create_subject_chart():
    sessions = db.get_all_sessions()
    df = pd.DataFrame(sessions, columns=['id', 'start_time', 'end_time', 'duration', 'subject', 'weather', 'location'])
    subject_times = df.groupby('subject')['duration'].sum()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(subject_times.values, labels=subject_times.index, autopct='%1.1f%%')
    ax.set_title('Study Time by Subject')
    return fig

def create_weekly_chart():
    sessions = db.get_all_sessions()
    df = pd.DataFrame(sessions, columns=['id', 'start_time', 'end_time', 'duration', 'subject', 'weather', 'location'])
    df['start_time'] = pd.to_datetime(df['start_time'])
    daily_times = df.groupby(df['start_time'].dt.date)['duration'].sum() / 3600  # Convert to hours
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(daily_times.index, daily_times.values, marker='o')
    ax.set_title('Study Hours by Date')
    ax.set_xlabel('Date')
    ax.set_ylabel('Hours')
    plt.xticks(rotation=45)
    return fig

def main():
    st.title("📚 StudyMetrics")
    
    # Create two columns for layout
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        # Timer section
        st.markdown("### Study Timer")
        subject = st.selectbox(
            "Select Subject:",
            ["General", "Math", "Science", "History", "Language"]
        )
        
        # Initialize session state
        if 'time_elapsed' not in st.session_state:
            st.session_state.time_elapsed = 0
        if 'running' not in st.session_state:
            st.session_state.running = False
        if 'last_update' not in st.session_state:
            st.session_state.last_update = time.time()
        
        # Timer display
        st.markdown(f'<p class="timer-display">{format_time(st.session_state.time_elapsed)}</p>', unsafe_allow_html=True)
        
        # Control buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start" if not st.session_state.running else "⏸️ Stop"):
                st.session_state.running = not st.session_state.running
                if not st.session_state.running:
                    db.save_session(
                        duration=st.session_state.time_elapsed,
                        subject=subject,
                        weather="Unknown"
                    )
        
        with col2:
            if st.button("🔄 Reset"):
                st.session_state.time_elapsed = 0
                st.session_state.running = False
    
    with right_col:
        # Weather and stats
        weather_data = weather_service.get_weather()
        if weather_data:
            st.markdown(f"### Current Weather")
            st.write(f"🌡️ {weather_data['temperature']}°C")
            st.write(f"☁️ {weather_data['condition']}")
    
    # Analytics Section
    st.markdown("---")
    st.header("📊 Analytics")
    
    # Create three columns for analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Subject Distribution")
        st.pyplot(create_subject_chart())
    
    with col2:
        st.subheader("Study Trends")
        st.pyplot(create_weekly_chart())
    
    # Update timer
    if st.session_state.running:
        current_time = time.time()
        st.session_state.time_elapsed += int(current_time - st.session_state.last_update)
        st.session_state.last_update = current_time
        st.experimental_rerun()
    else:
        st.session_state.last_update = time.time()

if __name__ == "__main__":
    main()