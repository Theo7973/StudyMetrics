import streamlit as st
import time
from datetime import datetime
from database import DatabaseManager
from api_service import WeatherService
from enhanced_analytics import EnhancedAnalytics
from data_utils import DataExporter, ErrorHandler, validate_study_session

# Page configuration
st.set_page_config(
    page_title="StudyMetrics Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    db = DatabaseManager()
    weather_service = WeatherService()
    analytics = EnhancedAnalytics(db)
    exporter = DataExporter(db)
    return db, weather_service, analytics, exporter

db, weather_service, analytics, exporter = init_services()

# Custom CSS with modern styling
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
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

def main():
    st.title("📚 StudyMetrics Pro")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Study Timer", "Analytics Dashboard", "Export Data"]
    )
    
    if page == "Study Timer":
        show_timer_page()
    elif page == "Analytics Dashboard":
        show_analytics_page()
    else:
        show_export_page()

def show_timer_page():
    st.header("⏱️ Study Timer")
    
    # Create two columns for layout
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        # Subject selection with error handling
        try:
            subject = st.selectbox(
                "Select Subject:",
                ["General", "Math", "Science", "History", "Language"]
            )
            
            # Initialize session state
            if 'time_elapsed' not in st.session_state:
                st.session_state.time_elapsed = 0
            if 'running' not in st.session_state:
                st.session_state.running = False
            
            # Timer display
            st.markdown(
                f'<div class="timer-display">{format_time(st.session_state.time_elapsed)}</div>',
                unsafe_allow_html=True
            )
            
            # Control buttons
            col1,