"""
Extensible Data Source Manager
Provides architecture for adding new data sources:
- ARGO floats (current)
- Ocean gliders (future)
- Moored buoys (future)
- Satellite data (future)
- CTD casts (future)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OceanDataSource(ABC):
    """
    Abstract base class for all ocean data sources
    Defines common interface for data ingestion
    """
    
    def __init__(self, source_name: str, source_type: str):
        self.source_name = source_name
        self.source_type = source_type
        self.metadata = {}
    
    @abstractmethod
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate data format and required columns"""
        pass
    
    @abstractmethod
    def extract_data(self, file_path: str) -> pd.DataFrame:
        """Extract data from source file"""
        pass
    
    @abstractmethod
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert to standard FloatChat format"""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict:
        """Return data source metadata"""
        pass
    
    def process_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Complete processing pipeline"""
        try:
            logger.info(f"Processing {self.source_type}: {file_path}")
            
            # Extract
            raw_data = self.extract_data(file_path)
            
            # Validate
            if not self.validate_data(raw_data):
                logger.error(f"Validation failed for {file_path}")
                return None
            
            # Standardize
            standardized = self.standardize_data(raw_data)
            
            # Add source metadata
            standardized['data_source'] = self.source_name
            standardized['source_type'] = self.source_type
            standardized['ingestion_time'] = datetime.now()
            
            logger.info(f"✅ Processed {len(standardized)} records from {self.source_type}")
            return standardized
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None


class ARGOFloatDataSource(OceanDataSource):
    """
    ARGO Float data source (current implementation)
    """
    
    def __init__(self):
        super().__init__("ARGO Global", "argo_float")
        self.required_columns = ['latitude', 'longitude', 'timestamp', 'pressure', 'temperature', 'salinity']
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate ARGO data structure"""
        return all(col in data.columns for col in self.required_columns)
    
    def extract_data(self, file_path: str) -> pd.DataFrame:
        """Extract from NetCDF"""
        from data_processing.netcdf_extractor import NetCDFExtractor
        extractor = NetCDFExtractor(file_path)
        return extractor.extract_profiles()
    
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Already in standard format"""
        df['platform_type'] = 'ARGO_FLOAT'
        return df
    
    def get_metadata(self) -> Dict:
        return {
            'source': 'ARGO Global Data Repository',
            'url': 'ftp.ifremer.fr/ifremer/argo',
            'parameters': ['temperature', 'salinity', 'pressure', 'dissolved_oxygen', 'chlorophyll', 'ph'],
            'coverage': 'Global oceans',
            'update_frequency': 'Real-time',
            'data_format': 'NetCDF'
        }


class OceanGliderDataSource(OceanDataSource):
    """
    Ocean Glider data source (future implementation)
    High-resolution profiles with horizontal transects
    """
    
    def __init__(self):
        super().__init__("Ocean Gliders", "glider")
        self.required_columns = ['latitude', 'longitude', 'timestamp', 'depth', 'temperature', 'salinity']
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate glider data"""
        return all(col in data.columns for col in self.required_columns)
    
    def extract_data(self, file_path: str) -> pd.DataFrame:
        """
        Extract from glider-specific format
        TODO: Implement based on glider data format (often NetCDF or MAT files)
        """
        logger.warning("Glider data extraction not yet implemented")
        # Placeholder - to be implemented
        return pd.DataFrame()
    
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert glider data to FloatChat standard"""
        # Convert depth to pressure (approximate)
        df['pressure'] = df['depth'] * 1.0  # 1 dbar ≈ 1 meter
        df['platform_type'] = 'OCEAN_GLIDER'
        df['glider_id'] = df.get('glider_id', 'UNKNOWN')
        return df
    
    def get_metadata(self) -> Dict:
        return {
            'source': 'Various glider programs',
            'parameters': ['temperature', 'salinity', 'dissolved_oxygen', 'chlorophyll', 'backscatter'],
            'coverage': 'Regional - mission dependent',
            'advantages': 'High spatial resolution, targeted sampling',
            'data_format': 'NetCDF, MAT, ASCII',
            'typical_mission_duration': '30-90 days'
        }


