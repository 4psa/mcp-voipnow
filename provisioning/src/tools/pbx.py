import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict,  Any

# Define type
TYPE = "PBX"

# Tool registry containing all PBX tool configurations
TOOL_REGISTRY = {
    "get_regions": {
        "allowed_keys": ["code", "region"],
        "method_type": "GetRegions",
        "tool_name": "get-regions",
        "tool_description": "Retrieve regions for the provided code",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Country code"
                },
                "region": {
                    "type": "string",
                    "description": "Region name to filter result"
                }
            },
            "required": ["code"]
        }
    },
    "get_phone_languages": {
        "allowed_keys": [],
        "method_type": "GetPhoneLang",
        "tool_name": "get-phone-languages",
        "tool_description": "Retrieve phone languages",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {}
        }
    },
    "get_interface_languages": {
        "allowed_keys": [],
        "method_type": "GetInterfaceLang",
        "tool_name": "get-interface-languages",
        "tool_description": "Retrieve interface languages",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {}
        }
    },
    "get_timezone": {
        "allowed_keys": [],
        "method_type": "GetTimezone",
        "tool_name": "get-timezone",
        "tool_description": "Retrieve timezone",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Country code"
                }
            }
        }
    },
    "get_custom_alerts": {
        "allowed_keys": ["userID", "userIdentifier", "displayLevel", "filter"],
        "method_type": "GetCustomAlerts",
        "tool_name": "get-custom-alerts",
        "tool_description": "Retrieve custom alerts for the provided user ID or user identifier",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "userID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Custom alert owner ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "Custom alert owner identifier"
                },
                "displayLevel": {
                    "type": "string",
                    "description": "Custom alert: display Level",
                    "enum": ["admin", "reseller", "client", "extension"],
                    "default": "admin"
                },
                "filter": {
                    "type": "string",
                    "description": "Filter custom alerts list by text"
                }
            },
            "allOf": [
                {
                    "not": {
                        "allOf": [
                            {"required": ["userID"]},
                            {"required": ["userIdentifier"]},
                        ]
                    }
                },
            ]
        }
    },
    "get_custom_buttons": {
        "allowed_keys": ["userID", "userIdentifier", "filter"],
        "method_type": "GetCustomButtons",
        "tool_name": "get-custom-buttons",
        "tool_description": "Retrieve custom buttons for the provided user ID or user identifier",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "userID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Custom alert owner ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "Custom alert owner identifier"
                },
                "filter": {
                    "type": "string",
                    "description": "Filter custom buttons list by text"
                }
            },
            "allOf": [
                {
                    "not": {
                        "allOf": [
                            {"required": ["userID"]},
                            {"required": ["userIdentifier"]},
                        ]
                    }
                },
            ]
        }
    },
    "get_device_details": {
        "allowed_keys": ["deviceID", "serial"],
        "method_type": "GetDeviceDetails",
        "tool_name": "get-device-details",
        "tool_description": "Retrieve details for the provided device ID or serial",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "deviceID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "The ID of the device"
                },
                "serial": {
                    "type": "string",
                    "description": "Device serial"
                }
            },
            "oneOf": [
                {"required": ["deviceID"]},
                {"required": ["serial"]}
            ]
        }
    },
    "get_devices": {
        "allowed_keys": ["ownerID", "userID", "userIdentifier", "assignedOrganizationID", "assignedExtensions"],
        "method_type": "GetDevices",
        "tool_name": "get-devices",
        "tool_description": "Retrieve devices for the provided owner ID, user ID, user identifier, assigned organization ID, or assigned extensions",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "ownerID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "ID of the owner of the device"
                },
                "userID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Devices seen by user with this ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "Devices seen by user with this identifier"
                },
                "assignedOrganizationID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "ID of the client assigned to the device"
                },
                "assignedExtensions": {
                    "type": "array",
                    "items": {"type": "integer", "minimum": 1},
                    "description": "Extensions assigned to the device"
                }
            },
            "allOf": [
                {
                    "not": {
                        "allOf": [
                            {"required": ["userID"]},
                            {"required": ["userIdentifier"]},
                            {"required": ["ownerID"]},
                        ]
                    }
                },
                {
                    "not": {
                        "allOf": [
                            {"required": ["assignedOrganizationID"]},
                            {"required": ["assignedExtensions"]},
                        ]
                    }
                },
            ]
        }
    },
    "get_equipment_list": {
        "allowed_keys": [],
        "method_type": "GetEquipmentList",
        "tool_name": "get-equipment-list",
        "tool_description": "Retrieve equipment list",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {}
        }
    },
    "get_file_languages": {
        "allowed_keys": ["ID"],
        "method_type": "GetFileLanguages",
        "tool_name": "get-file-languages",
        "tool_description": "Retrieve file languages",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "ID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Sound file id"
                }
            },
            "required": ["ID"]
        }
    },
    "get_folders": {
        "allowed_keys": ["userID", "userIdentifier", "musicOnHold", "emptyFolder", "folderID", "languageID", "musicOnHold", "system", "status"],
        "method_type": "GetFolders",
        "tool_name": "get-folders",
        "tool_description": "Retrieve folders for the provided user ID or user identifier",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "userID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "User ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "User identifier"
                },
                "musicOnHold": {
                    "type": "integer",
                    "description": "0: folders that do not contain music on hold, 1: folders that contain only music on hold, -1: all folders",
                    "default": 0,
                    "enum": [-1, 0, 1]
                },
                "emptyFolder": {
                    "type": "integer",
                    "description": "0: all folders, 1: non empty folders",
                    "default": 0,
                    "enum": [0, 1]
                }
            },
            "allOf": [
                {
                    "not": {
                        "allOf": [
                            {"required": ["userID"]},
                            {"required": ["userIdentifier"]},
                        ]
                    }
                },
            ]
        }
    },
    "get_owned_sounds": {
        "allowed_keys": ["userID", "userIdentifier", "folderID", "languageID", "musicOnHold", "system", "status"],
        "method_type": "GetOwnedSounds",
        "tool_name": "get-owned-sounds",
        "tool_description": "Retrieve owned sounds for the provided user ID or user identifier",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "userID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "User ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "User identifier"
                },
                "folderID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Set 0 for all folders"
                },
                "languageID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Set 0 for all files"
                },
                "musicOnHold": {
                    "type": "integer",
                    "description": "0: non music on hold sounds, 1: music on hold files, -1: all files",
                    "default": -1,
                    "enum": [-1, 0, 1]
                },
                "system": {
                    "type": "integer",
                    "description": "0: non system sounds, 1 - system sounds, -1: all files",
                    "default": -1,
                    "enum": [-1, 0, 1]
                },
                "status": {
                    "type": "integer",
                    "description": "Status filter",
                    "default": -1
                }
            },
            "allOf": [
                {
                    "not": {
                        "allOf": [
                            {"required": ["userID"]},
                            {"required": ["userIdentifier"]},
                        ]
                    }
                },
            ]
        }
    },
    "get_schema_versions": {
        "allowed_keys": [],
        "method_type": "GetSchemaVersions",
        "tool_name": "get-schema-versions",
        "tool_description": "Retrieve schema versions",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {}
        }
    },
    "get_shared_sounds": {
        "allowed_keys": ["userID", "userIdentifier", "own", "shared"],
        "method_type": "GetSharedSounds",
        "tool_name": "get-shared-sounds",
        "tool_description": "Retrieve shared sounds for the provided user ID or user identifier",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "userID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "User ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "User identifier"
                },
                "own": {
                    "type": "boolean",
                    "description": "Filter shared sounds created by the user or all sounds to which this user has access to",
                    "default": True
                }
            },
            "allOf": [
                {
                    "not": {
                        "allOf": [
                            {"required": ["userID"]},
                            {"required": ["userIdentifier"]},
                        ]
                    }
                },
            ]
        }
    },
    "get_templates": {
        "allowed_keys": ["ID", "userLevel", "extensionType", "userID", "userIdentifier"],
        "method_type": "GetTemplates",
        "tool_name": "get-templates",
        "tool_description": "Retrieve templates for the provided user ID or user identifier",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "ID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "User template ID"
                },
                "userLevel": {
                    "type": "string",
                    "description": "Possible values: serviceProvider, organization, user, extension",
                    "enum": ["serviceProvider", "organization", "user", "extension"]
                },
                "extensionType": {
                    "type": "string",
                    "description": "Filter by extension type",
                    "enum": ["term", "phoneQueue", "ivr", "voicecenter", "conference", "callback", "callcard", "intercom", "queuecenter"],
                    "default": "term"
                },
                "userID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Template owner ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "Template owner identifier"
                }
            },
            "allOf": [
                {
                    "not": {
                        "allOf": [
                            {"required": ["userID"]},
                            {"required": ["userIdentifier"]},
                        ]
                    }
                },
            ]
        }
    },
    "get_time_interval_blocks": {
        "allowed_keys": ["filter", "userID", "userIdentifier"],
        "method_type": "GetTimeIntervalBlocks",
        "tool_name": "get-time-interval-blocks",
        "tool_description": "Retrieve time intervals blocks for the provided user ID or user identifier",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "filter": {
                    "type": "string",
                    "description": "Filter time interval blocks list byname"
                },
                "userID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Time interval owner ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "Time interval owner identifier"
                }
            },
            "allOf": [
                {
                    "not": {
                        "allOf": [
                            {"required": ["userID"]},
                            {"required": ["userIdentifier"]},
                        ]
                    }
                },
            ]
        }
    },
    "get_time_intervals": {
        "allowed_keys": ["ID"],
        "method_type": "GetTimeIntervals",
        "tool_name": "get-time-intervals",
        "tool_description": "Retrieve time intervals for the provided time interval block ID",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "ID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Time interval block ID"
                }
            },
            "required": ["ID"]
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
# These reference the tool names from the registry
GET_REGIONS_TOOL_NAME = TOOL_REGISTRY["get_regions"]["tool_name"]
GET_PHONE_LANGUAGES_TOOL_NAME = TOOL_REGISTRY["get_phone_languages"]["tool_name"]
GET_INTERFACE_LANGUAGES_TOOL_NAME = TOOL_REGISTRY["get_interface_languages"]["tool_name"]
GET_TIMEZONE_TOOL_NAME = TOOL_REGISTRY["get_timezone"]["tool_name"]
GET_CUSTOM_ALERTS_TOOL_NAME = TOOL_REGISTRY["get_custom_alerts"]["tool_name"]
GET_CUSTOM_BUTTONS_TOOL_NAME = TOOL_REGISTRY["get_custom_buttons"]["tool_name"]
GET_DEVICE_DETAILS_TOOL_NAME = TOOL_REGISTRY["get_device_details"]["tool_name"]
GET_DEVICES_TOOL_NAME = TOOL_REGISTRY["get_devices"]["tool_name"]
GET_EQUIPMENT_LIST_TOOL_NAME = TOOL_REGISTRY["get_equipment_list"]["tool_name"]
GET_FILE_LANGUAGES_TOOL_NAME = TOOL_REGISTRY["get_file_languages"]["tool_name"]
GET_FOLDERS_TOOL_NAME = TOOL_REGISTRY["get_folders"]["tool_name"]
GET_OWNED_SOUNDS_TOOL_NAME = TOOL_REGISTRY["get_owned_sounds"]["tool_name"]
GET_SCHEMA_VERSIONS_TOOL_NAME = TOOL_REGISTRY["get_schema_versions"]["tool_name"]
GET_SHARED_SOUNDS_TOOL_NAME = TOOL_REGISTRY["get_shared_sounds"]["tool_name"]
GET_TEMPLATES_TOOL_NAME = TOOL_REGISTRY["get_templates"]["tool_name"]
GET_TIME_INTERVAL_BLOCKS_TOOL_NAME = TOOL_REGISTRY["get_time_interval_blocks"]["tool_name"]
GET_TIME_INTERVALS_TOOL_NAME = TOOL_REGISTRY["get_time_intervals"]["tool_name"]

