import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Define type
TYPE = "Extension"

# Tool registry containing all Extension tool configurations
TOOL_REGISTRY = {
    "add_extension": {
        "allowed_keys": [
            "extensionNo", "templateID", "extensionType", "label", "password",
            "passwordAuto", "forceUpdate", "parentID", "parentIdentifier",
            "parentLogin", "fromUser", "fromUserIdentifier", "verbose",
            "notifyOnly", "otherNotifyEmail"
        ],
        "method_type": "AddExtension",
        "tool_name": "add-extension",
        "tool_description": "Add extension to a User. Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). Extensions belong to Users (parentID = User ID).",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "extensionNo": {
                    "type": "string",
                    "description": "The extension number to add",
                },
                "templateID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Template ID",
                },
                "extensionType": {
                    "type": "string",
                    "description": "The type of extension to add",
                    "enum": [
                        "term", "phoneQueue", "ivr", "voicecenter", "conference",
                        "callback", "callcard", "intercom", "queuecenter"
                    ],
                    "default": "term",
                },
                "label": {
                    "type": "string",
                    "description": "The label for the extension",
                },
                "password": {
                    "type": "string",
                    "description": "The password for the extension",
                },
                "passwordAuto": {
                    "type": "boolean",
                    "description": "The password auto generation for the entity",
                    "default": False,
                },
                "forceUpdate": {
                    "type": "boolean",
                    "description": "The force update for entity on duplicate login (new login computed)",
                    "default": False,
                },
                "parentID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "User ID that owns this extension.",
                },
                "parentIdentifier": {
                    "type": "string",
                    "description": "User identifier that owns this extension. Alternative to parentID.",
                },
                "parentLogin": {
                    "type": "string",
                    "description": "User login that owns this extension. Alternative to parentID.",
                },
                "fromUser": {
                    "type": "string",
                    "description": "Context user ID for admin delegation.",
                },
                "fromUserIdentifier": {
                    "type": "string",
                    "description": "Context user identifier for admin delegation. Alternative to fromUser.",
                },
                "verbose": {
                    "type": "boolean",
                    "description": "Response verbosity. Set 1 to receive detailed information on newly created account",
                    "default": False,
                },
                "notifyOnly": {
                    "type": "string",
                    "description": "Mask of 4 bits to setup notification preferences ASPOU (ADMIN{0/1}, SERVICE_PROVIDER{0/1}, ORGANIZATION{0/1}, USER{0/1})",
                },
                "otherNotifyEmail": {
                    "type": "string",
                    "description": "Additional notification email for the entity. The email address where to send email when a new account is created; usually used in automation.",
                },
            },
            "required": ["extensionNo", "label"],
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
    "get_extensions": {
        "allowed_keys": ["extensionType", "templateID", "filter", "parentID", "parentIdentifier"],
        "method_type": "GetExtensions",
        "tool_name": "get-extensions",
        "tool_description": "Retrieve extensions. Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). Filter by User with parentID.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "extensionType": {
                    "type": "string",
                    "description": "The type of extension to retrieve",
                    "enum": [
                        "term", "phoneQueue", "ivr", "voicecenter", "conference",
                        "callback", "callcard", "intercom", "queuecenter"
                    ],
                    "default": "term",
                },
                "templateID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Template ID"
                },
                "filter": {
                    "type": "string",
                    "description": "The filter for the entity",
                    "enum": ["name", "company", "email", "login"],
                },
                "parentID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "User ID to filter extensions (shows User's extensions)."
                },
                "parentIdentifier": {
                    "type": "string",
                    "description": "User identifier to filter extensions. Alternative to parentID.",
                },
            },
            "required": [],
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
    },
    "delete_extension": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "DeleteExtension",
        "tool_name": "delete-extension",
        "tool_description": "Delete the extension for the provided extended number",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "extendedNumber": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "description": "A list of extension extended numbers to be deleted",
                }
            },
            "required": ["extendedNumber"],
        }
    },
    "get_provision_file": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "GetProvisionFile",
        "tool_name": "get-provision-file",
        "tool_description": "Retrieve the provision file for the provided extended number",
        "input_schema": {
            "type": "object",
            "properties": {
                "extendedNumber": {"type": "string"}
            },
            "required": ["extendedNumber"],
            "additionalProperties": False,
        }
    },
    "get_queue_agents": {
        "allowed_keys": ["extendedNumber", "filter"],
        "method_type": "GetQueueAgents",
        "tool_name": "get-queue-agents",
        "tool_description": "Retrieve the agents for the provided queue",
        "input_schema": {
            "type": "object",
            "properties": {
                "extendedNumber": {"type": "string"},
                "filter": {
                    "type": "string",
                    "enum": ["all", "local", "remote"],
                    "default": "all",
                },
            },
            "required": ["extendedNumber"],
            "additionalProperties": False,
        }
    },
    "get_queue_membership": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "GetQueueMembership",
        "tool_name": "get-queue-membership",
        "tool_description": "Retrieve the membership for the provided queue",
        "input_schema": {
            "type": "object",
            "properties": {
                "extendedNumber": {"type": "string"}
            },
            "required": ["extendedNumber"],
            "additionalProperties": False,
        }
    },
    "get_scheduled_conferences": {
        "allowed_keys": ["extendedNumber", "filter", "interval"],
        "method_type": "GetScheduledConferences",
        "tool_name": "get-scheduled-conferences",
        "tool_description": "Retrieve the scheduled conferences for the provided extension",
        "input_schema": {
            "type": "object",
            "properties": {
                "filter": {"type": "string"},
                "interval": {
                    "type": "string",
                    "enum": ["anytime", "today", "tomorrow", "next_week", "next_month", "in_the_past"],
                    "default": "anytime",
                },
                "extendedNumber": {"type": "string"},
            },
            "required": ["extendedNumber"],
            "allOf": [
                {
                    "not": {
                        "allOf": [
                            {"required": ["filter"]},
                            {"required": ["interval"]},
                        ]
                    }
                }
            ],
            "additionalProperties": False,
        }
    },
    "get_scheduled_conference_sessions": {
        "allowed_keys": ["extendedNumber", "started", "ended", "conferenceNumber"],
        "method_type": "GetScheduledConferenceSessions",
        "tool_name": "get-scheduled-conference-sessions",
        "tool_description": "Retrieve the scheduled conference sessions for the provided extension",
        "input_schema": {
            "type": "object",
            "properties": {
                "started": {"type": "string", "format": "date"},
                "ended": {"type": "string", "format": "date"},
                "conferenceNumber": {"type": "string"},
                "extendedNumber": {"type": "string"},
            },
            "required": ["conferenceNumber", "extendedNumber"],
            "additionalProperties": False,
        }
    },
    "get_scheduled_conference_details": {
        "allowed_keys": ["extendedNumber", "conferenceNumber"],
        "method_type": "GetScheduledConferenceDetails",
        "tool_name": "get-scheduled-conference-details",
        "tool_description": "Retrieve the scheduled conference details for the provided extension",
        "input_schema": {
            "type": "object",
            "properties": {
                "conferenceNumber": {"type": "string"},
                "extendedNumber": {"type": "string"},
            },
            "required": ["conferenceNumber", "extendedNumber"],
            "additionalProperties": False,
        }
    },
    "get_auth_caller_id": {
        "allowed_keys": ["ID", "filter", "extendedNumber"],
        "method_type": "GetAuthCallerID",
        "tool_name": "get-auth-caller-id",
        "tool_description": "Retrieve the auth caller id for the provided extended number",
        "input_schema": {
            "type": "object",
            "properties": {
                "ID": {"type": "integer"},
                "filter": {"type": "string"},
                "extendedNumber": {"type": "string"},
            },
            "additionalProperties": False,
            "allOf": [
                {
                    "not": {
                        "allOf": [{"required": ["ID"]}, {"required": ["filter", "extendedNumber"]}]
                    }
                }
            ],
        }
    },
    "get_auth_caller_id_recharges": {
        "allowed_keys": ["ID"],
        "method_type": "GetAuthCallerIDRecharges",
        "tool_name": "get-auth-caller-id-recharges",
        "tool_description": "Retrieve the auth caller id recharges for the provided extended number",
        "input_schema": {
            "type": "object",
            "properties": {
                "ID": {"type": "integer"},
            },
            "required": ["ID"],
            "additionalProperties": False,
        }
    },
    "get_available_caller_id": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "GetAvailableCallerID",
        "tool_name": "get-available-caller-id",
        "tool_description": "Retrieve the available caller id for the provided extended number",
        "input_schema": {
            "type": "object",
            "properties": {
                "extendedNumber": {"type": "string"},
            },
            "additionalProperties": False,
        }
    },
    "get_call_recording_settings": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "GetCallRecordingSettings",
        "tool_name": "get-call-recording-settings",
        "tool_description": "Retrieve the call recording settings for the provided extension",
        "input_schema": {
            "type": "object",
            "properties": {"extendedNumber": {"type": "string"}},
            "required": ["extendedNumber"],
            "additionalProperties": False,
        }
    },
    "get_call_rules_in": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "GetCallRulesIn",
        "tool_name": "get-call-rules-in",
        "tool_description": "Retrieve the inbound call rules for the provided extension",
        "input_schema": {
            "type": "object",
            "properties": {"extendedNumber": {"type": "string"}},
            "required": ["extendedNumber"],
            "additionalProperties": False,
        }
    },
    "get_card_code_recharges": {
        "allowed_keys": ["ID"],
        "method_type": "GetCardCodeRecharges",
        "tool_name": "get-card-code-recharges",
        "tool_description": "Retrieve recharge operations for a calling card",
        "input_schema": {
            "type": "object",
            "properties": {"ID": {"type": "integer"}},
            "required": ["ID"],
            "additionalProperties": False,
        }
    },
    "get_card_code": {
        "allowed_keys": ["ID", "filter", "extendedNumber"],
        "method_type": "GetCardCode",
        "tool_name": "get-card-code",
        "tool_description": "Retrieve calling card details by ID, filter or extension",
        "input_schema": {
            "type": "object",
            "properties": {
                "ID": {"type": "integer"},
                "filter": {"type": "string"},
                "extendedNumber": {"type": "string"},
            },
            "oneOf": [
                {"required": ["ID"]},
                {"required": ["filter"]},
                {"required": ["extendedNumber"]},
            ],
            "additionalProperties": False,
        }
    },
    "get_conference_settings": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "GetConferenceSettings",
        "tool_name": "get-conference-settings",
        "tool_description": "Retrieve conference settings for the provided extension",
        "input_schema": {
            "type": "object",
            "properties": {"extendedNumber": {"type": "string"}},
            "required": ["extendedNumber"],
            "additionalProperties": False,
        }
    },
    "get_extension_details": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "GetExtensionDetails",
        "tool_name": "get-extension-details",
        "tool_description": "Retrieve details for the provided extension",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "extendedNumber": {
                    "type": "string",
                    "description": "Extension extended number",
                },
            },
            "required": ["extendedNumber"],
        }
    },
    "get_extension_settings": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "GetExtensionSettings",
        "tool_name": "get-extension-settings",
        "tool_description": "Retrieve settings for the provided extension",
        "input_schema": {
            "type": "object",
            "properties": {"extendedNumber": {"type": "string"}},
            "required": ["extendedNumber"],
            "additionalProperties": False,
        }
    },
    "get_fax_center_settings": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "GetFaxCenterSettings",
        "tool_name": "get-fax-center-settings",
        "tool_description": "Retrieve fax center settings for the provided extension",
        "input_schema": {
            "type": "object",
            "properties": {"extendedNumber": {"type": "string"}},
            "required": ["extendedNumber"],
            "additionalProperties": False,
        }
    },
    "get_sip_preferences": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "GetSIPPreferences",
        "tool_name": "get-sip-preferences",
        "tool_description": "Retrieve SIP preferences for the provided extension",
        "input_schema": {
            "type": "object",
            "properties": {"extendedNumber": {"type": "string"}},
            "required": ["extendedNumber"],
            "additionalProperties": False,
        }
    },
    "get_voicemail_settings": {
        "allowed_keys": ["extendedNumber"],
        "method_type": "GetVoicemailSettings",
        "tool_name": "get-voicemail-settings",
        "tool_description": "Retrieve voicemail settings for the provided extension",
        "input_schema": {
            "type": "object",
            "properties": {"extendedNumber": {"type": "string"}},
            "required": ["extendedNumber"],
            "additionalProperties": False,
        }
    }
}

