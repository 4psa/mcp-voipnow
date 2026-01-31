import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Tool registry containing entity get permissions limits tool configuration
TOOL_REGISTRY = {
    "get_permissions_limits": {
        "allowed_keys": ["ID", "identifier"],
        "method_type": "GetPL",
        "tool_name": "get-permissions-limits",
        "tool_description": "Get permissions/limits for entity by ID or identifier. Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Entity type: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
                    "enum": ["User", "Organization", "ServiceProvider"],
                },
                "ID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Entity ID"
                },
                "identifier": {
                    "type": "string",
                    "description": "Entity identifier. Alternative to ID.",
                },
            },
            "required": ["type"],
            "allOf": [
                {
                    "oneOf": [
                        {"required": ["ID"]},
                        {"required": ["identifier"]}
                    ]
                }
            ]
        }
    }
}

# Generate tool schema
def _create_tool_schema(tool_config: Dict[str, Any]) -> types.Tool:
    """Create a Tool schema from configuration."""
    return types.Tool(
        name=tool_config["tool_name"],
        description=tool_config["tool_description"],
        inputSchema=tool_config["input_schema"]
    )

# Create tool schema
TOOL_SCHEMAS = {
    func_name: _create_tool_schema(config) 
    for func_name, config in TOOL_REGISTRY.items()
}

# Backwards compatibility constants
GET_PERMISSIONS_LIMITS_TOOL_NAME = TOOL_REGISTRY["get_permissions_limits"]["tool_name"]
GET_PERMISSIONS_LIMITS_TOOL_DESCRIPTION = TOOL_REGISTRY["get_permissions_limits"]["tool_description"]
GET_PERMISSIONS_LIMITS_TOOL_SCHEMA = TOOL_SCHEMAS["get_permissions_limits"]
METHOD_TYPE = TOOL_REGISTRY["get_permissions_limits"]["method_type"]
ALLOWED_KEYS = TOOL_REGISTRY["get_permissions_limits"]["allowed_keys"]


# Asynchronous function to get permissions and limits for a user, organization, or service provider
async def get_permissions_limits(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve permissions and limits for a user, organizations, or service providers by ID or identifier.

    Args:
        arguments (dict): The input arguments either 'ID' or 'identifier'.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects.
    """
    # Use entity-specific execution with dynamic type
    return await utils._execute_operation(
        arguments, config, logger,
        METHOD_TYPE,
        ALLOWED_KEYS,
        GET_PERMISSIONS_LIMITS_TOOL_SCHEMA,
        arguments["type"]  # Dynamic type based on arguments
    )