# All tool schemas accessible by name - backwards compatibility for main.py
GET_REGIONS_TOOL_SCHEMA = TOOL_SCHEMAS["get_regions"]
GET_PHONE_LANGUAGES_TOOL_SCHEMA = TOOL_SCHEMAS["get_phone_languages"]
GET_INTERFACE_LANGUAGES_TOOL_SCHEMA = TOOL_SCHEMAS["get_interface_languages"]
GET_TIMEZONE_TOOL_SCHEMA = TOOL_SCHEMAS["get_timezone"]
GET_CUSTOM_ALERTS_TOOL_SCHEMA = TOOL_SCHEMAS["get_custom_alerts"]
GET_CUSTOM_BUTTONS_TOOL_SCHEMA = TOOL_SCHEMAS["get_custom_buttons"]
GET_DEVICE_DETAILS_TOOL_SCHEMA = TOOL_SCHEMAS["get_device_details"]
GET_DEVICES_TOOL_SCHEMA = TOOL_SCHEMAS["get_devices"]
GET_EQUIPMENT_LIST_TOOL_SCHEMA = TOOL_SCHEMAS["get_equipment_list"]
GET_FILE_LANGUAGES_TOOL_SCHEMA = TOOL_SCHEMAS["get_file_languages"]
GET_FOLDERS_TOOL_SCHEMA = TOOL_SCHEMAS["get_folders"]
GET_OWNED_SOUNDS_TOOL_SCHEMA = TOOL_SCHEMAS["get_owned_sounds"]
GET_SCHEMA_VERSIONS_TOOL_SCHEMA = TOOL_SCHEMAS["get_schema_versions"]
GET_SHARED_SOUNDS_TOOL_SCHEMA = TOOL_SCHEMAS["get_shared_sounds"]
GET_TEMPLATES_TOOL_SCHEMA = TOOL_SCHEMAS["get_templates"]
GET_TIME_INTERVAL_BLOCKS_TOOL_SCHEMA = TOOL_SCHEMAS["get_time_interval_blocks"]
GET_TIME_INTERVALS_TOOL_SCHEMA = TOOL_SCHEMAS["get_time_intervals"]


