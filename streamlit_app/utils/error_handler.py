import streamlit as st
import traceback
from typing import Callable, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('floatchat.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('FloatChat')


def handle_errors(func: Callable) -> Callable:
    """Decorator for error handling"""
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            st.error(f"An error occurred: {str(e)}")
            return None
    return wrapper


class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def handle_database_error(e: Exception):
        """Handle database errors"""
        logger.error(f"Database error: {e}")
        st.error("🔴 Database connection error. Please check your configuration.")
        st.info("Try refreshing the page or contact support if the issue persists.")
    
    @staticmethod
    def handle_api_error(e: Exception):
        """Handle API errors"""
        logger.error(f"API error: {e}")
        st.error("🔴 AI service error. Please try again.")
        st.info("If this persists, check your API key in .env file.")
    
    @staticmethod
    def handle_data_error(e: Exception):
        """Handle data processing errors"""
        logger.error(f"Data error: {e}")
        st.error("🔴 Data processing error.")
        st.info("This may be due to data format issues. Please verify your input.")