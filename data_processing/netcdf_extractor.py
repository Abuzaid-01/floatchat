import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class NetCDFExtractor:
    """Extract ARGO data from NetCDF files"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.ds = None
    
    def load_netcdf(self):
        """Load NetCDF file"""
        try:
            self.ds = xr.open_dataset(self.file_path)
            print(f"✅ Loaded NetCDF file: {self.file_path}")
            return True
        except Exception as e:
            print(f"❌ Error loading NetCDF: {e}")
            return False
    
    def extract_profiles(self) -> pd.DataFrame:
        """Extract all profiles from NetCDF file"""
        if self.ds is None:
            self.load_netcdf()
        
        profiles = []
        
        # Get dimensions
        n_prof = self.ds.dims.get('N_PROF', 1)
        n_levels = self.ds.dims.get('N_LEVELS', 0)
        
        for prof_idx in range(n_prof):
            # Extract profile metadata
            lat = float(self.ds['LATITUDE'].values[prof_idx])
            lon = float(self.ds['LONGITUDE'].values[prof_idx])
            juld = self.ds['JULD'].values[prof_idx]
            
            # Convert Julian date to datetime
            timestamp = self._julian_to_datetime(juld)
            
            # Get float ID and cycle number
            try:
                float_id = str(self.ds['PLATFORM_NUMBER'].values[prof_idx])
                cycle_num = int(self.ds['CYCLE_NUMBER'].values[prof_idx])
            except:
                float_id = None
                cycle_num = None
            
            # Extract profile data
            for level_idx in range(n_levels):
                pressure = self.ds['PRES'].values[prof_idx, level_idx]
                temp = self.ds['TEMP'].values[prof_idx, level_idx]
                sal = self.ds['PSAL'].values[prof_idx, level_idx]
                
                # Skip NaN values
                if np.isnan(pressure) or np.isnan(temp) or np.isnan(sal):
                    continue
                
                profile_data = {
                    'float_id': float_id,
                    'cycle_number': cycle_num,
                    'latitude': lat,
                    'longitude': lon,
                    'timestamp': timestamp,
                    'pressure': float(pressure),
                    'temperature': float(temp),
                    'salinity': float(sal)
                }
                
                # Add QC flags if available
                try:
                    profile_data['temp_qc'] = int(self.ds['TEMP_QC'].values[prof_idx, level_idx])
                    profile_data['sal_qc'] = int(self.ds['PSAL_QC'].values[prof_idx, level_idx])
                except:
                    pass
                
                profiles.append(profile_data)
        
        df = pd.DataFrame(profiles)
        print(f"✅ Extracted {len(df)} measurements from {n_prof} profiles")
        return df
    
    def _julian_to_datetime(self, julian_date):
        """Convert Julian date to datetime"""
        try:
            # Check if it's already a datetime object (numpy.datetime64)
            if hasattr(julian_date, 'dtype') and np.issubdtype(julian_date.dtype, np.datetime64):
                # Already a datetime, just convert to pandas Timestamp
                return pd.Timestamp(julian_date)
            
            # Check if it's a string that can be parsed
            if isinstance(julian_date, (str, bytes)):
                return pd.to_datetime(julian_date)
            
            # Otherwise, assume it's Julian days since 1950-01-01
            # ARGO uses days since 1950-01-01
            reference_date = pd.Timestamp('1950-01-01')
            return reference_date + pd.Timedelta(days=float(julian_date))
        except Exception as e:
            print(f"⚠️ Warning: Could not convert date: {e}")
            return pd.Timestamp('1950-01-01')
    
    def get_profile_summary(self) -> Dict:
        """Get summary statistics of the dataset"""
        if self.ds is None:
            self.load_netcdf()
        
        summary = {
            'n_profiles': self.ds.dims.get('N_PROF', 0),
            'n_levels': self.ds.dims.get('N_LEVELS', 0),
            'latitude_range': (
                float(self.ds['LATITUDE'].min().values),
                float(self.ds['LATITUDE'].max().values)
            ),
            'longitude_range': (
                float(self.ds['LONGITUDE'].min().values),
                float(self.ds['LONGITUDE'].max().values)
            ),
            'variables': list(self.ds.data_vars.keys())
        }
        return summary
    
    def close(self):
        """Close NetCDF file"""
        if self.ds is not None:
            self.ds.close()

# Usage example
if __name__ == "__main__":
    extractor = NetCDFExtractor("data/raw/argo_profile.nc")
    df = extractor.extract_profiles()
    df.to_csv("data/processed/argo_profiles.csv", index=False)
    print(extractor.get_profile_summary())
    extractor.close()

# import xarray as xr
# import pandas as pd
# import numpy as np
# from pathlib import Path
# from typing import List, Dict, Optional
# from datetime import datetime
# import warnings
# warnings.filterwarnings('ignore')

# class EnhancedNetCDFExtractor:
#     """
#     Production-grade ARGO NetCDF extractor with:
#     - BGC parameter support
#     - Robust error handling
#     - QC flag validation
#     - Multi-file batch processing
#     """
    
