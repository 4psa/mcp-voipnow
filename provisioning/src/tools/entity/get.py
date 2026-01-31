import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Tool registry containing entity get tool configuration
TOOL_REGISTRY = {
    "get": {
        "allowed_keys": ["templateID", "serverID", "filter", "parentID", "parentIdentifier"],
        "method_type": "Get",
        "tool_name": "get",
        "tool_description": "Retrieve entities (users, organizations, service providers). Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). Use parentID to filter.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Entity type to retrieve: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
                    "enum": ["User", "Organization", "ServiceProvider"],
                },
                "templateID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Account template ID"
                },
                "serverID": {
                    "type": "string",
                    "description": "Set CTRLPANEL to filter only account added from 4PSA VoipNow control panel",
                },
                "filter": {
                    "type": "string",
                    "description": "Filter list",
                    "enum": ["name", "company", "email", "login"],
                },
                "parentID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Filter by parent ID: ServiceProvider ID shows Organizations, Organization ID shows Users."
                },
                "parentIdentifier": {
                    "type": "string",
                    "description": "Filter by parent identifier. Alternative to parentID.",
                },
            },
            "required": ["type"],
            "allOf": [
                {
                    "not": {
                        "allOf": [
                            {"required": ["parentID"]},
                            {"required": ["parentIdentifier"]}
                        ]
                    }
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
GET_TOOL_NAME = TOOL_REGISTRY["get"]["tool_name"]
GET_TOOL_DESCRIPTION = TOOL_REGISTRY["get"]["tool_description"]
GET_TOOL_SCHEMA = TOOL_SCHEMAS["get"]
METHOD_TYPE = TOOL_REGISTRY["get"]["method_type"]
ALLOWED_KEYS = TOOL_REGISTRY["get"]["allowed_keys"]


# Asynchronous function to get all users, organizations, or service providers
async def get(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve users, organizations, or service providers based on the provided parameters.

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
        GET_TOOL_SCHEMA,
        arguments["type"]  # Dynamic type based on arguments
    )
