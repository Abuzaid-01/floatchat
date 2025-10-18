import streamlit as st
import pandas as pd
from visualization.map_plots import MapVisualizer

class MapView:
    """Map visualization component for Streamlit"""
    
    def __init__(self):
        self.visualizer = MapVisualizer()
    
    def render(self, df: pd.DataFrame):
        """Render map visualizations"""
        
        # Visualization options
        st.sidebar.subheader("🗺️ Map Options")
        
        map_type = st.sidebar.selectbox(
            "Visualization Type",
            ["Float Locations", "Density Heatmap", "Time Animation"]
        )
        
        if map_type == "Float Locations":
            # Color by parameter
            color_options = [col for col in df.columns 
                           if col in ['temperature', 'salinity', 'pressure', 
                                     'dissolved_oxygen', 'chlorophyll']]
            
            if color_options:
                color_by = st.sidebar.selectbox("Color By", color_options)
            else:
                color_by = 'temperature'
            
            fig = self.visualizer.create_float_trajectory_map(
                df,
                color_by=color_by,
                title=f"ARGO Float Locations (colored by {color_by})"
            )
            
        elif map_type == "Density Heatmap":
            fig = self.visualizer.create_density_heatmap(
                df,
                title="ARGO Float Data Density"
            )
            
        else:  # Time Animation
            if 'timestamp' in df.columns:
                fig = self.visualizer.create_time_animated_map(
                    df,
                    title="ARGO Float Trajectories Over Time"
                )
            else:
                st.warning("Timestamp column not available for animation")
                fig = self.visualizer.create_float_trajectory_map(df)
        
        # Display map
        st.plotly_chart(fig, use_container_width=True)
        
        # Add geographic statistics
        self._display_geo_stats(df)
    
    def _display_geo_stats(self, df: pd.DataFrame):
        """Display geographic statistics"""
        if 'latitude' in df.columns and 'longitude' in df.columns:
            st.subheader("📍 Geographic Coverage")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Latitude Range**")
                st.write(f"{df['latitude'].min():.2f}°N to {df['latitude'].max():.2f}°N")
                
            with col2:
                st.markdown("**Longitude Range**")
                st.write(f"{df['longitude'].min():.2f}°E to {df['longitude'].max():.2f}°E")