#     # Quality Control thresholds
#     QC_GOOD = [1, 2]  # Good and probably good data
#     QC_ACCEPTABLE = [1, 2, 5, 8]  # Include corrected and interpolated
    
#     def __init__(self, file_path: str, strict_qc: bool = True):
#         self.file_path = file_path
#         self.ds = None
#         self.strict_qc = strict_qc
#         self.errors = []
#         self.warnings = []
    
#     def load_netcdf(self) -> bool:
#         """Load NetCDF file with error handling"""
#         try:
#             self.ds = xr.open_dataset(self.file_path, decode_times=False)
#             print(f"✅ Loaded: {Path(self.file_path).name}")
#             self._validate_dataset()
#             return True
#         except Exception as e:
#             self.errors.append(f"Load error: {str(e)}")
#             print(f"❌ Failed to load {self.file_path}: {e}")
#             return False
    
#     def _validate_dataset(self):
#         """Validate required variables exist"""
#         required_vars = ['LATITUDE', 'LONGITUDE', 'JULD', 'PRES', 'TEMP', 'PSAL']
#         missing = [v for v in required_vars if v not in self.ds.variables]
        
#         if missing:
#             self.warnings.append(f"Missing variables: {missing}")
        
#         # Check for BGC variables
#         bgc_vars = ['DOXY', 'CHLA', 'BBP700', 'PH_IN_SITU_TOTAL', 'NITRATE']
#         available_bgc = [v for v in bgc_vars if v in self.ds.variables]
#         if available_bgc:
#             print(f"📊 BGC parameters found: {', '.join(available_bgc)}")
    
#     def extract_profiles(self, validate_qc: bool = True) -> pd.DataFrame:
#         """
#         Extract all profiles with comprehensive parameter support
        
#         Args:
#             validate_qc: Apply quality control filtering
#         """
#         if self.ds is None:
#             if not self.load_netcdf():
#                 return pd.DataFrame()
        
#         profiles = []
#         n_prof = self.ds.dims.get('N_PROF', 1)
#         n_levels = self.ds.dims.get('N_LEVELS', 0)
        
#         print(f"📊 Processing {n_prof} profiles with {n_levels} levels each...")
        
#         for prof_idx in range(n_prof):
#             try:
#                 profile_meta = self._extract_profile_metadata(prof_idx)
                
#                 for level_idx in range(n_levels):
#                     level_data = self._extract_level_data(
#                         prof_idx, level_idx, validate_qc
#                     )
                    
#                     if level_data:
#                         level_data.update(profile_meta)
#                         profiles.append(level_data)
                        
#             except Exception as e:
#                 self.errors.append(f"Profile {prof_idx} error: {str(e)}")
#                 continue
        
#         df = pd.DataFrame(profiles)
        
#         if not df.empty:
#             df = self._post_process_dataframe(df)
#             print(f"✅ Extracted {len(df)} valid measurements")
#             print(f"   Profiles: {df.groupby(['float_id', 'cycle_number']).ngroups}")
#             print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
#         return df
    
