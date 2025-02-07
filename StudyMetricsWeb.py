import streamlit as st
import time
from datetime import datetime
from database import DatabaseManager
from api_service import WeatherService

# Page configuration
st.set_page_config(
    page_title="StudyMetrics",
    layout="wide"
)

# Initialize services
@st.cache_resource
def init_services():
    db = DatabaseManager()
    weather_service = WeatherService()
    return db, weather_service

db, weather_service = init_services()

# Initialize session state
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

def handle_reset():
    """Reset timer callback"""
    st.session_state.running = False
    st.session_state.start_time = None
    st.session_state.elapsed_time = 0

def main():
    st.title("📚 StudyMetrics")
    
    # Timer container
    st.header("⏱️ Study Timer")
    
    # Subject selection
    subject = st.selectbox(
        "Select Subject:",
        ["General", "Math", "Science", "History", "Language"]
    )
    
    # Timer display
    st.markdown("""
        <style>
        .timer-display {
            font-size: 4rem;
            text-align: center;
            padding: 2rem;
            background: linear-gradient(45deg, #1e88e5, #1565c0);
            color: white;
            border-radius: 15px;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Calculate and display current time
    current_elapsed = calculate_elapsed_time()
    st.markdown(
        f'<div class="timer-display">{format_time(current_elapsed)}</div>',
        unsafe_allow_html=True
    )
    
    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.running:
            if st.button("▶️ Start", key="start"):
                handle_start()
        else:
            if st.button("⏸️ Stop", key="stop"):
                handle_stop(subject)
    
    with col2:
        if st.button("🔄 Reset", key="reset"):
            handle_reset()
    
    # Weather display
    weather_data = weather_service.get_weather()
    if weather_data:
        st.sidebar.markdown("### Current Weather")
        st.sidebar.write(f"🌡️ {weather_data['temperature']}°C")
        st.sidebar.write(f"☁️ {weather_data['condition']}")
    
    # Force refresh while timer is running
    if st.session_state.running:
        time.sleep(0.1)  # Small delay to prevent excessive refreshing
        st.experimental_rerun()

if __name__ == "__main__":
    main()