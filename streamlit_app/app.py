# import streamlit as st
# import sys
# from pathlib import Path

# # Add project root to path
# sys.path.append(str(Path(__file__).parent.parent))

# from streamlit_app.components.chat_interface import ChatInterface
# from streamlit_app.components.map_view import MapView
# from streamlit_app.components.profile_viewer import ProfileViewer
# from streamlit_app.components.sidebar import Sidebar
# from streamlit_app.utils.session_state import SessionStateManager
# from rag_engine.query_processor import QueryProcessor
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Page configuration
# st.set_page_config(
#     page_title="FloatChat - ARGO Data Explorer",
#     page_icon="🌊",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS for better appearance and readability
# st.markdown("""
#     <style>
#     /* Import modern font */
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
#     /* Global styles - High contrast text */
#     * {
#         font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
#     }
    
#     /* Main container background */
#     .main {
#         background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
#     }
    
#     /* Main header - Ocean blue gradient with shadow */
#     .main-header {
#         font-size: 3rem;
#         font-weight: 800;
#         background: linear-gradient(135deg, #0066cc, #00c6ff);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         background-clip: text;
#         text-align: center;
#         padding: 1.5rem 0;
#         text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
#         letter-spacing: -0.5px;
#     }
    
#     /* Sub-header - Dark with high contrast */
#     .sub-header {
#         font-size: 1.3rem;
#         color: #1a202c;
#         text-align: center;
#         margin-bottom: 2rem;
#         font-weight: 600;
#     }
    
#     /* User message - Bright blue theme with strong text */
#     .stChatMessage[data-testid="user"] {
#         background: linear-gradient(135deg, #cfe9ff 0%, #a8d8ff 100%) !important;
#         border-left: 5px solid #0066cc !important;
#         border-radius: 12px;
#         padding: 1.2rem;
#         margin: 0.8rem 0;
#         box-shadow: 0 3px 10px rgba(0,102,204,0.15);
#     }
    
#     /* Assistant message - Professional white/light theme with border */
#     .stChatMessage[data-testid="assistant"] {
#         background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
#         border-left: 5px solid #00b894 !important;
#         border-radius: 12px;
#         padding: 1.2rem;
#         margin: 0.8rem 0;
#         box-shadow: 0 3px 10px rgba(0,184,148,0.15);
#     }
    
#     /* All text - Maximum contrast for readability */
#     .stChatMessage p, 
#     .stChatMessage span, 
#     .stChatMessage div,
#     [data-testid="stChatMessageContent"],
#     [data-testid="stChatMessageContent"] p,
#     [data-testid="stChatMessageContent"] span,
#     [data-testid="stChatMessageContent"] div {
#         color: #000000 !important;
#         font-size: 1.05rem !important;
#         line-height: 1.7 !important;
#         font-weight: 500 !important;
#     }
    
#     /* Strong emphasis */
#     strong, b {
#         color: #000000 !important;
#         font-weight: 700 !important;
#     }
    
#     /* Headers in content - Bold and visible */
#     h1, h2, h3, h4, h5, h6 {
#         color: #000000 !important;
#         font-weight: 700 !important;
#         margin-top: 1rem !important;
#         margin-bottom: 0.5rem !important;
#     }
    
#     h1 { font-size: 2.2rem !important; }
#     h2 { font-size: 1.8rem !important; }
#     h3 { font-size: 1.5rem !important; }
    
#     /* Regular markdown text - Black for max visibility */
#     .stMarkdown, .stMarkdown p, .stMarkdown div {
#         color: #000000 !important;
#         font-weight: 500 !important;
#     }
    
#     /* Code blocks - Professional dark theme */
#     code {
#         background-color: #282c34 !important;
#         color: #61dafb !important;
#         padding: 4px 10px !important;
#         border-radius: 6px !important;
#         font-family: 'Fira Code', 'Consolas', 'Monaco', monospace !important;
#         border: 1px solid #3d4451 !important;
#         font-size: 0.95rem !important;
#         font-weight: 500 !important;
#     }
    
#     /* SQL code blocks */
#     .stCodeBlock {
#         background-color: #282c34 !important;
#         border: 2px solid #3d4451 !important;
#         border-radius: 8px !important;
#         box-shadow: 0 2px 8px rgba(0,0,0,0.2);
#     }
    
#     .stCodeBlock code {
#         color: #61dafb !important;
#         font-size: 1rem !important;
#     }
    
#     /* Metrics - Eye-catching styling */
#     [data-testid="stMetricValue"] {
#         color: #0066cc !important;
#         font-weight: 800 !important;
#         font-size: 2.2rem !important;
#         text-shadow: 1px 1px 2px rgba(0,102,204,0.2);
#     }
    
#     [data-testid="stMetricLabel"] {
#         color: #000000 !important;
#         font-weight: 700 !important;
#         font-size: 1rem !important;
#         text-transform: uppercase;
#         letter-spacing: 0.5px;
#     }
    
#     [data-testid="stMetricDelta"] {
#         font-weight: 600 !important;
#     }
    
#     /* Info boxes - High contrast */
#     .stAlert {
#         background-color: #fff9e6 !important;
#         color: #000000 !important;
#         border: 2px solid #ffc107 !important;
#         border-radius: 8px !important;
#         font-weight: 600 !important;
#         padding: 1rem !important;
#     }
    
#     /* Success messages */
#     .stSuccess {
#         background-color: #d4edda !important;
#         color: #000000 !important;
#         border: 2px solid #28a745 !important;
#         font-weight: 600 !important;
#     }
    
#     /* Error messages */
#     .stError {
#         background-color: #f8d7da !important;
#         color: #000000 !important;
#         border: 2px solid #dc3545 !important;
#         font-weight: 600 !important;
#     }
    
#     /* Warning messages */
#     .stWarning {
#         background-color: #fff3cd !important;
#         color: #000000 !important;
#         border: 2px solid #ff9800 !important;
#         font-weight: 600 !important;
#     }
    
#     /* Info messages */
#     .stInfo {
#         background-color: #d1ecf1 !important;
#         color: #000000 !important;
#         border: 2px solid #17a2b8 !important;
#         font-weight: 600 !important;
#     }
    
#     /* Dataframe styling - Professional table */
#     .dataframe {
#         color: #000000 !important;
#         font-size: 0.95rem !important;
#         font-weight: 500 !important;
#         border: 2px solid #dee2e6 !important;
#         border-radius: 8px !important;
#     }
    
