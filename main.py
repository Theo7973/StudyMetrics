# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('TkAgg')
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from datetime import datetime
import pandas as pd
import winsound
from database import DatabaseManager
from api_service import WeatherService
from analytics import EnhancedAnalytics
from data_exporter import DataExporter
from error_handler import validate_study_session, ValidationError

class ModernStyle:
    COLORS = {
        'primary': '#2A2F4F',
        'secondary': '#917FB3',
        'accent': '#E5BEEC',
        'background': '#FDE2F3',
        'text': '#2A2F4F',
        'success': '#50C878',
        'warning': '#FFD700',
        'error': '#FF4747',
        'card_bg': '#FFFFFF'
    }
    
    FONTS = {
        'h1': ('Segoe UI', 20, 'bold'),
        'h2': ('Segoe UI', 14, 'bold'),
        'body': ('Segoe UI', 12),
        'numeric': ('Courier New', 14)
    }

class ModernAnalytics(EnhancedAnalytics):
    def create_study_trends_plot(self):
        df = self.get_study_data()
        if df.empty:
            return self._create_empty_figure("No study data available")

        fig = Figure(figsize=(10, 5), facecolor=ModernStyle.COLORS['card_bg'])
        ax = fig.add_subplot(111)
        
        df['date'] = df['start_time'].dt.date
        daily_study = df.groupby(['date', 'subject'])['duration_hours'].sum().reset_index()
        
        subjects = daily_study['subject'].unique()
        colors = plt.cm.viridis(range(len(subjects)))
        
        for subject, color in zip(subjects, colors):
            subject_data = daily_study[daily_study['subject'] == subject]
            ax.plot(subject_data['date'], subject_data['duration_hours'], 
                   marker='o', linestyle='-', color=color, markersize=8,
                   linewidth=2, label=subject)

        ax.set_title('Study Hours Trend', fontsize=14, pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Hours Studied', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(frameon=False, fontsize=10)
        ax.tick_params(axis='both', which='major', labelsize=10)
        fig.tight_layout()

        return fig

    def create_productivity_dashboard(self):
        df = self.get_study_data()
        if df.empty:
            return self._create_empty_figure("No productivity data available")

        fig = Figure(figsize=(12, 8), facecolor=ModernStyle.COLORS['card_bg'])
        gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)

        # Subject Distribution
        ax1 = fig.add_subplot(gs[0, 0])
        subject_data = df.groupby('subject')['duration_hours'].sum()
        explode = [0.1 if i == subject_data.idxmax() else 0 for i in subject_data.index]
        ax1.pie(subject_data, labels=subject_data.index, autopct='%1.1f%%',
                startangle=90, explode=explode, shadow=True,
                colors=plt.cm.Pastel1(range(len(subject_data))))
        ax1.set_title('Subject Distribution', fontsize=12, pad=15)

        # Hourly Productivity
        ax2 = fig.add_subplot(gs[0, 1])
        df['hour'] = df['start_time'].dt.hour
        hourly_data = df.groupby('hour')['duration_hours'].mean()
        ax2.bar(hourly_data.index, hourly_data.values, 
               color=ModernStyle.COLORS['secondary'])
        ax2.set_title('Hourly Productivity', fontsize=12)
        ax2.set_xlabel('Hour of Day', fontsize=10)
        ax2.set_ylabel('Average Hours', fontsize=10)
        ax2.grid(axis='y', linestyle='--', alpha=0.6)

        # Weekly Pattern
        ax3 = fig.add_subplot(gs[1, 0])
        df['weekday'] = pd.Categorical(
            df['start_time'].dt.day_name(),
            categories=self._weekday_order,
            ordered=True
        )
        weekly_data = df.groupby('weekday')['duration_hours'].mean()
        ax3.plot(weekly_data.index, weekly_data.values, 
                marker='o', color=ModernStyle.COLORS['primary'])
        ax3.fill_between(weekly_data.index, weekly_data.values,
                        color=ModernStyle.COLORS['accent'], alpha=0.3)
        ax3.set_title('Weekly Pattern', fontsize=12)
        ax3.set_xlabel('Weekday', fontsize=10)
        ax3.set_ylabel('Average Hours', fontsize=10)
        ax3.grid(True, linestyle='--', alpha=0.6)
        plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')

        # Weather Impact
        ax4 = fig.add_subplot(gs[1, 1])
        weather_data = df.groupby('weather_condition')['duration_hours'].mean()
        ax4.barh(weather_data.index, weather_data.values,
                color=ModernStyle.COLORS['secondary'])
        ax4.set_title('Weather Impact', fontsize=12)
        ax4.set_xlabel('Average Hours', fontsize=10)
        ax4.grid(axis='x', linestyle='--', alpha=0.6)

        fig.tight_layout()
        return fig

