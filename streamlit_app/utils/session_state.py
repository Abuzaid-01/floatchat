import streamlit as st

class SessionStateManager:
    """Manage Streamlit session state variables"""
    
    def initialize(self):
        """Initialize all session state variables"""
        
        # Chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Last query results
        if 'last_query_results' not in st.session_state:
            st.session_state.last_query_results = None
        
        # Query settings
        if 'top_k' not in st.session_state:
            st.session_state.top_k = 3
        
        if 'max_results' not in st.session_state:
            st.session_state.max_results = 1000
        
        # User preferences
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
        
        if 'map_style' not in st.session_state:
            st.session_state.map_style = 'open-street-map'
    
    def reset(self):
        """Reset all session state"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        self.initialize()