class MooredBuoyDataSource(OceanDataSource):
    """
    Moored Buoy data source (future implementation)
    Time-series at fixed locations
    """
    
    def __init__(self):
        super().__init__("Moored Buoys", "moored_buoy")
        self.required_columns = ['latitude', 'longitude', 'timestamp', 'depth', 'temperature']
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate buoy data"""
        return all(col in data.columns for col in self.required_columns)
    
    def extract_data(self, file_path: str) -> pd.DataFrame:
        """
        Extract from buoy format
        TODO: Implement based on buoy data format
        """
        logger.warning("Buoy data extraction not yet implemented")
        return pd.DataFrame()
    
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert buoy data to standard"""
        df['pressure'] = df['depth'] * 1.0
        df['platform_type'] = 'MOORED_BUOY'
        df['buoy_id'] = df.get('buoy_id', 'UNKNOWN')
        return df
    
    def get_metadata(self) -> Dict:
        return {
            'source': 'RAMA, PIRATA, TAO arrays',
            'parameters': ['temperature', 'salinity', 'currents', 'winds', 'air_pressure'],
            'coverage': 'Tropical oceans',
            'advantages': 'High temporal resolution, continuous monitoring',
            'data_format': 'NetCDF, ASCII'
        }


class SatelliteDataSource(OceanDataSource):
    """
    Satellite data source (future implementation)
    Surface parameters from remote sensing
    """
    
    def __init__(self):
        super().__init__("Satellite Observations", "satellite")
        self.required_columns = ['latitude', 'longitude', 'timestamp', 'sst']  # Sea Surface Temperature
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate satellite data"""
        return all(col in data.columns for col in self.required_columns)
    
    def extract_data(self, file_path: str) -> pd.DataFrame:
        """
        Extract from satellite format (HDF, NetCDF)
        TODO: Implement satellite data extraction
        """
        logger.warning("Satellite data extraction not yet implemented")
        return pd.DataFrame()
    
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert satellite data to standard"""
        # Satellite data is surface only
        df['pressure'] = 0.0  # Surface
        df['depth'] = 0.0
        df['temperature'] = df['sst']  # Sea Surface Temperature
        df['platform_type'] = 'SATELLITE'
        df['satellite_id'] = df.get('satellite', 'UNKNOWN')
        return df
    
    def get_metadata(self) -> Dict:
        return {
            'source': 'MODIS, VIIRS, AVHRR',
            'parameters': ['sst', 'chlorophyll', 'ocean_color', 'sea_level', 'sea_ice'],
            'coverage': 'Global, surface only',
            'advantages': 'High spatial coverage, synoptic view',
            'limitations': 'Surface only, cloud interference',
            'data_format': 'HDF, NetCDF'
        }


class CTDCastDataSource(OceanDataSource):
    """
    CTD Cast data source (future implementation)
    Ship-based vertical profiles
    """
    
    def __init__(self):
        super().__init__("CTD Casts", "ctd_cast")
        self.required_columns = ['latitude', 'longitude', 'timestamp', 'pressure', 'temperature', 'salinity', 'conductivity']
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate CTD data"""
        return all(col in data.columns for col in self.required_columns)
    
    def extract_data(self, file_path: str) -> pd.DataFrame:
        """
        Extract from CTD format (.cnv, .ros, .btl)
        TODO: Implement CTD data extraction
        """
        logger.warning("CTD data extraction not yet implemented")
        return pd.DataFrame()
    
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert CTD data to standard"""
        df['platform_type'] = 'CTD_CAST'
        df['cruise_id'] = df.get('cruise_id', 'UNKNOWN')
        df['cast_id'] = df.get('cast_id', 'UNKNOWN')
        return df
    
    def get_metadata(self) -> Dict:
        return {
            'source': 'Research vessels, CLIVAR, GO-SHIP',
            'parameters': ['temperature', 'salinity', 'conductivity', 'dissolved_oxygen', 'nutrients'],
            'coverage': 'Along ship tracks',
            'advantages': 'High vertical resolution, full water column, precise measurements',
            'data_format': 'CNV, ROS, BTL, NetCDF'
        }


