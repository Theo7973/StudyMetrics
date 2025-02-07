import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, List

class EnhancedAnalytics:
    def __init__(self, db_manager):
        self.db = db_manager
        self._weekday_order = ['Monday', 'Tuesday', 'Wednesday', 
                             'Thursday', 'Friday', 'Saturday', 'Sunday']

    def get_study_data(self) -> pd.DataFrame:
        """Fetch and prepare study session data with proper type handling."""
        sessions = self.db.get_all_sessions()
        
        if not sessions:
            return pd.DataFrame()
            
        df = pd.DataFrame(sessions, columns=[
            'id', 'start_time', 'end_time', 'duration', 
            'subject', 'weather_condition', 'location'
        ])
        
        # Convert and validate datetime fields
        df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
        df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')
        
        # Handle invalid durations
        df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
        df['duration_hours'] = df['duration'] / 3600
        
        # Clean invalid rows
        df = df.dropna(subset=['start_time', 'duration_hours'])
        return df

    def create_study_trends_plot(self) -> go.Figure:
        """Create interactive plot with enhanced features."""
        df = self.get_study_data()
        
        if df.empty:
            return self._create_empty_figure("No study data available")
        
        # Aggregate data
        daily_study = df.groupby([df['start_time'].dt.date, 'subject'])['duration_hours'].sum().reset_index()
        
        # Create base figure
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
            },
            hover_data={'subject': True, 'duration_hours': ':.2f'}
        )
        
        # Add peak session annotations
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
        
        # Add interactive elements
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1d", step="day", stepmode="backward"),
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            ),
            hovermode='x unified',
            plot_bgcolor='rgba(240,240,240,0.9)'
        )
        
        return fig

    def create_productivity_analysis(self) -> go.Figure:
        """Create comprehensive productivity dashboard with enhanced visuals."""
        df = self.get_study_data()
        
        if df.empty:
            return self._create_empty_figure("No productivity data available")
        
        # Prepare data
        df['hour'] = df['start_time'].dt.hour
        df['weekday'] = pd.Categorical(
            df['start_time'].dt.day_name(),
            categories=self._weekday_order,
            ordered=True
        )
        
        # Create figure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Subject Time Distribution',
                'Hourly Productivity Patterns',
                'Weather Impact Analysis',
                'Weekly Study Rhythm'
            ),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "polar"}]]
        )
        
        # Subject Distribution Pie Chart
        subject_data = df.groupby('subject', observed=False)['duration_hours'].sum()
        fig.add_trace(
            go.Pie(
                labels=subject_data.index,
                values=subject_data.values,
                hole=0.4,
                hoverinfo='label+percent+value',
                textinfo='percent'
            ),
            row=1, col=1
        )
        
        # Hourly Productivity Bar Chart
        hourly_data = df.groupby('hour', observed=False)['duration_hours'].mean()
        fig.add_trace(
            go.Bar(
                x=hourly_data.index,
                y=hourly_data.values,
                marker_color='#636efa',
                hoverinfo='x+y'
            ),
            row=1, col=2
        )
        
        # Weather Impact Bar Chart
        weather_data = df.groupby('weather_condition', observed=False)['duration_hours'].mean()
        fig.add_trace(
            go.Bar(
                x=weather_data.index,
                y=weather_data.values,
                marker_color='#00cc96',
                hoverinfo='x+y'
            ),
            row=2, col=1
        )
        
        # Weekly Pattern Radar Chart
        weekly_data = df.groupby('weekday', observed=False)['duration_hours'].mean()
        fig.add_trace(
            go.Scatterpolar(
                r=weekly_data.values,
                theta=weekly_data.index,
                fill='toself',
                line_color='#ef553b',
                hoverinfo='theta+r'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text='Productivity Analysis Dashboard',
            showlegend=False,
            margin=dict(t=100),
            annotations=[
                dict(
                    text="Hover over elements for details!",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=1.15
                )
            ]
        )
        
        return fig

    def generate_insights_report(self) -> Tuple[str, List[str]]:
        """Generate detailed insights report with statistical analysis."""
        df = self.get_study_data()
        
        if df.empty:
            return "No data available for insights", []
        
        insights = []
        warnings = []
        
        # Basic statistics
        total_hours = df['duration_hours'].sum()
        avg_session = df['duration_hours'].mean()
        insights.append(f"📊 Total Study Time: {total_hours:.1f} hours")
        insights.append(f"⏱️ Average Session Duration: {avg_session:.1f} hours")
        
        # Subject analysis
        subject_stats = df.groupby('subject')['duration_hours'].agg(['sum', 'count', 'mean'])
        top_subject = subject_stats['sum'].idxmax()
        insights.append(
            f"🏆 Top Subject: {top_subject} "
            f"({subject_stats.loc[top_subject, 'sum']:.1f} hours over "
            f"{subject_stats.loc[top_subject, 'count']} sessions)"
        )
        
        # Time analysis
        peak_hour = df.groupby(df['start_time'].dt.hour)['duration_hours'].sum().idxmax()
        insights.append(f"⏰ Peak Productivity Hour: {peak_hour:02d}:00")
        
        # Weather analysis
        if 'weather_condition' in df.columns:
            weather_impact = df.groupby('weather_condition')['duration_hours'].mean()
            best_weather = weather_impact.idxmax()
            insights.append(
                f"🌤️ Best Studying Weather: {best_weather} "
                f"(avg {weather_impact[best_weather]:.1f} hours/session)"
            )
        
        # Warnings
        if (df['duration_hours'] > 8).any():
            warnings.append("⚠️ Long sessions detected (over 8 hours)! Consider taking more breaks.")
            
        if df['subject'].nunique() == 1:
            warnings.append("⚠️ You're focusing heavily on one subject. Consider diversifying your study topics.")
        
        return '\n'.join(insights), warnings

    def _create_empty_figure(self, message: str) -> go.Figure:
        """Create placeholder figure for empty datasets."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(
            plot_bgcolor='white',
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False)
        )
        return fig