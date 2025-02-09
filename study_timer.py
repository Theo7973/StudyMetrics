import tkinter as tk
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
        self.update_weather()  # Initial weather update
        self.update_stats()    # Initial stats update
        
    def setup_gui(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Apply theme configuration
        style = ttk.Style()
        style.configure("Timer.TLabel", font=('Arial', 48))
        style.configure("Stats.TLabel", font=('Arial', 12))
        style.configure("Weather.TLabel", font=('Arial', 10))
        
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
            style="Timer.TLabel"
        )
        self.timer_display.grid(row=1, column=0, columnspan=2, pady=20)
        
        # Weather info
        self.weather_frame = ttk.LabelFrame(self.main_frame, text="Current Weather", padding="5")
        self.weather_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.weather_temp = ttk.Label(self.weather_frame, style="Weather.TLabel")
        self.weather_temp.grid(row=0, column=0, padx=5)
        
        self.weather_cond = ttk.Label(self.weather_frame, style="Weather.TLabel")
        self.weather_cond.grid(row=0, column=1, padx=5)
        
        self.weather_humid = ttk.Label(self.weather_frame, style="Weather.TLabel")
        self.weather_humid.grid(row=0, column=2, padx=5)
        
        # Control buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(
            self.button_frame,
            text="Start",
            command=self.toggle_timer,
            width=20
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.reset_button = ttk.Button(
            self.button_frame,
            text="Reset",
            command=self.reset_timer,
            width=20
        )
        self.reset_button.grid(row=0, column=1, padx=5)
        
        # Stats display
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="Statistics", padding="5")
        self.stats_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.stats_label = ttk.Label(self.stats_frame, style="Stats.TLabel")
        self.stats_label.grid(row=0, column=0)
        
    def toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.start_button.config(text="Start")
            self.save_current_session()
        else:
            self.timer_running = True
            self.start_button.config(text="Stop")
            self.update_timer()
    
    def update_timer(self):
        if self.timer_running:
            self.time_elapsed += 1
            self.update_display()
            self.root.after(1000, self.update_timer)
    
    def update_display(self):
        hours = self.time_elapsed // 3600
        minutes = (self.time_elapsed % 3600) // 60
        seconds = self.time_elapsed % 60
        self.timer_display.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def reset_timer(self):
        if self.timer_running:
            self.save_current_session()
        self.time_elapsed = 0
        self.timer_running = False
        self.start_button.config(text="Start")
        self.update_display()
        self.update_stats()
    
    def save_current_session(self):
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session: {str(e)}")
    
    def update_weather(self):
        try:
            weather_data = self.weather_service.get_weather()
            if weather_data:
                self.weather_temp.config(text=f"Temperature: {weather_data['temperature']}°F")
                self.weather_cond.config(text=f"Condition: {weather_data['condition']}")
                self.weather_humid.config(text=f"Humidity: {weather_data['humidity']}%")
        except Exception as e:
            print(f"Weather update failed: {str(e)}")
        
        # Update weather every 2 minutes
        self.root.after(120000, self.update_weather)
    
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