class DataSourceManager:
    """
    Manages multiple data sources
    Provides unified interface for data ingestion
    """
    
    def __init__(self):
        self.sources: Dict[str, OceanDataSource] = {}
        self.registered_types = []
        
        # Register default sources
        self._register_default_sources()
    
    def _register_default_sources(self):
        """Register built-in data sources"""
        self.register_source(ARGOFloatDataSource())
        # Future sources ready to enable
        # self.register_source(OceanGliderDataSource())
        # self.register_source(MooredBuoyDataSource())
        # self.register_source(SatelliteDataSource())
        # self.register_source(CTDCastDataSource())
        
        logger.info(f"✅ Registered {len(self.sources)} data sources")
    
    def register_source(self, source: OceanDataSource):
        """Register a new data source"""
        self.sources[source.source_type] = source
        self.registered_types.append(source.source_type)
        logger.info(f"📌 Registered data source: {source.source_name} ({source.source_type})")
    
    def get_source(self, source_type: str) -> Optional[OceanDataSource]:
        """Get data source by type"""
        return self.sources.get(source_type)
    
    def list_sources(self) -> List[Dict]:
        """List all registered data sources"""
        return [
            {
                'type': source_type,
                'name': source.source_name,
                'metadata': source.get_metadata(),
                'status': 'active' if source_type == 'argo_float' else 'planned'
            }
            for source_type, source in self.sources.items()
        ]
    
    def process_file(self, file_path: str, source_type: str) -> Optional[pd.DataFrame]:
        """Process file from specific source"""
        source = self.get_source(source_type)
        
        if not source:
            logger.error(f"Unknown source type: {source_type}")
            return None
        
        return source.process_file(file_path)
    
    def auto_detect_source(self, file_path: str) -> Optional[str]:
        """
        Auto-detect data source type from file
        Based on file extension and content
        """
        import os
        
        ext = os.path.splitext(file_path)[1].lower()
        
        # File extension based detection
        extension_map = {
            '.nc': 'argo_float',  # Could also be glider or satellite
            '.nc4': 'argo_float',
            '.mat': 'glider',
            '.cnv': 'ctd_cast',
            '.ros': 'ctd_cast',
            '.btl': 'ctd_cast',
            '.hdf': 'satellite',
            '.h5': 'satellite'
        }
        
        detected = extension_map.get(ext)
        
        if detected:
            logger.info(f"Auto-detected source type: {detected}")
            return detected
        
        # Content-based detection (for .nc files)
        if ext in ['.nc', '.nc4']:
            try:
                import netCDF4 as nc
                with nc.Dataset(file_path, 'r') as ncfile:
                    # Check global attributes
                    if 'argo' in str(ncfile.getncattr('source')).lower():
                        return 'argo_float'
                    elif 'glider' in str(ncfile.getncattr('source')).lower():
                        return 'glider'
                    elif 'satellite' in str(ncfile.getncattr('source')).lower():
                        return 'satellite'
            except:
                pass
        
        logger.warning(f"Could not auto-detect source type for {file_path}")
        return None
    
    def batch_process(self, file_list: List[str], source_type: Optional[str] = None) -> pd.DataFrame:
        """
        Process multiple files
        Auto-detect source if not specified
        """
        all_data = []
        
        for file_path in file_list:
            # Auto-detect if needed
            if not source_type:
                detected_type = self.auto_detect_source(file_path)
                if not detected_type:
                    logger.warning(f"Skipping {file_path} - unknown type")
                    continue
            else:
                detected_type = source_type
            
            # Process file
            data = self.process_file(file_path, detected_type)
            
            if data is not None:
                all_data.append(data)
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            logger.info(f"✅ Batch processed {len(file_list)} files, {len(combined)} total records")
            return combined
        else:
            logger.warning("No data processed from batch")
            return pd.DataFrame()
    
    def get_statistics(self) -> Dict:
        """Get statistics about registered sources"""
        return {
            'total_sources': len(self.sources),
            'active_sources': sum(1 for s in self.list_sources() if s['status'] == 'active'),
            'planned_sources': sum(1 for s in self.list_sources() if s['status'] == 'planned'),
            'supported_types': self.registered_types,
            'sources': self.list_sources()
        }


