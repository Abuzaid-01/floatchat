# Data Storage Guide

FloatChat stores ARGO ocean data in **both raw NetCDF and processed CSV formats**.

## 📁 Directory Structure

```
FloatChat/data/
├── raw/              # Original NetCDF files (.nc)
├── processed/        # Extracted CSV files
├── sample/           # Sample data for testing
└── vector_store/     # FAISS embeddings
```

## 🔄 How to Add New Data

### Method 1: Automatic Processing (Recommended)

Add a new NetCDF file and automatically process it:

```bash
cd FloatChat
python scripts/process_netcdf_files.py add --file /path/to/your/file.nc
```

This will:
1. ✅ Copy NetCDF to `data/raw/`
2. ✅ Extract and save CSV to `data/processed/`
3. ✅ Load data into PostgreSQL database

### Method 2: Manual Steps

#### Step 1: Add NetCDF File
Copy your `.nc` file to the `data/raw/` directory:
```bash
cp your_argo_data.nc FloatChat/data/raw/
```

#### Step 2: Process NetCDF to CSV
Extract all NetCDF files in `data/raw/`:
```bash
python scripts/process_netcdf_files.py process
```

#### Step 3: Load CSV to Database
Load all CSV files to PostgreSQL:
```bash
python scripts/process_netcdf_files.py load
```

## 📊 Check Your Data

View summary of stored data:
```bash
python scripts/process_netcdf_files.py summary
```

Output example:
```
📊 DATA STORAGE SUMMARY
================================================================

📁 Raw NetCDF Files (3):
   - 20251017_prof.nc (2.5 MB)
   - 20251018_prof.nc (3.1 MB)
   - 20251019_prof.nc (2.8 MB)

📊 Processed CSV Files (3):
   - 20251017_prof.csv (450 KB)
   - 20251018_prof.csv (520 KB)
   - 20251019_prof.csv (480 KB)

🗄️ Database Records: 12,567
```

## 🎯 Usage Examples

### Example 1: Add Single File
```bash
# Download ARGO data
wget ftp://ftp.ifremer.fr/argo/dac/.../2902696_prof.nc

# Add to FloatChat
python scripts/process_netcdf_files.py add --file 2902696_prof.nc
```

### Example 2: Batch Processing
```bash
# Copy multiple files
cp *.nc FloatChat/data/raw/

# Process all at once
python scripts/process_netcdf_files.py process
python scripts/process_netcdf_files.py load
```

### Example 3: Reprocess Everything
```bash
# Reprocess all NetCDF files
python scripts/process_netcdf_files.py process

# Reload to database
python scripts/process_netcdf_files.py load
```

## 💾 Data Formats

### Raw NetCDF (.nc)
- **Location**: `data/raw/`
- **Format**: Binary NetCDF4
- **Contains**: Original ARGO profile data with all variables
- **Use**: Long-term storage, reprocessing

### Processed CSV
- **Location**: `data/processed/`
- **Format**: CSV (text)
- **Contains**: Extracted profiles with key parameters
- **Columns**: float_id, cycle_number, latitude, longitude, timestamp, pressure, temperature, salinity, etc.
- **Use**: Easy viewing, importing, analysis

### Database (PostgreSQL)
- **Table**: `argo_profiles`
- **Indexed**: lat/lon, timestamp, float_id
- **Use**: Fast queries via SQL, RAG system

## 🔍 Where is Your Current Data?

```bash
# Check raw NetCDF files
ls -lh FloatChat/data/raw/

# Check processed CSV files
ls -lh FloatChat/data/processed/

# Check database
psql -U postgres -d floatchat -c "SELECT COUNT(*) FROM argo_profiles;"
```

## 🗑️ Managing Data

### Delete Specific File
```bash
# Remove from raw
rm FloatChat/data/raw/filename.nc

# Remove from processed
rm FloatChat/data/processed/filename.csv

# Clean database (use SQL or reload)
```

### Clear All Data
```bash
# Clear raw files
rm FloatChat/data/raw/*.nc

# Clear processed files
rm FloatChat/data/processed/*.csv

# Clear database
psql -U postgres -d floatchat -c "TRUNCATE TABLE argo_profiles;"
```

## 📈 Storage Space

Typical file sizes:
- **NetCDF**: 1-5 MB per file (compressed binary)
- **CSV**: 100-500 KB per file (text)
- **Database**: ~1 KB per measurement record

For 1000 ARGO profiles:
- Raw: ~3 GB
- CSV: ~500 MB
- Database: ~100 MB (with indexes)

## 🚀 Performance Tips

1. **Keep raw NetCDF files** - You can always reprocess with better algorithms
2. **CSV for sharing** - Easy to share, view in Excel, import to other tools
3. **Database for queries** - Fastest for complex queries and RAG system
4. **Backup regularly** - Both raw and database

## 🔧 Troubleshooting

### "No NetCDF files found"
```bash
# Check directory
ls FloatChat/data/raw/
# Should see .nc files, not just .gitkeep
```

### "Database connection failed"
```bash
# Start PostgreSQL
brew services start postgresql@16

# Check database exists
psql -U postgres -l | grep floatchat
```

### "CSV extraction failed"
- Check NetCDF file is not corrupted
- Ensure xarray and netCDF4 packages are installed
- Try opening file manually: `python -c "import xarray as xr; ds = xr.open_dataset('file.nc'); print(ds)"`

## 📝 Notes

- ✅ **Both formats stored**: Raw NetCDF in `data/raw/`, processed CSV in `data/processed/`
- ✅ **Automatic backup**: Raw files preserved for reprocessing
- ✅ **Version control**: `.gitkeep` files ensure directories exist in Git
- ✅ **Database sync**: CSV files can be reloaded anytime
- ✅ **Scalable**: Add unlimited files, process in batches

## 🎓 Next Steps

1. Add more NetCDF files to `data/raw/`
2. Run `python scripts/process_netcdf_files.py process`
3. Load to database with `python scripts/process_netcdf_files.py load`
4. Use FloatChat to query your data! 🌊

For questions or issues, check the main README or documentation.