class StudyTimer:
    def __init__(self, root):
        self.root = root
        self.style = ModernStyle()
        self.root.configure(bg=self.style.COLORS['background'])
        
        # Initialize services
        self.db = DatabaseManager()
        self.weather_service = WeatherService()
        self.analytics = ModernAnalytics(self.db)
        self.exporter = DataExporter(self.db)

        # Application state
        self.time_elapsed = 0
        self.timer_running = False
        self.current_weather = None
        self.achievements = {
            '10_hours': False,
            '50_hours': False,
            '100_hours': False
        }

        # Setup UI
        self.create_widgets()
        self.load_initial_values()
        self.update_weather()
        self.update_progress()
        self.check_achievements()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=self.style.COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left panel
        left_panel = tk.Frame(main_frame, bg=self.style.COLORS['background'])
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        # Right panel
        right_panel = tk.Frame(main_frame, bg=self.style.COLORS['background'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left panel components
        self.create_control_card(left_panel)
        self.create_weather_card(left_panel)
        self.create_goals_card(left_panel)
        self.create_session_history(left_panel)
        self.create_achievements_card(left_panel)

        # Right panel components
        self.create_analytics_display(right_panel)

    def create_control_card(self, parent):
        card = tk.Frame(parent, bg=self.style.COLORS['card_bg'], padx=20, pady=20)
        card.pack(fill=tk.X, pady=10)

        ttk.Label(card, text="STUDY SESSION", font=self.style.FONTS['h2'], 
                background=self.style.COLORS['card_bg']).pack(anchor=tk.W)
        
        self.subject_var = tk.StringVar(value="General")
        ttk.Combobox(card, textvariable=self.subject_var,
                    values=["General", "Math", "Science", "History", "Language"],
                    state="readonly", font=self.style.FONTS['body']).pack(fill=tk.X, pady=10)

        self.timer_display = ttk.Label(card, text="00:00:00", 
                                      font=('Courier New', 48, 'bold'),
                                      foreground=self.style.COLORS['primary'],
                                      background=self.style.COLORS['card_bg'])
        self.timer_display.pack(pady=15)

        # Progress bars
        self.progress_frame = tk.Frame(card, bg=self.style.COLORS['card_bg'])
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        self.daily_progress = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL,
                                            length=200, mode='determinate')
        self.daily_progress.pack(fill=tk.X, pady=5)
        self.daily_label = ttk.Label(self.progress_frame, 
                                    background=self.style.COLORS['card_bg'])
        self.daily_label.pack()
        
        self.weekly_progress = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL,
                                             length=200, mode='determinate')
        self.weekly_progress.pack(fill=tk.X, pady=5)
        self.weekly_label = ttk.Label(self.progress_frame, 
                                     background=self.style.COLORS['card_bg'])
        self.weekly_label.pack()

        # Control buttons
        btn_frame = tk.Frame(card, bg=self.style.COLORS['card_bg'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="START", command=self.toggle_timer,
                                  bg=self.style.COLORS['primary'], fg='white',
                                  font=self.style.FONTS['h2'], relief='flat')
        self.start_btn.pack(side=tk.LEFT, expand=True, padx=5)
        
        tk.Button(btn_frame, text="RESET", command=self.reset_timer,
                  bg=self.style.COLORS['error'], fg='white',
                  font=self.style.FONTS['h2'], relief='flat').pack(side=tk.LEFT, expand=True, padx=5)

    def create_goals_card(self, parent):
        card = tk.Frame(parent, bg=self.style.COLORS['card_bg'], padx=20, pady=20)
        card.pack(fill=tk.X, pady=10)

        ttk.Label(card, text="STUDY GOALS", font=self.style.FONTS['h2'], 
                background=self.style.COLORS['card_bg']).pack(anchor=tk.W)

        # Daily goal
        daily_frame = tk.Frame(card, bg=self.style.COLORS['card_bg'])
        daily_frame.pack(fill=tk.X, pady=10)
        ttk.Label(daily_frame, text="Daily (hrs):", font=self.style.FONTS['body'],
                 background=self.style.COLORS['card_bg']).pack(side=tk.LEFT)
        self.daily_goal_entry = ttk.Spinbox(daily_frame, from_=0, to=24,
                                           format="%.1f", increment=0.5,
                                           font=self.style.FONTS['body'], width=8)
        self.daily_goal_entry.pack(side=tk.RIGHT)

        # Weekly goal
        weekly_frame = tk.Frame(card, bg=self.style.COLORS['card_bg'])
        weekly_frame.pack(fill=tk.X, pady=10)
        ttk.Label(weekly_frame, text="Weekly (hrs):", font=self.style.FONTS['body'],
                 background=self.style.COLORS['card_bg']).pack(side=tk.LEFT)
        self.weekly_goal_entry = ttk.Spinbox(weekly_frame, from_=0, to=168,
                                            increment=1, font=self.style.FONTS['body'], width=8)
        self.weekly_goal_entry.pack(side=tk.RIGHT)

        tk.Button(card, text="UPDATE GOALS", command=self.update_goals,
                  bg=self.style.COLORS['primary'], fg='white',
                  font=self.style.FONTS['body'], relief='flat').pack(fill=tk.X, pady=10)

    def create_weather_card(self, parent):
        card = tk.Frame(parent, bg=self.style.COLORS['card_bg'], padx=20, pady=20)
        card.pack(fill=tk.X, pady=10)

        ttk.Label(card, text="CURRENT WEATHER", font=self.style.FONTS['h2'], 
                background=self.style.COLORS['card_bg']).pack(anchor=tk.W)
        
        self.weather_labels = {
            'temp': ttk.Label(card, font=self.style.FONTS['body'], 
                            background=self.style.COLORS['card_bg']),
            'cond': ttk.Label(card, font=self.style.FONTS['body'], 
                            background=self.style.COLORS['card_bg']),
            'humid': ttk.Label(card, font=self.style.FONTS['body'], 
                             background=self.style.COLORS['card_bg'])
        }

        for lbl in self.weather_labels.values():
            lbl.pack(anchor=tk.W, pady=2)

    def create_session_history(self, parent):
        card = tk.Frame(parent, bg=self.style.COLORS['card_bg'], padx=20, pady=20)
        card.pack(fill=tk.X, pady=10)

        ttk.Label(card, text="RECENT SESSIONS", font=self.style.FONTS['h2'], 
                background=self.style.COLORS['card_bg']).pack(anchor=tk.W)

        columns = ('subject', 'duration', 'date')
        self.session_tree = ttk.Treeview(card, columns=columns, show='headings', height=5)
        
        self.session_tree.heading('subject', text='Subject')
        self.session_tree.heading('duration', text='Duration')
        self.session_tree.heading('date', text='Date')
        
        self.session_tree.column('subject', width=80)
        self.session_tree.column('duration', width=60)
        self.session_tree.column('date', width=100)
        
        self.session_tree.pack(fill=tk.X)
        self.update_session_history()

    def create_achievements_card(self, parent):
        card = tk.Frame(parent, bg=self.style.COLORS['card_bg'], padx=20, pady=20)
        card.pack(fill=tk.X, pady=10)

        ttk.Label(card, text="ACHIEVEMENTS", font=self.style.FONTS['h2'], 
                background=self.style.COLORS['card_bg']).pack(anchor=tk.W)
        
        self.achievement_frame = tk.Frame(card, bg=self.style.COLORS['card_bg'])
        self.achievement_frame.pack(fill=tk.X, pady=10)
        
        self.achievement_labels = {
            '10_hours': ttk.Label(self.achievement_frame, text="★ 10 Hours", 
                                 font=self.style.FONTS['body'], foreground='#AAAAAA'),
            '50_hours': ttk.Label(self.achievement_frame, text="★★ 50 Hours", 
                                 font=self.style.FONTS['body'], foreground='#AAAAAA'),
            '100_hours': ttk.Label(self.achievement_frame, text="★★★ 100 Hours", 
                                  font=self.style.FONTS['body'], foreground='#AAAAAA')
        }
        
        for label in self.achievement_labels.values():
            label.pack(side=tk.LEFT, padx=10)

    def create_analytics_display(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Trend Analysis Tab
        self.trend_frame = ttk.Frame(notebook)
        self._update_trend_plot()
        notebook.add(self.trend_frame, text="Study Trends")

        # Productivity Dashboard Tab
        self.dashboard_frame = ttk.Frame(notebook)
        self._update_dashboard()
        notebook.add(self.dashboard_frame, text="Productivity Dashboard")

    def _update_trend_plot(self):
        if hasattr(self, 'trend_canvas'):
            self.trend_canvas.get_tk_widget().destroy()
            
        self.trend_fig = self.analytics.create_study_trends_plot()
        self.trend_canvas = FigureCanvasTkAgg(self.trend_fig, master=self.trend_frame)
        self.trend_canvas.draw()
        self.trend_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        NavigationToolbar2Tk(self.trend_canvas, self.trend_frame)

    def _update_dashboard(self):
        if hasattr(self, 'dashboard_canvas'):
            self.dashboard_canvas.get_tk_widget().destroy()
            
        self.dashboard_fig = self.analytics.create_productivity_dashboard()
        self.dashboard_canvas = FigureCanvasTkAgg(self.dashboard_fig, master=self.dashboard_frame)
        self.dashboard_canvas.draw()
        self.dashboard_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        NavigationToolbar2Tk(self.dashboard_canvas, self.dashboard_frame)

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
            messagebox.showinfo("Success", "Goals updated successfully")
            self.update_progress()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for goals")

    def update_progress(self):
        goals = self.db.get_current_goals()
        daily_study = self.db.get_daily_study_time()
        weekly_study = self.db.get_weekly_study_time()

        # Daily progress
        daily_hrs = daily_study / 3600
        if goals['daily'] > 0:
            daily_percent = (daily_study / goals['daily']) * 100
            self.daily_progress['value'] = min(daily_percent, 100)
            self.daily_label.config(text=f"Daily: {daily_hrs:.1f}h / {goals['daily']/3600:.1f}h")
        
        # Weekly progress
        weekly_hrs = weekly_study / 3600
        if goals['weekly'] > 0:
            weekly_percent = (weekly_study / goals['weekly']) * 100
            self.weekly_progress['value'] = min(weekly_percent, 100)
            self.weekly_label.config(text=f"Weekly: {weekly_hrs:.1f}h / {goals['weekly']/3600:.1f}h")

    def check_achievements(self):
        total_time = self.db.get_total_study_time()
        total_hours = total_time / 3600
        
        if total_hours >= 10 and not self.achievements['10_hours']:
            self.achievement_labels['10_hours'].config(foreground='#FFD700')
            self.show_achievement("10 Hours Studied!")
            self.achievements['10_hours'] = True
            
        if total_hours >= 50 and not self.achievements['50_hours']:
            self.achievement_labels['50_hours'].config(foreground='#FFD700')
            self.show_achievement("50 Hours Studied!")
            self.achievements['50_hours'] = True
            
        if total_hours >= 100 and not self.achievements['100_hours']:
            self.achievement_labels['100_hours'].config(foreground='#FFD700')
            self.show_achievement("100 Hours Studied!")
            self.achievements['100_hours'] = True

    def show_achievement(self, text):
        winsound.MessageBeep()
        messagebox.showinfo("Achievement Unlocked!", text)

    def update_session_history(self):
        for row in self.session_tree.get_children():
            self.session_tree.delete(row)
            
        sessions = self.db.get_all_sessions()[-5:]  # Last 5 sessions
        for session in sessions:
            duration = f"{session[3]/3600:.1f}h"
            date = session[1].strftime('%Y-%m-%d')
            self.session_tree.insert('', 'end', values=(session[4], duration, date))

    def toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.start_btn.config(text="START")
            self.save_session()
        else:
            self.timer_running = True
            self.start_btn.config(text="STOP")
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
        self.start_btn.config(text="START")
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
                self.update_progress()
                self.check_achievements()
                self.update_session_history()
                self._update_trend_plot()
                self._update_dashboard()
            except ValidationError as e:
                messagebox.showerror("Validation Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save session: {str(e)}")
            finally:
                self.time_elapsed = 0

    def _apply_preset(self, minutes):
        if messagebox.askyesno("Confirm", f"Log {minutes} minute session?"):
            try:
                duration = minutes * 60
                validate_study_session(duration, self.subject_var.get())
                self.db.save_session(
                    duration=duration,
                    subject=self.subject_var.get(),
                    weather=self.current_weather['condition'] if self.current_weather else "Unknown"
                )
                messagebox.showinfo("Saved", "Preset session logged successfully")
                self.update_progress()
                self.check_achievements()
                self.update_session_history()
                self._update_trend_plot()
                self._update_dashboard()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_data(self, format_type):
        try:
            if format_type == 'csv':
                filename = self.exporter.export_to_csv()
            elif format_type == 'excel':
                filename = self.exporter.export_to_excel()
            else:
                raise ValidationError("Invalid export format")
            
            messagebox.showinfo("Export Successful", f"Data exported to:\n{filename}")
            self.update_session_history()
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTimer(root)
    root.mainloop()