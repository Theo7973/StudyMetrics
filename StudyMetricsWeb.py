import streamlit as st
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
from database import DatabaseManager
from api_service import WeatherService

# Page configuration
st.set_page_config(
    page_title="StudyMetrics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    db = DatabaseManager()
    weather_service = WeatherService()
    return db, weather_service

db, weather_service = init_services()

# Session state initialization
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0
if 'running' not in st.session_state:
    st.session_state.running = False

def format_time(seconds):
    """Format seconds into HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def calculate_elapsed_time():
    """Calculate elapsed time based on start_time"""
    if st.session_state.running and st.session_state.start_time is not None:
        current_time = time.time()
        return st.session_state.elapsed_time + (current_time - st.session_state.start_time)
    return st.session_state.elapsed_time

def handle_start():
    """Start timer callback"""
    st.session_state.running = True
    st.session_state.start_time = time.time()

def handle_stop(subject):
    """Stop timer callback"""
    if st.session_state.running:
        current_time = time.time()
        st.session_state.elapsed_time += (current_time - st.session_state.start_time)
        st.session_state.running = False
        st.session_state.start_time = None
        
        # Save session
        weather_data = weather_service.get_weather()
        weather_condition = weather_data['condition'] if weather_data else "Unknown"
        db.save_session(
            duration=int(st.session_state.elapsed_time),
            subject=subject,
            weather=weather_condition
        )
        st.success(f"Session saved: {format_time(st.session_state.elapsed_time)}")
        st.session_state.elapsed_time = 0  # Reset after saving

def handle_reset():
    """Reset timer callback"""
    st.session_state.running = False
    st.session_state.start_time = None
    st.session_state.elapsed_time = 0

def show_analytics():
    """Display interactive analytics charts"""
    st.header("📈 Study Analytics")
    
    try:
        sessions = db.get_all_sessions()
        if not sessions:
            st.info("No study sessions recorded yet!")
            return
            
        df = pd.DataFrame(sessions, columns=[
            "id", "start_time", "end_time", "duration", 
            "subject", "weather_condition", "location"
        ])
        
        # Convert duration to hours
        df['duration_hours'] = df['duration'] / 3600
        
        # Time Distribution Chart
        st.subheader("Study Time Distribution")
        fig1 = px.pie(df, names='subject', values='duration_hours',
                     title="Time Spent per Subject")
        st.plotly_chart(fig1, use_container_width=True)
        
        # Time Trend Chart
        st.subheader("Study Time Trend")
        df['date'] = pd.to_datetime(df['start_time']).dt.date
        time_series = df.groupby('date')['duration_hours'].sum().reset_index()
        fig2 = px.line(time_series, x='date', y='duration_hours',
                      title="Daily Study Time Trend")
        st.plotly_chart(fig2, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def main():
    st.title("📚 StudyMetrics")
    
    # Timer Section
    st.header("⏱️ Study Timer")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        subject = st.selectbox(
            "Select Subject:",
            ["General", "Math", "Science", "History", "Language"],
            key="subject_select"
        )
        
        current_elapsed = calculate_elapsed_time()
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem; 
                      background: #1e88e5; color: white; 
                      border-radius: 15px; font-size: 2.5rem;">
                {format_time(current_elapsed)}
            </div>
        """, unsafe_allow_html=True)
        
        control_col1, control_col2 = st.columns(2)
        with control_col1:
            if not st.session_state.running:
                if st.button("▶️ Start Session", key="start", use_container_width=True):
                    handle_start()
            else:
                if st.button("⏹️ Stop Session", key="stop", type="primary", use_container_width=True):
                    handle_stop(subject)
        
        with control_col2:
            if st.button("🔄 Reset Timer", key="reset", use_container_width=True):
                handle_reset()
    
    with col2:
        st.subheader("Current Weather")
        weather_data = weather_service.get_weather()
        if weather_data:
            st.metric(label="Temperature", value=f"{weather_data['temperature']}°C")
            st.metric(label="Condition", value=weather_data['condition'])
        else:
            st.warning("Weather service unavailable")
    
    # Analytics Section
    show_analytics()

if __name__ == "__main__":
    main()