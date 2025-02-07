import pandas as pd
import json
from datetime import datetime
import logging
from typing import Optional, Dict, Any
import traceback

class DataExporter:
    def __init__(self, db_manager):
        self.db = db_manager
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for the data exporter."""
        logging.basicConfig(
            filename='study_tracker.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('StudyTracker')

    def export_to_csv(self, filename: str = None) -> str:
        """Export study sessions to CSV file."""
        try:
            if filename is None:
                filename = f'study_sessions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            sessions = self.db.get_all_sessions()
            df = pd.DataFrame(sessions, columns=[
                'id', 'start_time', 'end_time', 'duration',
                'subject', 'weather_condition', 'location'
            ])
            
            df.to_csv(filename, index=False)
            self.logger.info(f"Successfully exported data to {filename}")
            return filename
        
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {str(e)}")
            raise ExportError(f"Failed to export data: {str(e)}")

    def export_to_excel(self, filename: str = None) -> str:
        """Export study sessions to Excel file with multiple sheets."""
        try:
            if filename is None:
                filename = f'study_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            
            # Create Excel writer
            with pd.ExcelWriter(filename) as writer:
                # Export raw data
                sessions = self.db.get_all_sessions()
                df = pd.DataFrame(sessions, columns=[
                    'id', 'start_time', 'end_time', 'duration',
                    'subject', 'weather_condition', 'location'
                ])
                df.to_excel(writer, sheet_name='Raw Data', index=False)
                
                # Export subject summary
                subject_summary = df.groupby('subject').agg({
                    'duration': ['count', 'sum', 'mean']
                }).round(2)
                subject_summary.columns = ['Total Sessions', 'Total Duration', 'Average Duration']
                subject_summary.to_excel(writer, sheet_name='Subject Summary')
                
                # Export weekly summary
                df['start_time'] = pd.to_datetime(df['start_time'])
                weekly_summary = df.groupby(df['start_time'].dt.strftime('%Y-Week %W'))[
                    'duration'
                ].sum().reset_index()
                weekly_summary.to_excel(writer, sheet_name='Weekly Summary', index=False)
            
            self.logger.info(f"Successfully exported data to {filename}")
            return filename
        
        except Exception as e:
            self.logger.error(f"Failed to export Excel: {str(e)}")
            raise ExportError(f"Failed to export data: {str(e)}")

class ErrorHandler:
    """Central error handling for the application."""
    
    @staticmethod
    def handle_api_error(func):
        """Decorator for handling API-related errors."""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                logging.error(f"API Error in {func.__name__}: {str(e)}")
                return {
                    'error': True,
                    'message': "Weather service temporarily unavailable",
                    'details': str(e)
                }
        return wrapper
    
    @staticmethod
    def handle_database_error(func):
        """Decorator for handling database-related errors."""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except sqlite3.Error as e:
                logging.error(f"Database Error in {func.__name__}: {str(e)}")
                return {
                    'error': True,
                    'message': "Database operation failed",
                    'details': str(e)
                }
        return wrapper

class ExportError(Exception):
    """Custom exception for export-related errors."""
    pass

class ValidationError(Exception):
    """Custom exception for data validation errors."""
    pass

def validate_study_session(
    duration: int,
    subject: str,
    weather: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """Validate study session data before saving."""
    errors = {}
    
    # Validate duration
    if not isinstance(duration, (int, float)) or duration <= 0:
        errors['duration'] = "Duration must be a positive number"
    
    # Validate subject
    valid_subjects = {"General", "Math", "Science", "History", "Language"}
    if not subject or subject not in valid_subjects:
        errors['subject'] = f"Subject must be one of: {', '.join(valid_subjects)}"
    
    # Optional field validation
    if weather and not isinstance(weather, str):
        errors['weather'] = "Weather must be a string"
    
    if location and not isinstance(location, str):
        errors['location'] = "Location must be a string"
    
    if errors:
        raise ValidationError(json.dumps(errors))
    
    return {
        'duration': duration,
        'subject': subject,
        'weather': weather,
        'location': location
    }