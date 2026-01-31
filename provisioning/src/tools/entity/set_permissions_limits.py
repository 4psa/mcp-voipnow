import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Tool registry containing entity set permissions limits tool configuration
TOOL_REGISTRY = {
    "set_permissions_limits": {
        "allowed_keys_common": [
            "extensionManag", "extFeatureManag", "sipManag", "sipTrunkingManag",
            "soundManag", "numberManag", "callAPIManag", "callerIDManag",
            "provisionManag", "accountExpire", "accountExpireDays", "phoneExtMax",
            "queueExtMax", "ivrExtMax", "voicemailExtMax", "queuecenterExtMax",
            "confExtMax", "callbackExtMax", "callbackCallerIDMax", "callCardExtMax",
            "callCardCodesMax", "intercomExtMax", "concurentCalls", "concurentInternalCalls",
            "queueMembersMax", "mailboxMax", "storage"
        ],
        "allowed_keys_user": [
            "multiUser", "ID", "identifier", "shareVoicemail", "shareFaxes", 
            "shareRecordings", "shareCallHistory"
        ],
        "allowed_keys_organization": [
            "permsManag", "chargingPlanManag", "userMax", "ID", "identifier", "organizationType"
        ],
        "allowed_keys_service_provider": [
            "permsManag", "chargingPlanManag", "userMax", "organizationMax",
            "organizationManag", "stackedManag", "organizationMax", "ID", "identifier"
        ],
        "method_type": "SetPL",
        "tool_name": "set-permissions-limits",
        "tool_description": "Set permissions/limits for entity by ID or identifier. Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
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
                "extensionManag": {
                    "type": "boolean",
                    "description": "Enable extension and user management",
                },
                "extFeatureManag": {
                    "type": "boolean",
                    "description": "Enable extension features management",
                },
                "sipManag": {
                    "type": "boolean",
                    "description": "Enable Phone extension SIP management",
                },
                "sipTrunkingManag": {
                    "type": "boolean",
                    "description": "Enable SIP trunking management",
                },
                "soundManag": {
                    "type": "boolean",
                    "description": "Enable sound management",
                },
                "numberManag": {
                    "type": "boolean",
                    "description": "Enable Phone numbers management",
                },
                "callAPIManag": {
                    "type": "boolean",
                    "description": "Enable UnifiedAPI management",
                },
                "callerIDManag": {
                    "type": "boolean",
                    "description": "Enable CallerID management",
                },
                "provisionManag": {
                    "type": "string",
                    "description": "Enable Provision device management",
                    "enum": ["0", "2", "4"],
                    "default": "0",
                },
                "accountExpire": {
                    "type": "string",
                    "description": "Account expiration date, should be date format (YYYY-MM-DD) or 'unlimited' for no expiration",
                    "default": "unlimited",
                },
                "accountExpireDays": {
                    "type": "string",
                    "description": "Account expiration number of days counted from setup, should be a number or 'unlimited' for no expiration",
                    "default": "unlimited",
                },
                "phoneExtMax": {
                    "type": "string",
                    "description": "The maximum number of phone terminal extensions for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "queueExtMax": {
                    "type": "string",
                    "description": "The maximum number of queue extensions for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "ivrExtMax": {
                    "type": "string",
                    "description": "The maximum number of IVR extensions for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "voicemailExtMax": {
                    "type": "string",
                    "description": "The maximum number of voicemail center extensions for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "queuecenterExtMax": {
                    "type": "string",
                    "description": "The maximum number of queue login center extensions for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "confExtMax": {
                    "type": "string",
                    "description": "The maximum number of conference extensions for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "callbackExtMax": {
                    "type": "string",
                    "description": "The maximum number of callback extensions for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "callbackCallerIDMax": {
                    "type": "string",
                    "description": "The maximum number of callback caller IDs for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "callCardExtMax": {
                    "type": "string",
                    "description": "The maximum number of call card extensions for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "callCardCodesMax": {
                    "type": "string",
                    "description": "The maximum number of call card codes for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "intercomExtMax": {
                    "type": "string",
                    "description": "The maximum number of intercom/paging extensions for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "concurentCalls": {
                    "type": "string",
                    "description": "The maximum number of public concurrent calls for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "concurentInternalCalls": {
                    "type": "string",
                    "description": "The maximum number of internal concurrent calls for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "queueMembersMax": {
                    "type": "string",
                    "description": "The maximum number of queue members for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "mailboxMax": {
                    "type": "string",
                    "description": "The maximum number of mailboxes for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "storage": {
                    "type": "string",
                    "description": "The maximum amount of storage(MB) for the entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "multiUser": {
                    "type": "boolean",
                    "description": "Multi user aware property for User entity",
                },
                "shareVoicemail": {
                    "type": "string",
                    "description": "Share voicemail messages with other users for User entity, should be a groupID or 'everybody' for no restriction",
                },
                "shareFaxes": {
                    "type": "string",
                    "description": "Share faxes messages with other users for User entity, should be a groupID or 'everybody' for no restriction",
                },
                "shareRecordings": {
                    "type": "string",
                    "description": "Share recordings messages with other users for User entity, should be a groupID or 'everybody' for no restriction",
                },
                "shareCallHistory": {
                    "type": "string",
                    "description": "Share call history messages with other users for User entity, should be a groupID or 'everybody' for no restriction",
                },
                "permsManag": {
                    "type": "boolean",
                    "description": "Enable roles management for Organization entity",
                },
                "chargingPlanManag": {
                    "type": "boolean",
                    "description": "Enable charging plan management for Organization entity",
                },
                "userMax": {
                    "type": "string",
                    "description": "The maximum number of users for the Organization entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
                },
                "organizationType": {
                    "type": "string",
                    "description": "The type of the Organization entity, should be 0 for Business, 1 for Residential group.",
                    "enum": ["0", "1"],
                    "default": "0",
                },
                "organizationManag": {
                    "type": "boolean",
                    "description": "Enable organization management for ServiceProvider entity",
                },
                "stackedManag": {
                    "type": "boolean",
                    "description": "Enable See stacked phone numbers for ServiceProvider entity",
                },
                "organizationMax": {
                    "type": "string",
                    "description": "The maximum number of organizations for the ServiceProvider entity, should be a number or 'unlimited' for no limit",
                    "default": "unlimited",
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
                        {"required": ["accountExpire"]},
                        {"required": ["accountExpireDays"]}
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
SET_PERMISSIONS_LIMITS_TOOL_NAME = TOOL_REGISTRY["set_permissions_limits"]["tool_name"]
SET_PERMISSIONS_LIMITS_TOOL_DESCRIPTION = TOOL_REGISTRY["set_permissions_limits"]["tool_description"]
SET_PERMISSIONS_LIMITS_TOOL_SCHEMA = TOOL_SCHEMAS["set_permissions_limits"]
METHOD_TYPE = TOOL_REGISTRY["set_permissions_limits"]["method_type"]

# Define allowed keys for the input arguments (backwards compatibility)
COMMON_ALLOWED_KEYS = TOOL_REGISTRY["set_permissions_limits"]["allowed_keys_common"]

USER_ALLOWED_KEYS = TOOL_REGISTRY["set_permissions_limits"]["allowed_keys_user"]
ORGANIZATION_ALLOWED_KEYS = TOOL_REGISTRY["set_permissions_limits"]["allowed_keys_organization"] 
SERVICE_PROVIDER_ALLOWED_KEYS = TOOL_REGISTRY["set_permissions_limits"]["allowed_keys_service_provider"]

ALLOWED_KEYS = {
    "User": COMMON_ALLOWED_KEYS + USER_ALLOWED_KEYS,
    "Organization": COMMON_ALLOWED_KEYS + ORGANIZATION_ALLOWED_KEYS,
    "ServiceProvider": COMMON_ALLOWED_KEYS + SERVICE_PROVIDER_ALLOWED_KEYS,
}

KEYS_THAT_ALLOW_UNLIMITED = [
    "organizationMax",
    "userMax",
    "phoneExtMax",
    "queueExtMax",
    "ivrExtMax",
    "voicemailExtMax",
    "queuecenterExtMax",
    "confExtMax",
    "callbackExtMax",
    "callbackCallerIDMax",
    "callCardExtMax",
    "callCardCodesMax",
    "intercomExtMax",
    "concurentCalls",
    "concurentInternalCalls",
    "queueMembersMax",
    "mailboxMax",
    "storage",
    "accountExpireDays",
]

KEYS_THAT_ALLOW_EVERYBODY = [
    "shareVoicemail",
    "shareFaxes",
    "shareRecordings",
    "shareCallHistory",
]


# Asynchronous function to set permissions and limits for a user, organization, or service provider
async def set_permissions_limits(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Set permissions and limits for a user, organizations, or service providers by ID or identifier.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects.
    """
    # Preserve the complex data processing logic for unlimited/everybody values
    for key in arguments:
        if key in KEYS_THAT_ALLOW_UNLIMITED:
            if arguments[key] == "unlimited":
                arguments[key] = {"unlimited": True, "_value_1": 0}
            elif arguments[key].isnumeric():
                arguments[key] = {"unlimited": False, "_value_1": arguments[key]}

        if key in KEYS_THAT_ALLOW_EVERYBODY:
            if arguments[key] == "everybody":
                arguments[key] = {"everybody": True}
            elif arguments[key].isnumeric():
                arguments[key] = {"groupID": int(arguments[key])}

    # Use entity-specific execution with dynamic type
    return await utils._execute_operation(
        arguments, config, logger,
        METHOD_TYPE,
        ALLOWED_KEYS[arguments["type"]],
        SET_PERMISSIONS_LIMITS_TOOL_SCHEMA,
        arguments["type"]  # Dynamic type based on arguments
    )
