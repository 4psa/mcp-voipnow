import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Tool registry containing entity move organization tool configuration
TOOL_REGISTRY = {
    "move_organization": {
        "allowed_keys": [
            "ID", "identifier", "serviceProviderID", "serviceProviderIdentifier",
            "chargingPlanID", "chargingPlanIdentifier"
        ],
        "method_type": "Move",
        "tool_name": "move-organization",
        "tool_description": "Move Organization to different ServiceProvider. Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). Keeps all child Users/Extensions.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Entity type to move (only Organizations can move between ServiceProviders)",
                    "enum": ["Organization"],
                },
                "ID": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                        "minimum": 0, 
                    },
                    "description": "Organization IDs to move to new ServiceProvider.",
                },
                "identifier": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "description": "Organization identifiers to move. Alternative to ID.",
                },
                "serviceProviderID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Target ServiceProvider ID (new parent for Organizations).",
                },
                "serviceProviderIdentifier": {
                    "type": "string",
                    "description": "Target ServiceProvider identifier. Alternative to serviceProviderID.",
                },
                "chargingPlanID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Charging plan ID for moved Organizations.",
                },
                "chargingPlanIdentifier": {
                    "type": "string",
                    "description": "Charging plan identifier. Alternative to chargingPlanID.",
                },
            },
            "required": ["type"],
            "allOf": [
                {
                    "oneOf": [
                        {"required": ["ID"]},
                        {"required": ["identifier"]}
                    ]
                },
                {
                    "oneOf": [
                        {"required": ["serviceProviderID"]},
                        {"required": ["serviceProviderIdentifier"]}
                    ]
                },
                {
                    "oneOf": [
                        {"required": ["chargingPlanID"]},
                        {"required": ["chargingPlanIdentifier"]}
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
MOVE_ORGANIZATION_TOOL_NAME = TOOL_REGISTRY["move_organization"]["tool_name"]
MOVE_ORGANIZATION_TOOL_DESCRIPTION = TOOL_REGISTRY["move_organization"]["tool_description"]
MOVE_ORGANIZATION_TOOL_SCHEMA = TOOL_SCHEMAS["move_organization"]
METHOD_TYPE = TOOL_REGISTRY["move_organization"]["method_type"]
ALLOWED_KEYS = TOOL_REGISTRY["move_organization"]["allowed_keys"]


# Asynchronous function to move organization to a specific service provider
async def move_organization(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Move organization to a specific service provider.

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
        MOVE_ORGANIZATION_TOOL_SCHEMA,
        arguments["type"]  # Dynamic type based on arguments
    )