#     .dataframe thead th {
#         background: linear-gradient(135deg, #0066cc, #0052a3) !important;
#         color: white !important;
#         font-weight: 700 !important;
#         padding: 14px 10px !important;
#         text-transform: uppercase !important;
#         letter-spacing: 0.5px !important;
#         border: none !important;
#     }
    
#     .dataframe tbody td {
#         color: #000000 !important;
#         font-weight: 500 !important;
#         padding: 12px 10px !important;
#         border-bottom: 1px solid #e9ecef !important;
#     }
    
#     .dataframe tbody tr:nth-child(even) {
#         background-color: #f8f9fa !important;
#     }
    
#     .dataframe tbody tr:hover {
#         background-color: #e3f2fd !important;
#         transition: background-color 0.2s ease;
#     }
    
#     /* Sidebar styling - Modern and clean */
#     [data-testid="stSidebar"] {
#         background: linear-gradient(180deg, #ffffff 0%, #f0f4f8 100%);
#         border-right: 2px solid #e0e6ed;
#     }
    
#     [data-testid="stSidebar"] .stMarkdown,
#     [data-testid="stSidebar"] .stMarkdown p {
#         color: #000000 !important;
#         font-weight: 600 !important;
#     }
    
#     [data-testid="stSidebar"] h1,
#     [data-testid="stSidebar"] h2,
#     [data-testid="stSidebar"] h3 {
#         color: #0066cc !important;
#     }
    
#     /* Tabs - Modern tab design */
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 4px;
#         background-color: #f8f9fa;
#         padding: 8px;
#         border-radius: 10px;
#     }
    
#     .stTabs [data-baseweb="tab"] {
#         color: #000000 !important;
#         font-weight: 600 !important;
#         padding: 12px 24px !important;
#         border-radius: 8px !important;
#         transition: all 0.3s ease;
#     }
    
#     .stTabs [data-baseweb="tab"]:hover {
#         background-color: #e3f2fd !important;
#     }
    
#     .stTabs [aria-selected="true"] {
#         background: linear-gradient(135deg, #0066cc, #0052a3) !important;
#         color: white !important;
#         box-shadow: 0 4px 12px rgba(0,102,204,0.3);
#     }
    
#     /* Expander styling - Modern accordion */
#     .streamlit-expanderHeader {
#         background: linear-gradient(135deg, #f8f9fa, #e9ecef) !important;
#         color: #000000 !important;
#         font-weight: 700 !important;
#         border: 2px solid #dee2e6 !important;
#         border-radius: 8px !important;
#         padding: 12px 16px !important;
#         transition: all 0.3s ease;
#     }
    
#     .streamlit-expanderHeader:hover {
#         background: linear-gradient(135deg, #e9ecef, #dee2e6) !important;
#         border-color: #0066cc !important;
#     }
    
#     /* Button styling - Professional call-to-action */
#     .stButton button {
#         background: linear-gradient(135deg, #0066cc, #0052a3) !important;
#         color: white !important;
#         font-weight: 700 !important;
#         border-radius: 8px !important;
#         border: none !important;
#         padding: 0.75rem 2rem !important;
#         transition: all 0.3s ease !important;
#         text-transform: uppercase;
#         letter-spacing: 0.5px;
#         box-shadow: 0 4px 12px rgba(0,102,204,0.3);
#     }
    
#     .stButton button:hover {
#         background: linear-gradient(135deg, #0052a3, #003d7a) !important;
#         box-shadow: 0 6px 16px rgba(0,102,204,0.4) !important;
#         transform: translateY(-2px);
#     }
    
#     /* Input fields - Clean and modern */
#     .stTextInput input, .stTextArea textarea, .stSelectbox select {
#         border: 2px solid #d1d9e0 !important;
#         border-radius: 8px !important;
#         color: #000000 !important;
#         font-weight: 500 !important;
#         padding: 12px !important;
#         font-size: 1rem !important;
#     }
    
#     .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
#         border-color: #0066cc !important;
#         box-shadow: 0 0 0 3px rgba(0,102,204,0.15) !important;
#         outline: none !important;
#     }
    
#     /* Download button styling */
#     .stDownloadButton button {
#         background: linear-gradient(135deg, #00b894, #00a383) !important;
#         color: white !important;
#         font-weight: 700 !important;
#         border-radius: 8px !important;
#         padding: 0.75rem 1.5rem !important;
#         box-shadow: 0 4px 12px rgba(0,184,148,0.3);
#     }
    
#     .stDownloadButton button:hover {
#         background: linear-gradient(135deg, #00a383, #008f72) !important;
#         box-shadow: 0 6px 16px rgba(0,184,148,0.4) !important;
#     }
    
#     /* Checkbox and radio styling */
#     .stCheckbox, .stRadio {
#         color: #000000 !important;
#         font-weight: 600 !important;
#     }
    
#     /* Spinner - Beautiful loading animation */
#     .stSpinner > div {
#         border-top-color: #0066cc !important;
#     }
    
#     /* Progress bar */
#     .stProgress > div > div > div {
#         background: linear-gradient(90deg, #0066cc, #00c6ff) !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# class FloatChatApp:
#     """
#     Main FloatChat Application.
#     Orchestrates all components: chat, visualization, data management.
#     """
    
#     def __init__(self):
#         # Initialize session state
#         self.session_manager = SessionStateManager()
#         self.session_manager.initialize()
        
#         # Initialize components
#         self.query_processor = QueryProcessor()
#         self.sidebar = Sidebar()
#         self.chat_interface = ChatInterface(self.query_processor)
#         self.map_view = MapView()
#         self.profile_viewer = ProfileViewer()
    
#     def run(self):
#         """Main application loop"""
        
#         # Beautiful Header with wave emoji
#         st.markdown('<div class="main-header">🌊 FloatChat - ARGO Data Explorer</div>', unsafe_allow_html=True)
#         st.markdown(
#             '<div class="sub-header">🤖 AI-Powered Ocean Data Discovery • 🌍 Global Coverage • 📊 Real-Time Analysis</div>',
#             unsafe_allow_html=True
#         )
        
#         # Sidebar
#         self.sidebar.render()
        
#         # Main content area - Enhanced Tabs with icons
#         tab1, tab2, tab3, tab4 = st.tabs([
#             "💬 Chat Interface",
#             "🗺️ Geographic Map",
#             "📊 Profile Analysis",
#             "📈 Data Explorer"
#         ])
        
#         with tab1:
#             self._render_chat_tab()
        
#         with tab2:
#             self._render_map_tab()
        
#         with tab3:
#             self._render_profile_tab()
        
#         with tab4:
#             self._render_data_explorer_tab()
        
