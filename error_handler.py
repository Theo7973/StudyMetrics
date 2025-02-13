# -*- coding: utf-8 -*-
import logging
import functools
from logging.handlers import RotatingFileHandler

class ErrorHandler:
    """Central error handling class with decorators for error handling"""
    
    @staticmethod
    def handle_api_error(func):
        """Decorator for handling API-related errors"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"API Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper

    @staticmethod
    def handle_database_error(func):
        """Decorator for handling database-related errors"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Database Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper

def setup_logging():
    """Configure logging system with proper encoding"""
    logger = logging.getLogger('StudyTracker')
    logger.setLevel(logging.INFO)
    
    handler = RotatingFileHandler(
        'study_tracker.log',
        maxBytes=1024*1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Initialize logging when module is imported
setup_logging()

class ExportError(Exception):
    """Custom exception for export failures"""
    pass

class ValidationError(Exception):
    """Custom exception for data validation failures"""
    pass

def validate_study_session(duration, subject):
    """Validate study session parameters"""
    valid_subjects = {"General", "Math", "Science", "History", "Language"}
    if not isinstance(duration, (int, float)) or duration <= 0:
        raise ValidationError("Duration must be a positive number")
    if subject not in valid_subjects:
        raise ValidationError(f"Invalid subject. Valid options: {', '.join(valid_subjects)}")