# -*- coding: utf-8 -*-
import sqlite3
import threading
import os
import appdirs
from datetime import datetime, timedelta
from error_handler import ErrorHandler

class DatabaseManager:
    _local = threading.local()
    
    def __init__(self):
        # Get platform-specific data directory
        self.data_dir = appdirs.user_data_dir("StudyMetricsPro", "StudyTracker")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.db_file = os.path.join(self.data_dir, "study_sessions.db")
        self._init_db()

    def _get_conn(self):
        if not hasattr(DatabaseManager._local, "conn"):
            DatabaseManager._local.conn = sqlite3.connect(
                self.db_file, 
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            DatabaseManager._local.conn.execute("PRAGMA journal_mode=WAL")
        return DatabaseManager._local.conn

    def _init_db(self):
        conn = self._get_conn()
        conn.execute('PRAGMA encoding = "UTF-8";')
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration INTEGER,
                    subject TEXT,
                    weather_condition TEXT,
                    location TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS study_goals (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    daily_goal INTEGER DEFAULT 0,
                    weekly_goal INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    @ErrorHandler.handle_database_error
    def save_session(self, duration, subject, weather="", location=""):
        with self._get_conn() as conn:
            end_time = datetime.now()
            start_time = end_time - timedelta(seconds=duration)
            conn.execute('''
                INSERT INTO study_sessions 
                (start_time, end_time, duration, subject, weather_condition, location)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (start_time, end_time, duration, subject, weather, location))

    # Rest of the methods remain the same but add context managers for transactions
    @ErrorHandler.handle_database_error
    def get_all_sessions(self):
        with self._get_conn() as conn:
            return conn.execute('SELECT * FROM study_sessions').fetchall()

    @ErrorHandler.handle_database_error
    def get_total_study_time(self):
        with self._get_conn() as conn:
            result = conn.execute('SELECT SUM(duration) FROM study_sessions').fetchone()
            return result[0] or 0

    @ErrorHandler.handle_database_error
    def save_goals(self, daily, weekly):
        with self._get_conn() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO study_goals 
                (id, daily_goal, weekly_goal)
                VALUES (1, ?, ?)
            ''', (daily, weekly))

    @ErrorHandler.handle_database_error
    def get_current_goals(self):
        with self._get_conn() as conn:
            result = conn.execute(
                'SELECT daily_goal, weekly_goal FROM study_goals WHERE id = 1'
            ).fetchone()
            return {'daily': result[0] if result else 0, 
                    'weekly': result[1] if result else 0}

    @ErrorHandler.handle_database_error
    def get_daily_study_time(self):
        with self._get_conn() as conn:
            result = conn.execute('''
                SELECT SUM(duration) 
                FROM study_sessions 
                WHERE DATE(start_time) = DATE('now', 'localtime')
            ''').fetchone()
            return result[0] or 0

    @ErrorHandler.handle_database_error
    def get_weekly_study_time(self):
        with self._get_conn() as conn:
            result = conn.execute('''
                SELECT SUM(duration) 
                FROM study_sessions 
                WHERE strftime('%Y-%W', start_time, 'localtime') = 
                      strftime('%Y-%W', 'now', 'localtime')
            ''').fetchone()
            return result[0] or 0