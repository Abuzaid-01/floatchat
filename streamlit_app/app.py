import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from streamlit_app.components.chat_interface import ChatInterface
from streamlit_app.components.map_view import MapView
from streamlit_app.components.profile_viewer import ProfileViewer
from streamlit_app.components.sidebar import Sidebar
from streamlit_app.utils.session_state import SessionStateManager
from rag_engine.query_processor import QueryProcessor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="FloatChat - ARGO Data Explorer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance and readability
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #444;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Chat message styling - better contrast */
    .stChatMessage {
        background-color: #f0f8ff !important;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #d0e8ff;
    }
    
    /* User message - light blue background */
    [data-testid="stChatMessageContent"] {
        color: #1a1a1a !important;
        font-size: 1rem;
    }
    
    /* Assistant message - light green background */
    .stChatMessage[data-testid="stChatMessage"]:has([aria-label="assistant"]) {
        background-color: #f0fff4 !important;
        border: 1px solid #c6f6d5;
    }
    
    /* Make all text darker for better readability */
    .stMarkdown, p, span, div {
        color: #1a1a1a !important;
    }
    
    /* Code blocks with dark background */
    code {
        background-color: #2d2d2d !important;
        color: #f8f8f2 !important;
        padding: 2px 6px;
        border-radius: 3px;
    }
    
    /* SQL code blocks */
    .stCodeBlock {
        background-color: #2d2d2d !important;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
        font-weight: bold;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #e6f3ff !important;
        color: #1a1a1a !important;
        border: 1px solid #b3d9ff;
    }
    
    /* Dataframe text */
    .dataframe {
        color: #1a1a1a !important;
    }
    </style>
""", unsafe_allow_html=True)

class FloatChatApp:
    """
    Main FloatChat Application.
    Orchestrates all components: chat, visualization, data management.
    """
    
    def __init__(self):
        # Initialize session state
        self.session_manager = SessionStateManager()
        self.session_manager.initialize()
        
        # Initialize components
        self.query_processor = QueryProcessor()
        self.sidebar = Sidebar()
        self.chat_interface = ChatInterface(self.query_processor)
        self.map_view = MapView()
        self.profile_viewer = ProfileViewer()
    
    def run(self):
        """Main application loop"""
        
        # Header
        st.markdown('<div class="main-header">🌊 FloatChat</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">AI-Powered ARGO Ocean Data Discovery and Visualization</div>',
            unsafe_allow_html=True
        )
        
        # Sidebar
        self.sidebar.render()
        
        # Main content area - Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "💬 Chat",
            "🗺️ Map View",
            "📊 Profile Viewer",
            "📈 Data Explorer"
        ])
        
        with tab1:
            self._render_chat_tab()
        
        with tab2:
            self._render_map_tab()
        
        with tab3:
            self._render_profile_tab()
        
        with tab4:
            self._render_data_explorer_tab()
        
        # Footer
        st.markdown("---")
        st.markdown(
            "**FloatChat** - Developed for Smart India Hackathon 2025 | "
            "Ministry of Earth Sciences (MoES) | INCOIS"
        )
    
    def _render_chat_tab(self):
        """Render chat interface tab"""
        st.subheader("Ask Questions About ARGO Data")
        
        # Example queries
        with st.expander("📝 Example Queries"):
            st.markdown("""
            - Show me temperature profiles in the Arabian Sea
            - What's the average salinity near the equator in March 2023?
            - Find ARGO floats between 10°N-20°N and 60°E-80°E
            - Compare temperature profiles from different months
            - Show the deepest measurements in the Indian Ocean
            """)
        
        # Render chat interface
        self.chat_interface.render()
    
    def _render_map_tab(self):
        """Render map visualization tab"""
        st.subheader("Geographic Distribution of ARGO Floats")
        
        # Check if we have query results
        if st.session_state.get('last_query_results') is not None:
            results = st.session_state.last_query_results
            if results['success'] and not results['results'].empty:
                self.map_view.render(results['results'])
            else:
                st.info("No data to display. Run a query in the Chat tab first.")
        else:
            st.info("No data to display. Run a query in the Chat tab first.")
    
    def _render_profile_tab(self):
        """Render profile visualization tab"""
        st.subheader("Temperature and Salinity Profiles")
        
        if st.session_state.get('last_query_results') is not None:
            results = st.session_state.last_query_results
            if results['success'] and not results['results'].empty:
                self.profile_viewer.render(results['results'])
            else:
                st.info("No data to display. Run a query in the Chat tab first.")
        else:
            st.info("No data to display. Run a query in the Chat tab first.")
    
    def _render_data_explorer_tab(self):
        """Render raw data explorer tab"""
        st.subheader("Raw Data Table")
        
        if st.session_state.get('last_query_results') is not None:
            results = st.session_state.last_query_results
            if results['success'] and not results['results'].empty:
                df = results['results']
                
                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Records", len(df))
                with col2:
                    if 'float_id' in df.columns:
                        st.metric("Unique Floats", df['float_id'].nunique())
                with col3:
                    if 'temperature' in df.columns:
                        st.metric("Avg Temperature", f"{df['temperature'].mean():.2f}°C")
                with col4:
                    if 'salinity' in df.columns:
                        st.metric("Avg Salinity", f"{df['salinity'].mean():.2f} PSU")
                
                # Display data table
                st.dataframe(df, use_container_width=True)
                
                # Export options
                st.subheader("Export Data")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="argo_data.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    json = df.to_json(orient='records', indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json,
                        file_name="argo_data.json",
                        mime="application/json"
                    )
            else:
                st.info("No data to display. Run a query in the Chat tab first.")
        else:
            st.info("No data to display. Run a query in the Chat tab first.")

# Run the app
if __name__ == "__main__":
    app = FloatChatApp()
    app.run()