class DataIntegrationPipeline:
    """
    Pipeline for integrating multi-source data
    Handles conflicts, merging, and quality control
    """
    
    def __init__(self):
        self.source_manager = DataSourceManager()
    
    def integrate_data(
        self,
        datasets: List[pd.DataFrame],
        priority_order: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Integrate data from multiple sources
        
        Args:
            datasets: List of DataFrames from different sources
            priority_order: Order of source priority for conflict resolution
        """
        if not datasets:
            return pd.DataFrame()
        
        if len(datasets) == 1:
            return datasets[0]
        
        # Combine all datasets
        combined = pd.concat(datasets, ignore_index=True)
        
        # Remove duplicates (same location, time, depth)
        combined = self._remove_duplicates(combined, priority_order)
        
        # Quality control
        combined = self._apply_quality_control(combined)
        
        # Sort by time and location
        combined = combined.sort_values(['timestamp', 'latitude', 'longitude', 'pressure'])
        
        return combined
    
    def _remove_duplicates(
        self,
        df: pd.DataFrame,
        priority_order: Optional[List[str]]
    ) -> pd.DataFrame:
        """
        Remove duplicate measurements
        Keep highest priority source
        """
        # Define duplicate criteria (same location, time, depth)
        duplicate_cols = ['latitude', 'longitude', 'timestamp', 'pressure']
        
        # Round to avoid floating point issues
        for col in ['latitude', 'longitude', 'pressure']:
            df[f'{col}_rounded'] = df[col].round(2)
        
        df['timestamp_rounded'] = pd.to_datetime(df['timestamp']).dt.floor('H')
        
        rounded_cols = [f'{col}_rounded' for col in ['latitude', 'longitude', 'pressure']] + ['timestamp_rounded']
        
        # Sort by priority if specified
        if priority_order and 'source_type' in df.columns:
            df['priority'] = df['source_type'].map(
                {source: i for i, source in enumerate(priority_order)}
            )
            df = df.sort_values('priority')
        
        # Keep first occurrence (highest priority)
        df_unique = df.drop_duplicates(subset=rounded_cols, keep='first')
        
        # Remove temporary columns
        cols_to_drop = [col for col in df_unique.columns if col.endswith('_rounded') or col == 'priority']
        df_unique = df_unique.drop(columns=cols_to_drop, errors='ignore')
        
        logger.info(f"Removed {len(df) - len(df_unique)} duplicate measurements")
        
        return df_unique
    
    def _apply_quality_control(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply cross-source quality control
        """
        initial_count = len(df)
        
        # Physical limits
        df = df[
            (df['temperature'] >= -2) & (df['temperature'] <= 40) &
            (df['salinity'] >= 0) & (df['salinity'] <= 42) &
            (df['pressure'] >= 0) & (df['pressure'] <= 12000)
        ]
        
        # Remove obvious outliers (3 sigma)
        for param in ['temperature', 'salinity']:
            if param in df.columns:
                mean = df[param].mean()
                std = df[param].std()
                df = df[np.abs(df[param] - mean) <= 3 * std]
        
        removed = initial_count - len(df)
        if removed > 0:
            logger.info(f"QC: Removed {removed} records ({removed/initial_count*100:.1f}%)")
        
        return df
    
    def create_unified_dataset(
        self,
        file_paths: Dict[str, List[str]]
    ) -> pd.DataFrame:
        """
        Create unified dataset from multiple sources
        
        Args:
            file_paths: Dict mapping source_type to list of file paths
                       e.g., {'argo_float': ['file1.nc'], 'glider': ['file2.mat']}
        """
        datasets = []
        
        for source_type, files in file_paths.items():
            source_data = self.source_manager.batch_process(files, source_type)
            if not source_data.empty:
                datasets.append(source_data)
        
        if datasets:
            return self.integrate_data(datasets)
        else:
            return pd.DataFrame()


# Singleton instance
data_source_manager = DataSourceManager()
integration_pipeline = DataIntegrationPipeline()


# Example usage
if __name__ == "__main__":
    # List available sources
    manager = DataSourceManager()
    
    print("📊 Registered Data Sources:")
    for source_info in manager.list_sources():
        print(f"\n{source_info['name']} ({source_info['type']})")
        print(f"  Status: {source_info['status']}")
        print(f"  Metadata: {source_info['metadata']}")
    
    print("\n" + "="*60)
    print("Future Extension Example:")
    print("="*60)
    print("""
    # To add glider support in future:
    
    1. Uncomment in _register_default_sources():
       self.register_source(OceanGliderDataSource())
    
    2. Implement extract_data() method in OceanGliderDataSource
    
    3. Test with glider files:
       glider_data = manager.process_file('glider_data.nc', 'glider')
    
    4. Integrate with ARGO data:
       combined = integration_pipeline.integrate_data([argo_data, glider_data])
    
    Same pattern for buoys, satellites, CTD casts!
    """)