# Generate tool schemas for each function


def _create_tool_schema(tool_config: Dict[str, Any]) -> types.Tool:
    """Create a Tool schema from configuration."""
    return types.Tool(
        name=tool_config["tool_name"],
        description=tool_config["tool_description"],
        inputSchema=tool_config["input_schema"]
    )


# Create all tool schemas
TOOL_SCHEMAS = {
    func_name: _create_tool_schema(config)
    for func_name, config in TOOL_REGISTRY.items()
}

# Backwards compatibility constants for main.py
ADD_EXTENSION_TOOL_NAME = TOOL_REGISTRY["add_extension"]["tool_name"]
GET_EXTENSIONS_TOOL_NAME = TOOL_REGISTRY["get_extensions"]["tool_name"]
DELETE_EXTENSION_TOOL_NAME = TOOL_REGISTRY["delete_extension"]["tool_name"]
GET_PROVISION_FILE_TOOL_NAME = TOOL_REGISTRY["get_provision_file"]["tool_name"]
GET_QUEUE_AGENTS_TOOL_NAME = TOOL_REGISTRY["get_queue_agents"]["tool_name"]
GET_QUEUE_MEMBERSHIP_TOOL_NAME = TOOL_REGISTRY["get_queue_membership"]["tool_name"]
GET_SCHEDULED_CONFERENCES_TOOL_NAME = TOOL_REGISTRY["get_scheduled_conferences"]["tool_name"]
GET_SCHEDULED_CONFERENCE_DETAILS_TOOL_NAME = TOOL_REGISTRY[
    "get_scheduled_conference_details"]["tool_name"]
