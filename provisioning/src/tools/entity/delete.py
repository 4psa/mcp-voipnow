import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Tool registry containing entity delete tool configuration
TOOL_REGISTRY = {
    "delete": {
        "allowed_keys": ["ID", "identifier"],
        "method_type": "Delete",
        "tool_name": "delete",
        "tool_description": "Delete entity (users, organizations, service providers). Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). WARNING: Deleting higher-level entities cascades to children.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Entity type to delete: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). Cascades to children.",
                    "enum": ["User", "Organization", "ServiceProvider"],
                },
                "ID": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                        "minimum": 0,
                    },
                    "description": "IDs of entities to delete (may cascade to children).",
                },
                "identifier": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "description": "Identifiers of entities to delete. Alternative to ID (may cascade to children).",
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
DELETE_TOOL_NAME = TOOL_REGISTRY["delete"]["tool_name"]
DELETE_TOOL_DESCRIPTION = TOOL_REGISTRY["delete"]["tool_description"]
DELETE_TOOL_SCHEMA = TOOL_SCHEMAS["delete"]
METHOD_TYPE = TOOL_REGISTRY["delete"]["method_type"]
ALLOWED_KEYS = TOOL_REGISTRY["delete"]["allowed_keys"]


# Asynchronous function to delete a user, organization, or service provider
async def delete(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Delete a user, organization, or service provider by ID or identifier.

    Args:
        arguments (dict): The input arguments containing either 'ID' or 'identifier'.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    # Use entity-specific execution with dynamic type
    return await utils._execute_operation(
        arguments, config, logger,
        METHOD_TYPE,
        ALLOWED_KEYS,
        DELETE_TOOL_SCHEMA,
        arguments["type"]  # Dynamic type based on arguments
    )
