#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/abuzaid/Desktop/final/netcdf/FloatChat')

from mcp_server.mcp_protocol import MCPToolResult

# Test 1: Default isError should be False
result = MCPToolResult(content=[{"type": "text", "text": "success"}])
print(f"✓ isError default: {result.isError}")
assert result.isError == False, "isError should default to False"

# Test 2: to_dict should work
d = result.to_dict()
print(f"✓ to_dict works: {d}")
assert 'isError' in d, "to_dict should include isError"
assert d['isError'] == False, "isError in dict should be False"

# Test 3: Setting isError to True
error_result = MCPToolResult(content=[{"type": "text", "text": "error"}], isError=True)
print(f"✓ isError can be set: {error_result.isError}")
assert error_result.isError == True

print("\n✅ All tests passed! MCP protocol fixed.")
