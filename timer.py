import tkinter as tk
from tkinter import ttk
import time

class StudyTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Timer")
        
        # Timer variables
        self.time_elapsed = 0
        self.timer_running = False
        
        # Create display
        self.timer_display = ttk.Label(
            root,
            text="00:00:00",
            font=('Arial', 30)
        )
        self.timer_display.pack(pady=20)
        
        # Create buttons
        self.start_button = ttk.Button(
            root,
            text="Start",
            command=self.toggle_timer
        )
        self.start_button.pack(pady=5)
        
        self.reset_button = ttk.Button(
            root,
            text="Reset",
            command=self.reset_timer
        )
        self.reset_button.pack(pady=5)
    
    def toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.start_button.config(text="Start")
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
        self.time_elapsed = 0
        self.timer_running = False
        self.start_button.config(text="Start")
        self.timer_display.config(text="00:00:00")

def main():
    root = tk.Tk()
    app = StudyTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()