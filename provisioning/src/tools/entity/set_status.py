import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Tool registry containing entity set status tool configuration
TOOL_REGISTRY = {
    "set_status": {
        "allowed_keys": ["status", "phoneStatus", "ID", "identifier"],
        "method_type": "SetStatus",
        "tool_name": "set-status",
        "tool_description": "Set status for entity by ID or identifier. Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Entity type: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
                    "enum": ["User", "Organization", "ServiceProvider"],
                },
                "status": {
                    "type": "boolean",
                    "description": "The status for the entity",
                },
                "phoneStatus": {
                    "type": "string",
                    "description": "The phone status for the entity",
                    "enum": ["1", "16", "32", "64"],
                    "default": "1",
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
SET_STATUS_TOOL_NAME = TOOL_REGISTRY["set_status"]["tool_name"]
SET_STATUS_TOOL_DESCRIPTION = TOOL_REGISTRY["set_status"]["tool_description"]
SET_STATUS_TOOL_SCHEMA = TOOL_SCHEMAS["set_status"]
METHOD_TYPE = TOOL_REGISTRY["set_status"]["method_type"]
ALLOWED_KEYS = TOOL_REGISTRY["set_status"]["allowed_keys"]


# Asynchronous function to set status for a user, organization, or service provider
async def set_status(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Set status for a user, organization, or service provider by ID or identifier.

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
        TOOL_SCHEMAS["set_status"],
        arguments["type"]  # Dynamic type based on arguments
    )