#         # Enhanced Footer
#         st.markdown("---")
#         st.markdown("""
#             <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 10px; margin-top: 2rem;'>
#                 <p style='font-weight: 700; font-size: 1.1rem; color: #000000; margin-bottom: 0.5rem;'>
#                     🏆 <strong>FloatChat</strong> - Smart India Hackathon 2025
#                 </p>
#                 <p style='font-weight: 600; color: #0066cc; margin: 0;'>
#                     Ministry of Earth Sciences (MoES) • Indian National Centre for Ocean Information Services (INCOIS)
#                 </p>
#                 <p style='font-weight: 500; color: #666; font-size: 0.9rem; margin-top: 0.5rem;'>
#                     Powered by Google Gemini AI • Built with Streamlit • Data from ARGO Global Ocean Observing System
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
    
#     def _render_chat_tab(self):
#         """Render chat interface tab"""
        
#         # Add beautiful header with icon
#         st.markdown("""
#             <div style='background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; border-left: 5px solid #0066cc;'>
#                 <h2 style='color: #000000; margin: 0; font-weight: 700;'>💬 Ask Questions About ARGO Ocean Data</h2>
#                 <p style='color: #000000; margin: 0.5rem 0 0 0; font-weight: 600;'>
#                     Natural language queries powered by AI • Get instant insights from 1.2M+ ocean measurements
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
        
#         # Example queries in a beautiful card
#         with st.expander("� **Example Queries - Click to See**", expanded=False):
#             st.markdown("""
#             <div style='background: #ffffff; padding: 1rem; border-radius: 8px; border: 2px solid #e3f2fd;'>
#                 <h4 style='color: #0066cc; margin-top: 0;'>🔍 Try these sample questions:</h4>
#                 <ul style='color: #000000; font-weight: 600; line-height: 2;'>
#                     <li>📊 <strong>Compare the average temperature between Oct 1 and Oct 2</strong></li>
#                     <li>🌡️ <strong>Show me temperature profiles in the Arabian Sea</strong></li>
#                     <li>🌊 <strong>What's the average salinity near the equator?</strong></li>
#                     <li>📍 <strong>Find ARGO floats between 10°N-20°N and 60°E-80°E</strong></li>
#                     <li>📈 <strong>Show the deepest measurements in the Indian Ocean</strong></li>
#                     <li>🗓️ <strong>Which month has the warmest water in 2025?</strong></li>
#                 </ul>
#             </div>
#             """, unsafe_allow_html=True)
        
#         # Render chat interface
#         self.chat_interface.render()
    
#     def _render_map_tab(self):
#         """Render map visualization tab"""
        
#         # Beautiful header
#         st.markdown("""
#             <div style='background: linear-gradient(135deg, #e8f5e9, #c8e6c9); padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; border-left: 5px solid #00b894;'>
#                 <h2 style='color: #000000; margin: 0; font-weight: 700;'>🗺️ Geographic Distribution of ARGO Floats</h2>
#                 <p style='color: #000000; margin: 0.5rem 0 0 0; font-weight: 600;'>
#                     Interactive maps showing float locations, density, and trajectories
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
        
#         # Check if we have query results
#         if st.session_state.get('last_query_results') is not None:
#             results = st.session_state.last_query_results
#             if results['success'] and not results['results'].empty:
#                 self.map_view.render(results['results'])
#             else:
#                 st.info("📍 No data to display. Run a query in the Chat tab first to see map visualizations.")
#         else:
#             st.info("📍 No data to display. Run a query in the Chat tab first to see map visualizations.")
    
#     def _render_profile_tab(self):
#         """Render profile visualization tab"""
        
#         # Beautiful header
#         st.markdown("""
#             <div style='background: linear-gradient(135deg, #fff3e0, #ffe0b2); padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; border-left: 5px solid #ff9800;'>
#                 <h2 style='color: #000000; margin: 0; font-weight: 700;'>📊 Temperature and Salinity Profiles</h2>
#                 <p style='color: #000000; margin: 0.5rem 0 0 0; font-weight: 600;'>
#                     Vertical profiles, T-S diagrams, and multi-parameter analysis
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
        
#         if st.session_state.get('last_query_results') is not None:
#             results = st.session_state.last_query_results
#             if results['success'] and not results['results'].empty:
#                 self.profile_viewer.render(results['results'])
#             else:
#                 st.info("📊 No data to display. Run a query in the Chat tab first to see profile visualizations.")
#         else:
#             st.info("📊 No data to display. Run a query in the Chat tab first to see profile visualizations.")
    
#     def _render_data_explorer_tab(self):
#         """Render raw data explorer tab"""
        
#         # Beautiful header
#         st.markdown("""
#             <div style='background: linear-gradient(135deg, #f3e5f5, #e1bee7); padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; border-left: 5px solid #9c27b0;'>
#                 <h2 style='color: #000000; margin: 0; font-weight: 700;'>📈 Raw Data Explorer & Export</h2>
#                 <p style='color: #000000; margin: 0.5rem 0 0 0; font-weight: 600;'>
#                     Browse, filter, and download query results in multiple formats
#                 </p>
#             </div>
#         """, unsafe_allow_html=True)
        
#         if st.session_state.get('last_query_results') is not None:
#             results = st.session_state.last_query_results
#             if results['success'] and not results['results'].empty:
#                 df = results['results']
                
#                 # Display statistics
#                 col1, col2, col3, col4 = st.columns(4)
#                 with col1:
#                     st.metric("Total Records", len(df))
#                 with col2:
#                     if 'float_id' in df.columns:
#                         st.metric("Unique Floats", df['float_id'].nunique())
#                 with col3:
#                     if 'temperature' in df.columns:
#                         st.metric("Avg Temperature", f"{df['temperature'].mean():.2f}°C")
#                 with col4:
#                     if 'salinity' in df.columns:
#                         st.metric("Avg Salinity", f"{df['salinity'].mean():.2f} PSU")
                
#                 # Display data table with header
#                 st.markdown("### 📋 Data Table")
#                 st.dataframe(df, use_container_width=True, height=400)
                
#                 # Export options with beautiful styling
#                 st.markdown("---")
#                 st.markdown("""
#                     <h3 style='color: #000000; font-weight: 700;'>💾 Export Options</h3>
#                     <p style='color: #000000; font-weight: 600;'>Download your query results in different formats</p>
#                 """, unsafe_allow_html=True)
                
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     csv = df.to_csv(index=False)
#                     st.download_button(
#                         label="📥 Download CSV",
#                         data=csv,
#                         file_name="argo_data.csv",
#                         mime="text/csv"
#                     )
                
