import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

class EnhancedAnalytics:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_study_data(self):
        """Fetch and prepare study session data."""
        sessions = self.db.get_all_sessions()
        df = pd.DataFrame(sessions, columns=[
            'id', 'start_time', 'end_time', 'duration', 
            'subject', 'weather_condition', 'location'
        ])
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        df['duration_hours'] = df['duration'] / 3600
        return df

    def create_study_trends_plot(self):
        """Create an interactive study trends visualization."""
        df = self.get_study_data()
        
        # Daily aggregation
        daily_study = df.groupby([
            df['start_time'].dt.date, 
            'subject'
        ])['duration_hours'].sum().reset_index()

        fig = px.line(
            daily_study, 
            x='start_time', 
            y='duration_hours',
            color='subject',
            title='Study Hours Trend by Subject',
            labels={
                'start_time': 'Date',
                'duration_hours': 'Hours Studied',
                'subject': 'Subject'
            }
        )
        
        fig.update_layout(
            hovermode='x unified',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig

    def create_productivity_analysis(self):
        """Create a comprehensive productivity analysis dashboard."""
        df = self.get_study_data()
        
        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Study Time Distribution by Subject',
                'Average Session Duration by Time of Day',
                'Study Sessions by Weather',
                'Weekly Study Pattern'
            )
        )
        
        # 1. Subject distribution (pie chart)
        subject_total = df.groupby('subject')['duration_hours'].sum()
        fig.add_trace(
            go.Pie(
                labels=subject_total.index,
                values=subject_total.values,
                showlegend=True
            ),
            row=1, col=1
        )
        
        # 2. Time of day analysis (bar chart)
        df['hour'] = df['start_time'].dt.hour
        hourly_avg = df.groupby('hour')['duration_hours'].mean()
        fig.add_trace(
            go.Bar(
                x=hourly_avg.index,
                y=hourly_avg.values,
                showlegend=False
            ),
            row=1, col=2
        )
        
        # 3. Weather impact (bar chart)
        weather_study = df.groupby('weather_condition')['duration_hours'].mean()
        fig.add_trace(
            go.Bar(
                x=weather_study.index,
                y=weather_study.values,
                showlegend=False
            ),
            row=2, col=1
        )
        
        # 4. Weekly pattern (radar chart)
        df['weekday'] = df['start_time'].dt.day_name()
        weekly_study = df.groupby('weekday')['duration_hours'].mean()
        fig.add_trace(
            go.Scatterpolar(
                r=weekly_study.values,
                theta=weekly_study.index,
                fill='toself',
                showlegend=False
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="Study Productivity Analysis Dashboard"
        )
        
        return fig

    def generate_insights_report(self):
        """Generate a text report with key insights."""
        df = self.get_study_data()
        
        insights = []
        
        # Most productive subject
        subject_total = df.groupby('subject')['duration_hours'].sum()
        most_studied = subject_total.idxmax()
        
        insights.append(
            f"Most studied subject: {most_studied} "
            f"({subject_total[most_studied]:.1f} hours)"
        )
        
        # Best study time
        hourly_avg = df.groupby(df['start_time'].dt.hour)['duration_hours'].mean()
        best_hour = hourly_avg.idxmax()
        
        insights.append(
            f"Most productive hour: {best_hour}:00 "
            f"(avg: {hourly_avg[best_hour]:.1f} hours)"
        )
        
        # Weather impact
        weather_impact = df.groupby('weather_condition')['duration_hours'].mean()
        best_weather = weather_impact.idxmax()
        
        insights.append(
            f"Most productive weather: {best_weather} "
            f"(avg: {weather_impact[best_weather]:.1f} hours)"
        )
        
        return "\n".join(insights)