async def get_regions(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve regions for the provided code.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_regions"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_REGIONS_TOOL_SCHEMA,
        TYPE
    )


async def get_phone_languages(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve phone languages.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_phone_languages"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_PHONE_LANGUAGES_TOOL_SCHEMA,
        TYPE
    )


async def get_interface_languages(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve interface languages.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_interface_languages"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_INTERFACE_LANGUAGES_TOOL_SCHEMA,
        TYPE
    )


async def get_timezone(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve timezone.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_timezone"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_TIMEZONE_TOOL_SCHEMA,
        TYPE
    )


async def get_custom_alerts(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve custom alerts for the provided user ID or user identifier.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_custom_alerts"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CUSTOM_ALERTS_TOOL_SCHEMA,
        TYPE
    )


async def get_custom_buttons(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve custom buttons for the provided user ID or user identifier.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_custom_buttons"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CUSTOM_BUTTONS_TOOL_SCHEMA,
        TYPE
    )


async def get_device_details(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve details for the provided device ID or serial.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_device_details"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_DEVICE_DETAILS_TOOL_SCHEMA,
        TYPE
    )


async def get_devices(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve devices for the provided owner ID, user ID, user identifier, assigned organization ID, or assigned extensions.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_devices"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_DEVICES_TOOL_SCHEMA,
        TYPE
    )


