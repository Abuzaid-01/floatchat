import pandas as pd
from sqlalchemy.orm import Session
from database.db_setup import DatabaseSetup
from database.models import ArgoProfile
from tqdm import tqdm

class DataLoader:
    """Load processed data into database"""
    
    def __init__(self):
        self.db_setup = DatabaseSetup()
    
    def load_csv_to_db(self, csv_path: str, batch_size: int = 1000):
        """Load CSV data into database in batches"""
        print(f"📊 Loading data from {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Rename 'time' column to 'timestamp' if it exists
        if 'time' in df.columns:
            df = df.rename(columns={'time': 'timestamp'})
        
        # Convert timestamp column to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns', errors='coerce')
        
        session = self.db_setup.get_session()
        
        try:
            total_rows = len(df)
            for i in tqdm(range(0, total_rows, batch_size), desc="Loading batches"):
                batch = df.iloc[i:i+batch_size]
                
                # Create ArgoProfile objects
                profiles = [
                    ArgoProfile(**row.to_dict()) 
                    for _, row in batch.iterrows()
                ]
                
                session.bulk_save_objects(profiles)
                session.commit()
            
            print(f"✅ Successfully loaded {total_rows} records")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error loading data: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()
    
    def get_record_count(self) -> int:
        """Get total number of records in database"""
        session = self.db_setup.get_session()
        count = session.query(ArgoProfile).count()
        session.close()
        return count

# Usage
if __name__ == "__main__":
    loader = DataLoader()
    loader.load_csv_to_db("/Users/abuzaid/Desktop/final/netcdf/FloatChat/data/processed/argo_profiles.csv")
    print(f"Total records: {loader.get_record_count()}")
