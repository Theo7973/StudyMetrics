import tkinter as tk
import streamlit as st
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import time
from database import DatabaseManager
from api_service import WeatherService

class StudyTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("StudyMetrics")
        self.root.geometry("800x600")

        # Initialize services
        self.db = DatabaseManager()
        self.weather_service = WeatherService()

        # Timer variables
        self.time_elapsed = 0
        self.timer_running = False
        self.current_subject = "General"

        self.setup_gui()

    def setup_gui(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Subject selection
        self.subject_label = ttk.Label(self.main_frame, text="Study Subject:")
        self.subject_label.grid(row=0, column=0, pady=5)
        
        self.subject_var = tk.StringVar(value="General")
        self.subject_combo = ttk.Combobox(
            self.main_frame, 
            textvariable=self.subject_var,
            values=["General", "Math", "Science", "History", "Language"]
        )
        self.subject_combo.grid(row=0, column=1, pady=5)

        # Timer display
        self.timer_display = ttk.Label(
            self.main_frame,
            text="00:00:00",
            font=('Arial', 30)
        )
        self.timer_display.grid(row=1, column=0, columnspan=2, pady=20)

        # Weather info
        self.weather_label = ttk.Label(self.main_frame, text="Loading weather...")
        self.weather_label.grid(row=2, column=0, columnspan=2, pady=5)
        self.update_weather()

        # Control buttons
        self.start_button = ttk.Button(
            self.main_frame,
            text="Start",
            command=self.toggle_timer,
            width=20
        )
        self.start_button.grid(row=3, column=0, pady=10)

        self.reset_button = ttk.Button(
            self.main_frame,
            text="Reset",
            command=self.reset_timer,
            width=20
        )
        self.reset_button.grid(row=3, column=1, pady=10)

        # Stats display
        self.stats_label = ttk.Label(self.main_frame, text="Loading stats...")
        self.stats_label.grid(row=4, column=0, columnspan=2, pady=10)
        self.update_stats()

        # Add notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=5, column=0, columnspan=2, pady=10, sticky="nsew")

        # Timer tab (existing content)
        self.timer_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.timer_tab, text="Timer")

        # Analytics tab
        self.analytics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_tab, text="Analytics")

        # Add charts to analytics tab
        from analytics import Analytics
        self.analytics = Analytics(self.db)
        
        # Create and pack charts
        pie_chart = self.analytics.create_subject_pie_chart(self.analytics_tab)
        pie_chart.pack(pady=10)

        weekly_chart = self.analytics.create_weekly_study_chart(self.analytics_tab)
        weekly_chart.pack(pady=10)

    def toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.start_button.config(text="Start")
            # Save session when stopping
            self.save_current_session()
        else:
            self.timer_running = True
            self.start_button.config(text="Stop")
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.time_elapsed += 1
            hours = self.time_elapsed // 3600
            minutes = (self.time_elapsed % 3600) // 60
            seconds = self.time_elapsed % 60
            
            time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_display.config(text=time_string)
            
            self.root.after(1000, self.update_timer)

    def reset_timer(self):
        if self.timer_running:
            self.save_current_session()
        self.time_elapsed = 0
        self.timer_running = False
        self.start_button.config(text="Start")
        self.timer_display.config(text="00:00:00")
        self.update_stats()

    def save_current_session(self):
        weather_data = self.weather_service.get_weather()
        weather_condition = weather_data['condition'] if weather_data else "Unknown"
        
        self.db.save_session(
            duration=self.time_elapsed,
            subject=self.subject_var.get(),
            weather=weather_condition
        )
        self.update_stats()

    def update_weather(self):
        weather_data = self.weather_service.get_weather()
        if weather_data:
            self.weather_label.config(
                text=f"Current Weather: {weather_data['condition']}, "
                     f"{weather_data['temperature']}C"
            )
        self.root.after(300000, self.update_weather)  # Update every 5 minutes

    def update_stats(self):
        total_time = self.db.get_total_study_time()
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        
        self.stats_label.config(
            text=f"Total Study Time: {hours}h {minutes}m"
        )

# Create and run application
if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTimer(root)
    root.mainloop()