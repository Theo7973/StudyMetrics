import matplotlib.pyplot as plt
from matplotlib.figure import Figure
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
        
        # Convert and clean data
        df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
        df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')
        df['duration_hours'] = pd.to_numeric(df['duration'], errors='coerce') / 3600
        return df.dropna(subset=['start_time', 'duration_hours'])

    def create_study_trends_plot(self):
        df = self.get_study_data()
        if df.empty:
            return self._create_empty_figure("No study data available")
        
        # Process data with proper date handling
        df['date'] = df['start_time'].dt.date
        daily_study = df.groupby(['date', 'subject'])['duration_hours'].sum().reset_index()
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Plot lines for each subject
        for subject in daily_study['subject'].unique():
            subject_data = daily_study[daily_study['subject'] == subject]
            ax.plot(subject_data['date'], subject_data['duration_hours'], 
                   marker='o', label=subject)
        
        ax.set_title('Study Hours Trend')
        ax.set_xlabel('Date')
        ax.set_ylabel('Hours Studied')
        ax.legend()
        ax.grid(True)
        
        fig.tight_layout()
        return fig

    def create_productivity_dashboard(self):
        df = self.get_study_data()
        if df.empty:
            return self._create_empty_figure("No productivity data available")
        
        # Create figure with subplots
        fig = Figure(figsize=(12, 8))
        
        # Subject Distribution (Pie Chart)
        ax1 = fig.add_subplot(221)
        subject_data = df.groupby('subject')['duration_hours'].sum()
        ax1.pie(subject_data.values, labels=subject_data.index, autopct='%1.1f%%')
        ax1.set_title('Subject Distribution')

        # Hourly Productivity (Bar Chart)
        ax2 = fig.add_subplot(222)
        df['hour'] = df['start_time'].dt.hour
        hourly_data = df.groupby('hour')['duration_hours'].mean()
        ax2.bar(hourly_data.index, hourly_data.values)
        ax2.set_title('Hourly Productivity')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Average Hours')

        # Weather Impact (Bar Chart)
        ax3 = fig.add_subplot(223)
        weather_data = df.groupby('weather_condition')['duration_hours'].mean()
        ax3.bar(weather_data.index, weather_data.values)
        ax3.set_title('Weather Impact')
        ax3.set_xlabel('Weather')
        ax3.set_ylabel('Average Hours')
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

        # Weekly Pattern (Polar Plot)
        ax4 = fig.add_subplot(224, projection='polar')
        df['weekday'] = pd.Categorical(
            df['start_time'].dt.day_name(),
            categories=self._weekday_order,
            ordered=True
        )
        weekly_data = df.groupby('weekday')['duration_hours'].mean()
        angles = [i/float(len(self._weekday_order))*2*3.14159 for i in range(len(self._weekday_order))]
        angles += angles[:1]  # complete the circle
        values = weekly_data.values.tolist()
        values += values[:1]  # complete the circle
        ax4.plot(angles, values)
        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(self._weekday_order)
        ax4.set_title('Weekly Pattern')

        fig.tight_layout()
        return fig

    def _create_empty_figure(self, message):
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, message, horizontalalignment='center',
                verticalalignment='center', transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig