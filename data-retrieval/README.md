# data-retrieval

A library for building and running data retrieval tools for Decison Agent.

[中文文档](README.zh-CN.md)

## Quick Start

### Install Dependencies

```bash
cd data-retrieval
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### Start Service

```bash
# Method 1: Run tool_api_router.py directly
cd src/data_retrieval/tools
python tool_api_router.py

# Method 2: Use uvicorn
uvicorn data_retrieval.tools.tool_api_router:DEFAULT_APP --host 0.0.0.0 --port 9100
```

The service will be available at `http://localhost:9100`.

## Scripts

### Generate API Documentation

Use `scripts/generate_api_docs.py` to generate OpenAPI 3.0 specification API documentation without starting the service.

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate   # Linux/Mac

# Generate with default parameters (output to api.json, server URL: http://data-retrieval:9100)
python scripts/generate_api_docs.py

# Specify output path and server URL
python scripts/generate_api_docs.py ./api.json http://localhost:9100
```

**Parameters:**
- `output_path`: Output file path, defaults to `api.json`
- `server_url`: Server URL in API documentation, defaults to `http://data-retrieval:9100`
