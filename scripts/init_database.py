#!/usr/bin/env python3
"""
Initialize the complete FloatChat database.
Run this script once before starting the application.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_setup import DatabaseSetup
from data_processing.netcdf_extractor import NetCDFExtractor
from data_processing.data_loader import DataLoader
from data_processing.profile_summarizer import ProfileSummarizer
from vector_store.embeddings import EmbeddingGenerator
from vector_store.vector_db import FAISSVectorStore
from database.models import ProfileSummary
import os

def main():
    print("="*60)
    print("FloatChat Database Initialization")
    print("="*60)
    
    # Step 1: Create database tables
    print("\n📦 Step 1: Creating database tables...")
    db_setup = DatabaseSetup()
    
    if not db_setup.test_connection():
        print("❌ Database connection failed. Check your .env file.")
        return
    
    db_setup.create_tables()
    
    # Step 2: Load data from CSV
    print("\n📊 Step 2: Loading data from CSV...")
    loader = DataLoader()
    
    csv_path = "data/processed/argo_profiles.csv"
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        print("Please run data extraction first or provide the CSV file.")
        return
    
    loader.load_csv_to_db(csv_path)
    record_count = loader.get_record_count()
    print(f"✅ Loaded {record_count} records")
    
    # Step 3: Generate profile summaries
    print("\n📝 Step 3: Generating profile summaries...")
    summarizer = ProfileSummarizer()
    summarizer.generate_summaries()
    
    # Step 4: Create vector embeddings
    print("\n🧠 Step 4: Creating vector embeddings...")
    embedding_generator = EmbeddingGenerator()
    
    # Get all profile summaries
    session = db_setup.get_session()
    summaries = session.query(ProfileSummary).all()
    
    if not summaries:
        print("❌ No profile summaries found")
        session.close()
        return
    
    print(f"Found {len(summaries)} profile summaries")
    
    # Generate embeddings
    texts = [s.summary_text for s in summaries]
    embeddings = embedding_generator.generate_embeddings(texts)
    
    # Create metadata
    metadata = [
        {
            'id': s.id,
            'float_id': s.float_id,
            'cycle_number': s.cycle_number,
            'summary_text': s.summary_text,
            'latitude': s.latitude,
            'longitude': s.longitude,
            'timestamp': s.timestamp.isoformat() if s.timestamp else None
        }
        for s in summaries
    ]
    
    session.close()
    
    # Step 5: Create and populate vector store
    print("\n🗄️ Step 5: Creating vector store...")
    vector_store = FAISSVectorStore(dimension=embeddings.shape[1])
    vector_store.create_index()
    vector_store.add_vectors(embeddings, metadata)
    vector_store.save()
    
    print("\n" + "="*60)
    print("✅ Database initialization complete!")
    print("="*60)
    print(f"""
Summary:
- Database records: {record_count}
- Profile summaries: {len(summaries)}
- Vector embeddings: {embeddings.shape[0]}

You can now run the FloatChat application:
    streamlit run streamlit_app/app.py
    """)

if __name__ == "__main__":
    main()
