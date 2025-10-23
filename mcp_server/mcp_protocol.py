"""
Model Context Protocol (MCP) Implementation
Follows MCP specification for tool-based AI interactions
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json


class MCPMessageType(Enum):
    """MCP message types"""
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"


@dataclass
class MCPToolDefinition:
    """MCP Tool Definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MCPToolCall:
    """MCP Tool Call Request"""
    name: str
    arguments: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            name=data['name'],
            arguments=data.get('arguments', {})
        )


@dataclass
class MCPToolResult:
    """MCP Tool Call Result"""
    content: List[Dict[str, Any]]
    isError: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


class MCPProtocol:
    """
    Implementation of Model Context Protocol
    Provides standardized interface for AI tool interactions
    """
    
    def __init__(self):
        self.tools: Dict[str, MCPToolDefinition] = {}
        self.tool_handlers: Dict[str, callable] = {}
    
    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: callable
    ):
        """Register a tool with MCP"""
        tool_def = MCPToolDefinition(
            name=name,
            description=description,
            inputSchema=input_schema
        )
        
        self.tools[name] = tool_def
        self.tool_handlers[name] = handler
        
        print(f"✅ Registered MCP tool: {name}")
    
    def list_tools(self) -> List[Dict]:
        """List all available tools (MCP standard)"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def call_tool(self, tool_call: MCPToolCall) -> MCPToolResult:
        """Execute a tool call (MCP standard)"""
        if tool_call.name not in self.tool_handlers:
            return MCPToolResult(
                content=[{
                    "type": "text",
                    "text": f"Tool '{tool_call.name}' not found"
                }],
                isError=True
            )
        
        try:
            # Execute tool handler
            handler = self.tool_handlers[tool_call.name]
            result = handler(**tool_call.arguments)
            
            # Format as MCP response
            return MCPToolResult(
                content=[{
                    "type": "text",
                    "text": json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                }],
                isError=False
            )
        
        except Exception as e:
            return MCPToolResult(
                content=[{
                    "type": "text",
                    "text": f"Tool execution error: {str(e)}"
                }],
                isError=True
            )
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict]:
        """Get schema for a specific tool"""
        tool = self.tools.get(tool_name)
        return tool.to_dict() if tool else None
    
    def validate_tool_arguments(self, tool_name: str, arguments: Dict) -> tuple[bool, str]:
        """Validate tool arguments against schema"""
        if tool_name not in self.tools:
            return False, f"Tool '{tool_name}' not found"
        
        tool = self.tools[tool_name]
        schema = tool.inputSchema
        
        # Check required fields
        required = schema.get('required', [])
        missing = [field for field in required if field not in arguments]
        
        if missing:
            return False, f"Missing required fields: {missing}"
        
        return True, "Valid"


# MCP Resource definitions for ARGO data
@dataclass
class MCPResource:
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mimeType: str


class MCPResourceProvider:
    """Provides MCP resources (data sources)"""
    
    def __init__(self):
        self.resources: Dict[str, MCPResource] = {}
    
    def register_resource(self, resource: MCPResource):
        """Register a data resource"""
        self.resources[resource.uri] = resource
    
    def list_resources(self) -> List[Dict]:
        """List all available resources"""
        return [asdict(r) for r in self.resources.values()]
    
    def read_resource(self, uri: str) -> Dict:
        """Read a resource by URI"""
        if uri not in self.resources:
            return {"error": f"Resource '{uri}' not found"}
        
        resource = self.resources[uri]
        # Return resource metadata
        return asdict(resource)


# MCP Prompt templates
@dataclass
class MCPPromptTemplate:
    """MCP Prompt Template"""
    name: str
    description: str
    arguments: List[Dict[str, Any]]


class MCPPromptProvider:
    """Provides MCP prompt templates"""
    
    def __init__(self):
        self.prompts: Dict[str, MCPPromptTemplate] = {}
    
    def register_prompt(self, prompt: MCPPromptTemplate):
        """Register a prompt template"""
        self.prompts[prompt.name] = prompt
    
    def list_prompts(self) -> List[Dict]:
        """List all prompt templates"""
        return [asdict(p) for p in self.prompts.values()]
    
    def get_prompt(self, name: str, arguments: Dict = None) -> Optional[str]:
        """Get a prompt template"""
        if name not in self.prompts:
            return None
        
        prompt = self.prompts[name]
        # Return prompt with filled arguments
        return asdict(prompt)