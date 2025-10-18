import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional, List

class MapVisualizer:
    """
    Create interactive geographic visualizations.
    Uses Plotly for rich, zoomable maps.
    """
    
    def __init__(self):
        self.default_mapbox_style = "open-street-map"
    
    def create_float_trajectory_map(
        self,
        df: pd.DataFrame,
        color_by: str = 'temperature',
        title: str = "ARGO Float Locations"
    ) -> go.Figure:
        """
        Create interactive map showing float locations colored by parameter.
        
        Args:
            df: DataFrame with latitude, longitude, and parameter columns
            color_by: Column name to color points by
            title: Map title
            
        Returns:
            Plotly Figure object
        """
        if df.empty:
            return self._create_empty_map(title)
        
        # Prepare hover text
        hover_text = self._create_hover_text(df)
        
        # Create scatter mapbox
        fig = px.scatter_mapbox(
            df,
            lat='latitude',
            lon='longitude',
            color=color_by,
            size=[10] * len(df),  # Fixed size for visibility
            hover_data={
                'latitude': ':.2f',
                'longitude': ':.2f',
                color_by: ':.2f'
            },
            color_continuous_scale='Viridis',
            title=title,
            zoom=3
        )
        
        # Update layout
        fig.update_layout(
            mapbox_style=self.default_mapbox_style,
            height=600,
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )
        
        return fig
    
    def create_density_heatmap(
        self,
        df: pd.DataFrame,
        title: str = "ARGO Float Density"
    ) -> go.Figure:
        """
        Create heatmap showing concentration of measurements.
        Useful for identifying data-rich regions.
        """
        if df.empty:
            return self._create_empty_map(title)
        
        fig = go.Figure(go.Densitymapbox(
            lat=df['latitude'],
            lon=df['longitude'],
            radius=20,
            colorscale='Hot',
            showscale=True,
            hoverinfo='none'
        ))
        
        fig.update_layout(
            mapbox_style=self.default_mapbox_style,
            mapbox=dict(
                center=dict(
                    lat=df['latitude'].mean(),
                    lon=df['longitude'].mean()
                ),
                zoom=3
            ),
            title=title,
            height=600,
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )
        
        return fig
    
    def create_time_animated_map(
        self,
        df: pd.DataFrame,
        time_column: str = 'timestamp',
        title: str = "ARGO Float Trajectories Over Time"
    ) -> go.Figure:
        """
        Create animated map showing float movements over time.
        Great for visualizing temporal patterns.
        """
        if df.empty or time_column not in df.columns:
            return self._create_empty_map(title)
        
        # Convert timestamp to datetime
        df[time_column] = pd.to_datetime(df[time_column])
        df = df.sort_values(time_column)
        
        # Create time bins (monthly)
        df['time_period'] = df[time_column].dt.to_period('M').astype(str)
        
        fig = px.scatter_mapbox(
            df,
            lat='latitude',
            lon='longitude',
            animation_frame='time_period',
            color='temperature',
            size=[10] * len(df),
            hover_data=['latitude', 'longitude', 'temperature', 'salinity'],
            color_continuous_scale='RdYlBu_r',
            title=title,
            zoom=3
        )
        
        fig.update_layout(
            mapbox_style=self.default_mapbox_style,
            height=600,
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )
        
        return fig
    
    def _create_hover_text(self, df: pd.DataFrame) -> List[str]:
        """Create informative hover text for each point"""
        hover_texts = []
        for _, row in df.iterrows():
            text = f"Lat: {row['latitude']:.2f}°N<br>"
            text += f"Lon: {row['longitude']:.2f}°E<br>"
            if 'temperature' in row:
                text += f"Temp: {row['temperature']:.2f}°C<br>"
            if 'salinity' in row:
                text += f"Salinity: {row['salinity']:.2f} PSU"
            hover_texts.append(text)
        return hover_texts
    
    def _create_empty_map(self, title: str) -> go.Figure:
        """Create empty map with message"""
        fig = go.Figure(go.Scattermapbox())
        fig.update_layout(
            mapbox_style=self.default_mapbox_style,
            mapbox=dict(center=dict(lat=0, lon=70), zoom=2),
            title=title,
            height=600,
            annotations=[
                dict(
                    text="No data to display",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5
                )
            ]
        )
        return fig

# Usage
if __name__ == "__main__":
    # Test with sample data
    sample_df = pd.DataFrame({
        'latitude': [10.5, 11.2, 12.8, 13.5],
        'longitude': [75.3, 76.1, 77.5, 78.2],
        'temperature': [28.5, 27.8, 29.2, 28.9],
        'salinity': [34.5, 34.7, 34.3, 34.6],
        'timestamp': pd.date_range('2023-01-01', periods=4, freq='M')
    })
    
    visualizer = MapVisualizer()
    fig = visualizer.create_float_trajectory_map(sample_df)
    fig.show()
