# -*- coding: utf-8 -*-
import pandas as pd
import logging
from datetime import datetime
from error_handler import ExportError, ErrorHandler

class DataExporter:
    def __init__(self, db_manager):
        self.db = db_manager
        self.logger = logging.getLogger('StudyTracker')

    @ErrorHandler.handle_api_error
    def export_to_csv(self, filename=None):
        try:
            filename = filename or f'study_sessions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            df = pd.DataFrame(self.db.get_all_sessions(), columns=[
                'id', 'start_time', 'end_time', 'duration',
                'subject', 'weather_condition', 'location'
            ])
            df.to_csv(filename, index=False, encoding='utf-8')
            self.logger.info(f"Exported to CSV: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"CSV Export Error: {str(e)}")
            raise ExportError(f"CSV export failed: {str(e)}")

    @ErrorHandler.handle_api_error
    def export_to_excel(self, filename=None):
        try:
            filename = filename or f'study_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            with pd.ExcelWriter(filename) as writer:
                sessions = self.db.get_all_sessions()
                df = pd.DataFrame(sessions, columns=[
                    'id', 'start_time', 'end_time', 'duration',
                    'subject', 'weather_condition', 'location'
                ])
                df.to_excel(writer, sheet_name='Raw Data', index=False, encoding='utf-8')
                
                subject_summary = df.groupby('subject').agg({
                    'duration': ['count', 'sum', 'mean']
                }).round(2)
                subject_summary.to_excel(writer, sheet_name='Subject Summary')
                
                weekly_summary = df.groupby(pd.to_datetime(df['start_time']).dt.strftime('%Y-Week %W'))['duration'].sum()
                weekly_summary.to_excel(writer, sheet_name='Weekly Summary')
                
            self.logger.info(f"Exported to Excel: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Excel Export Error: {str(e)}")
            raise ExportError(f"Excel export failed: {str(e)}")