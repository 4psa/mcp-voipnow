import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Tool registry containing entity edit tool configuration
TOOL_REGISTRY = {
    "edit": {
        "allowed_keys_common": [
            "login", "firstName", "lastName", "company", "email", "passwordAuto",
            "password", "forceUpdate", "phone", "fax", "address", "city", "pcode",
            "country", "region", "timezone", "interfaceLang", "notes", "serverID",
            "chargingIdentifier", "subscriptionID"
        ],
        "allowed_keys_user": [
            "phoneLang", "channelRuleID", "role", "ID", "identifier", "fromUser",
            "fromUserIdentifier", "chargingPlanID", "chargingPlanIdentifier", 
            "verbose", "notifyOnly", "otherNotifyEmail", "dku", "accountFlag"
        ],
        "allowed_keys_organization": [
            "ID", "identifier", "fromUser", "fromUserIdentifier", "chargingPlanID",
            "chargingPlanIdentifier", "verbose", "notifyOnly", "otherNotifyEmail",
            "linkResourceID", "linkUUID", "dku", "accountFlag"
        ],
        "allowed_keys_service_provider": [
            "ID", "identifier", "chargingPlanID", "chargingPlanIdentifier", "verbose",
            "notifyOnly", "otherNotifyEmail", "linkResourceID", "linkUUID",
            "dku", "accountFlag"
        ],
        "method_type": "Edit",
        "tool_name": "edit",
        "tool_description": "Edit entity (users, organizations, service providers). Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). Specify entity with ID or identifier.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Entity type to edit: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
                    "enum": ["User", "Organization", "ServiceProvider"]
                },
                "login": {"type": "string", "description": "The login for the entity"},
                "firstName": {"type": "string", "description": "The first name for the entity"},
                "lastName": {"type": "string", "description": "The last name for the entity"},
                "company": {"type": "string", "description": "The company for the entity"},
                "email": {"type": "string", "description": "The email for the entity", "format": "email"},
                "passwordAuto": {
                    "type": "boolean",
                    "description": "The password auto generation for the entity",
                    "default": False,
                },
                "password": {"type": "string", "description": "The password for the entity"},
                "forceUpdate": {
                    "type": "boolean",
                    "description": "The force update for entity on duplicate login (new login computed)",
                    "default": False,
                },
                "phone": {"type": "string", "description": "The phone number for the entity"},
                "fax": {"type": "string", "description": "The fax number for the entity"},
                "address": {"type": "string", "description": "The address for the entity"},
                "city": {"type": "string", "description": "The city for the entity"},
                "pcode": {"type": "string", "description": "The postal code for the entity"},
                "country": {"type": "string", "description": "The country for the entity"},
                "region": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "The region for the entity. Use PBX:GetRegions method fot the list of all available regions",
                },
                "timezone": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "The timezone for the entity. Use PBX:GetTimezone method fot the list of all available timezones",
                },
                "interfaceLang": {"type": "string", "description": "The interface language for the entity"},
                "notes": {"type": "string", "description": "The notes for the entity"},
                "serverID": {
                    "type": "string",
                    "description": "Set CTRLPANEL to filter only account added from 4PSA VoipNow control panel",
                },
                "chargingIdentifier": {"type": "string", "description": "The charging identifier for the entity"},
                "subscriptionID": {"type": "string", "description": "The subscription ID attached to the account for the entity"},
                "phoneLang": {"type": "string", "description": "The language for the phone number for the user"},
                "channelRuleID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Outgoing routing rules group id for the user",
                },
                "role": {
                    "type": "string",
                    "description": "The role for the user",
                    "enum": ["member", "administrator", "owner"],
                    "default": "member",
                },
                "templateID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Account template ID",
                },
                "fromUser": {"type": "string", "description": "Context user ID for admin delegation."},
                "fromUserIdentifier": {"type": "string", "description": "Context user identifier for admin delegation. Alternative to fromUser."},
                "chargingPlanID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "The charging plan ID for the entity",
                },
                "chargingPlanIdentifier": {"type": "string", "description": "The charging plan identifier for the entity"},
                "ID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "ID of entity to edit.",
                },
                "identifier": {"type": "string", "description": "Identifier of entity to edit. Alternative to ID."},
                "verbose": {
                    "type": "boolean",
                    "description": "Response verbosity. Set 1 to receive detailed information on newly created account",
                    "default": False,
                },
                "notifyOnly": {"type": "string", "description": "Mask of 4 bits to setup notification preferences"},
                "otherNotifyEmail": {"type": "string", "description": "Additional notification email for the entity"},
                "dku": {"type": "string", "description": "DKU for the user"},
                "accountFlag": {"type": "string", "description": "Account flag for the user"},
                "linkResourceID": {"type": "string", "description": "Link resource ID for the entity"},
                "linkUUID": {"type": "string", "description": "Link UUID for the entity"},
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
                    "not": {
                        "allOf": [
                            {"required": ["chargingPlanID"]},
                            {"required": ["chargingPlanIdentifier"]}
                        ]
                    }   
                },
                {
                    "if": {
                        "not": {
                            "properties": {"type": {"const": "ServiceProvider"}}
                        }
                    },
                    "then": {
                        "not": {
                            "allOf": [
                                {"required": ["fromUser"]},
                                {"required": ["fromUserIdentifier"]}
                            ]
                        }
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
EDIT_TOOL_NAME = TOOL_REGISTRY["edit"]["tool_name"]
EDIT_TOOL_DESCRIPTION = TOOL_REGISTRY["edit"]["tool_description"]
EDIT_TOOL_SCHEMA = TOOL_SCHEMAS["edit"]
METHOD_TYPE = TOOL_REGISTRY["edit"]["method_type"]

# Define allowed keys for the input arguments (backwards compatibility)
COMMON_ALLOWED_KEYS = TOOL_REGISTRY["edit"]["allowed_keys_common"]

USER_ALLOWED_KEYS = TOOL_REGISTRY["edit"]["allowed_keys_user"]
ORGANIZATION_ALLOWED_KEYS = TOOL_REGISTRY["edit"]["allowed_keys_organization"] 
SERVICE_PROVIDER_ALLOWED_KEYS = TOOL_REGISTRY["edit"]["allowed_keys_service_provider"]

ALLOWED_KEYS = {
    "User": COMMON_ALLOWED_KEYS + USER_ALLOWED_KEYS,
    "Organization": COMMON_ALLOWED_KEYS + ORGANIZATION_ALLOWED_KEYS,
    "ServiceProvider": COMMON_ALLOWED_KEYS + SERVICE_PROVIDER_ALLOWED_KEYS,
}


# Asynchronous function to edit a user, organization, or service provider
async def edit(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Edit a user, organization, or service provider based on the provided parameters.

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
        ALLOWED_KEYS[arguments["type"]],
        EDIT_TOOL_SCHEMA,
        arguments["type"]  # Dynamic type based on arguments
    )
