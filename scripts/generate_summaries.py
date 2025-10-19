#!/usr/bin/env python3
"""
Generate text summaries for ARGO profiles and populate vector store.

This script:
1. Reads ARGO profiles from database
2. Generates text summaries for each unique profile
3. Stores summaries in profile_summaries table
4. Creates vector embeddings
5. Populates FAISS vector store
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_setup import DatabaseSetup
from database.models import ArgoProfile, ProfileSummary
from vector_store.embeddings import EmbeddingGenerator
from vector_store.vector_db import FAISSVectorStore
from sqlalchemy import text
import pandas as pd
from datetime import datetime


class ProfileSummarizer:
    """Generate text summaries for ARGO profiles"""
    
    def __init__(self):
        self.db_setup = DatabaseSetup()
    
    def generate_summary_text(self, profile_data: dict) -> str:
        """
        Generate human-readable summary text for a profile.
        This text will be used for semantic search.
        """
        summary_parts = []
        
        # Location
        lat = profile_data['latitude']
        lon = profile_data['longitude']
        lat_dir = 'N' if lat >= 0 else 'S'
        lon_dir = 'E' if lon >= 0 else 'W'
        summary_parts.append(
            f"ARGO float profile at {abs(lat):.2f}°{lat_dir}, {abs(lon):.2f}°{lon_dir}"
        )
        
        # Date
        if profile_data.get('timestamp'):
            date_str = profile_data['timestamp'].strftime('%B %Y')
            summary_parts.append(f"measured in {date_str}")
        
        # Ocean region (approximate)
        region = self._determine_region(lat, lon)
        if region:
            summary_parts.append(f"in the {region}")
        
        # Temperature statistics
        if profile_data.get('avg_temp') is not None:
            summary_parts.append(
                f"Temperature ranges from {profile_data['min_temp']:.2f}°C to "
                f"{profile_data['max_temp']:.2f}°C (avg {profile_data['avg_temp']:.2f}°C)"
            )
        
        # Salinity statistics
        if profile_data.get('avg_salinity') is not None and profile_data.get('min_salinity') is not None:
            summary_parts.append(
                f"Salinity ranges from {profile_data['min_salinity']:.2f} to "
                f"{profile_data['max_salinity']:.2f} PSU (avg {profile_data['avg_salinity']:.2f} PSU)"
            )
        
        # Depth range
        if profile_data.get('max_pressure') is not None:
            max_depth = profile_data['max_pressure']
            summary_parts.append(f"Depth coverage up to {max_depth:.0f} dbar")
        
        # Measurement count
        if profile_data.get('measurement_count'):
            summary_parts.append(
                f"Contains {profile_data['measurement_count']} measurements"
            )
        
        # Float ID
        if profile_data.get('float_id'):
            summary_parts.append(f"Float ID: {profile_data['float_id']}")
        
        return ". ".join(summary_parts) + "."
    
    def _determine_region(self, lat: float, lon: float) -> str:
        """Determine ocean region based on coordinates"""
        # Indian Ocean regions
        if 40 <= lon <= 100:
            if 5 <= lat <= 30:
                if 40 <= lon <= 80:
                    return "Arabian Sea"
                elif 80 <= lon <= 100:
                    return "Bay of Bengal"
            elif -10 <= lat <= 5:
                return "Equatorial Indian Ocean"
            elif -50 <= lat <= -10:
                return "Southern Indian Ocean"
        
        # Pacific Ocean
        if 100 <= lon <= 180 or -180 <= lon <= -70:
            if -10 <= lat <= 10:
                return "Equatorial Pacific Ocean"
            elif 10 <= lat <= 50:
                return "North Pacific Ocean"
            elif -50 <= lat <= -10:
                return "South Pacific Ocean"
        
        # Atlantic Ocean
        if -70 <= lon <= 20:
            if -10 <= lat <= 10:
                return "Equatorial Atlantic Ocean"
            elif 10 <= lat <= 50:
                return "North Atlantic Ocean"
            elif -50 <= lat <= -10:
                return "South Atlantic Ocean"
        
        return "Ocean"
    
    def generate_all_summaries(self):
        """Generate summaries for all unique profiles in database"""
        print("\n" + "="*60)
        print("📝 Generating Profile Summaries")
        print("="*60)
        
        with self.db_setup.get_session() as session:
            # Check if we have float_id data
            has_float_id = session.execute(text(
                "SELECT COUNT(*) FROM argo_profiles WHERE float_id IS NOT NULL"
            )).scalar()
            
            if has_float_id > 0:
                # Group by float_id and cycle_number if available
                print("📌 Grouping by float_id and cycle_number")
                query = text("""
                    SELECT 
                        float_id,
                        cycle_number,
                        AVG(latitude) as latitude,
                        AVG(longitude) as longitude,
                        MIN(timestamp) as timestamp,
                        AVG(temperature) as avg_temp,
                        MIN(temperature) as min_temp,
                        MAX(temperature) as max_temp,
                        AVG(salinity) as avg_salinity,
                        MIN(salinity) as min_salinity,
                        MAX(salinity) as max_salinity,
                        MAX(pressure) as max_pressure,
                        COUNT(*) as measurement_count
                    FROM argo_profiles
                    WHERE float_id IS NOT NULL
                    GROUP BY float_id, cycle_number
                    ORDER BY float_id, cycle_number
                """)
            else:
                # Group by location and date if no float_id
                print("📌 Grouping by location and date (no float_id available)")
                query = text("""
                    SELECT 
                        NULL as float_id,
                        NULL as cycle_number,
                        ROUND(CAST(latitude AS numeric), 2) as latitude,
                        ROUND(CAST(longitude AS numeric), 2) as longitude,
                        DATE(timestamp) as timestamp,
                        AVG(temperature) as avg_temp,
                        MIN(temperature) as min_temp,
                        MAX(temperature) as max_temp,
                        AVG(salinity) as avg_salinity,
                        MIN(salinity) as min_salinity,
                        MAX(salinity) as max_salinity,
                        MAX(pressure) as max_pressure,
                        COUNT(*) as measurement_count
                    FROM argo_profiles
                    GROUP BY 
                        ROUND(CAST(latitude AS numeric), 2),
                        ROUND(CAST(longitude AS numeric), 2),
                        DATE(timestamp)
                    ORDER BY timestamp DESC
                """)
            
            results = session.execute(query).fetchall()
            
            print(f"✅ Found {len(results)} unique profiles")
            
            if len(results) == 0:
                print("❌ No profiles to summarize")
                return 0
            
            # Clear existing summaries
            session.execute(text("DELETE FROM profile_summaries"))
            session.commit()
            print("🗑️ Cleared old summaries")
            
            # Generate summaries
            summaries_created = 0
            
            for row in results:
                profile_data = {
                    'float_id': row.float_id,
                    'cycle_number': row.cycle_number,
                    'latitude': float(row.latitude),
                    'longitude': float(row.longitude),
                    'timestamp': row.timestamp,
                    'avg_temp': float(row.avg_temp) if row.avg_temp else None,
                    'min_temp': float(row.min_temp) if row.min_temp else None,
                    'max_temp': float(row.max_temp) if row.max_temp else None,
                    'avg_salinity': float(row.avg_salinity) if row.avg_salinity else None,
                    'min_salinity': float(row.min_salinity) if row.min_salinity else None,
                    'max_salinity': float(row.max_salinity) if row.max_salinity else None,
                    'max_pressure': float(row.max_pressure) if row.max_pressure else None,
                    'measurement_count': int(row.measurement_count)
                }
                
                # Generate summary text
                summary_text = self.generate_summary_text(profile_data)
                
                # Create ProfileSummary object
                summary = ProfileSummary(
                    float_id=profile_data['float_id'],
                    cycle_number=profile_data['cycle_number'],
                    latitude=profile_data['latitude'],
                    longitude=profile_data['longitude'],
                    timestamp=profile_data['timestamp'],
                    summary_text=summary_text
                )
                
                session.add(summary)
                summaries_created += 1
                
                if summaries_created % 10 == 0:
                    print(f"   Generated {summaries_created}/{len(results)} summaries...")
            
            session.commit()
            print(f"✅ Created {summaries_created} summaries")
            
            return summaries_created


def populate_vector_store():
    """Generate embeddings and populate FAISS vector store"""
    print("\n" + "="*60)
    print("🔄 Populating Vector Store")
    print("="*60)
    
    db_setup = DatabaseSetup()
    
    # Get summaries from database
    with db_setup.get_session() as session:
        summaries = session.query(ProfileSummary).all()
    
    if not summaries:
        print("❌ No summaries found in database")
        return False
    
    print(f"📊 Processing {len(summaries)} summaries...")
    
    # Generate embeddings
    embedding_generator = EmbeddingGenerator()
    texts = [s.summary_text for s in summaries]
    
    print("🔄 Generating embeddings (this may take a minute)...")
    embeddings = embedding_generator.generate_embeddings(texts)
    print(f"✅ Generated {len(embeddings)} embeddings")
    
    # Create metadata
    metadata = [
        {
            'id': s.id,
            'float_id': s.float_id,
            'cycle_number': s.cycle_number,
            'summary_text': s.summary_text,
            'latitude': s.latitude,
            'longitude': s.longitude
        }
        for s in summaries
    ]
    
    # Create and save vector store
    vector_store = FAISSVectorStore()
    vector_store.create_index()
    vector_store.add_vectors(embeddings, metadata)
    vector_store.save()
    
    print(f"✅ Vector store saved with {len(embeddings)} vectors")
    
    # Verify
    vector_store_check = FAISSVectorStore()
    vector_store_check.load()
    print(f"✅ Verification: Vector store loaded successfully")
    
    return True


def main():
    """Complete workflow: Generate summaries and populate vector store"""
    print("\n" + "="*70)
    print("🚀 ARGO Profile Summary & Vector Store Population")
    print("="*70)
    
    # Step 1: Generate summaries
    summarizer = ProfileSummarizer()
    summary_count = summarizer.generate_all_summaries()
    
    if summary_count == 0:
        print("\n❌ No summaries generated. Exiting.")
        return
    
    # Step 2: Populate vector store
    success = populate_vector_store()
    
    if success:
        print("\n" + "="*70)
        print("✨ SUCCESS! Vector Store Ready")
        print("="*70)
        print("\n📊 Summary:")
        print(f"   • Profile summaries: {summary_count}")
        print(f"   • Vector embeddings: {summary_count}")
        print(f"   • Semantic search: ENABLED ✅")
        print("\n🎯 Your RAG system is now fully functional!")
        print("   Try queries like:")
        print("   - 'Find profiles in Arabian Sea'")
        print("   - 'Show me warm water profiles'")
        print("   - 'What data is available in Bay of Bengal?'")
        print("\n" + "="*70)
    else:
        print("\n❌ Vector store population failed")


if __name__ == "__main__":
    main()
