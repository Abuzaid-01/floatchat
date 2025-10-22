"""
FastAPI endpoint for MCP tool execution
Allows external systems to use FloatChat tools
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.mcp_server import MCPToolServer

app = FastAPI(
    title="FloatChat MCP API",
    description="Model Context Protocol API for ARGO Data Analysis",
    version="1.0.0"
)

# Initialize MCP server
mcp_server = MCPToolServer()

class ToolRequest(BaseModel):
    """MCP tool request"""
    tool_name: str
    parameters: Dict[str, Any]

class ToolResponse(BaseModel):
    """MCP tool response"""
    success: bool
    data: Dict[str, Any]
    error: str = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "FloatChat MCP API",
        "version": "1.0.0"
    }

@app.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    return {
        "tools": mcp_server.get_available_tools(),
        "count": len(mcp_server.get_available_tools())
    }

@app.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute an MCP tool"""
    try:
        result = mcp_server.execute_tool(request.tool_name, **request.parameters)
        
        if "error" in result:
            return ToolResponse(success=False, data=result, error=result["error"])
        
        return ToolResponse(success=True, data=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_argo_data(query: str, limit: int = 1000):
    """Direct query endpoint"""
    return mcp_server.execute_tool("query_argo_data", query=query, limit=limit)

@app.post("/sql-generate")
async def generate_sql(question: str, context: str = ""):
    """Generate SQL from natural language"""
    return mcp_server.execute_tool("generate_sql", question=question, context=context)

@app.get("/schema")
async def get_schema():
    """Get database schema"""
    return mcp_server.execute_tool("get_database_schema")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)