#     def _extract_profile_metadata(self, prof_idx: int) -> Dict:
#         """Extract profile-level metadata"""
#         meta = {}
        
#         # Position
#         meta['latitude'] = float(self.ds['LATITUDE'].values[prof_idx])
#         meta['longitude'] = float(self.ds['LONGITUDE'].values[prof_idx])
        
#         # Time
#         juld = self.ds['JULD'].values[prof_idx]
#         meta['timestamp'] = self._julian_to_datetime(juld)
        
#         # Float identification
#         try:
#             platform = self.ds['PLATFORM_NUMBER'].values[prof_idx]
#             meta['float_id'] = ''.join([chr(c) for c in platform if c != 0]).strip()
#         except:
#             meta['float_id'] = f"UNKNOWN_{prof_idx}"
        
#         try:
#             meta['cycle_number'] = int(self.ds['CYCLE_NUMBER'].values[prof_idx])
#         except:
#             meta['cycle_number'] = 0
        
#         # Data mode (R=realtime, D=delayed, A=adjusted)
#         try:
#             mode = self.ds['DATA_MODE'].values[prof_idx]
#             meta['data_mode'] = chr(mode) if isinstance(mode, int) else str(mode)
#         except:
#             meta['data_mode'] = 'R'
        
#         # Platform type
#         try:
#             ptype = self.ds.get('PLATFORM_TYPE')
#             if ptype is not None:
#                 meta['platform_type'] = str(ptype.values[prof_idx])
#         except:
#             meta['platform_type'] = 'ARGO'
        
#         return meta
    
#     def _extract_level_data(
#         self, prof_idx: int, level_idx: int, validate_qc: bool
#     ) -> Optional[Dict]:
#         """Extract data at specific pressure level with QC"""
#         data = {}
        
#         # Core parameters
#         params = {
#             'pressure': ('PRES', 'PRES_QC'),
#             'temperature': ('TEMP', 'TEMP_QC'),
#             'salinity': ('PSAL', 'PSAL_QC'),
#         }
        
#         # BGC parameters (optional)
#         bgc_params = {
#             'dissolved_oxygen': ('DOXY', 'DOXY_QC'),
#             'chlorophyll': ('CHLA', 'CHLA_QC'),
#             'bbp700': ('BBP700', 'BBP700_QC'),
#             'ph': ('PH_IN_SITU_TOTAL', 'PH_IN_SITU_TOTAL_QC'),
#             'nitrate': ('NITRATE', 'NITRATE_QC'),
#         }
        
#         # Extract core parameters
#         for param_name, (var_name, qc_name) in params.items():
#             value, qc = self._get_value_with_qc(
#                 var_name, qc_name, prof_idx, level_idx
#             )
            
#             if value is None or np.isnan(value):
#                 return None  # Skip invalid measurements
            
#             if validate_qc and not self._is_qc_acceptable(qc):
#                 return None  # Skip bad quality data
            
#             data[param_name] = float(value)
#             data[f'{param_name[:4]}_qc'] = int(qc) if qc is not None else 0
        
#         # Extract BGC parameters (if available)
#         for param_name, (var_name, qc_name) in bgc_params.items():
#             if var_name in self.ds.variables:
#                 value, qc = self._get_value_with_qc(
#                     var_name, qc_name, prof_idx, level_idx
#                 )
                
#                 if value is not None and not np.isnan(value):
#                     if not validate_qc or self._is_qc_acceptable(qc):
#                         data[param_name] = float(value)
#                         data[f'{param_name[:4]}_qc'] = int(qc) if qc else 0
        
#         return data if data else None
    
#     def _get_value_with_qc(
#         self, var_name: str, qc_name: str, prof_idx: int, level_idx: int
#     ) -> tuple:
#         """Get value and its QC flag"""
#         try:
#             value = self.ds[var_name].values[prof_idx, level_idx]
            
#             qc = None
#             if qc_name in self.ds.variables:
#                 qc_val = self.ds[qc_name].values[prof_idx, level_idx]
#                 qc = int(chr(qc_val)) if isinstance(qc_val, (int, np.integer)) else int(qc_val)
            
