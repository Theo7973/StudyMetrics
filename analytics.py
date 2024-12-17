import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime, timedelta

class Analytics:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_subject_pie_chart(self, frame):
        # Get data from database
        sessions = self.db.get_all_sessions()
        df = pd.DataFrame(sessions, columns=['id', 'start_time', 'end_time', 'duration', 'subject', 'weather', 'location'])
        
        # Group by subject and sum duration
        subject_times = df.groupby('subject')['duration'].sum()

        # Create pie chart
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.pie(subject_times.values, labels=subject_times.index, autopct='%1.1f%%')
        ax.set_title('Study Time by Subject')

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        return canvas.get_tk_widget()

    def create_weekly_study_chart(self, frame):
        # Get data from database
        sessions = self.db.get_all_sessions()
        df = pd.DataFrame(sessions, columns=['id', 'start_time', 'end_time', 'duration', 'subject', 'weather', 'location'])
        
        # Convert start_time to datetime if it's string
        df['start_time'] = pd.to_datetime(df['start_time'])
        
        # Group by date and sum duration
        daily_times = df.groupby(df['start_time'].dt.date)['duration'].sum()

        # Create line chart
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.plot(daily_times.index, daily_times.values / 3600)  # Convert to hours
        ax.set_title('Study Hours by Date')
        ax.set_xlabel('Date')
        ax.set_ylabel('Hours')
        fig.autofmt_xdate()  # Angle and align the tick labels

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        return canvas.get_tk_widget()