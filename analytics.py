# -*- coding: utf-8 -*-
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

class EnhancedAnalytics:
    def __init__(self, db_manager):
        self.db = db_manager
        self._weekday_order = ['Monday', 'Tuesday', 'Wednesday', 
                             'Thursday', 'Friday', 'Saturday', 'Sunday']

    def get_study_data(self):
        sessions = self.db.get_all_sessions()
        if not sessions:
            return pd.DataFrame()
            
        df = pd.DataFrame(sessions, columns=[
            "id", "start_time", "end_time", "duration",
            "subject", "weather_condition", "location"
        ])
        
        df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
        df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')
        df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
        df['duration_hours'] = df['duration'] / 3600
        return df.dropna(subset=['start_time', 'duration_hours'])

    def create_study_trends_plot(self):
        df = self.get_study_data()
        if df.empty:
            return self._create_empty_figure("No study data available")
        
        daily_study = df.groupby([df['start_time'].dt.date, 'subject'])['duration_hours'].sum().reset_index()
        
        fig = px.line(
            daily_study, 
            x='start_time', 
            y='duration_hours',
            color='subject',
            title='Study Hours Trend by Subject',
            labels={'start_time': 'Date', 'duration_hours': 'Hours Studied'},
            hover_data={'subject': True, 'duration_hours': ':.2f'}
        )
        
        max_sessions = daily_study.loc[daily_study.groupby('subject')['duration_hours'].idxmax()]
        for _, row in max_sessions.iterrows():
            fig.add_annotation(
                x=row['start_time'],
                y=row['duration_hours'],
                text=f"Peak {row['subject']}<br>{row['duration_hours']:.1f}h",
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-40
            )
            
        fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            )
        ),
        hovermode='x unified',  # Moved to main layout
        plot_bgcolor='rgba(240,240,240,0.9)'  # Moved to main layout
    )
        return fig

    def create_productivity_dashboard(self):
        df = self.get_study_data()
        if df.empty:
            return self._create_empty_figure("No productivity data available")
        
        df['hour'] = df['start_time'].dt.hour
        df['weekday'] = pd.Categorical(
            df['start_time'].dt.day_name(),
            categories=self._weekday_order,
            ordered=True
        )
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Subject Distribution',
                'Hourly Productivity',
                'Weather Impact',
                'Weekly Pattern'
            ),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "polar"}]]
        )
        
        # Subject Distribution
        subject_data = df.groupby('subject')['duration_hours'].sum()
        fig.add_trace(
            go.Pie(labels=subject_data.index, values=subject_data.values, hole=0.4),
            row=1, col=1
        )
        
        # Hourly Productivity
        hourly_data = df.groupby('hour')['duration_hours'].mean()
        fig.add_trace(
            go.Bar(x=hourly_data.index, y=hourly_data.values),
            row=1, col=2
        )
        
        # Weather Impact
        weather_data = df.groupby('weather_condition')['duration_hours'].mean()
        fig.add_trace(
            go.Bar(x=weather_data.index, y=weather_data.values),
            row=2, col=1
        )
        
        # Weekly Pattern
        weekly_data = df.groupby('weekday')['duration_hours'].mean()
        fig.add_trace(
            go.Scatterpolar(r=weekly_data.values, theta=weekly_data.index, fill='toself'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text='Productivity Dashboard',
            showlegend=False
        )
        return fig

    def _create_empty_figure(self, message):
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        return fig