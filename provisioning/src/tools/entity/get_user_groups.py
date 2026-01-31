import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Tool registry containing entity get user groups tool configuration
TOOL_REGISTRY = {
    "get_user_groups": {
        "allowed_keys": ["ID", "identifier", "share"],
        "method_type": "GetGroups",
        "tool_name": "get-user-groups",
        "tool_description": "Get user groups by ID or identifier. Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Entity type: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
                    "enum": ["User"],
                    "default": "User",
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
                "share": {
                    "type": "boolean",
                    "description": "Groups that this extension can share info with",
                    "default": False,
                },
            },
            "required": ["type", "share"],
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
GET_USER_GROUPS_TOOL_NAME = TOOL_REGISTRY["get_user_groups"]["tool_name"]
GET_USER_GROUPS_TOOL_DESCRIPTION = TOOL_REGISTRY["get_user_groups"]["tool_description"]
GET_USER_GROUPS_TOOL_SCHEMA = TOOL_SCHEMAS["get_user_groups"]
METHOD_TYPE = TOOL_REGISTRY["get_user_groups"]["method_type"]
ALLOWED_KEYS = TOOL_REGISTRY["get_user_groups"]["allowed_keys"]


# Asynchronous function to get the list of user groups IDs
async def get_user_groups(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve a list of groups IDs for user by ID or identifier.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects.
    """
    # Use entity-specific execution with dynamic type
    return await utils._execute_operation(
        arguments, config, logger,
        METHOD_TYPE,
        ALLOWED_KEYS,
        GET_USER_GROUPS_TOOL_SCHEMA,
        arguments["type"]  # Dynamic type based on arguments
    )