GET_AUTH_CALLER_ID_TOOL_NAME = TOOL_REGISTRY["get_auth_caller_id"]["tool_name"]
GET_AUTH_CALLER_ID_RECHARGES_TOOL_NAME = TOOL_REGISTRY["get_auth_caller_id_recharges"]["tool_name"]
GET_AVAILABLE_CALLER_ID_TOOL_NAME = TOOL_REGISTRY["get_available_caller_id"]["tool_name"]
GET_CALL_RECORDING_SETTINGS_TOOL_NAME = TOOL_REGISTRY["get_call_recording_settings"]["tool_name"]
GET_CALL_RULES_IN_TOOL_NAME = TOOL_REGISTRY["get_call_rules_in"]["tool_name"]
GET_CARD_CODE_RECHARGES_TOOL_NAME = TOOL_REGISTRY["get_card_code_recharges"]["tool_name"]
GET_CARD_CODE_TOOL_NAME = TOOL_REGISTRY["get_card_code"]["tool_name"]
GET_CONFERENCE_SETTINGS_TOOL_NAME = TOOL_REGISTRY["get_conference_settings"]["tool_name"]
GET_EXTENSION_DETAILS_TOOL_NAME = TOOL_REGISTRY["get_extension_details"]["tool_name"]
GET_EXTENSION_SETTINGS_TOOL_NAME = TOOL_REGISTRY["get_extension_settings"]["tool_name"]
GET_FAX_CENTER_SETTINGS_TOOL_NAME = TOOL_REGISTRY["get_fax_center_settings"]["tool_name"]
GET_SCHEDULED_CONFERENCE_SESSIONS_TOOL_NAME = TOOL_REGISTRY[
    "get_scheduled_conference_sessions"]["tool_name"]
