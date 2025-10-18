# FloatChat Setup Instructions

## Virtual Environment

### Created Virtual Environment
- **Location**: `/Users/abuzaid/Desktop/final/netcdf/venv/`
- **Python Version**: 3.14.0 (Homebrew)
- **Status**: ✅ Active and configured with pip

### Activation Commands

**Activate the virtual environment:**
```bash
cd /Users/abuzaid/Desktop/final/netcdf
source venv/bin/activate
```

**Deactivate:**
```bash
deactivate
```

## Installation

### Current Installation
Running: `pip install -r FloatChat/requirements.txt`

The installation process is underway. The dependency resolver is finding compatible versions for all packages.

### Note on Python 3.13 Issue
- The original Python 3.13 installation at `/Library/Frameworks/Python.framework/Versions/3.13/` appears to be corrupted (missing the `datetime` module)
- **Solution**: Created a new virtual environment using Homebrew's Python 3.14.0 instead
- This resolves the issue and provides a more up-to-date Python version

## Project Structure

```
FloatChat/
├── data/                   # Data directories
│   ├── raw/               # Raw NetCDF files
│   ├── processed/         # Processed data
│   └── sample/            # Sample data
├── database/              # Database layer
├── data_processing/       # Data extraction & processing
├── vector_store/          # Vector database (FAISS/Chroma)
├── rag_engine/           # RAG and LLM logic
├── visualization/         # Plotting and visualizations
├── api/                   # FastAPI backend
├── streamlit_app/        # Streamlit UI
├── tests/                 # Unit tests
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── docker/               # Docker configuration
```

## Dependencies Installed

- **Core**: Streamlit, LangChain, OpenAI
- **Database**: SQLAlchemy, PostgreSQL, Alembic
- **Vector Store**: FAISS, Sentence Transformers, ChromaDB
- **Data Processing**: xarray, netCDF4, pandas, numpy
- **Visualization**: Plotly, Folium, Matplotlib
- **API**: FastAPI, Uvicorn, Pydantic

## Next Steps

1. ✅ Virtual environment created
2. 🔄 Dependencies installing (in progress)
3. ⏳ Configure `.env` file (copy from `.env.example`)
4. ⏳ Initialize database
5. ⏳ Start development

## Troubleshooting

### If you encounter import errors:
1. Ensure virtual environment is activated
2. Check Python version: `python --version` (should be 3.14.0)
3. Verify pip location: `which pip` (should be in venv directory)

### To reinstall dependencies:
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r FloatChat/requirements.txt
```
