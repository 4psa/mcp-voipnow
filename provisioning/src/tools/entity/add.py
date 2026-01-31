import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Tool registry containing entity add tool configuration
TOOL_REGISTRY = {
    "add": {
        "allowed_keys_common": [
            "login", "firstName", "lastName", "company", "email", "passwordAuto", 
            "password", "forceUpdate", "phone", "fax", "address", "city", "pcode", 
            "country", "region", "timezone", "interfaceLang", "notes", "serverID", 
            "chargingIdentifier", "subscriptionID"
        ],
        "allowed_keys_user": [
            "phoneLang", "channelRuleID", "role", "templateID", "parentID", 
            "parentIdentifier", "parentLogin", "fromUser", "fromUserIdentifier", 
            "chargingPlanID", "chargingPlanIdentifier", "verbose", "notifyOnly", 
            "otherNotifyEmail", "dku", "accountFlag"
        ],
        "allowed_keys_organization": [
            "templateID", "channelRuleID", "identifier", "parentID", "parentIdentifier", 
            "parentLogin", "fromUser", "fromUserIdentifier", "chargingPlanID", 
            "chargingPlanIdentifier", "verbose", "notifyOnly", "otherNotifyEmail", 
            "linkResourceID", "linkUUID", "dku", "accountFlag"
        ],
        "allowed_keys_service_provider": [
            "channelRuleID", "chargingPlanID", "chargingPlanIdentifier", "templateID", 
            "parentID", "parentIdentifier", "verbose", "notifyOnly",
            "otherNotifyEmail", "linkResourceID", "linkUUID", "dku", "accountFlag"
        ],
        "method_type": "Add",
        "tool_name": "add",
        "tool_description": "Add entity (users, organizations, service providers). Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User).",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Entity type to add: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
                    "enum": ["User", "Organization", "ServiceProvider"],
                },
                "login": {"type": "string", "description": "The login for the entity"},
                "firstName": {"type": "string", "description": "The first name for the entity"},
                "lastName": {"type": "string", "description": "The last name for the entity"},
                "company": {"type": "string", "description": "The company for the entity"},
                "email": {"type": "string", "description": "The email for the entity"},
                "passwordAuto": {
                    "type": "boolean",
                    "description": "The password auto generation for the entity",
                    "default": False,
                },
                "password": {"type": "string", "description": "The password for the entity"},
                "forceUpdate": {
                    "type": "boolean",
                    "description": "The force update for entity on duplicate login",
                    "default": False,
                },
                "phone": {"type": "string", "description": "The phone for the entity"},
                "fax": {"type": "string", "description": "The fax for the entity"},
                "address": {"type": "string", "description": "The address for the entity"},
                "city": {"type": "string", "description": "The city for the entity"},
                "pcode": {"type": "string", "description": "The postal code for the entity"},
                "country": {"type": "string", "description": "The country for the entity"},
                "region": {"type": "string", "description": "The region for the entity"},
                "timezone": {"type": "string", "description": "The timezone for the entity"},
                "interfaceLang": {"type": "string", "description": "The interface language for the entity"},
                "notes": {"type": "string", "description": "The notes for the entity"},
                "serverID": {"type": "integer", "description": "The server ID for the entity"},
                "chargingIdentifier": {"type": "string", "description": "The charging identifier for the entity"},
                "subscriptionID": {"type": "string", "description": "The subscription ID for the entity"},
                "phoneLang": {"type": "string", "description": "The phone language for the user"},
                "channelRuleID": {"type": "integer", "description": "The channel rule ID for the user"},
                "role": {
                    "type": "string", 
                    "enum": ["admin", "reseller", "user"], 
                    "description": "The role for the user"
                },
                "templateID": {"type": "integer", "description": "The template ID for the user"},
                "parentID": {"type": "integer", "minimum": 0, "description": "Parent ID: ServiceProvider ID for Organizations, Organization ID for Users. Not needed for ServiceProviders."},
                "parentIdentifier": {"type": "string", "description": "Parent identifier: ServiceProvider identifier for Organizations, Organization identifier for Users. Alternative to parentID."},
                "parentLogin": {"type": "string", "description": "Parent login: ServiceProvider login for Organizations, Organization login for Users. Alternative to parentID."},
                "fromUser": {"type": "string", "description": "Context user ID for admin delegation (when creating on behalf of others)."},
                "fromUserIdentifier": {"type": "string", "description": "Context user identifier for admin delegation. Alternative to fromUser."},
                "chargingPlanID": {"type": "integer", "description": "The charging plan ID for the entity"},
                "chargingPlanIdentifier": {"type": "string", "description": "The charging plan identifier for the entity"},
                "verbose": {
                    "type": "boolean",
                    "description": "Response verbosity. Set 1 to receive detailed information on newly created account",
                    "default": False,
                },
                "notifyOnly": {
                    "type": "string",
                    "description": "Mask of 4 bits to setup notification preferences",
                },
                "otherNotifyEmail": {
                    "type": "string",
                    "description": "Additional notification email for the entity",
                },
                "dku": {"type": "string", "description": "DKU for the user"},
                "accountFlag": {"type": "string", "description": "Account flag for the user"},
                "identifier": {"type": "string", "description": "The identifier for the entity"},
                "linkResourceID": {"type": "string", "description": "Link resource ID for the entity"},
                "linkUUID": {"type": "string", "description": "Link UUID for the entity"},
            },
            "required": ["type"],
            "allOf": [
                {
                    "if": {"properties": {"type": {"const": "User"}}},
                    "then": {
                        "required": ["login"],
                        "allOf": [
                            {
                                "not": {
                                    "allOf": [
                                        {"required": ["fromUser"]},
                                        {"required": ["fromUserIdentifier"]}
                                    ]
                                }
                            },
                            {
                                "oneOf": [
                                    {"required": ["parentID"]},
                                    {"required": ["parentIdentifier"]},
                                    {"required": ["parentLogin"]}
                                ]
                            }
                        ]
                    }
                },
                {
                    "if": {"properties": {"type": {"const": "Organization"}}},
                    "then": {
                        "required": ["login"],
                        "oneOf": [
                            {"required": ["parentID"]},
                            {"required": ["parentIdentifier"]},
                            {"required": ["parentLogin"]}
                        ]
                    }
                },
                {
                    "if": {"properties": {"type": {"const": "ServiceProvider"}}},
                    "then": {"required": ["login"]}
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
ADD_TOOL_NAME = TOOL_REGISTRY["add"]["tool_name"]
ADD_TOOL_DESCRIPTION = TOOL_REGISTRY["add"]["tool_description"]
ADD_TOOL_SCHEMA = TOOL_SCHEMAS["add"]
METHOD_TYPE = TOOL_REGISTRY["add"]["method_type"]

# Define allowed keys for the input arguments (backwards compatibility)
COMMON_ALLOWED_KEYS = TOOL_REGISTRY["add"]["allowed_keys_common"]

USER_ALLOWED_KEYS = TOOL_REGISTRY["add"]["allowed_keys_user"]
ORGANIZATION_ALLOWED_KEYS = TOOL_REGISTRY["add"]["allowed_keys_organization"] 
SERVICE_PROVIDER_ALLOWED_KEYS = TOOL_REGISTRY["add"]["allowed_keys_service_provider"]

ALLOWED_KEYS = {
    "User": COMMON_ALLOWED_KEYS + USER_ALLOWED_KEYS,
    "Organization": COMMON_ALLOWED_KEYS + ORGANIZATION_ALLOWED_KEYS,
    "ServiceProvider": COMMON_ALLOWED_KEYS + SERVICE_PROVIDER_ALLOWED_KEYS,
}


# Asynchronous function to add a user, organization, or service provider
async def add(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Add a user, organization, or service provider based on the provided parameters.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects.
    """
    # If no password is provided, set passwordAuto to True
    if "password" not in arguments or arguments["password"] is None:
        arguments["passwordAuto"] = True

    # Use entity-specific execution with dynamic type
    return await utils._execute_operation(
        arguments, config, logger,
        METHOD_TYPE,
        ALLOWED_KEYS[arguments["type"]],
        ADD_TOOL_SCHEMA,
        arguments["type"]  # Dynamic type based on arguments
    )
