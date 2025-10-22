"""
Advanced oceanographic profile analytics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats
from database.db_setup import DatabaseSetup
from sqlalchemy import text

class AdvancedProfileAnalytics:
    """Advanced analysis tools for ARGO profiles"""
    
    def __init__(self):
        self.db_setup = DatabaseSetup()
    
    def calculate_thermocline(self, df: pd.DataFrame) -> Dict:
        """
        Calculate thermocline characteristics
        - Depth (pressure)
        - Strength (temperature gradient)
        - Width
        """
        df = df.sort_values('pressure')
        
        # Calculate temperature gradient
        df['temp_gradient'] = df['temperature'].diff() / df['pressure'].diff()
        
        # Find thermocline (maximum gradient)
        max_grad_idx = df['temp_gradient'].abs().idxmax()
        thermocline_depth = df.loc[max_grad_idx, 'pressure']
        thermocline_strength = abs(df.loc[max_grad_idx, 'temp_gradient'])
        
        return {
            'thermocline_depth_dbar': float(thermocline_depth),
            'thermocline_strength': float(thermocline_strength),
            'surface_temp': float(df['temperature'].iloc[0]),
            'deep_temp': float(df['temperature'].iloc[-1])
        }
    
    def calculate_mixed_layer_depth(self, df: pd.DataFrame, threshold: float = 0.5) -> float:
        """
        Calculate Mixed Layer Depth (MLD)
        Depth where temperature decreases by threshold from surface
        """
        df = df.sort_values('pressure')
        surface_temp = df['temperature'].iloc[0]
        mld_mask = df['temperature'] < (surface_temp - threshold)
        
        if mld_mask.any():
            return float(df[mld_mask]['pressure'].iloc[0])
        else:
            return float(df['pressure'].max())
    
    def identify_water_masses(self, df: pd.DataFrame) -> List[Dict]:
        """
        Identify water masses using T-S characteristics
        """
        water_masses = []
        
        if 'salinity' not in df.columns:
            return water_masses
        
        df = df.sort_values('pressure')
        
        # Temperature-Salinity thresholds for common water masses
        thresholds = {
            'Tropical Surface Water': {'temp_min': 20, 'sal_min': 34.5, 'sal_max': 35.5},
            'Central Water': {'temp_min': 10, 'temp_max': 20, 'sal_min': 34.2, 'sal_max': 35.5},
            'Antarctic Intermediate Water': {'temp_max': 5, 'sal_min': 33.8, 'sal_max': 34.4},
            'Deep Water': {'temp_max': 5, 'sal_min': 34.6}
        }
        
        for wm, criteria in thresholds.items():
            mask = pd.Series([True] * len(df))
            for key, val in criteria.items():
                if key == 'temp_min':
                    mask &= df['temperature'] >= val
                elif key == 'temp_max':
                    mask &= df['temperature'] <= val
                elif key == 'sal_min':
                    mask &= df['salinity'] >= val
                elif key == 'sal_max':
                    mask &= df['salinity'] <= val
            
            if mask.any():
                subset = df[mask]
                water_masses.append({
                    'water_mass': wm,
                    'depth_range': (float(subset['pressure'].min()), float(subset['pressure'].max())),
                    'count': int(mask.sum())
                })
        
        return water_masses
    
    def calculate_oxygen_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate dissolved oxygen statistics"""
        if 'dissolved_oxygen' not in df.columns:
            return {}
        
        do = df['dissolved_oxygen'].dropna()
        
        if len(do) == 0:
            return {}
        
        return {
            'min_oxygen': float(do.min()),
            'max_oxygen': float(do.max()),
            'mean_oxygen': float(do.mean()),
            'std_oxygen': float(do.std()),
            'oxygen_minimum_zone': float(do[do == do.min()].index[0]) if len(do) > 0 else None
        }
    
    def detect_anomalies(self, df: pd.DataFrame, parameter: str = 'temperature',
                        threshold: float = 2.0) -> List[Dict]:
        """
        Detect anomalies using statistical methods
        threshold: number of standard deviations
        """
        df = df.copy()
        
        if parameter not in df.columns:
            return []
        
        data = df[parameter].dropna()
        mean = data.mean()
        std = data.std()
        
        df['is_anomaly'] = np.abs(df[parameter] - mean) > (threshold * std)
        
        anomalies = []
        for idx, row in df[df['is_anomaly']].iterrows():
            anomalies.append({
                'depth': float(row['pressure']) if 'pressure' in row else None,
                'value': float(row[parameter]),
                'deviation_std': float((row[parameter] - mean) / std),
                'timestamp': row['timestamp'] if 'timestamp' in row else None
            })
        
        return anomalies
    
    def regional_comparison(self, region1: str, region2: str,
                           parameter: str = 'temperature') -> Dict:
        """Compare parameters between regions"""
        session = self.db_setup.get_session()
        
        for region in [region1, region2]:
            query = text(f"""
            SELECT {parameter}, COUNT(*) as count
            FROM argo_profiles
            WHERE ocean_region ILIKE '%{region}%'
              AND {parameter} IS NOT NULL
            GROUP BY ROUND({parameter}, 1)
            ORDER BY {parameter}
            """)
            
            df = pd.read_sql(query, session.bind)
        
        session.close()
        
        return {"region1": region1, "region2": region2, "parameter": parameter}
    
    def trend_analysis(self, region: str, parameter: str, days: int = 90) -> Dict:
        """Analyze trends over time"""
        session = self.db_setup.get_session()
        
        query = text(f"""
        SELECT DATE_TRUNC('week', timestamp) as week,
               AVG({parameter}) as avg_value,
               COUNT(*) as measurements
        FROM argo_profiles
        WHERE ocean_region ILIKE '%{region}%'
          AND timestamp >= CURRENT_DATE - INTERVAL '{days} days'
          AND {parameter} IS NOT NULL
        GROUP BY DATE_TRUNC('week', timestamp)
        ORDER BY week
        """)
        
        df = pd.read_sql(query, session.bind)
        session.close()
        
        if len(df) < 2:
            return {"success": False, "message": "Insufficient data"}
        
        # Calculate trend
        x = np.arange(len(df))
        y = df['avg_value'].values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return {
            "region": region,
            "parameter": parameter,
            "trend": "increasing" if slope > 0 else "decreasing",
            "slope": float(slope),
            "r_squared": float(r_value ** 2),
            "significant": p_value < 0.05,
            "weeks_analyzed": len(df)
        }