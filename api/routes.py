"""
Enhanced API routes with caching and batch operations
"""

from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import text
import asyncio

from database.db_setup import DatabaseSetup
from rag_engine.query_processor import QueryProcessor
from advanced_analytics.profile_analytics import AdvancedProfileAnalytics

router = APIRouter(prefix="/api/v1", tags=["FloatChat API"])

# Initialize components
db_setup = DatabaseSetup()
query_processor = QueryProcessor()
analytics = AdvancedProfileAnalytics()

# In-memory cache (simple implementation)
query_cache = {}

class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    limit: int = 1000
    use_cache: bool = True

class BatchQueryRequest(BaseModel):
    """Batch query request"""
    queries: List[str]
    parallel: bool = False

class SavedQuery(BaseModel):
    """Saved query model"""
    name: str
    description: str
    query: str
    tags: List[str] = []

class ExportRequest(BaseModel):
    """Export request model"""
    format: str = "csv"  # csv, json, parquet, netcdf
    include_analysis: bool = False

# Regular API Routes

@router.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FloatChat API"
    }

@router.post("/query")
async def query_data(request: QueryRequest):
    """Execute a query with optional caching"""
    
    # Check cache
    if request.use_cache and request.query in query_cache:
        cached = query_cache[request.query]
        if (datetime.now() - cached['timestamp']).seconds < 3600:  # 1 hour cache
            return {
                "success": True,
                "data": cached['result'],
                "cached": True,
                "cached_at": cached['timestamp'].isoformat()
            }
    
    # Execute query
    try:
        result = query_processor.process_query(request.query)
        
        if result['success']:
            # Cache result
            query_cache[request.query] = {
                'result': result['results'].to_dict('records')[:request.limit],
                'timestamp': datetime.now()
            }
            
            return {
                "success": True,
                "data": result['results'].to_dict('records')[:request.limit],
                "record_count": len(result['results']),
                "execution_time": result.get('execution_time', 0),
                "cached": False
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-query")
async def batch_query(request: BatchQueryRequest, background_tasks: BackgroundTasks):
    """Execute multiple queries"""
    
    results = []
    
    if request.parallel:
        # Execute in parallel
        tasks = [
            query_processor.process_query(q)
            for q in request.queries
        ]
        results = await asyncio.gather(*tasks)
    else:
        # Execute sequentially
        for query in request.queries:
            result = query_processor.process_query(query)
            results.append(result)
    
    return {
        "success": True,
        "queries_executed": len(request.queries),
        "results": [
            {
                "query": request.queries[i],
                "success": results[i]['success'],
                "record_count": len(results[i]['results']) if results[i]['success'] else 0,
                "error": results[i].get('error') if not results[i]['success'] else None
            }
            for i in range(len(request.queries))
        ]
    }

@router.get("/floats/{float_id}")
async def get_float_info(float_id: str):
    """Get information about a specific float"""
    session = db_setup.get_session()
    
    try:
        query = text(f"""
            SELECT 
                float_id,
                COUNT(*) as total_measurements,
                COUNT(DISTINCT cycle_number) as total_cycles,
                MIN(timestamp) as first_measurement,
                MAX(timestamp) as last_measurement,
                AVG(latitude) as avg_latitude,
                AVG(longitude) as avg_longitude,
                MIN(temperature) as min_temp,
                MAX(temperature) as max_temp,
                AVG(temperature) as avg_temp,
                MIN(salinity) as min_sal,
                MAX(salinity) as max_sal,
                AVG(salinity) as avg_sal
            FROM argo_profiles
            WHERE float_id = '{float_id}'
            GROUP BY float_id
        """)
        
        result = session.execute(query).fetchone()
        session.close()
        
        if result:
            return {
                "float_id": result[0],
                "total_measurements": result[1],
                "total_cycles": result[2],
                "first_measurement": result[3].isoformat() if result[3] else None,
                "last_measurement": result[4].isoformat() if result[4] else None,
                "avg_location": {"lat": float(result[5]), "lon": float(result[6])},
                "temperature": {
                    "min": float(result[7]),
                    "max": float(result[8]),
                    "mean": float(result[9])
                },
                "salinity": {
                    "min": float(result[10]),
                    "max": float(result[11]),
                    "mean": float(result[12])
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Float not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regions")
async def get_regions():
    """Get available ocean regions"""
    session = db_setup.get_session()
    
    try:
        query = text("""
            SELECT DISTINCT ocean_region, COUNT(*) as measurements
            FROM argo_profiles
            WHERE ocean_region IS NOT NULL
            GROUP BY ocean_region
            ORDER BY measurements DESC
        """)
        
        results = session.execute(query).fetchall()
        session.close()
        
        return {
            "regions": [
                {
                    "name": row[0],
                    "measurements": row[1]
                }
                for row in results
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/thermocline")
async def analyze_thermocline(query: str):
    """Analyze thermocline for query results"""
    try:
        result = query_processor.process_query(query)
        
        if result['success']:
            thermocline = analytics.calculate_thermocline(result['results'])
            return {
                "success": True,
                "thermocline": thermocline,
                "record_count": len(result['results'])
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/water-masses")
async def identify_water_masses(query: str):
    """Identify water masses in query results"""
    try:
        result = query_processor.process_query(query)
        
        if result['success']:
            water_masses = analytics.identify_water_masses(result['results'])
            return {
                "success": True,
                "water_masses": water_masses,
                "record_count": len(result['results'])
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/trends")
async def analyze_trends(region: str, parameter: str, days: int = 90):
    """Analyze trends in a region"""
    try:
        trend = analytics.trend_analysis(region, parameter, days)
        return {"success": True, "trend_analysis": trend}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def database_statistics():
    """Get database statistics"""
    session = db_setup.get_session()
    
    try:
        from database.models import ArgoProfile
        
        total_records = session.query(ArgoProfile).count()
        unique_floats = session.query(ArgoProfile.float_id).distinct().count()
        
        query = text("""
            SELECT 
                MIN(timestamp) as earliest,
                MAX(timestamp) as latest,
                COUNT(DISTINCT ocean_region) as regions,
                COUNT(DISTINCT cycle_number) as max_cycles,
                AVG(temperature) as avg_temp,
                AVG(salinity) as avg_sal
            FROM argo_profiles
        """)
        
        result = session.execute(query).fetchone()
        session.close()
        
        return {
            "total_records": total_records,
            "unique_floats": unique_floats,
            "date_range": {
                "earliest": result[0].isoformat() if result[0] else None,
                "latest": result[1].isoformat() if result[1] else None
            },
            "regions_covered": result[2],
            "cycles": result[3],
            "average_temperature": float(result[4]),
            "average_salinity": float(result[5])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_data(query: str, format_type: str = "csv"):
    """Export query results in various formats"""
    try:
        result = query_processor.process_query(query)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        df = result['results']
        
        if format_type == "csv":
            return {
                "format": "csv",
                "data": df.to_csv(index=False),
                "records": len(df)
            }
        
        elif format_type == "json":
            return {
                "format": "json",
                "data": df.to_json(orient='records'),
                "records": len(df)
            }
        
        elif format_type == "parquet":
            # Would require pyarrow
            parquet_bytes = df.to_parquet(index=False)
            return {
                "format": "parquet",
                "data": parquet_bytes.hex(),
                "records": len(df)
            }
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))