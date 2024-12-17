import sqlite3
from datetime import datetime, timedelta  # Add timedelta import

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('study_sessions.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                end_time DATETIME,
                duration INTEGER,
                subject TEXT,
                weather_condition TEXT,
                location TEXT
            )
        ''')
        self.conn.commit()

    def save_session(self, duration, subject, weather="", location=""):
        cursor = self.conn.cursor()
        end_time = datetime.now()
        # Convert duration (seconds) to timedelta
        duration_delta = timedelta(seconds=duration)
        start_time = end_time - duration_delta
        
        cursor.execute('''
            INSERT INTO study_sessions 
            (start_time, end_time, duration, subject, weather_condition, location)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (start_time, end_time, duration, subject, weather, location))
        self.conn.commit()

    def get_all_sessions(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM study_sessions')
        return cursor.fetchall()

    def get_total_study_time(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(duration) FROM study_sessions')
        return cursor.fetchone()[0] or 0