GET_SIP_PREFERENCES_TOOL_NAME = TOOL_REGISTRY["get_sip_preferences"]["tool_name"]
GET_VOICEMAIL_SETTINGS_TOOL_NAME = TOOL_REGISTRY["get_voicemail_settings"]["tool_name"]

# Tool schemas for backwards compatibility
ADD_EXTENSION_TOOL_SCHEMA = TOOL_SCHEMAS["add_extension"]
GET_EXTENSIONS_TOOL_SCHEMA = TOOL_SCHEMAS["get_extensions"]
DELETE_EXTENSION_TOOL_SCHEMA = TOOL_SCHEMAS["delete_extension"]
GET_PROVISION_FILE_TOOL_SCHEMA = TOOL_SCHEMAS["get_provision_file"]
GET_QUEUE_AGENTS_TOOL_SCHEMA = TOOL_SCHEMAS["get_queue_agents"]
GET_QUEUE_MEMBERSHIP_TOOL_SCHEMA = TOOL_SCHEMAS["get_queue_membership"]
GET_SCHEDULED_CONFERENCES_TOOL_SCHEMA = TOOL_SCHEMAS["get_scheduled_conferences"]
GET_SCHEDULED_CONFERENCE_DETAILS_TOOL_SCHEMA = TOOL_SCHEMAS["get_scheduled_conference_details"]
GET_AUTH_CALLER_ID_TOOL_SCHEMA = TOOL_SCHEMAS["get_auth_caller_id"]
GET_AUTH_CALLER_ID_RECHARGES_TOOL_SCHEMA = TOOL_SCHEMAS["get_auth_caller_id_recharges"]
GET_AVAILABLE_CALLER_ID_TOOL_SCHEMA = TOOL_SCHEMAS["get_available_caller_id"]
GET_CALL_RECORDING_SETTINGS_TOOL_SCHEMA = TOOL_SCHEMAS["get_call_recording_settings"]
GET_CALL_RULES_IN_TOOL_SCHEMA = TOOL_SCHEMAS["get_call_rules_in"]
GET_CARD_CODE_RECHARGES_TOOL_SCHEMA = TOOL_SCHEMAS["get_card_code_recharges"]
GET_CARD_CODE_TOOL_SCHEMA = TOOL_SCHEMAS["get_card_code"]
GET_CONFERENCE_SETTINGS_TOOL_SCHEMA = TOOL_SCHEMAS["get_conference_settings"]
GET_EXTENSION_DETAILS_TOOL_SCHEMA = TOOL_SCHEMAS["get_extension_details"]
GET_EXTENSION_SETTINGS_TOOL_SCHEMA = TOOL_SCHEMAS["get_extension_settings"]
GET_FAX_CENTER_SETTINGS_TOOL_SCHEMA = TOOL_SCHEMAS["get_fax_center_settings"]
GET_SCHEDULED_CONFERENCE_SESSIONS_TOOL_SCHEMA = TOOL_SCHEMAS["get_scheduled_conference_sessions"]
GET_SIP_PREFERENCES_TOOL_SCHEMA = TOOL_SCHEMAS["get_sip_preferences"]
GET_VOICEMAIL_SETTINGS_TOOL_SCHEMA = TOOL_SCHEMAS["get_voicemail_settings"]