async def get_equipment_list(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve equipment list.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_equipment_list"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_EQUIPMENT_LIST_TOOL_SCHEMA,
        TYPE
    )


async def get_file_languages(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve file languages.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_file_languages"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_FILE_LANGUAGES_TOOL_SCHEMA,
        TYPE
    )


async def get_folders(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve folders for the provided user ID or user identifier.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_folders"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_FOLDERS_TOOL_SCHEMA,
        TYPE
    )


async def get_owned_sounds(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve owned sounds for the provided user ID or user identifier.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_owned_sounds"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_OWNED_SOUNDS_TOOL_SCHEMA,
        TYPE
    )


async def get_schema_versions(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve schema versions.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_schema_versions"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_SCHEMA_VERSIONS_TOOL_SCHEMA,
        TYPE
    )


async def get_shared_sounds(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve shared sounds for the provided user ID or user identifier.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_shared_sounds"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_SHARED_SOUNDS_TOOL_SCHEMA,
        TYPE
    )


async def get_templates(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve templates for the provided user ID or user identifier.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.
    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_templates"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_TEMPLATES_TOOL_SCHEMA,
        TYPE
    )


async def get_time_interval_blocks(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve time intervals blocks for the provided user ID or user identifier.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_time_interval_blocks"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_TIME_INTERVAL_BLOCKS_TOOL_SCHEMA,
        TYPE
    )


async def get_time_intervals(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve time intervals for the provided time interval block ID.
    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_time_intervals"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_TIME_INTERVALS_TOOL_SCHEMA,
        TYPE
    )
