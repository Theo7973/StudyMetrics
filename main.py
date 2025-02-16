# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('TkAgg')  # Set backend before other imports
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from database import DatabaseManager
from api_service import WeatherService
from analytics import EnhancedAnalytics
from data_exporter import DataExporter
from error_handler import validate_study_session, ValidationError

class StudyTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("StudyMetrics Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        # Initialize services
        self.db = DatabaseManager()
        self.weather_service = WeatherService()
        self.analytics = EnhancedAnalytics(self.db)
        self.exporter = DataExporter(self.db)

        # Application state
        self.time_elapsed = 0
        self.timer_running = False
        self.current_weather = None

        # UI Components
        self.trend_fig = None
        self.trend_canvas = None
        self.dashboard_fig = None
        self.dashboard_canvas = None
        self.trend_frame = None
        self.dashboard_frame = None

        # Setup UI
        self.create_widgets()
        self.load_initial_values()
        self.update_weather()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left control panel
        left_panel = ttk.Frame(main_frame, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Right analytics panel
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left panel components
        self.create_subject_selector(left_panel)
        self.create_timer_controls(left_panel)
        self.create_weather_display(left_panel)
        self.create_goal_controls(left_panel)
        self.create_stats_display(left_panel)
        self.create_export_controls(left_panel)

        # Right panel components
        self.create_analytics_display(right_panel)

    def create_subject_selector(self, parent):
        frame = ttk.LabelFrame(parent, text="Study Subject", padding=10)
        frame.pack(fill=tk.X, pady=5)

        self.subject_var = tk.StringVar(value="General")
        ttk.Combobox(
            frame,
            textvariable=self.subject_var,
            values=["General", "Math", "Science", "History", "Language"],
            state="readonly",
            font=('Arial', 12)
        ).pack(fill=tk.X, padx=5, pady=5)

    def create_timer_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="Study Timer", padding=10)
        frame.pack(fill=tk.X, pady=5)

        # Timer display
        self.timer_display = ttk.Label(
            frame,
            text="00:00:00",
            font=('Courier New', 48),
            anchor=tk.CENTER
        )
        self.timer_display.pack(pady=10)

        # Control buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)

        self.start_btn = ttk.Button(
            btn_frame,
            text="Start",
            command=self.toggle_timer,
            width=10
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Reset",
            command=self.reset_timer,
            width=10
        ).pack(side=tk.LEFT, padx=5)

    def create_weather_display(self, parent):
        frame = ttk.LabelFrame(parent, text="Current Weather", padding=10)
        frame.pack(fill=tk.X, pady=5)

        self.weather_labels = {
            'temp': ttk.Label(frame, font=('Arial', 12)),
            'cond': ttk.Label(frame, font=('Arial', 12)),
            'humid': ttk.Label(frame, font=('Arial', 12))
        }

        for lbl in self.weather_labels.values():
            lbl.pack(anchor=tk.W)

    def create_goal_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="Study Goals", padding=10)
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text="Daily Goal (hours):").grid(row=0, column=0, sticky=tk.W)
        self.daily_goal_entry = ttk.Spinbox(
            frame,
            from_=0,
            to=24,
            format="%.1f",
            increment=0.5,
            font=('Arial', 12)
        )
        self.daily_goal_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Weekly Goal (hours):").grid(row=1, column=0, sticky=tk.W)
        self.weekly_goal_entry = ttk.Spinbox(
            frame,
            from_=0,
            to=168,
            increment=1,
            font=('Arial', 12))
        self.weekly_goal_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Button(
            frame,
            text="Update Goals",
            command=self.update_goals
        ).grid(row=2, column=0, columnspan=2, pady=5)

    def create_stats_display(self, parent):
        frame = ttk.LabelFrame(parent, text="Study Statistics", padding=10)
        frame.pack(fill=tk.X, pady=5)

        self.stats_label = ttk.Label(frame, font=('Arial', 12))
        self.stats_label.pack()

        self.goal_progress = {
            'daily': ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=200),
            'weekly': ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=200)
        }

        ttk.Label(frame, text="Daily Progress:").pack(anchor=tk.W)
        self.goal_progress['daily'].pack(fill=tk.X, pady=2)
        ttk.Label(frame, text="Weekly Progress:").pack(anchor=tk.W)
        self.goal_progress['weekly'].pack(fill=tk.X, pady=2)

    def create_export_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="Data Export", padding=10)
        frame.pack(fill=tk.X, pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(
            btn_frame,
            text="Export to CSV",
            command=lambda: self.export_data('csv')
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_frame,
            text="Export to Excel",
            command=lambda: self.export_data('excel')
        ).pack(side=tk.LEFT, padx=2)

    def create_analytics_display(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Trend Analysis Tab
        self.trend_frame = ttk.Frame(notebook)
        self.trend_fig = self.analytics.create_study_trends_plot()
        self.trend_canvas = FigureCanvasTkAgg(self.trend_fig, master=self.trend_frame)
        self.trend_canvas.draw()
        self.trend_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        notebook.add(self.trend_frame, text="Study Trends")

        # Productivity Dashboard Tab
        self.dashboard_frame = ttk.Frame(notebook)
        self.dashboard_fig = self.analytics.create_productivity_dashboard()
        self.dashboard_canvas = FigureCanvasTkAgg(self.dashboard_fig, master=self.dashboard_frame)
        self.dashboard_canvas.draw()
        self.dashboard_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        notebook.add(self.dashboard_frame, text="Productivity Dashboard")

        # Refresh button
        refresh_btn = ttk.Button(
            parent,
            text="Refresh Dashboards",
            command=self.update_dashboards
        )
        refresh_btn.pack(pady=10)

    def update_dashboards(self):
        # Update trend plot
        self.trend_fig = self.analytics.create_study_trends_plot()
        self.trend_canvas.get_tk_widget().destroy()
        self.trend_canvas = FigureCanvasTkAgg(self.trend_fig, master=self.trend_frame)
        self.trend_canvas.draw()
        self.trend_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Update dashboard
        self.dashboard_fig = self.analytics.create_productivity_dashboard()
        self.dashboard_canvas.get_tk_widget().destroy()
        self.dashboard_canvas = FigureCanvasTkAgg(self.dashboard_fig, master=self.dashboard_frame)
        self.dashboard_canvas.draw()
        self.dashboard_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_initial_values(self):
        goals = self.db.get_current_goals()
        self.daily_goal_entry.delete(0, tk.END)
        self.daily_goal_entry.insert(0, f"{goals['daily']/3600:.1f}")
        self.weekly_goal_entry.delete(0, tk.END)
        self.weekly_goal_entry.insert(0, f"{goals['weekly']/3600:.0f}")

    def update_weather(self):
        try:
            weather = self.weather_service.get_weather()
            self.current_weather = weather
            self.weather_labels['temp'].config(
                text=f"Temperature: {weather['temperature']}\u00b0F"
            )
            self.weather_labels['cond'].config(
                text=f"Condition: {weather['condition']}"
            )
            self.weather_labels['humid'].config(
                text=f"Humidity: {weather['humidity']}%"
            )
        except Exception as e:
            messagebox.showerror("Weather Error", f"Failed to update weather: {str(e)}")
        
        self.root.after(300000, self.update_weather)

    def update_goals(self):
        try:
            daily = float(self.daily_goal_entry.get()) * 3600
            weekly = float(self.weekly_goal_entry.get()) * 3600
            self.db.save_goals(int(daily), int(weekly))
            self.update_progress()
            messagebox.showinfo("Success", "Goals updated successfully")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for goals")

    def update_progress(self):
        goals = self.db.get_current_goals()
        daily_study = self.db.get_daily_study_time()
        weekly_study = self.db.get_weekly_study_time()

        # Daily progress
        if goals['daily'] > 0:
            daily_percent = (daily_study / goals['daily']) * 100
            self.goal_progress['daily']['value'] = min(daily_percent, 100)
        else:
            self.goal_progress['daily']['value'] = 0

        # Weekly progress
        if goals['weekly'] > 0:
            weekly_percent = (weekly_study / goals['weekly']) * 100
            self.goal_progress['weekly']['value'] = min(weekly_percent, 100)
        else:
            self.goal_progress['weekly']['value'] = 0

    def toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.start_btn.config(text="Start")
            self.save_session()
        else:
            self.timer_running = True
            self.start_btn.config(text="Stop")
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
        self.time_elapsed = 0
        self.timer_running = False
        self.start_btn.config(text="Start")
        self.timer_display.config(text="00:00:00")
        self.save_session()

    def save_session(self):
        if self.time_elapsed > 0:
            try:
                validate_study_session(self.time_elapsed, self.subject_var.get())
                self.db.save_session(
                    duration=self.time_elapsed,
                    subject=self.subject_var.get(),
                    weather=self.current_weather['condition'] if self.current_weather else "Unknown"
                )
                messagebox.showinfo("Saved", "Study session saved successfully")
                self.update_stats()
                self.update_dashboards()
                self.update_progress()
            except ValidationError as e:
                messagebox.showerror("Validation Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save session: {str(e)}")
            finally:
                self.time_elapsed = 0

    def update_stats(self):
        total_time = self.db.get_total_study_time()
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        self.stats_label.config(text=f"Total Study Time: {hours}h {minutes}m")

    def export_data(self, format_type):
        try:
            if format_type == 'csv':
                filename = self.exporter.export_to_csv()
            elif format_type == 'excel':
                filename = self.exporter.export_to_excel()
            else:
                raise ValidationError("Invalid export format")
            
            messagebox.showinfo("Export Successful", f"Data exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTimer(root)
    root.mainloop()