async def add_extension(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Add a extension to an entity.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    # If no password is provided, set passwordAuto to True
    if "password" not in arguments or arguments["password"] is None:
        arguments["passwordAuto"] = True

    tool_config = TOOL_REGISTRY["add_extension"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        ADD_EXTENSION_TOOL_SCHEMA,
        TYPE
    )


async def get_extensions(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve extensions.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_extensions"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_EXTENSIONS_TOOL_SCHEMA,
        TYPE
    )


async def delete_extension(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Delete the extension for the provided extended number.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["delete_extension"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        DELETE_EXTENSION_TOOL_SCHEMA,
        TYPE
    )


async def get_provision_file(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve the provision file for the provided extended number.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_provision_file"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_PROVISION_FILE_TOOL_SCHEMA,
        TYPE
    )


async def get_queue_agents(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve the agents for the provided queue.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_queue_agents"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_QUEUE_AGENTS_TOOL_SCHEMA,
        TYPE
    )


async def get_queue_membership(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve the membership for the provided queue.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_queue_membership"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_QUEUE_MEMBERSHIP_TOOL_SCHEMA,
        TYPE
    )


async def get_scheduled_conferences(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve the scheduled conferences for the provided extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_scheduled_conferences"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_SCHEDULED_CONFERENCES_TOOL_SCHEMA,
        TYPE
    )


async def get_scheduled_conference_details(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve the scheduled conference details for the provided extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_scheduled_conference_details"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_SCHEDULED_CONFERENCE_DETAILS_TOOL_SCHEMA,
        TYPE
    )


async def get_auth_caller_id(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve the auth caller id for the provided extended number.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_auth_caller_id"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_AUTH_CALLER_ID_TOOL_SCHEMA,
        TYPE
    )


async def get_auth_caller_id_recharges(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve the auth caller id recharges for the provided extended number.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_auth_caller_id_recharges"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_AUTH_CALLER_ID_RECHARGES_TOOL_SCHEMA,
        TYPE
    )


async def get_available_caller_id(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve the available caller id for the provided extended number.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_available_caller_id"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_AVAILABLE_CALLER_ID_TOOL_SCHEMA,
        TYPE
    )


async def get_call_recording_settings(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve the call recording settings for the provided extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_call_recording_settings"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CALL_RECORDING_SETTINGS_TOOL_SCHEMA,
        TYPE
    )


async def get_call_rules_in(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve the inbound call rules for the provided extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_call_rules_in"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CALL_RULES_IN_TOOL_SCHEMA,
        TYPE
    )


async def get_card_code_recharges(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve recharge operations for a calling card.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_card_code_recharges"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CARD_CODE_RECHARGES_TOOL_SCHEMA,
        TYPE
    )


async def get_card_code(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve calling card details by ID, filter or extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_card_code"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CARD_CODE_TOOL_SCHEMA,
        TYPE
    )


async def get_conference_settings(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve conference settings for the provided extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_conference_settings"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CONFERENCE_SETTINGS_TOOL_SCHEMA,
        TYPE
    )


async def get_extension_details(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve details for the provided extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_extension_details"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_EXTENSION_DETAILS_TOOL_SCHEMA,
        TYPE
    )


async def get_extension_settings(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve settings for the provided extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_extension_settings"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_EXTENSION_SETTINGS_TOOL_SCHEMA,
        TYPE
    )


async def get_fax_center_settings(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve fax center settings for the provided extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_fax_center_settings"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_FAX_CENTER_SETTINGS_TOOL_SCHEMA,
        TYPE
    )


async def get_scheduled_conference_sessions(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve scheduled conference sessions for the provided extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_scheduled_conference_sessions"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_SCHEDULED_CONFERENCE_SESSIONS_TOOL_SCHEMA,
        TYPE
    )


async def get_sip_preferences(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve SIP preferences for the provided extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_sip_preferences"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_SIP_PREFERENCES_TOOL_SCHEMA,
        TYPE
    )


async def get_voicemail_settings(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve voicemail settings for the provided extension.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_voicemail_settings"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_VOICEMAIL_SETTINGS_TOOL_SCHEMA,
        TYPE
    )