#                 with col2:
#                     json = df.to_json(orient='records', indent=2)
#                     st.download_button(
#                         label="📥 Download JSON",
#                         data=json,
#                         file_name="argo_data.json",
#                         mime="application/json"
#                     )
#             else:
#                 st.info("No data to display. Run a query in the Chat tab first.")
#         else:
#             st.info("No data to display. Run a query in the Chat tab first.")

# # Run the app
# if __name__ == "__main__":
#     app = FloatChatApp()
#     app.run()




import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Add project root to path FIRST (before any local imports)
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_processing.netcdf_exporter import NetCDFExporter, export_dataframe_to_netcdf, export_dataframe_to_ascii

from streamlit_app.components.mcp_chat_interface import MCPChatInterface, render_mcp_capabilities
from streamlit_app.components.advanced_viz_panel import AdvancedVizPanel
from mcp_server.mcp_query_processor import mcp_query_processor
from streamlit_app.components.chat_interface import ChatInterface
from streamlit_app.components.map_view import MapView
from streamlit_app.components.profile_viewer import ProfileViewer
from streamlit_app.components.sidebar import Sidebar
from streamlit_app.utils.session_state import SessionStateManager
from rag_engine.query_processor import QueryProcessor
from database.db_setup import DatabaseSetup
from database.models import ArgoProfile, QueryLog
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="FloatChat - ARGO Data Explorer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Production Grade
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Header */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1e3a8a, #0891b2, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Chat Messages - Enhanced Contrast */
    .stChatMessage {
        background-color: #ffffff !important;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* User message */
    .stChatMessage[data-testid="stChatMessage"]:has([aria-label="user"]) {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
        border-left: 4px solid #3b82f6;
    }
    
    /* Assistant message */
    .stChatMessage[data-testid="stChatMessage"]:has([aria-label="assistant"]) {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
        border-left: 4px solid #10b981;
    }
    
    /* Text Contrast */
    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: #1e293b !important;
        line-height: 1.6;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: #1e293b !important;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    
    code {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        padding: 3px 8px;
        border-radius: 4px;
        font-family: 'Fira Code', monospace;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 700;
        font-size: 1.75rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transform: translateY(-1px);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8fafc;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 8px;
        color: #64748b;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e2e8f0;
        color: #1e293b;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
        font-weight: 600;
        color: #1e293b !important;
    }
    
    /* Info/Warning/Success boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
        padding: 1rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Dataframe */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.6rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-success {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .status-warning {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .status-info {
        background-color: #dbeafe;
        color: #1e40af;
    }
    </style>
""", unsafe_allow_html=True)


class ProductionFloatChatApp:
    """
    Production-grade FloatChat Application with:
    - Error handling
    - Performance monitoring
    - User analytics
    - Data validation
    - Export capabilities
    """
    
    # def __init__(self):
    #     # Initialize session state
    #     self.session_manager = SessionStateManager()
    #     self.session_manager.initialize()
        
    #     # Initialize database
    #     try:
    #         self.db_setup = DatabaseSetup()
    #         if not self.db_setup.test_connection():
    #             st.error("🔴 Database connection failed. Please check configuration.")
    #             st.stop()
    #     except Exception as e:
    #         st.error(f"🔴 Database initialization error: {e}")
    #         st.stop()
        
    #     # Initialize components
    #     try:
    #         self.query_processor = QueryProcessor()
    #         self.sidebar = Sidebar()
    #         self.chat_interface = ChatInterface(self.query_processor)
    #         self.map_view = MapView()
    #         self.profile_viewer = ProfileViewer()
    #     except Exception as e:
    #         st.error(f"🔴 Component initialization error: {e}")
    #         st.stop()
        
    #     # Analytics
    #     self._init_analytics()
    
    def __init__(self):
        # Initialize session state
        self.session_manager = SessionStateManager()
        self.session_manager.initialize()
    
        # Initialize database
        try:
            self.db_setup = DatabaseSetup()
            if not self.db_setup.test_connection():
                st.error("🔴 Database connection failed. Please check configuration.")
                st.stop()
        except Exception as e:
            st.error(f"🔴 Database initialization error: {e}")
            st.stop()
        
        # Initialize components - MCP ENABLED
        try:
            self.mcp_processor = mcp_query_processor  # MCP Query Processor
            self.sidebar = Sidebar()
            self.mcp_chat_interface = MCPChatInterface()  # MCP Chat Interface
            self.map_view = MapView()
            self.profile_viewer = ProfileViewer()
            self.advanced_viz = AdvancedVizPanel()  # Advanced Visualizations
        except Exception as e:
            st.error(f"🔴 Component initialization error: {e}")
            st.stop()
        
        # Analytics
        self._init_analytics()
        
        print("✅ FloatChat initialized with MCP support")
    
    def _render_advanced_viz_tab(self):
        """Advanced visualization tab"""
        st.subheader("🔬 Advanced Oceanographic Visualizations")
        
        if st.session_state.get('last_query_results') is not None:
            results = st.session_state.last_query_results
            if results['success'] and not results['results'].empty:
                self.advanced_viz.render(results['results'])
            else:
                st.info("🔍 No data to display. Run a query in the Chat tab first.")
        else:
            self._render_empty_state("advanced visualizations")








    
    def _init_analytics(self):
        """Initialize analytics tracking"""
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
        if 'total_queries' not in st.session_state:
            st.session_state.total_queries = 0
        if 'successful_queries' not in st.session_state:
            st.session_state.successful_queries = 0
    
    def run(self):
        """Main application loop"""
        
        # Header with status indicator
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="main-header">🌊 FloatChat Pro</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="sub-header">AI-Powered ARGO Ocean Data Discovery & Analysis Platform</div>',
                unsafe_allow_html=True
            )
        
        with col3:
            self._render_status_indicator()
        
        # Sidebar
        self.sidebar.render()
        
        # Main content area - Enhanced Tabs
        # tab1, tab2, tab3, tab4, tab5 = st.tabs([
        #     "💬 Intelligent Chat",
        #     "🗺️ Geographic Explorer",
        #     "📊 Profile Analysis",
        #     "📈 Data Analytics",
        #     "📥 Export & Reports"
        # ])
        
        # with tab1:
        #     self._render_chat_tab()
        
        # with tab2:
        #     self._render_map_tab()
        
        # with tab3:
        #     self._render_profile_tab()
        
        # with tab4:
        #     self._render_analytics_tab()
        
        # with tab5:
        #     self._render_export_tab()
        
        # # Footer with session info
        # self._render_footer()
        
        # Main content area - Enhanced Tabs with MCP
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "💬 Intelligent Chat (MCP)",
            "🗺️ Geographic Explorer",
            "📊 Profile Analysis",
            "🔬 Advanced Visualizations",
            "📈 Data Analytics",
            "📥 Export & Reports"
        ])
        
        with tab1:
            self._render_chat_tab()
        
        with tab2:
            self._render_map_tab()
        
        with tab3:
            self._render_profile_tab()
        
        with tab4:
            self._render_advanced_viz_tab()
        
        with tab5:
            self._render_analytics_tab()
        
        with tab6:
            self._render_export_tab()







    
    def _render_status_indicator(self):
        """Show system status"""
        try:
            session = self.db_setup.get_session()
            count = session.query(ArgoProfile).count()
            session.close()
            
            status_html = f"""
            <div style="text-align: right; padding-top: 1rem;">
                <span class="status-badge status-success">● ONLINE</span><br>
                <small style="color: #64748b;">{count:,} records</small>
            </div>
            """
            st.markdown(status_html, unsafe_allow_html=True)
        except:
            st.markdown(
                '<span class="status-badge status-warning">● LIMITED</span>',
                unsafe_allow_html=True
            )
    
    # def _render_chat_tab(self):
    #     """Enhanced chat interface"""
    #     st.subheader("🤖 Ask Questions About ARGO Data")
        
    #     # Quick action buttons
    #     col1, col2, col3, col4 = st.columns(4)
        
    #     with col1:
    #         if st.button("🌊 Recent Data", use_container_width=True):
    #             st.session_state.quick_query = "Show me data from the last 30 days"
    #     with col2:
    #         if st.button("📍 Arabian Sea", use_container_width=True):
    #             st.session_state.quick_query = "Show profiles in Arabian Sea"
    #     with col3:
    #         if st.button("📊 Statistics", use_container_width=True):
    #             st.session_state.quick_query = "Show me temperature statistics by region"
    #     with col4:
    #         if st.button("🔍 Deep Profiles", use_container_width=True):
    #             st.session_state.quick_query = "Show profiles deeper than 1000m"
        
    #     # Example queries in expander
    #     with st.expander("💡 Example Queries & Tips", expanded=False):
    #         st.markdown("""
    #         **Geographic Queries:**
    #         - Show me salinity profiles in the Arabian Sea
    #         - Find floats between 10°N-20°N and 60°E-80°E
    #         - What's the data coverage in Bay of Bengal?
            
    #         **Temporal Queries:**
    #         - Show recent data from last month
    #         - Temperature trends in March 2023
    #         - Compare winter vs summer profiles
            
    #         **Statistical Queries:**
    #         - Average temperature by depth in Indian Ocean
    #         - Salinity range in equatorial regions
    #         - Count of profiles by region
            
    #         **Profile Analysis:**
    #         - Show temperature profile for float 2902696
    #         - Compare salinity at different depths
    #         - Find deepest measurements
            
    #         **BGC Queries:**
    #         - Show dissolved oxygen levels
    #         - Chlorophyll distribution in coastal areas
    #         - pH measurements in Southern Ocean
            
    #         **💡 Tips:**
    #         - Be specific about regions, dates, and parameters
    #         - Use depth or pressure for vertical queries
    #         - Combine multiple conditions for precise results
    #         """)
        
    #     # Render chat
    #     self.chat_interface.render()
        
    #     # Query performance metrics
    #     if st.session_state.get('last_query_results'):
    #         self._render_query_metrics()
    
    def _render_chat_tab(self):
        """Enhanced chat interface with MCP"""
        st.subheader("🤖 AI-Powered Query Interface (MCP Enabled)")
        
        # Quick action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🌊 Recent Data", use_container_width=True):
                st.session_state.quick_query = "Show me data from the last 30 days"
        with col2:
            if st.button("📍 Arabian Sea", use_container_width=True):
                st.session_state.quick_query = "Show profiles in Arabian Sea"
        with col3:
            if st.button("📊 Calculate Thermocline", use_container_width=True):
                st.session_state.quick_query = "Calculate thermocline for Bay of Bengal"
        with col4:
            if st.button("🔬 Water Masses", use_container_width=True):
                st.session_state.quick_query = "Identify water masses in Arabian Sea"
        
        # Example queries
        with st.expander("💡 MCP-Powered Query Examples", expanded=False):
            st.markdown("""
            **Basic Queries:**
            - Show me temperature profiles in the Arabian Sea
            - What is the database structure?
            - Find recent data from October 2025
            
            **Advanced Analytics (MCP Tools):**
            - Calculate thermocline characteristics for Bay of Bengal
            - Identify water masses in the Indian Ocean
            - Compare temperature between Arabian Sea and Bay of Bengal
            - Analyze temporal trends in dissolved oxygen
            - Calculate mixed layer depth for recent profiles
            
            **BGC Queries:**
            - Show dissolved oxygen levels in Arabian Sea
            - Get chlorophyll and pH data for coastal regions
            
            **Profile Analysis:**
            - Analyze float 2902696 profile statistics
            - Find profiles similar to warm tropical surface water
            
            **💡 MCP automatically selects the right tools for your question!**
            """)
        
        # Render MCP chat interface
        self.mcp_chat_interface.render()
        
        # Query performance metrics
        if st.session_state.get('last_query_results'):
            results = st.session_state.last_query_results
            if results.get('mcp_enabled'):
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔧 MCP Tools Used", len(results.get('tools_used', [])))
            with col2:
                st.metric("📊 Records Retrieved", 
                         len(results['results']) if 'results' in results else 0)
            with col3:
                tools_str = ", ".join(results.get('tools_used', []))
                st.info(f"Tools: {tools_str}")









    def _render_query_metrics(self):
        """Show query performance metrics"""
        result = st.session_state.last_query_results
        
        if result.get('success'):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "⚡ Query Time",
                    f"{result.get('execution_time', 0):.2f}s",
                    delta=None
                )
            with col2:
                st.metric(
                    "📊 Records",
                    f"{result.get('result_count', 0):,}",
                    delta=None
                )
            with col3:
                complexity = result.get('complexity', 'medium')
                st.metric("🔧 Complexity", complexity.upper())
            with col4:
                st.metric("✅ Status", "SUCCESS", delta="Good")
    
    def _render_map_tab(self):
        """Enhanced map visualization"""
        st.subheader("🗺️ Geographic Distribution")
        
        if st.session_state.get('last_query_results') is not None:
            results = st.session_state.last_query_results
            if results['success'] and not results['results'].empty:
                df = results['results']
                
                # Map controls
                col1, col2 = st.columns([3, 1])
                
                with col2:
                    st.markdown("**Map Settings**")
                    map_type = st.selectbox(
                        "Visualization",
                        ["Scatter Plot", "Density Heatmap", "Time Animation"],
                        key="map_type_select"
                    )
                    
                    if 'temperature' in df.columns:
                        color_by = st.selectbox(
                            "Color By",
                            [c for c in df.columns if c in ['temperature', 'salinity', 'pressure', 'dissolved_oxygen']],
                            key="color_by_select"
                        )
                    else:
                        color_by = 'temperature'
                
                with col1:
                    self.map_view.render(df)
                
                # Geographic summary
                st.markdown("---")
                self._render_geographic_summary(df)
            else:
                st.info("🔍 No data to display. Run a query in the Chat tab first.")
        else:
            self._render_empty_state("map")
    
    def _render_geographic_summary(self, df: pd.DataFrame):
        """Show geographic coverage summary"""
        st.subheader("📍 Geographic Coverage")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Latitude Range", 
                     f"{df['latitude'].min():.1f}° to {df['latitude'].max():.1f}°")
        with col2:
            st.metric("Longitude Range",
                     f"{df['longitude'].min():.1f}° to {df['longitude'].max():.1f}°")
        with col3:
            if 'ocean_region' in df.columns:
                st.metric("Regions", df['ocean_region'].nunique())
        with col4:
            st.metric("Spatial Coverage", 
                     f"{(df['latitude'].max() - df['latitude'].min()) * (df['longitude'].max() - df['longitude'].min()):.0f} deg²")
    
    def _render_profile_tab(self):
        """Enhanced profile visualization"""
        st.subheader("📊 Oceanographic Profiles")
        
        if st.session_state.get('last_query_results') is not None:
            results = st.session_state.last_query_results
            if results['success'] and not results['results'].empty:
                df = results['results']
                
                # Profile controls
                col1, col2 = st.columns([3, 1])
                
                with col2:
                    st.markdown("**Profile Settings**")
                    plot_type = st.selectbox(
                        "Plot Type",
                        ["Temperature Profile", "T-S Diagram", "Multi-Parameter", "Comparison"],
                        key="profile_plot_type"
                    )
                    
                    if 'float_id' in df.columns and df['float_id'].nunique() > 1:
                        max_floats = min(10, df['float_id'].nunique())
                        selected_floats = st.multiselect(
                            "Select Floats",
                            df['float_id'].unique()[:20],
                            default=list(df['float_id'].unique()[:3]),
                            key="float_selector"
                        )
                
                with col1:
                    self.profile_viewer.render(df)
                
                # Profile statistics
                st.markdown("---")
                self._render_profile_statistics(df)
            else:
                st.info("🔍 No data to display. Run a query in the Chat tab first.")
        else:
            self._render_empty_state("profile")
    
    def _render_profile_statistics(self, df: pd.DataFrame):
        """Show profile statistics"""
        st.subheader("📈 Profile Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'pressure' in df.columns:
                st.metric("Max Depth", f"{df['pressure'].max():.0f} dbar")
                st.metric("Avg Depth", f"{df['pressure'].mean():.0f} dbar")
        
        with col2:
            if 'temperature' in df.columns:
                st.metric("Temp Range", 
                         f"{df['temperature'].min():.1f}°C - {df['temperature'].max():.1f}°C")
                st.metric("Avg Temp", f"{df['temperature'].mean():.1f}°C")
        
        with col3:
            if 'salinity' in df.columns:
                st.metric("Salinity Range",
                         f"{df['salinity'].min():.2f} - {df['salinity'].max():.2f} PSU")
                st.metric("Avg Salinity", f"{df['salinity'].mean():.2f} PSU")
        
        with col4:
            if 'float_id' in df.columns:
                st.metric("Unique Floats", df['float_id'].nunique())
                profiles = df.groupby(['float_id', 'cycle_number']).ngroups if 'cycle_number' in df.columns else 0
                st.metric("Total Profiles", profiles)
    
    def _render_analytics_tab(self):
        """Data analytics and insights"""
        st.subheader("📈 Data Analytics & Insights")
        
        if st.session_state.get('last_query_results') is not None:
            results = st.session_state.last_query_results
            if results['success'] and not results['results'].empty:
                df = results['results']
                
                # Time series analysis
                if 'timestamp' in df.columns:
                    st.markdown("### 📅 Temporal Analysis")
                    self._render_temporal_analysis(df)
                
                st.markdown("---")
                
                # Statistical analysis
                st.markdown("### 📊 Statistical Summary")
                self._render_statistical_analysis(df)
                
                st.markdown("---")
                
                # Regional analysis
                if 'ocean_region' in df.columns:
                    st.markdown("### 🗺️ Regional Distribution")
                    self._render_regional_analysis(df)
            else:
                st.info("🔍 No data to display. Run a query in the Chat tab first.")
        else:
            self._render_empty_state("analytics")
    
    def _render_temporal_analysis(self, df: pd.DataFrame):
        """Temporal trends analysis"""
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['year_month'] = df['timestamp'].dt.to_period('M').astype(str)
        
        # Measurements over time
        temporal = df.groupby('year_month').size().reset_index(name='count')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=temporal['year_month'],
            y=temporal['count'],
            mode='lines+markers',
            name='Measurements',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Measurements Over Time",
            xaxis_title="Month",
            yaxis_title="Number of Measurements",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_statistical_analysis(self, df: pd.DataFrame):
        """Statistical summary"""
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        
        if len(numeric_cols) > 0:
            stats_df = df[numeric_cols].describe().T
            st.dataframe(stats_df.style.format("{:.2f}"), use_container_width=True)
    
    def _render_regional_analysis(self, df: pd.DataFrame):
        """Regional distribution analysis"""
        region_counts = df['ocean_region'].value_counts()
        
        fig = go.Figure(data=[
            go.Bar(
                x=region_counts.index,
                y=region_counts.values,
                marker=dict(
                    color=region_counts.values,
                    colorscale='Viridis',
                    showscale=True
                )
            )
        ])
        
        fig.update_layout(
            title="Data Distribution by Ocean Region",
            xaxis_title="Region",
            yaxis_title="Number of Measurements",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # def _render_export_tab(self):
    #     """Export and reporting"""
    #     st.subheader("📥 Export Data & Generate Reports")
        
    #     if st.session_state.get('last_query_results') is not None:
    #         results = st.session_state.last_query_results
    #         if results['success'] and not results['results'].empty:
    #             df = results['results']
                
    #             st.markdown("### 💾 Download Options")
                
    #             col1, col2, col3 = st.columns(3)
                
    #             with col1:
    #                 csv = df.to_csv(index=False)
    #                 st.download_button(
    #                     label="📄 Download CSV",
    #                     data=csv,
    #                     file_name=f"argo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    #                     mime="text/csv",
    #                     use_container_width=True
    #                 )
                
    #             with col2:
    #                 json_data = df.to_json(orient='records', indent=2)
    #                 st.download_button(
    #                     label="📋 Download JSON",
    #                     data=json_data,
    #                     file_name=f"argo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    #                     mime="application/json",
    #                     use_container_width=True
    #                 )
                
    #             with col3:
    #                 excel_buffer = self._create_excel_export(df)
    #                 st.download_button(
    #                     label="📊 Download Excel",
    #                     data=excel_buffer,
    #                     file_name=f"argo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
    #                     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    #                     use_container_width=True
    #                 )
                
    #             # Report generation
    #             st.markdown("---")
    #             st.markdown("### 📑 Generate Report")
                
    #             if st.button("🎯 Generate Summary Report", use_container_width=True):
    #                 report = self._generate_summary_report(df)
    #                 st.markdown(report)
                    
    #                 st.download_button(
    #                     label="📥 Download Report (MD)",
    #                     data=report,
    #                     file_name=f"argo_report_{datetime.now().strftime('%Y%m%d')}.md",
    #                     mime="text/markdown",
    #                     use_container_width=True
    #                 )
    #         else:
    #             st.info("🔍 No data to export. Run a query first.")
    #     else:
    #         self._render_empty_state("export")
    
    def _render_export_tab(self):
        """Export and reporting - ENHANCED with NetCDF"""
        st.subheader("📥 Export Data & Generate Reports")
        
        if st.session_state.get('last_query_results') is not None:
            results = st.session_state.last_query_results
            if results['success'] and not results['results'].empty:
                df = results['results']
                
                st.markdown("### 💾 Download Options")
                
                # Create tabs for different export formats
                export_tab1, export_tab2, export_tab3, export_tab4 = st.tabs([
                    "📄 CSV/JSON", "🌊 NetCDF", "📋 ARGO ASCII", "📊 Excel"
                ])
                
                with export_tab1:
                    st.markdown("#### Standard Formats")
                    col1, col2 = st.columns(2)
                
                    with col1:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📄 Download CSV",
                            data=csv,
                            file_name=f"argo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        st.caption(f"Comma-separated values • {len(csv)} bytes")
                
                    with col2:
                        json_data = df.to_json(orient='records', indent=2)
                        st.download_button(
                            label="📋 Download JSON",
                            data=json_data,
                            file_name=f"argo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                        st.caption(f"JSON format • {len(json_data)} bytes")
                
                with export_tab2:
                    st.markdown("#### NetCDF Format (CF-Compliant)")
                    st.info("📦 NetCDF export creates ARGO-compliant files with full metadata")
                
                    # NetCDF export options
                    include_bgc = st.checkbox("Include BGC parameters", value=True)
                    add_metadata = st.checkbox("Add custom metadata", value=False)
                
                    custom_metadata = {}
                    if add_metadata:
                        custom_metadata['author'] = st.text_input("Author", "FloatChat User")
                        custom_metadata['project'] = st.text_input("Project", "Smart India Hackathon 2025")
                        custom_metadata['purpose'] = st.text_area("Purpose", "ARGO data analysis")
                
                    if st.button("🌊 Generate NetCDF File", use_container_width=True):
                        with st.spinner("Creating NetCDF file..."):
                            try:
                                from data_processing.netcdf_exporter import NetCDFExporter
                                from io import BytesIO
                                import tempfile
                            
                                # Create temporary file
                                with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as tmp:
                                    exporter = NetCDFExporter()
                                    success = exporter.export_to_netcdf(
                                        df, 
                                        tmp.name,
                                        metadata=custom_metadata if custom_metadata else None
                                    )
                                
                                    if success:
                                        # Read file for download
                                        with open(tmp.name, 'rb') as f:
                                            netcdf_data = f.read()
                                    
                                        st.download_button(
                                            label="📥 Download NetCDF File",
                                            data=netcdf_data,
                                            file_name=f"argo_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.nc",
                                            mime="application/x-netcdf",
                                            use_container_width=True
                                        )
                                    
                                        st.success(f"✅ NetCDF file created successfully ({len(netcdf_data) / 1024:.2f} KB)")
                                    
                                        # Show validation
                                        validation = exporter.validate_netcdf(tmp.name)
                                        with st.expander("📋 File Validation"):
                                            st.json(validation)
                                    else:
                                        st.error("❌ NetCDF export failed")
                            
                                # Cleanup
                                import os
                                os.unlink(tmp.name)
                            
                            except Exception as e:
                                st.error(f"❌ Error creating NetCDF: {e}")
                                import traceback
                                st.code(traceback.format_exc())
                
                with export_tab3:
                    st.markdown("#### ARGO ASCII Format")
                    st.info("📄 ARGO-specific ASCII format for data exchange")
                
                    if st.button("📋 Generate ARGO ASCII", use_container_width=True):
                        with st.spinner("Creating ASCII file..."):
                            try:
                                from data_processing.netcdf_exporter import NetCDFExporter
                                import tempfile
                            
                                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                                    exporter = NetCDFExporter()
                                    exporter._write_argo_ascii(df, Path(tmp.name))
                                
                                    with open(tmp.name, 'r') as f:
                                        ascii_data = f.read()
                                
                                    st.download_button(
                                        label="📥 Download ARGO ASCII",
                                        data=ascii_data,
                                        file_name=f"argo_ascii_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                                
                                    # Preview
                                    with st.expander("👁️ Preview (first 20 lines)"):
                                        st.code('\n'.join(ascii_data.split('\n')[:20]))
                            
                                os.unlink(tmp.name)
                                st.success("✅ ARGO ASCII file generated")
                            
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                
                with export_tab4:
                    st.markdown("#### Excel Workbook")
                    excel_buffer = self._create_excel_export(df)
                    st.download_button(
                        label="📊 Download Excel",
                        data=excel_buffer,
                        file_name=f"argo_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    st.caption("Multi-sheet workbook with data, statistics, and metadata")
                
                # Report generation
                st.markdown("---")
                st.markdown("### 📑 Generate Analysis Report")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    report_format = st.selectbox(
                        "Report Format",
                        ["Markdown", "HTML", "PDF (Future)"]
                    )
                
                with col2:
                    include_viz = st.checkbox("Include visualizations", value=True)
                
                if st.button("🎯 Generate Summary Report", use_container_width=True):
                    report = self._generate_summary_report(df)
                    st.markdown(report)
                    
                    st.download_button(
                        label="📥 Download Report (MD)",
                        data=report,
                        file_name=f"argo_report_{datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
            else:
                st.info("🔍 No data to export. Run a query first.")
        else:
            self._render_empty_state("export")
    
    def _create_excel_export(self, df: pd.DataFrame):
        """Create Excel file with multiple sheets"""
        from io import BytesIO
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main data
            df.to_excel(writer, sheet_name='Data', index=False)
            
            # Summary statistics
            numeric_df = df.select_dtypes(include=['float64', 'int64'])
            if not numeric_df.empty:
                numeric_df.describe().to_excel(writer, sheet_name='Statistics')
            
            # Metadata
            metadata = pd.DataFrame({
                'Property': ['Export Date', 'Total Records', 'Date Range', 'Columns'],
                'Value': [
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    len(df),
                    f"{df['timestamp'].min()} to {df['timestamp'].max()}" if 'timestamp' in df.columns else 'N/A',
                    ', '.join(df.columns.tolist())
                ]
            })
            metadata.to_excel(writer, sheet_name='Metadata', index=False)
        
        output.seek(0)
        return output
    
    def _generate_summary_report(self, df: pd.DataFrame) -> str:
        """Generate markdown summary report"""
        report = f"""# ARGO Float Data Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Dataset Overview

- **Total Records**: {len(df):,}
- **Unique Floats**: {df['float_id'].nunique() if 'float_id' in df.columns else 'N/A'}
- **Date Range**: {df['timestamp'].min()} to {df['timestamp'].max() if 'timestamp' in df.columns else 'N/A'}

---

## 🗺️ Geographic Coverage

- **Latitude Range**: {df['latitude'].min():.2f}°N to {df['latitude'].max():.2f}°N
- **Longitude Range**: {df['longitude'].min():.2f}°E to {df['longitude'].max():.2f}°E
"""
        
        if 'ocean_region' in df.columns:
            report += f"\n### Regional Distribution\n\n"
            for region, count in df['ocean_region'].value_counts().items():
                report += f"- **{region}**: {count:,} measurements ({count/len(df)*100:.1f}%)\n"
        
        report += f"\n---\n\n## 🌡️ Temperature Analysis\n\n"
        if 'temperature' in df.columns:
            report += f"""
- **Range**: {df['temperature'].min():.2f}°C to {df['temperature'].max():.2f}°C
- **Mean**: {df['temperature'].mean():.2f}°C
- **Median**: {df['temperature'].median():.2f}°C
- **Std Dev**: {df['temperature'].std():.2f}°C
"""
        
        report += f"\n---\n\n## 💧 Salinity Analysis\n\n"
        if 'salinity' in df.columns:
            report += f"""
- **Range**: {df['salinity'].min():.2f} to {df['salinity'].max():.2f} PSU
- **Mean**: {df['salinity'].mean():.2f} PSU
- **Median**: {df['salinity'].median():.2f} PSU
- **Std Dev**: {df['salinity'].std():.2f} PSU
"""
        
        report += f"\n---\n\n## 📏 Depth Analysis\n\n"
        if 'pressure' in df.columns:
            report += f"""
- **Maximum Depth**: {df['pressure'].max():.0f} dbar
- **Mean Depth**: {df['pressure'].mean():.0f} dbar
- **Median Depth**: {df['pressure'].median():.0f} dbar
"""
        
        if any(col in df.columns for col in ['dissolved_oxygen', 'chlorophyll', 'ph']):
            report += f"\n---\n\n## 🧪 BGC Parameters\n\n"
            
            if 'dissolved_oxygen' in df.columns:
                report += f"### Dissolved Oxygen\n"
                report += f"- Range: {df['dissolved_oxygen'].min():.2f} to {df['dissolved_oxygen'].max():.2f} μmol/kg\n"
                report += f"- Mean: {df['dissolved_oxygen'].mean():.2f} μmol/kg\n\n"
            
            if 'chlorophyll' in df.columns:
                report += f"### Chlorophyll\n"
                report += f"- Range: {df['chlorophyll'].min():.3f} to {df['chlorophyll'].max():.3f} mg/m³\n"
                report += f"- Mean: {df['chlorophyll'].mean():.3f} mg/m³\n\n"
            
            if 'ph' in df.columns:
                report += f"### pH\n"
                report += f"- Range: {df['ph'].min():.2f} to {df['ph'].max():.2f}\n"
                report += f"- Mean: {df['ph'].mean():.2f}\n\n"
        
        report += f"\n---\n\n## ℹ️ Data Quality\n\n"
        report += f"- **Data Mode**: {df['data_mode'].value_counts().to_dict() if 'data_mode' in df.columns else 'N/A'}\n"
        report += f"- **Missing Values**: {df.isnull().sum().sum()} cells\n"
        report += f"- **Completeness**: {(1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100:.1f}%\n"
        
        report += f"\n---\n\n*Report generated by FloatChat Pro - ARGO Data Analysis Platform*\n"
        
        return report
    
    def _render_empty_state(self, tab_name: str):
        """Render empty state for tabs"""
        st.info(f"""
        ### 🔍 No Data Available
        
        To view {tab_name} visualizations:
        1. Go to the **Chat** tab
        2. Ask a question about ARGO data
        3. Results will appear here automatically
        
        **Try these examples:**
        - "Show me recent data from the last 30 days"
        - "Temperature profiles in Arabian Sea"
        - "Statistics by ocean region"
        """)
    
    def _render_footer(self):
        """Render application footer"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **FloatChat Pro**  
            Version 2.0 | Production Release  
            Ministry of Earth Sciences (MoES) | INCOIS
            """)
        
        with col2:
            session_duration = datetime.now() - st.session_state.session_start
            st.markdown(f"""
            **Session Info**  
            Duration: {session_duration.seconds // 60} minutes  
            Queries: {st.session_state.total_queries}  
            Success Rate: {(st.session_state.successful_queries / max(st.session_state.total_queries, 1) * 100):.0f}%
            """)
        
        with col3:
            st.markdown("""
            **Support**  
            📧 [support@floatchat.org](mailto:support@floatchat.org)  
            📚 [Documentation](https://docs.floatchat.org)  
            💬 [Feedback](https://feedback.floatchat.org)
            """)


# Run the app
if __name__ == "__main__":
    try:
        app = ProductionFloatChatApp()
        app.run()
    except Exception as e:
        st.error(f"🔴 Critical Application Error: {e}")
        st.error("Please contact support if this issue persists.")
        
        if st.button("🔄 Restart Application"):
            st.rerun()