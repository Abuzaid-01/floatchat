import streamlit as st
from database.db_setup import DatabaseSetup
from database.models import ArgoProfile

class Sidebar:
    """Sidebar component with database info and settings"""
    
    def __init__(self):
        self.db_setup = DatabaseSetup()
    
    def render(self):
        """Render sidebar content"""
        
        with st.sidebar:
            st.title("⚙️ Settings")
            
            # Database statistics
            self._render_database_stats()
            
            st.markdown("---")
            
            # Query settings
            self._render_query_settings()
            
            st.markdown("---")
            
            # Information
            self._render_info()
            
            st.markdown("---")
            
            # Clear chat button
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.last_query_results = None
                st.success("Chat history cleared!")
                st.rerun()
    
    def _render_database_stats(self):
        """Display database statistics"""
        st.subheader("📊 Database Stats")
        
        try:
            session = self.db_setup.get_session()
            
            # Get counts
            total_records = session.query(ArgoProfile).count()
            unique_floats = session.query(ArgoProfile.float_id).distinct().count()
            
            # Get date range
            date_range = session.query(
                ArgoProfile.timestamp
            ).order_by(ArgoProfile.timestamp).first()
            
            session.close()
            
            # Display metrics
            st.metric("Total Records", f"{total_records:,}")
            st.metric("Unique Floats", unique_floats)
            
            if date_range:
                st.caption(f"Data from {date_range[0].strftime('%Y-%m-%d')}")
            
        except Exception as e:
            st.error(f"Database connection error: {e}")
    
    def _render_query_settings(self):
        """Render query settings"""
        st.subheader("🔧 Query Settings")
        
        # Number of similar profiles to retrieve
        top_k = st.slider(
            "Similar Profiles",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of similar profiles to use for context"
        )
        st.session_state.top_k = top_k
        
        # Max results to display
        max_results = st.slider(
            "Max Results",
            min_value=100,
            max_value=10000,
            value=1000,
            step=100,
            help="Maximum number of results to display"
        )
        st.session_state.max_results = max_results
    
    def _render_info(self):
        """Render information section"""
        st.subheader("ℹ️ About")
        
        st.markdown("""
        **FloatChat** is an AI-powered conversational interface for exploring ARGO ocean float data.
        
        **Features:**
        - Natural language queries
        - Interactive visualizations
        - Real-time data analysis
        - Export capabilities
        
        **Data Source:**
        ARGO Global Data Repository
        """)
        
        # Links
        st.markdown("**Resources:**")
        st.markdown("- [ARGO Program](https://argo.ucsd.edu/)")
        st.markdown("- [INCOIS](https://incois.gov.in/)")
        st.markdown("- [GitHub](https://github.com)")
