import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from database import DatabaseManager
from api_service import WeatherService

st.set_page_config(
    page_title="StudyMetrics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    return DatabaseManager(), WeatherService()

db, weather_service = init_services()

# Timer state
if 'timer' not in st.session_state:
    st.session_state.timer = {
        'start_time': None,
        'elapsed': 0,
        'running': False
    }

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_elapsed_time():
    if st.session_state.timer['running']:
        current = time.time()
        start = st.session_state.timer['start_time']
        return current - start + st.session_state.timer['elapsed']
    return st.session_state.timer['elapsed']

def handle_start():
    st.session_state.timer['running'] = True
    st.session_state.timer['start_time'] = time.time()

def handle_stop(subject):
    if st.session_state.timer['running']:
        final_time = get_elapsed_time()
        st.session_state.timer['running'] = False
        st.session_state.timer['elapsed'] = 0
        st.session_state.timer['start_time'] = None
        
        weather_data = weather_service.get_weather()
        weather_condition = weather_data.get('condition', 'Unknown') if weather_data else 'Unknown'
        
        db.save_session(
            duration=int(final_time),
            subject=subject,
            weather=weather_condition
        )
        st.success(f"Session saved: {format_time(final_time)}")

def handle_reset():
    st.session_state.timer['running'] = False
    st.session_state.timer['start_time'] = None
    st.session_state.timer['elapsed'] = 0

def main():
    st.title("📚 StudyMetrics")
    
    # Timer Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        subject = st.selectbox(
            "Select Subject:",
            ["General", "Math", "Science", "History", "Language"],
            key="subject_select"
        )
        
        # Timer Display (using placeholder for smoother updates)
        time_display = st.empty()
        time_display.markdown(f"""
            <div style="text-align: center; padding: 2rem; 
                      background: #1e88e5; color: white; 
                      border-radius: 15px; font-size: 2.5rem;">
                {format_time(get_elapsed_time())}
            </div>
        """, unsafe_allow_html=True)
        
        # Controls
        col3, col4 = st.columns(2)
        with col3:
            if not st.session_state.timer['running']:
                if st.button("▶️ Start", key="start", use_container_width=True):
                    handle_start()
            else:
                if st.button("⏹️ Stop", key="stop", type="primary", use_container_width=True):
                    handle_stop(subject)
        
        with col4:
            if st.button("🔄 Reset", key="reset", use_container_width=True):
                handle_reset()
    
    # Weather Section
    with col2:
        st.subheader("Florida Weather")
        weather_data = weather_service.get_weather()
        if weather_data:
            st.metric(
                label="Temperature", 
                value=f"{weather_data['temperature']}°F",
                delta=f"Feels like {weather_data['feels_like']}°F"
            )
            st.metric("Condition", weather_data['condition'])
            st.metric("Humidity", f"{weather_data['humidity']}%")
        else:
            st.warning("Weather service temporarily unavailable")
    
    # Analytics Section (your existing analytics code here)
    # ...

    # Update timer more frequently but with less overhead
    if st.session_state.timer['running']:
        time.sleep(0.05)  # Reduced sleep time for more frequent updates
        st.rerun()

if __name__ == "__main__":
    main()