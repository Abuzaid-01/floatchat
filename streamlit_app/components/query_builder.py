"""
Advanced query builder with visual filters
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional

class QueryBuilder:
    """Visual SQL query builder"""
    
    def __init__(self):
        self.filters = []
        self.selected_columns = []
    
    def render(self) -> str:
        """Render query builder and return SQL"""
        
        st.subheader("🏗️ Visual Query Builder")
        
        # Column selection
        st.markdown("### 1️⃣ Select Columns")
        all_columns = [
            "latitude", "longitude", "timestamp", "pressure", 
            "temperature", "salinity", "dissolved_oxygen", 
            "chlorophyll", "ph", "float_id", "cycle_number"
        ]
        
        selected_cols = st.multiselect(
            "Columns to retrieve",
            all_columns,
            default=["latitude", "longitude", "temperature", "salinity"]
        )
        
        # Filters
        st.markdown("### 2️⃣ Add Filters")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            filter_column = st.selectbox("Filter by", all_columns)
        
        with col2:
            filter_type = st.selectbox(
                "Condition",
                ["equals", "greater than", "less than", "between", "in range"]
            )
        
        with col3:
            add_filter = st.button("➕ Add Filter")
        
        # Geographic filter
        st.markdown("### 3️⃣ Geographic Bounds")
        
        geo_col1, geo_col2 = st.columns(2)
        
        with geo_col1:
            lat_min = st.number_input("Min Latitude", -90.0, 90.0, -90.0)
            lon_min = st.number_input("Min Longitude", -180.0, 180.0, -180.0)
        
        with geo_col2:
            lat_max = st.number_input("Max Latitude", -90.0, 90.0, 90.0)
            lon_max = st.number_input("Max Longitude", -180.0, 180.0, 180.0)
        
        # Time filter
        st.markdown("### 4️⃣ Time Range")
        
        time_col1, time_col2 = st.columns(2)
        
        with time_col1:
            start_date = st.date_input("Start Date")
        
        with time_col2:
            end_date = st.date_input("End Date")
        
        # Build SQL
        sql = self._build_sql(
            selected_cols, 
            lat_min, lat_max, 
            lon_min, lon_max,
            start_date, end_date
        )
        
        # Display generated SQL
        st.markdown("### 📝 Generated SQL")
        st.code(sql, language="sql")
        
        # Limit
        limit = st.slider("Results Limit", 100, 10000, 1000)
        
        if st.button("▶️ Execute Query", type="primary"):
            return sql
        
        return None
    
    def _build_sql(self, columns: List[str], lat_min: float, lat_max: float,
                   lon_min: float, lon_max: float, start_date, end_date) -> str:
        """Build SQL query from filters"""
        
        col_str = ", ".join(columns) if columns else "*"
        
        sql = f"SELECT {col_str} FROM argo_profiles WHERE 1=1"
        
        # Geographic filter
        sql += f" AND latitude BETWEEN {lat_min} AND {lat_max}"
        sql += f" AND longitude BETWEEN {lon_min} AND {lon_max}"
        
        # Time filter
        sql += f" AND timestamp >= '{start_date}' AND timestamp <= '{end_date}'"
        
        # Quality control
        sql += " AND temp_qc IN (1,2) AND sal_qc IN (1,2)"
        
        sql += " ORDER BY timestamp DESC LIMIT 1000;"
        
        return sql