"""
Advanced Visualization Panel
Provides access to specialized oceanographic plots
"""

import streamlit as st
import pandas as pd
from visualization.advanced_plots import advanced_plots


class AdvancedVizPanel:
    """
    Panel for advanced oceanographic visualizations
    """
    
    def __init__(self):
        self.plotter = advanced_plots
    
    def render(self, df: pd.DataFrame):
        """Render advanced visualization panel"""
        
        if df.empty:
            st.info("No data available. Run a query first.")
            return
        
        st.subheader("🔬 Advanced Oceanographic Visualizations")
        
        # Visualization selector
        viz_type = st.selectbox(
            "Select Visualization Type",
            [
                "Section Plot",
                "Hovmöller Diagram",
                "T-S Density Plot",
                "Property-Property Plot",
                "Multi-Profile Comparison",
                "Depth Histogram",
                "Spatial Interpolation",
                "Anomaly Plot"
            ]
        )
        
        # Parameter selector
        available_params = [col for col in df.columns 
                           if col in ['temperature', 'salinity', 'pressure', 
                                     'dissolved_oxygen', 'chlorophyll', 'ph']]
        
        if viz_type == "Section Plot":
            parameter = st.selectbox("Parameter", available_params)
            fig = self.plotter.create_section_plot(df, parameter)
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "Hovmöller Diagram":
            if 'timestamp' in df.columns:
                parameter = st.selectbox("Parameter", available_params)
                fig = self.plotter.create_hovmoller_diagram(df, parameter)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Timestamp data required for Hovmöller diagram")
        
        elif viz_type == "T-S Density Plot":
            if 'temperature' in df.columns and 'salinity' in df.columns:
                fig = self.plotter.create_ts_density_plot(df)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Temperature and salinity data required")
        
        elif viz_type == "Property-Property Plot":
            col1, col2 = st.columns(2)
            with col1:
                param1 = st.selectbox("X-axis Parameter", available_params, key='pp_x')
            with col2:
                param2 = st.selectbox("Y-axis Parameter", available_params, key='pp_y')
            
            if param1 != param2:
                fig = self.plotter.create_property_property_plot(df, param1, param2)
                st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "Multi-Profile Comparison":
            selected_params = st.multiselect(
                "Select Parameters",
                available_params,
                default=available_params[:2]
            )
            
            if selected_params:
                group_by = st.selectbox(
                    "Group By",
                    [col for col in ['float_id', 'timestamp', 'cycle_number'] if col in df.columns]
                )
                fig = self.plotter.create_multi_profile_comparison(
                    df, group_by, selected_params
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "Depth Histogram":
            parameter = st.selectbox("Parameter", available_params)
            bins = st.slider("Number of Depth Bins", 5, 50, 20)
            fig = self.plotter.create_depth_histogram(df, parameter, bins)
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "Spatial Interpolation":
            if 'latitude' in df.columns and 'longitude' in df.columns:
                parameter = st.selectbox("Parameter", available_params)
                depth = st.slider(
                    "Depth Level (dbar)",
                    float(df['pressure'].min()),
                    float(df['pressure'].max()),
                    10.0
                )
                fig = self.plotter.create_spatial_interpolation(df, parameter, depth)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Geographic coordinates required")
        
        elif viz_type == "Anomaly Plot":
            parameter = st.selectbox("Parameter", available_params)
            baseline = st.radio("Baseline", ["mean", "median"])
            fig = self.plotter.create_anomaly_plot(df, parameter, baseline)
            st.plotly_chart(fig, use_container_width=True)
        
        # Add interpretation guide
        self._render_interpretation_guide(viz_type)
    
    def _render_interpretation_guide(self, viz_type: str):
        """Render interpretation guide for visualization"""
        
        guides = {
            "Section Plot": """
            **How to Read:**
            - X-axis: Geographic position (latitude or longitude)
            - Y-axis: Depth (pressure in dbar)
            - Colors: Parameter values
            - Contour lines: Isolines of equal value
            
            **What to Look For:**
            - Horizontal patterns: Water masses at specific depths
            - Vertical patterns: Mixing processes
            - Sloping lines: Fronts and currents
            """,
            "Hovmöller Diagram": """
            **How to Read:**
            - X-axis: Time
            - Y-axis: Depth
            - Colors: Parameter values
            
            **What to Look For:**
            - Vertical movements: Upwelling/downwelling events
            - Seasonal cycles: Regular temporal patterns
            - Anomalies: Unusual events
            """,
            "T-S Density Plot": """
            **How to Read:**
            - X-axis: Salinity (PSU)
            - Y-axis: Temperature (°C)
            - Colors: Depth or other parameter
            - Gray contours: Density isolines
            
            **What to Look For:**
            - Clusters: Different water masses
            - Diagonal patterns: Mixing lines
            - Density: Stability indicators
            """
        }
        
        if viz_type in guides:
            with st.expander("📖 Interpretation Guide"):
                st.markdown(guides[viz_type])