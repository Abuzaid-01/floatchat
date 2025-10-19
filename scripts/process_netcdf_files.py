"""
Script to process NetCDF files and store both raw and processed data.

This script:
1. Keeps raw NetCDF files in data/raw/
2. Extracts data and saves CSV in data/processed/
3. Loads CSV data into PostgreSQL database
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from data_processing.netcdf_extractor import NetCDFExtractor
from data_processing.data_loader import DataLoader
from database.db_setup import DatabaseSetup


def process_single_netcdf(netcdf_path: str, output_csv: str = None):
    """
    Process a single NetCDF file
    
    Args:
        netcdf_path: Path to NetCDF file
        output_csv: Optional path for output CSV (default: data/processed/)
    """
    print(f"\n{'='*60}")
    print(f"Processing: {netcdf_path}")
    print(f"{'='*60}")
    
    # Extract data from NetCDF
    extractor = NetCDFExtractor(netcdf_path)
    if not extractor.load_netcdf():
        print("❌ Failed to load NetCDF file")
        return False
    
    # Extract profiles
    df = extractor.extract_profiles()
    
    if df.empty:
        print("⚠️ No data extracted")
        return False
    
    # Determine output path
    if output_csv is None:
        filename = Path(netcdf_path).stem + ".csv"
        output_csv = Path(__file__).parent.parent / "data" / "processed" / filename
    
    # Save to CSV
    df.to_csv(output_csv, index=False)
    print(f"✅ Saved CSV: {output_csv}")
    print(f"   Records: {len(df)}")
    
    return output_csv


def process_all_netcdf_files():
    """Process all NetCDF files in data/raw/ directory"""
    raw_data_dir = Path(__file__).parent.parent / "data" / "raw"
    
    # Find all NetCDF files
    netcdf_files = list(raw_data_dir.glob("*.nc"))
    
    print(f"\n🔍 Found {len(netcdf_files)} NetCDF files")
    
    if not netcdf_files:
        print("⚠️ No NetCDF files found in data/raw/")
        print("   Please add .nc files to FloatChat/data/raw/")
        return
    
    processed_files = []
    
    for nc_file in netcdf_files:
        try:
            csv_path = process_single_netcdf(str(nc_file))
            if csv_path:
                processed_files.append(csv_path)
        except Exception as e:
            print(f"❌ Error processing {nc_file.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Processed {len(processed_files)} files successfully")
    print(f"{'='*60}")
    
    return processed_files


def load_csv_to_database(csv_path: str):
    """Load a CSV file into PostgreSQL database"""
    print(f"\n📊 Loading data into database...")
    
    loader = DataLoader()
    success = loader.load_csv_to_db(csv_path)
    
    if success:
        print(f"✅ Data loaded to database successfully")
    else:
        print(f"❌ Failed to load data to database")
    
    return success


def load_all_csv_to_database():
    """Load all CSV files from data/processed/ into database"""
    processed_dir = Path(__file__).parent.parent / "data" / "processed"
    csv_files = list(processed_dir.glob("*.csv"))
    
    print(f"\n🔍 Found {len(csv_files)} CSV files")
    
    total_loaded = 0
    
    for csv_file in csv_files:
        if csv_file.name == '.gitkeep':
            continue
        
        print(f"\n{'='*60}")
        print(f"Loading: {csv_file.name}")
        print(f"{'='*60}")
        
        try:
            if load_csv_to_database(str(csv_file)):
                total_loaded += 1
        except Exception as e:
            print(f"❌ Error loading {csv_file.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Loaded {total_loaded}/{len(csv_files)} files to database")
    print(f"{'='*60}")


def add_new_data(netcdf_path: str, load_to_db: bool = True):
    """
    Complete workflow: Add new NetCDF file and load to database
    
    Args:
        netcdf_path: Path to the NetCDF file
        load_to_db: Whether to load into database (default: True)
    
    Usage:
        python scripts/process_netcdf_files.py path/to/your/file.nc
    """
    import shutil
    
    # Copy NetCDF to raw directory
    raw_dir = Path(__file__).parent.parent / "data" / "raw"
    nc_filename = Path(netcdf_path).name
    destination = raw_dir / nc_filename
    
    print(f"\n📁 Copying NetCDF file to data/raw/...")
    shutil.copy(netcdf_path, destination)
    print(f"✅ Copied: {destination}")
    
    # Process the file
    csv_path = process_single_netcdf(str(destination))
    
    if csv_path and load_to_db:
        load_csv_to_database(str(csv_path))
    
    print(f"\n{'='*60}")
    print(f"✨ Complete! Your data is stored:")
    print(f"   📄 Raw NetCDF: {destination}")
    print(f"   📊 Processed CSV: {csv_path}")
    if load_to_db:
        print(f"   🗄️ Database: Loaded")
    print(f"{'='*60}")


def show_data_summary():
    """Show summary of stored data"""
    raw_dir = Path(__file__).parent.parent / "data" / "raw"
    processed_dir = Path(__file__).parent.parent / "data" / "processed"
    
    raw_files = list(raw_dir.glob("*.nc"))
    csv_files = [f for f in processed_dir.glob("*.csv") if f.name != '.gitkeep']
    
    print(f"\n{'='*60}")
    print(f"📊 DATA STORAGE SUMMARY")
    print(f"{'='*60}")
    print(f"\n📁 Raw NetCDF Files ({len(raw_files)}):")
    for f in raw_files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"   - {f.name} ({size_mb:.2f} MB)")
    
    print(f"\n📊 Processed CSV Files ({len(csv_files)}):")
    for f in csv_files:
        size_kb = f.stat().st_size / 1024
        print(f"   - {f.name} ({size_kb:.2f} KB)")
    
    # Database summary
    try:
        db = DatabaseSetup()
        from sqlalchemy import text
        with db.get_session() as session:
            result = session.execute(text("SELECT COUNT(*) FROM argo_profiles")).scalar()
            print(f"\n🗄️ Database Records: {result:,}")
    except Exception as e:
        print(f"\n⚠️ Database: {e}")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Process ARGO NetCDF files and manage data storage"
    )
    
    parser.add_argument(
        'action',
        choices=['process', 'load', 'add', 'summary'],
        help='Action to perform: process (extract NetCDF), load (load CSV to DB), add (complete workflow), summary (show data)'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        help='Path to NetCDF file (for "add" action)'
    )
    
    args = parser.parse_args()
    
    if args.action == 'process':
        print("\n🔄 Processing all NetCDF files in data/raw/...")
        process_all_netcdf_files()
    
    elif args.action == 'load':
        print("\n📊 Loading all CSV files to database...")
        load_all_csv_to_database()
    
    elif args.action == 'add':
        if not args.file:
            print("❌ Error: --file argument required for 'add' action")
            print("\nUsage: python scripts/process_netcdf_files.py add --file path/to/file.nc")
        else:
            add_new_data(args.file)
    
    elif args.action == 'summary':
        show_data_summary()
    
    print("\n✅ Done!")
