import sqlite3
from datetime import datetime, timedelta
import threading

class DatabaseManager:
    _local = threading.local()
    
    def __init__(self, db_file="study_sessions.db"):
        self.db_file = db_file
        self._init_db()

    def _get_conn(self):
        if not hasattr(DatabaseManager._local, "conn"):
            DatabaseManager._local.conn = sqlite3.connect(
                self.db_file, 
                check_same_thread=False
            )
        return DatabaseManager._local.conn

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
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
        conn.commit()

    def save_session(self, duration, subject, weather="", location=""):
        conn = self._get_conn()
        cursor = conn.cursor()
        end_time = datetime.now()
        duration_delta = timedelta(seconds=duration)
        start_time = end_time - duration_delta
        
        cursor.execute('''
            INSERT INTO study_sessions 
            (start_time, end_time, duration, subject, weather_condition, location)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (start_time, end_time, duration, subject, weather, location))
        conn.commit()

    def get_all_sessions(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM study_sessions')
        return cursor.fetchall()

    def get_total_study_time(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(duration) FROM study_sessions')
        return cursor.fetchone()[0] or 0