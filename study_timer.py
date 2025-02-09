# -*- coding: utf-8 -*-
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from database import DatabaseManager
from api_service import WeatherService

class StudyTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("StudyMetrics")
        self.root.geometry("1200x800")

        # Initialize services
        self.db = DatabaseManager()
        self.weather_service = WeatherService()

        # Timer variables
        self.time_elapsed = 0
        self.timer_running = False

        # Create main frames
        self.left_frame = ttk.Frame(root, padding="10")
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        
        self.right_frame = ttk.Frame(root, padding="10")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        self.setup_left_panel()
        self.setup_right_panel()
        self.update_weather()
        self.update_charts()

    def setup_left_panel(self):
        # Subject selection
        subject_frame = ttk.LabelFrame(self.left_frame, text="Study Subject", padding="10")
        subject_frame.pack(fill=tk.X, pady=10)

        self.subject_var = tk.StringVar(value="General")
        self.subject_combo = ttk.Combobox(
            subject_frame,
            textvariable=self.subject_var,
            values=["General", "Math", "Science", "History", "Language"],
            width=30
        )
        self.subject_combo.pack(pady=5)

        # Timer display
        timer_frame = ttk.LabelFrame(self.left_frame, text="Study Timer", padding="10")
        timer_frame.pack(fill=tk.X, pady=10)

        self.timer_display = ttk.Label(
            timer_frame,
            text="00:00:00",
            font=('Arial', 48)
        )
        self.timer_display.pack(pady=10)

        # Control buttons
        button_frame = ttk.Frame(timer_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(
            button_frame,
            text="Start",
            command=self.toggle_timer,
            width=20
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(
            button_frame,
            text="Reset",
            command=self.reset_timer,
            width=20
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Weather info
        weather_frame = ttk.LabelFrame(self.left_frame, text="Current Weather", padding="10")
        weather_frame.pack(fill=tk.X, pady=10)

        self.weather_temp = ttk.Label(weather_frame, font=('Arial', 12))
        self.weather_temp.pack()
        
        self.weather_cond = ttk.Label(weather_frame, font=('Arial', 12))
        self.weather_cond.pack()
        
        self.weather_humid = ttk.Label(weather_frame, font=('Arial', 12))
        self.weather_humid.pack()

        # Stats display
        stats_frame = ttk.LabelFrame(self.left_frame, text="Study Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, font=('Arial', 12))
        self.stats_label.pack()

    def setup_right_panel(self):
        # Analytics title
        ttk.Label(
            self.right_frame,
            text="Study Analytics",
            font=('Arial', 16, 'bold')
        ).pack(pady=10)

        # Charts will be added here
        self.charts_frame = ttk.Frame(self.right_frame)
        self.charts_frame.pack(fill=tk.BOTH, expand=True)

    def update_charts(self):
        # Clear previous charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        # Get study data
        sessions = self.db.get_all_sessions()
        if not sessions:
            ttk.Label(self.charts_frame, text="No study data available").pack()
            return

        df = pd.DataFrame(sessions, columns=[
            "id", "start_time", "end_time", "duration",
            "subject", "weather_condition", "location"
        ])

        # Create figure with subplots
        fig = plt.Figure(figsize=(8, 8))

        # Subject distribution pie chart
        ax1 = fig.add_subplot(211)
        subject_times = df.groupby('subject')['duration'].sum()
        ax1.pie(subject_times.values, labels=subject_times.index, autopct='%1.1f%%')
        ax1.set_title('Time Distribution by Subject')

        # Daily study trend
        ax2 = fig.add_subplot(212)
        df['date'] = pd.to_datetime(df['start_time']).dt.date
        daily_time = df.groupby('date')['duration'].sum() / 3600  # Convert to hours
        ax2.plot(daily_time.index, daily_time.values)
        ax2.set_title('Daily Study Hours')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Hours')
        fig.autofmt_xdate()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.start_button.config(text="Start")
            self.save_session()
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
            self.timer_display.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)

    def reset_timer(self):
        if self.timer_running:
            self.save_session()
        self.time_elapsed = 0
        self.timer_running = False
        self.start_button.config(text="Start")
        self.timer_display.config(text="00:00:00")
        self.update_stats()

    def save_session(self):
        try:
            weather_data = self.weather_service.get_weather()
            weather_condition = weather_data['condition'] if weather_data else "Unknown"
            
            self.db.save_session(
                duration=self.time_elapsed,
                subject=self.subject_var.get(),
                weather=weather_condition
            )
            
            messagebox.showinfo(
                "Session Saved",
                f"Study session saved successfully!\nDuration: {self.time_elapsed//3600:02d}:{(self.time_elapsed%3600)//60:02d}:{self.time_elapsed%60:02d}"
            )
            
            self.update_stats()
            self.update_charts()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session: {str(e)}")

    def update_weather(self):
        try:
            weather_data = self.weather_service.get_weather()
            if weather_data:
                self.weather_temp.config(text=f"Temperature: {weather_data['temperature']}F")
                self.weather_cond.config(text=f"Condition: {weather_data['condition']}")
                self.weather_humid.config(text=f"Humidity: {weather_data['humidity']}%")
        except Exception as e:
            print(f"Weather update failed: {str(e)}")
        
        self.root.after(300000, self.update_weather)  # Update every 5 minutes

    def update_stats(self):
        try:
            total_time = self.db.get_total_study_time()
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            
            stats_text = f"Total Study Time: {hours}h {minutes}m"
            self.stats_label.config(text=stats_text)
        except Exception as e:
            print(f"Stats update failed: {str(e)}")

def main():
    root = tk.Tk()
    app = StudyTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()