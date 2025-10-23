"""
Advanced Oceanographic Visualizations
Production-grade scientific plots
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List, Dict
from scipy.interpolate import griddata


class AdvancedOceanPlots:
    """
    Advanced visualization for oceanographic data
    """
    
    def __init__(self):
        self.color_scales = {
            'temperature': 'RdYlBu_r',
            'salinity': 'Viridis',
            'oxygen': 'Blues',
            'chlorophyll': 'Greens'
        }
    
    def create_section_plot(
        self,
        df: pd.DataFrame,
        parameter: str = 'temperature',
        title: str = None
    ) -> go.Figure:
        """
        Create oceanographic section plot (depth vs distance)
        Shows vertical structure along a transect
        """
        
        if df.empty or 'pressure' not in df.columns:
            return self._empty_figure(title or "Section Plot")
        
        # Sort by latitude or longitude
        if 'latitude' in df.columns:
            df = df.sort_values('latitude')
            distance = df['latitude'].values
            x_label = 'Latitude (°N)'
        else:
            df = df.sort_values('longitude')
            distance = df['longitude'].values
            x_label = 'Longitude (°E)'
        
        depth = df['pressure'].values
        values = df[parameter].values
        
        # Create grid for interpolation
        xi = np.linspace(distance.min(), distance.max(), 100)
        yi = np.linspace(depth.min(), depth.max(), 100)
        xi, yi = np.meshgrid(xi, yi)
        
        # Interpolate
        zi = griddata((distance, depth), values, (xi, yi), method='linear')
        
        # Create contour plot
        fig = go.Figure(data=go.Contour(
            x=xi[0],
            y=yi[:, 0],
            z=zi,
            colorscale=self.color_scales.get(parameter, 'Viridis'),
            colorbar=dict(title=parameter.capitalize()),
            contours=dict(
                showlabels=True,
                labelfont=dict(size=10, color='white')
            )
        ))
        
        fig.update_yaxes(
            title='Pressure (dbar)',
            autorange='reversed'
        )
        fig.update_xaxes(title=x_label)
        
        fig.update_layout(
            title=title or f"{parameter.capitalize()} Section",
            height=500,
            hovermode='closest'
        )
        
        return fig
    
    def create_hovmoller_diagram(
        self,
        df: pd.DataFrame,
        parameter: str = 'temperature',
        title: str = None
    ) -> go.Figure:
        """
        Create Hovmöller diagram (time vs depth)
        Shows temporal evolution of vertical structure
        """
        
        if df.empty or 'timestamp' not in df.columns or 'pressure' not in df.columns:
            return self._empty_figure(title or "Hovmöller Diagram")
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Pivot for heatmap
        pivot = df.pivot_table(
            values=parameter,
            index='pressure',
            columns='timestamp',
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            x=pivot.columns,
            y=pivot.index,
            z=pivot.values,
            colorscale=self.color_scales.get(parameter, 'Viridis'),
            colorbar=dict(title=parameter.capitalize())
        ))
        
        fig.update_yaxes(
            title='Pressure (dbar)',
            autorange='reversed'
        )
        fig.update_xaxes(title='Time')
        
        fig.update_layout(
            title=title or f"{parameter.capitalize()} Hovmöller Diagram",
            height=500
        )
        
        return fig
    
    def create_ts_density_plot(
        self,
        df: pd.DataFrame,
        title: str = "T-S Diagram with Density Contours"
    ) -> go.Figure:
        """
        Create T-S diagram with density (sigma-theta) contours
        Standard oceanographic analysis
        """
        
        if df.empty or 'temperature' not in df.columns or 'salinity' not in df.columns:
            return self._empty_figure(title)
        
        # Calculate potential density (simplified)
        # For production, use gsw (Gibbs SeaWater) library
        df['density'] = 1000 + 0.7 * df['salinity'] - 0.2 * df['temperature']
        
        # Create scatter plot
        fig = px.scatter(
            df,
            x='salinity',
            y='temperature',
            color='pressure',
            color_continuous_scale='Viridis_r',
            labels={
                'salinity': 'Salinity (PSU)',
                'temperature': 'Temperature (°C)',
                'pressure': 'Pressure (dbar)'
            },
            title=title
        )
        
        # Add density contours
        sal_range = np.linspace(df['salinity'].min(), df['salinity'].max(), 50)
        temp_range = np.linspace(df['temperature'].min(), df['temperature'].max(), 50)
        sal_grid, temp_grid = np.meshgrid(sal_range, temp_range)
        density_grid = 1000 + 0.7 * sal_grid - 0.2 * temp_grid
        
        fig.add_trace(go.Contour(
            x=sal_range,
            y=temp_range,
            z=density_grid,
            showscale=False,
            contours=dict(
                showlabels=True,
                labelfont=dict(size=10, color='gray')
            ),
            line=dict(color='gray', width=1),
            opacity=0.3,
            name='Density (kg/m³)'
        ))
        
        fig.update_layout(height=600)
        
        return fig
    
    def create_property_property_plot(
        self,
        df: pd.DataFrame,
        param1: str,
        param2: str,
        color_by: str = 'pressure',
        title: str = None
    ) -> go.Figure:
        """
        Create property-property plot (e.g., O2 vs Temperature)
        """
        
        if df.empty or param1 not in df.columns or param2 not in df.columns:
            return self._empty_figure(title or f"{param1} vs {param2}")
        
        fig = px.scatter(
            df,
            x=param1,
            y=param2,
            color=color_by,
            color_continuous_scale='Viridis',
            labels={
                param1: param1.replace('_', ' ').capitalize(),
                param2: param2.replace('_', ' ').capitalize(),
                color_by: color_by.replace('_', ' ').capitalize()
            },
            title=title or f"{param2.capitalize()} vs {param1.capitalize()}"
        )
        
        fig.update_layout(height=600)
        
        return fig
    
    def create_multi_profile_comparison(
        self,
        df: pd.DataFrame,
        group_by: str = 'float_id',
        parameters: List[str] = ['temperature', 'salinity'],
        title: str = "Multi-Profile Comparison"
    ) -> go.Figure:
        """
        Create multi-panel profile comparison
        """
        
        if df.empty:
            return self._empty_figure(title)
        
        n_params = len(parameters)
        
        fig = make_subplots(
            rows=1,
            cols=n_params,
            subplot_titles=[p.capitalize() for p in parameters],
            shared_yaxes=True
        )
        
        groups = df.groupby(group_by)
        colors = px.colors.qualitative.Set1
        
        for i, param in enumerate(parameters, 1):
            if param not in df.columns:
                continue
            
            for j, (name, group) in enumerate(groups):
                group = group.sort_values('pressure')
                
                fig.add_trace(
                    go.Scatter(
                        x=group[param],
                        y=group['pressure'],
                        mode='lines',
                        name=str(name),
                        line=dict(color=colors[j % len(colors)]),
                        showlegend=(i == 1)  # Only show legend for first subplot
                    ),
                    row=1,
                    col=i
                )
        
        fig.update_yaxes(title_text='Pressure (dbar)', autorange='reversed', row=1, col=1)
        
        for i, param in enumerate(parameters, 1):
            fig.update_xaxes(title_text=param.capitalize(), row=1, col=i)
        
        fig.update_layout(
            title=title,
            height=600,
            hovermode='closest'
        )
        
        return fig
    
    def create_depth_histogram(
        self,
        df: pd.DataFrame,
        parameter: str = 'temperature',
        depth_bins: int = 20,
        title: str = None
    ) -> go.Figure:
        """
        Create histogram of parameter values by depth
        """
        
        if df.empty or parameter not in df.columns or 'pressure' not in df.columns:
            return self._empty_figure(title or "Depth Histogram")
        
        # Create depth bins
        df['depth_bin'] = pd.cut(df['pressure'], bins=depth_bins)
        
        fig = go.Figure()
        
        for depth_bin in sorted(df['depth_bin'].unique()):
            data = df[df['depth_bin'] == depth_bin][parameter]
            
            fig.add_trace(go.Histogram(
                x=data,
                name=str(depth_bin),
                opacity=0.7
            ))
        
        fig.update_layout(
            barmode='overlay',
            title=title or f"{parameter.capitalize()} Distribution by Depth",
            xaxis_title=parameter.capitalize(),
            yaxis_title='Count',
            height=500
        )
        
        return fig
    
    def create_spatial_interpolation(
        self,
        df: pd.DataFrame,
        parameter: str = 'temperature',
        depth_level: float = 10.0,
        title: str = None
    ) -> go.Figure:
        """
        Create spatial interpolation at specific depth
        """
        
        if df.empty:
            return self._empty_figure(title or "Spatial Interpolation")
        
        # Filter by depth
        depth_data = df[abs(df['pressure'] - depth_level) < 5]
        
        if depth_data.empty:
            return self._empty_figure(title or f"No data at {depth_level}m depth")
        
        # Create grid
        lat = depth_data['latitude'].values
        lon = depth_data['longitude'].values
        values = depth_data[parameter].values
        
        # Grid interpolation
        lat_grid = np.linspace(lat.min(), lat.max(), 50)
        lon_grid = np.linspace(lon.min(), lon.max(), 50)
        lon_grid, lat_grid = np.meshgrid(lon_grid, lat_grid)
        
        values_grid = griddata(
            (lon, lat),
            values,
            (lon_grid, lat_grid),
            method='cubic'
        )
        
        fig = go.Figure(data=go.Contour(
            x=lon_grid[0],
            y=lat_grid[:, 0],
            z=values_grid,
            colorscale=self.color_scales.get(parameter, 'Viridis'),
            colorbar=dict(title=parameter.capitalize()),
            contours=dict(showlabels=True)
        ))
        
        # Add measurement points
        fig.add_trace(go.Scatter(
            x=lon,
            y=lat,
            mode='markers',
            marker=dict(color='black', size=5),
            name='Measurements'
        ))
        
        fig.update_layout(
            title=title or f"{parameter.capitalize()} at {depth_level}m depth",
            xaxis_title='Longitude (°E)',
            yaxis_title='Latitude (°N)',
            height=600
        )
        
        return fig
    
    def create_anomaly_plot(
        self,
        df: pd.DataFrame,
        parameter: str = 'temperature',
        baseline: str = 'mean',
        title: str = None
    ) -> go.Figure:
        """
        Create anomaly plot (deviation from baseline)
        """
        
        if df.empty or parameter not in df.columns or 'pressure' not in df.columns:
            return self._empty_figure(title or "Anomaly Plot")
        
        # Calculate baseline
        if baseline == 'mean':
            baseline_values = df.groupby('pressure')[parameter].mean()
        elif baseline == 'median':
            baseline_values = df.groupby('pressure')[parameter].median()
        else:
            return self._empty_figure("Invalid baseline")
        
        # Calculate anomalies
        df = df.copy()
        df['baseline'] = df['pressure'].map(baseline_values)
        df['anomaly'] = df[parameter] - df['baseline']
        
        fig = go.Figure()
        
        # Plot profiles colored by anomaly
        if 'timestamp' in df.columns:
            for timestamp, group in df.groupby('timestamp'):
                fig.add_trace(go.Scatter(
                    x=group['anomaly'],
                    y=group['pressure'],
                    mode='lines',
                    name=str(timestamp),
                    hovertemplate='Anomaly: %{x:.2f}<br>Depth: %{y:.0f}m'
                ))
        else:
            fig.add_trace(go.Scatter(
                x=df['anomaly'],
                y=df['pressure'],
                mode='markers',
                marker=dict(
                    color=df['anomaly'],
                    colorscale='RdBu_r',
                    colorbar=dict(title='Anomaly')
                )
            ))
        
        # Add zero line
        fig.add_vline(x=0, line_dash="dash", line_color="gray")
        
        fig.update_yaxes(title='Pressure (dbar)', autorange='reversed')
        fig.update_xaxes(title=f'{parameter.capitalize()} Anomaly')
        
        fig.update_layout(
            title=title or f"{parameter.capitalize()} Anomaly from {baseline.capitalize()}",
            height=600
        )
        
        return fig
    
    def _empty_figure(self, title: str) -> go.Figure:
        """Create empty figure with message"""
        fig = go.Figure()
        fig.update_layout(
            title=title,
            annotations=[
                dict(
                    text="No data available for this visualization",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16)
                )
            ],
            height=500
        )
        return fig


# Singleton instance
advanced_plots = AdvancedOceanPlots()