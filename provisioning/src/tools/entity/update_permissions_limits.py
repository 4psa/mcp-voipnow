import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Tool registry containing entity update permissions limits tool configuration
TOOL_REGISTRY = {
    "update_permissions_limits": {
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
            "multiUser", "ID", "identifier"
        ],
        "allowed_keys_organization": [
            "permsManag", "chargingPlanManag", "userMax", "ID", "identifier"
        ],
        "allowed_keys_service_provider": [
            "permsManag", "chargingPlanManag", "userMax", "organizationMax",
            "stackedManag", "organizationMax", "ID", "identifier"
        ],
        "method_type": "UpdatePL",
        "tool_name": "update-permissions-limits",
        "tool_description": "Update permissions/limits for entity by ID or identifier. Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Entity type: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User)",
                    "enum": ["User", "Organization", "ServiceProvider"],
                },
                "operation": {
                    "type": "string",
                    "description": "Available options for UpdateUserPL, UpdateOrganizationPL and UpdateServiceProviderPL",
                    "enum": ["increase", "decrease", "unlimited", "value"],
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
                },
                "accountExpireDays": {
                    "type": "string",
                    "description": "Account expiration number of days counted from setup, should be a number or 'unlimited' for no expiration",
                },
                "phoneExtMax": {
                    "type": "string",
                    "description": "The maximum number of phone terminal extensions for the entity, should be a number ",
                },
                "queueExtMax": {
                    "type": "string",
                    "description": "The maximum number of queue extensions for the entity, should be a number ",
                },
                "ivrExtMax": {
                    "type": "string",
                    "description": "The maximum number of IVR extensions for the entity, should be a number ",
                },
                "voicemailExtMax": {
                    "type": "string",
                    "description": "The maximum number of voicemail center extensions for the entity, should be a number ",
                },
                "queuecenterExtMax": {
                    "type": "string",
                    "description": "The maximum number of queue login center extensions for the entity, should be a number ",
                },
                "confExtMax": {
                    "type": "string",
                    "description": "The maximum number of conference extensions for the entity, should be a number ",
                },
                "callbackExtMax": {
                    "type": "string",
                    "description": "The maximum number of callback extensions for the entity, should be a number ",
                },
                "callbackCallerIDMax": {
                    "type": "string",
                    "description": "The maximum number of callback caller IDs for the entity, should be a number ",
                },
                "callCardExtMax": {
                    "type": "string",
                    "description": "The maximum number of call card extensions for the entity, should be a number ",
                },
                "callCardCodesMax": {
                    "type": "string",
                    "description": "The maximum number of call card codes for the entity, should be a number ",
                },
                "intercomExtMax": {
                    "type": "string",
                    "description": "The maximum number of intercom/paging extensions for the entity, should be a number ",
                },
                "concurentCalls": {
                    "type": "string",
                    "description": "The maximum number of public concurrent calls for the entity, should be a number ",
                },
                "concurentInternalCalls": {
                    "type": "string",
                    "description": "The maximum number of internal concurrent calls for the entity, should be a number ",
                },
                "queueMembersMax": {
                    "type": "string",
                    "description": "The maximum number of queue members for the entity, should be a number ",
                },
                "mailboxMax": {
                    "type": "string",
                    "description": "The maximum number of mailboxes for the entity, should be a number ",
                },
                "storage": {
                    "type": "string",
                    "description": "The maximum amount of storage(MB) for the entity, should be a number ",
                },
                "multiUser": {
                    "type": "boolean",
                    "description": "Multi user aware property for User entity",
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
                    "description": "The maximum number of users for the Organization entity, should be a number ",
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
                    "description": "The maximum number of organizations for the ServiceProvider entity, should be a number ",
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
                    "not": {
                        "allOf": [
                            {"required": ["accountExpire"]},
                            {"required": ["accountExpireDays"]}
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
UPDATE_PERMISSIONS_LIMITS_TOOL_NAME = TOOL_REGISTRY["update_permissions_limits"]["tool_name"]
UPDATE_PERMISSIONS_LIMITS_TOOL_DESCRIPTION = TOOL_REGISTRY["update_permissions_limits"]["tool_description"]
UPDATE_PERMISSIONS_LIMITS_TOOL_SCHEMA = TOOL_SCHEMAS["update_permissions_limits"]
METHOD_TYPE = TOOL_REGISTRY["update_permissions_limits"]["method_type"]

# Define allowed keys for the input arguments (backwards compatibility)
COMMON_ALLOWED_KEYS = TOOL_REGISTRY["update_permissions_limits"]["allowed_keys_common"]

USER_ALLOWED_KEYS = TOOL_REGISTRY["update_permissions_limits"]["allowed_keys_user"]
ORGANIZATION_ALLOWED_KEYS = TOOL_REGISTRY["update_permissions_limits"]["allowed_keys_organization"] 
SERVICE_PROVIDER_ALLOWED_KEYS = TOOL_REGISTRY["update_permissions_limits"]["allowed_keys_service_provider"]

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


# Asynchronous function to update permissions and limits for a user, organization, or service provider
async def update_permissions_limits(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Update permissions and limits for a user, organizations, or service providers by ID or identifier.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects.
    """
    # Preserve the complex data processing logic for unlimited values and operations
    for key in arguments:
        if (
            key in KEYS_THAT_ALLOW_UNLIMITED
            and arguments["operation"] is not None
            and arguments[key] is not None
            and key != "accountExpire"
        ):
            if arguments["operation"] == "unlimited":
                arguments[key] = {arguments["operation"]: True}
            else:
                arguments[key] = {arguments["operation"]: arguments[key]}

        if key == "accountExpire":
            if "operation" not in arguments:
                arguments[key] = {"_value_1": arguments[key], "unlimited": False}
            elif arguments["operation"] != "unlimited":
                logger.debug(f"Operation {arguments['operation']} could not be applied for accountExpire")
                arguments[key] = {"_value_1": arguments[key], "unlimited": False}

    # Use entity-specific execution with dynamic type
    return await utils._execute_operation(
        arguments, config, logger,
        METHOD_TYPE,
        ALLOWED_KEYS[arguments["type"]],
        UPDATE_PERMISSIONS_LIMITS_TOOL_SCHEMA,
        arguments["type"]  # Dynamic type based on arguments
    )
