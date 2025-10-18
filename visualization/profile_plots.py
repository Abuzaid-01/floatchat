import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Optional

class ProfilePlotter:
    """
    Create oceanographic profile visualizations.
    Specialized plots for vertical temperature/salinity structure.
    """
    
    def create_temperature_profile(
        self,
        df: pd.DataFrame,
        float_ids: Optional[List[str]] = None,
        title: str = "Temperature-Depth Profile"
    ) -> go.Figure:
        """
        Create classic T-S diagram (Temperature vs Depth).
        The most common oceanographic visualization.
        
        Args:
            df: DataFrame with pressure and temperature columns
            float_ids: Specific float IDs to plot
            title: Plot title
        """
        fig = go.Figure()
        
        if df.empty:
            return self._empty_figure(title)
        
        # Group by float_id and cycle_number
        if 'float_id' in df.columns and 'cycle_number' in df.columns:
            groups = df.groupby(['float_id', 'cycle_number'])
            
            for (fid, cycle), group in groups:
                if float_ids and fid not in float_ids:
                    continue
                
                group = group.sort_values('pressure')
                fig.add_trace(go.Scatter(
                    x=group['temperature'],
                    y=group['pressure'],
                    mode='lines+markers',
                    name=f"Float {fid} Cycle {cycle}",
                    hovertemplate='Temp: %{x:.2f}°C<br>Depth: %{y:.1f}m<extra></extra>'
                ))
        else:
            # Single profile
            df = df.sort_values('pressure')
            fig.add_trace(go.Scatter(
                x=df['temperature'],
                y=df['pressure'],
                mode='lines+markers',
                name='Profile',
                hovertemplate='Temp: %{x:.2f}°C<br>Depth: %{y:.1f}m<extra></extra>'
            ))
        
        # Invert y-axis (depth increases downward)
        fig.update_yaxes(autorange='reversed', title='Pressure (dbar)')
        fig.update_xaxes(title='Temperature (°C)')
        fig.update_layout(
            title=title,
            height=600,
            hovermode='closest',
            showlegend=True
        )
        
        return fig
    
    def create_ts_diagram(
        self,
        df: pd.DataFrame,
        title: str = "Temperature-Salinity Diagram"
    ) -> go.Figure:
        """
        Create T-S diagram colored by depth.
        Shows water mass characteristics.
        """
        if df.empty:
            return self._empty_figure(title)
        
        fig = px.scatter(
            df,
            x='salinity',
            y='temperature',
            color='pressure',
            color_continuous_scale='Viridis',
            labels={
                'salinity': 'Salinity (PSU)',
                'temperature': 'Temperature (°C)',
                'pressure': 'Pressure (dbar)'
            },
            title=title,
            hover_data=['latitude', 'longitude', 'pressure']
        )
        
        fig.update_layout(height=600)
        return fig
    
    def create_multi_parameter_profile(
        self,
        df: pd.DataFrame,
        parameters: List[str] = ['temperature', 'salinity'],
        title: str = "Multi-Parameter Profile"
    ) -> go.Figure:
        """
        Create side-by-side profiles of multiple parameters.
        Useful for comparing different measurements at same location.
        """
        if df.empty:
            return self._empty_figure(title)
        
        # Create subplots
        from plotly.subplots import make_subplots
        
        n_params = len(parameters)
        fig = make_subplots(
            rows=1,
            cols=n_params,
            subplot_titles=[p.capitalize() for p in parameters],
            shared_yaxes=True
        )
        
        df = df.sort_values('pressure')
        
        for i, param in enumerate(parameters, 1):
            if param not in df.columns:
                continue
            
            fig.add_trace(
                go.Scatter(
                    x=df[param],
                    y=df['pressure'],
                    mode='lines+markers',
                    name=param.capitalize(),
                    showlegend=False
                ),
                row=1,
                col=i
            )
            
            fig.update_xaxes(title_text=param.capitalize(), row=1, col=i)
        
        fig.update_yaxes(title_text='Pressure (dbar)', autorange='reversed', row=1, col=1)
        fig.update_layout(
            title=title,
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_profile_comparison(
        self,
        df: pd.DataFrame,
        group_by: str = 'timestamp',
        title: str = "Profile Comparison"
    ) -> go.Figure:
        """
        Compare multiple profiles side-by-side.
        Great for temporal or spatial comparisons.
        """
        if df.empty:
            return self._empty_figure(title)
        
        fig = go.Figure()
        
        # Group data
        if group_by in df.columns:
            groups = df.groupby(group_by)
            
            for name, group in groups:
                group = group.sort_values('pressure')
                fig.add_trace(go.Scatter(
                    x=group['temperature'],
                    y=group['pressure'],
                    mode='lines',
                    name=str(name),
                    hovertemplate='Temp: %{x:.2f}°C<br>Depth: %{y:.1f}m<extra></extra>'
                ))
        
        fig.update_yaxes(autorange='reversed', title='Pressure (dbar)')
        fig.update_xaxes(title='Temperature (°C)')
        fig.update_layout(
            title=title,
            height=600,
            hovermode='closest'
        )
        
        return fig
    
    def _empty_figure(self, title: str) -> go.Figure:
        """Create empty figure with message"""
        fig = go.Figure()
        fig.update_layout(
            title=title,
            height=600,
            annotations=[
                dict(
                    text="No data to display",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    font=dict(size=20)
                )
            ]
        )
        return fig

# Usage
if __name__ == "__main__":
    # Test data
    sample_df = pd.DataFrame({
        'pressure': [10, 50, 100, 200, 500, 1000],
        'temperature': [28.5, 27.2, 25.8, 22.5, 18.2, 12.5],
        'salinity': [34.5, 34.6, 34.8, 35.0, 35.2, 35.3],
        'latitude': [10.5] * 6,
        'longitude': [75.3] * 6
    })
    
    plotter = ProfilePlotter()
    fig = plotter.create_temperature_profile(sample_df)
    fig.show()
