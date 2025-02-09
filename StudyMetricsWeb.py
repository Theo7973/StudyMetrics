import streamlit as st
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
from database import DatabaseManager
from api_service import WeatherService

# Performance optimization for Streamlit
st.set_page_config(
    page_title="StudyMetrics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services with caching
@st.cache_resource
def init_services():
    return DatabaseManager(), WeatherService()

db, weather_service = init_services()

# Session state initialization
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0
if 'running' not in st.session_state:
    st.session_state.running = False
if 'last_weather_update' not in st.session_state:
    st.session_state.last_weather_update = 0
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def update_weather():
    current_time = time.time()
    # Update weather every 5 minutes
    if (current_time - st.session_state.last_weather_update) > 300:
        st.session_state.weather_data = weather_service.get_weather()
        st.session_state.last_weather_update = current_time
    return st.session_state.weather_data

def handle_start():
    st.session_state.running = True
    st.session_state.start_time = time.time()

def handle_stop(subject):
    if st.session_state.running:
        final_time = st.session_state.elapsed_time
        st.session_state.running = False
        st.session_state.start_time = None
        st.session_state.elapsed_time = 0
        
        try:
            weather_data = update_weather()
            weather_condition = weather_data.get('condition', 'Unknown') if weather_data else 'Unknown'
            db.save_session(
                duration=int(final_time),
                subject=subject,
                weather=weather_condition
            )
            st.success(f"Session saved: {format_time(final_time)}")
        except Exception as e:
            st.error(f"Error saving session: {str(e)}")

def handle_reset():
    st.session_state.running = False
    st.session_state.start_time = None
    st.session_state.elapsed_time = 0

@st.cache_data(ttl=300)  # Cache analytics for 5 minutes
def get_analytics_data():
    sessions = db.get_all_sessions()
    if not sessions:
        return None
        
    df = pd.DataFrame(sessions, columns=[
        "id", "start_time", "end_time", "duration", 
        "subject", "weather_condition", "location"
    ])
    df['duration_hours'] = df['duration'] / 3600
    df['date'] = pd.to_datetime(df['start_time']).dt.date
    return df

def main():
    st.title("📚 StudyMetrics")
    
    # Create a placeholder for the timer display
    timer_placeholder = st.empty()
    
    # Timer Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        subject = st.selectbox(
            "Select Subject:",
            ["General", "Math", "Science", "History", "Language"],
            key="subject_select"
        )
        
        # Update timer if running
        if st.session_state.running and st.session_state.start_time is not None:
            st.session_state.elapsed_time = time.time() - st.session_state.start_time
        
        # Display timer
        timer_placeholder.markdown(f"""
            <div style="text-align: center; padding: 2rem; 
                      background: #1e88e5; color: white; 
                      border-radius: 15px; font-size: 2.5rem;">
                {format_time(st.session_state.elapsed_time)}
            </div>
        """, unsafe_allow_html=True)
        
        # Controls
        col3, col4 = st.columns(2)
        with col3:
            if not st.session_state.running:
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
        st.subheader("Current Weather")
        weather_data = update_weather()
        if weather_data:
            st.metric("Temperature", f"{weather_data['temperature']}°C")
            st.metric("Condition", weather_data['condition'])
            st.metric("Humidity", f"{weather_data['humidity']}%")
    
    # Analytics Section
    st.header("📈 Study Analytics")
    df = get_analytics_data()
    
    if df is not None:
        # Summary metrics
        total_hours = df['duration_hours'].sum()
        total_sessions = len(df)
        avg_duration = df['duration_hours'].mean()
        
        metrics_cols = st.columns(3)
        metrics_cols[0].metric("Total Hours", f"{total_hours:.1f}")
        metrics_cols[1].metric("Sessions", total_sessions)
        metrics_cols[2].metric("Avg Duration", f"{avg_duration:.1f}h")
        
        # Charts
        chart_cols = st.columns(2)
        with chart_cols[0]:
            fig1 = px.pie(
                df, 
                names='subject', 
                values='duration_hours',
                title="Study Time Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with chart_cols[1]:
            daily_data = df.groupby('date')['duration_hours'].sum().reset_index()
            fig2 = px.line(
                daily_data, 
                x='date', 
                y='duration_hours',
                title="Daily Study Hours",
                labels={'duration_hours': 'Hours', 'date': 'Date'}
            )
            fig2.update_traces(line_color='#1e88e5')
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No study sessions recorded yet!")

    # Auto-refresh for timer
    if st.session_state.running:
        st.rerun()

if __name__ == "__main__":
    main()