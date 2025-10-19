import time
from functools import wraps
from typing import Dict
import streamlit as st


class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self):
        if 'performance_metrics' not in st.session_state:
            st.session_state.performance_metrics = {
                'query_times': [],
                'db_times': [],
                'render_times': []
            }
    
    @staticmethod
    def measure_time(operation: str):
        """Decorator to measure execution time"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start
                
                # Store metric
                if 'performance_metrics' in st.session_state:
                    if operation not in st.session_state.performance_metrics:
                        st.session_state.performance_metrics[operation] = []
                    st.session_state.performance_metrics[operation].append(duration)
                
                print(f"⏱️ {operation}: {duration:.3f}s")
                return result
            return wrapper
        return decorator
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of performance metrics"""
        metrics = st.session_state.get('performance_metrics', {})
        
        summary = {}
        for operation, times in metrics.items():
            if times:
                summary[operation] = {
                    'avg': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
        
        return summary