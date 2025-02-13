# -*- coding: utf-8 -*-
import sqlite3
import threading
from datetime import datetime, timedelta
from error_handler import ErrorHandler

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
        conn.execute('PRAGMA encoding = "UTF-8";')
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                daily_goal INTEGER,
                weekly_goal INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

    @ErrorHandler.handle_database_error
    def save_session(self, duration, subject, weather="", location=""):
        conn = self._get_conn()
        cursor = conn.cursor()
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=duration)
        
        cursor.execute('''
            INSERT INTO study_sessions 
            (start_time, end_time, duration, subject, weather_condition, location)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (start_time, end_time, duration, subject, weather, location))
        conn.commit()

    @ErrorHandler.handle_database_error
    def get_all_sessions(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM study_sessions')
        return cursor.fetchall()

    @ErrorHandler.handle_database_error
    def get_total_study_time(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(duration) FROM study_sessions')
        return cursor.fetchone()[0] or 0

    @ErrorHandler.handle_database_error
    def save_goals(self, daily, weekly):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO study_goals (id, daily_goal, weekly_goal)
            VALUES (1, ?, ?)
        ''', (daily, weekly))
        conn.commit()

    @ErrorHandler.handle_database_error
    def get_current_goals(self):
        cursor = self._get_conn().cursor()
        cursor.execute('SELECT daily_goal, weekly_goal FROM study_goals WHERE id = 1')
        result = cursor.fetchone()
        return {'daily': result[0] if result else 0, 
                'weekly': result[1] if result else 0}

    @ErrorHandler.handle_database_error
    def get_daily_study_time(self):
        cursor = self._get_conn().cursor()
        cursor.execute('''
            SELECT SUM(duration) 
            FROM study_sessions 
            WHERE DATE(start_time) = DATE('now')
        ''')
        return cursor.fetchone()[0] or 0

    @ErrorHandler.handle_database_error
    def get_weekly_study_time(self):
        cursor = self._get_conn().cursor()
        cursor.execute('''
            SELECT SUM(duration) 
            FROM study_sessions 
            WHERE strftime('%Y-%W', start_time) = strftime('%Y-%W', 'now')
        ''')
        return cursor.fetchone()[0] or 0