#             return value, qc
#         except:
#             return None, None
    
#     def _is_qc_acceptable(self, qc: Optional[int]) -> bool:
#         """Check if QC flag is acceptable"""
#         if qc is None:
#             return not self.strict_qc  # Accept if not strict
        
#         threshold = self.QC_GOOD if self.strict_qc else self.QC_ACCEPTABLE
#         return qc in threshold
    
#     def _julian_to_datetime(self, julian_date) -> pd.Timestamp:
#         """Convert ARGO Julian date to datetime"""
#         try:
#             reference = pd.Timestamp('1950-01-01')
#             if np.isnan(julian_date):
#                 return reference
#             return reference + pd.Timedelta(days=float(julian_date))
#         except:
#             return pd.Timestamp('1950-01-01')
    
#     def _post_process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
#         """Clean and enhance extracted data"""
#         # Remove duplicates
#         df = df.drop_duplicates(
#             subset=['float_id', 'cycle_number', 'pressure', 'timestamp']
#         )
        
#         # Sort by float, cycle, and pressure
#         df = df.sort_values(['float_id', 'cycle_number', 'pressure'])
        
#         # Add computed fields
#         df['depth_m'] = df['pressure'] * 1.0  # Approximation
#         df['year'] = pd.to_datetime(df['timestamp']).dt.year
#         df['month'] = pd.to_datetime(df['timestamp']).dt.month
        
#         # Add ocean region
#         df['ocean_region'] = df.apply(
#             lambda row: self._determine_region(row['latitude'], row['longitude']),
#             axis=1
#         )
        
#         return df
    
#     def _determine_region(self, lat: float, lon: float) -> str:
#         """Determine ocean region - Enhanced for Indian Ocean"""
#         regions = {
#             'Arabian Sea': (5, 30, 40, 80),
#             'Bay of Bengal': (5, 25, 80, 100),
#             'Equatorial Indian Ocean': (-10, 5, 40, 100),
#             'Southern Indian Ocean': (-50, -10, 20, 120),
#             'Andaman Sea': (5, 20, 92, 100),
#             'Red Sea': (12, 30, 32, 44),
#         }
        
#         for region, (lat_min, lat_max, lon_min, lon_max) in regions.items():
#             if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
#                 return region
        
#         # Default regions
#         if 20 <= lon <= 120 and -60 <= lat <= 30:
#             return 'Indian Ocean'
#         elif -180 <= lon < 20:
#             return 'Atlantic Ocean'
#         elif 120 <= lon <= 180:
#             return 'Pacific Ocean'
#         else:
#             return 'Other'
    
#     def extract_float_trajectory(self, float_id: str) -> pd.DataFrame:
#         """Extract complete trajectory for a specific float"""
#         df = self.extract_profiles(validate_qc=True)
#         return df[df['float_id'] == float_id].copy()
    
#     def get_summary(self) -> Dict:
#         """Get comprehensive dataset summary"""
#         if self.ds is None:
#             return {}
        
#         summary = {
#             'filename': Path(self.file_path).name,
#             'n_profiles': self.ds.dims.get('N_PROF', 0),
#             'n_levels': self.ds.dims.get('N_LEVELS', 0),
#             'variables': list(self.ds.data_vars.keys()),
#             'dimensions': dict(self.ds.dims),
#             'errors': self.errors,
#             'warnings': self.warnings,
#         }
        
#         # Spatial extent
#         if 'LATITUDE' in self.ds.variables:
#             summary['lat_range'] = (
#                 float(self.ds['LATITUDE'].min().values),
#                 float(self.ds['LATITUDE'].max().values)
#             )
#             summary['lon_range'] = (
#                 float(self.ds['LONGITUDE'].min().values),
#                 float(self.ds['LONGITUDE'].max().values)
#             )
        
#         # Temporal extent
#         if 'JULD' in self.ds.variables:
#             juld = self.ds['JULD'].values
#             valid_dates = juld[~np.isnan(juld)]
#             if len(valid_dates) > 0:
#                 summary['date_range'] = (
#                     self._julian_to_datetime(valid_dates.min()),
#                     self._julian_to_datetime(valid_dates.max())
#                 )
        
