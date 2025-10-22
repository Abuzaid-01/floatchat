"""
Caching system for improved performance
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional
import pickle
import pandas as pd

class CacheManager:
    """Manage query and computation caches"""
    
    def __init__(self, cache_dir: str = "./data_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> dict:
        """Load cache metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save cache metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str, max_age_hours: int = 24) -> Optional[pd.DataFrame]:
        """Retrieve from cache if valid"""
        key = self._get_cache_key(query)
        cache_path = self.cache_dir / f"{key}.pkl"
        
        if not cache_path.exists():
            return None
        
        # Check age
        if key in self.metadata:
            cached_time = datetime.fromisoformat(self.metadata[key]['timestamp'])
            if (datetime.now() - cached_time) > timedelta(hours=max_age_hours):
                return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except:
            return None
    
    def set(self, query: str, data: pd.DataFrame):
        """Store in cache"""
        key = self._get_cache_key(query)
        cache_path = self.cache_dir / f"{key}.pkl"
        
        # Save data
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        
        # Update metadata
        self.metadata[key] = {
            'query': query[:100],  # Store first 100 chars
            'timestamp': datetime.now().isoformat(),
            'size_mb': data.memory_usage(deep=True).sum() / (1024 * 1024),
            'records': len(data)
        }
        
        self._save_metadata()
    
    def clear_old(self, max_age_hours: int = 168):  # 1 week default
        """Remove old cache entries"""
        now = datetime.now()
        
        keys_to_remove = []
        for key, meta in self.metadata.items():
            cached_time = datetime.fromisoformat(meta['timestamp'])
            if (now - cached_time) > timedelta(hours=max_age_hours):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            cache_path = self.cache_dir / f"{key}.pkl"
            if cache_path.exists():
                cache_path.unlink()
            del self.metadata[key]
        
        self._save_metadata()
        return len(keys_to_remove)
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.pkl")) / (1024 * 1024)
        
        return {
            'cached_queries': len(self.metadata),
            'total_size_mb': total_size,
            'entries': self.metadata
        }

# Create __init__.py
# Create file: data_cache/__init__.py
