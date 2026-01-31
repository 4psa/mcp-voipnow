import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters, McpError
from pathlib import Path

# Load .env from the project root directory
env_path = Path(__file__).parent.parent / '.env'
if not env_path.exists():
    raise FileNotFoundError(f"Environment file not found at {env_path}")
load_dotenv(env_path)

class MCPAgent:
    def __init__(self) -> None:    
        self.server_params = StdioServerParameters(
            command="node",
            args=["../dist/index.js","--config", "../config.json"],
        )
        self.valid_tools: List[str] = []

    async def initialize(self) -> bool:
        """Initialize connection and list available tools"""
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    self.valid_tools = [t.name for t in tools.tools]
                    print("Available MCP Tools:")
                    print(json.dumps(self.valid_tools, indent=2))
                    return True
        except McpError as e:
            print(f"MCP Connection Error [{e.code}]: {e.message}")
            return False
        except Exception as e:
            print(f"Unexpected error during initialization: {str(e)}")
            return False

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a specified tool with given parameters"""
        if tool_name not in self.valid_tools:
            raise ValueError(f"Invalid tool: {tool_name}")
        
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, params)
                    if not result:
                        print(f"No result from {tool_name}")
                        return None
                        
                    if not hasattr(result, 'content'):
                        print(f"Result has no content attribute: {result}")
                        return None
                        
                    if not result.content:
                        print(f"Result content is empty for {tool_name}")
                        return None
                    
                    response_text = result.content[0].text
                    try:
                        parsed = json.loads(response_text)
                        print(f"\nResponse from {tool_name}:")
                        print(json.dumps(parsed, indent=2))
                        
                        if "error" in parsed:
                            error = parsed["error"]
                            if error["code"] == "access_denied":
                                print(f"Authorization error: {error['message']}")
                                print("Please check your VOIPNOW_URL_TOKEN and permissions")
                                return None
                            print(f"API error: [{error['code']}] {error['message']}")
                            return None
                            
                        return parsed
                    except json.JSONDecodeError:
                        print(f"Failed to parse response as JSON: {response_text}")
                        return None
                    
        except McpError as e:
            print(f"Tool Error ({tool_name}) [{e.code}]: {e.message}")
            return None
        except Exception as e:
            print(f"Unexpected error during tool execution: {str(e)}")
            return None

    async def get_active_calls(self, extension: str) -> Optional[Dict[str, Any]]:
        """Get active calls for the specified extension"""
        try:
            result = await self.execute_tool("phone-calls-list", {
                "extension": extension,
                "userId": "@me"
            })
            
            if result and isinstance(result, dict):
                if "entry" in result and result["entry"]:
                    print("\nActive calls found:")
                    print(json.dumps(result["entry"], indent=2))
                    return result
                else:
                    print("No active calls in the response")
            else:
                print(f"Invalid response format: {result}")
            
            return None
        except Exception as e:
            print(f"Error getting active calls: {str(e)}")
            return None

    async def create_test_call(self, extension: str, destination: str) -> Optional[Dict[str, Any]]:
        """Create a test call and return its details"""
        try:
            print("\nCreating a test call...")
            create_result = await self.execute_tool("phone-calls-create", {
                "type": "simple",
                "source": [extension],
                "destination": [destination],
                "extension": extension,
                "userId": "@me",
                "nonce": datetime.now().strftime("%Y%m%d%H%M%S")
            })
            
            if create_result:
                print("Test call created")
                await asyncio.sleep(2)  # Wait for call to be established
                return await self.get_active_calls(extension)
            
            print("Failed to create test call")
            return None
            
        except Exception as e:
            print(f"Error creating test call: {str(e)}")
            return None

    async def delete_call(self, extension: str, call_id: str) -> bool:
        """Delete a call"""
        try:
            result = await self.execute_tool("phone-calls-delete", {
                "userId": "@me",
                "extension": extension,
                "phoneCallId": call_id
            })
            return result is not None
        except Exception as e:
            print(f"Error deleting call: {str(e)}")
            return False