#         return summary
    
#     def close(self):
#         """Close dataset and cleanup"""
#         if self.ds is not None:
#             self.ds.close()
#             self.ds = None


# class BatchNetCDFProcessor:
#     """Process multiple NetCDF files efficiently"""
    
#     def __init__(self, data_dir: str):
#         self.data_dir = Path(data_dir)
#         self.processed_files = []
#         self.failed_files = []
    
#     def process_directory(
#         self, 
#         pattern: str = "*.nc",
#         output_file: str = "argo_profiles_complete.csv",
#         strict_qc: bool = True
#     ) -> pd.DataFrame:
#         """
#         Process all NetCDF files in directory
        
#         Args:
#             pattern: File pattern to match
#             output_file: Output CSV filename
#             strict_qc: Use strict QC filtering
#         """
#         nc_files = list(self.data_dir.glob(pattern))
        
#         if not nc_files:
#             print(f"❌ No files found matching {pattern} in {self.data_dir}")
#             return pd.DataFrame()
        
#         print(f"📂 Found {len(nc_files)} NetCDF files")
#         print(f"🔍 QC Mode: {'STRICT (QC 1-2 only)' if strict_qc else 'RELAXED (QC 1-2,5,8)'}")
        
#         all_profiles = []
        
#         for i, nc_file in enumerate(nc_files, 1):
#             print(f"\n[{i}/{len(nc_files)}] Processing {nc_file.name}...")
            
#             try:
#                 extractor = EnhancedNetCDFExtractor(str(nc_file), strict_qc=strict_qc)
#                 df = extractor.extract_profiles(validate_qc=True)
                
#                 if not df.empty:
#                     all_profiles.append(df)
#                     self.processed_files.append(nc_file.name)
#                     print(f"   ✅ Extracted {len(df)} measurements")
#                 else:
#                     print(f"   ⚠️ No valid data extracted")
                
#                 extractor.close()
                
#             except Exception as e:
#                 print(f"   ❌ Failed: {e}")
#                 self.failed_files.append((nc_file.name, str(e)))
        
#         # Combine all profiles
#         if all_profiles:
#             combined_df = pd.concat(all_profiles, ignore_index=True)
            
#             # Save to CSV
#             output_path = self.data_dir.parent / 'processed' / output_file
#             output_path.parent.mkdir(exist_ok=True)
#             combined_df.to_csv(output_path, index=False)
            
#             print(f"\n{'='*60}")
#             print(f"✅ PROCESSING COMPLETE")
#             print(f"{'='*60}")
#             print(f"📊 Total measurements: {len(combined_df):,}")
#             print(f"🌊 Unique floats: {combined_df['float_id'].nunique()}")
#             print(f"📍 Profiles: {combined_df.groupby(['float_id', 'cycle_number']).ngroups}")
#             print(f"📅 Date range: {combined_df['timestamp'].min()} to {combined_df['timestamp'].max()}")
#             print(f"🗺️ Regions: {combined_df['ocean_region'].value_counts().to_dict()}")
#             print(f"💾 Saved to: {output_path}")
            
#             if self.failed_files:
#                 print(f"\n⚠️ Failed files: {len(self.failed_files)}")
#                 for fname, error in self.failed_files:
#                     print(f"   - {fname}: {error}")
            
#             return combined_df
#         else:
#             print("\n❌ No data extracted from any files")
#             return pd.DataFrame()


# # Usage Example
# if __name__ == "__main__":
#     # Single file processing
#     extractor = EnhancedNetCDFExtractor(
#         "data/raw/argo_profile.nc",
#         strict_qc=True
#     )
    
#     df = extractor.extract_profiles(validate_qc=True)
#     print("\n📋 Summary:", extractor.get_summary())
    
#     # Batch processing
#     processor = BatchNetCDFProcessor("data/raw")
#     combined_df = processor.process_directory(
#         pattern="*.nc",
#         strict_qc=True
#     )