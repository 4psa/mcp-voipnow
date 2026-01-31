import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Define type
TYPE = "Channel"

# Tool registry containing all Channel tool configurations
TOOL_REGISTRY = {
    "get_channels": {
        "allowed_keys": ["groupID", "enabled", "flow", "filter"],
        "method_type": "GetChannels",
        "tool_name": "get-channels",
        "tool_description": "Retrieve channels.",
        "input_schema": {
            "type": "object",
            "properties": {
                "groupID": {"type": "integer"},
                "enabled": {"type": "boolean"},
                "flow": {"type": "string", "enum": ["in", "out", "both"]},
                "filter": {"type": "string"}
            },
            "additionalProperties": False,
        }
    },
    "get_codecs": {
        "allowed_keys": ["channelID"],
        "method_type": "GetCodecs",
        "tool_name": "get-codecs",
        "tool_description": "Retrieve codecs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channelID": {"type": "integer", "minimum": 0}
            },
            "additionalProperties": False,
        }
    },
    "get_public_no": {
        "allowed_keys": ["channelID", "inUse", "type", "filter", "userID", "userIdentifier", "extendedNumber"],
        "method_type": "GetPublicNo",
        "tool_name": "get-public-no",
        "tool_description": "Retrieve public no.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channelID": {"type": "integer", "minimum": 0},
                "inUse": {"type": "boolean", "default": False},
                "type": {"type": "string", "enum": ["exclusive", "stacked"]},
                "filter": {"type": "string"},
                "userID": {"type": "integer", "minimum": 0},
                "userIdentifier": {"type": "string"},
                "extendedNumber": {"type": "string"}
            },
            "required": ["channelID"],
            "additionalProperties": False,
            "oneOf": [
                {"required": ["userID"]},
                {"required": ["userIdentifier"]},
                {"required": ["extendedNumber"]}
            ]
        }
    },
    "get_public_no_poll": {
        "allowed_keys": ["extendedNumber", "userIdentifier", "userID"],
        "method_type": "GetPublicNoPoll",
        "tool_name": "get-public-no-poll",
        "tool_description": "Retrieve public no poll.",
        "input_schema": {
            "type": "object",
            "properties": {
                "extendedNumber": {"type": "string"},
                "userIdentifier": {"type": "string"},
                "userID": {"type": "integer", "minimum": 0}
            },
            "additionalProperties": False,
            "oneOf": [
                {"required": ["extendedNumber"]},
                {"required": ["userIdentifier"]},
                {"required": ["userID"]}
            ]
        }
    },
    "get_call_rules_out": {
        "allowed_keys": ["ID"],
        "method_type": "GetCallRulesOut",
        "tool_name": "get-call-rules-out",
        "tool_description": "Retrieve call rules out.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ID": {"type": "integer", "minimum": 0}
            },
            "additionalProperties": False,
        }
    },
    "get_call_rules_out_group": {
        "allowed_keys": ["userID", "status", "filter"],
        "method_type": "GetCallRulesOutGroup",
        "tool_name": "get-call-rules-out-group",
        "tool_description": "Retrieve call rules out group.",
        "input_schema": {
            "type": "object",
            "properties": {
                "userID": {"type": "integer", "minimum": 0},
                "status": {"type": "boolean", "default": False},
                "filter": {"type": "string"}
            },
            "additionalProperties": False,
        }
    },
    "get_channel_group_poll": {
        "allowed_keys": ["channelID"],
        "method_type": "GetChannelGroupPoll",
        "tool_name": "get-channel-group-poll",
        "tool_description": "Retrieve channel group poll.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channelID": {"type": "integer", "minimum": 0}
            },
            "required": ["channelID"],
            "additionalProperties": False,
        }
    },
    "get_channel_groups": {
        "allowed_keys": ["channelID", "filter"],
        "method_type": "GetChannelGroups",
        "tool_name": "get-channel-groups",
        "tool_description": "Retrieve channel groups.",
        "input_schema": {
            "type": "object",
            "properties": {
                "channelID": {"type": "integer", "minimum": 0},
                "filter": {"type": "string"}
            },
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
GET_CHANNELS_TOOL_NAME = TOOL_REGISTRY["get_channels"]["tool_name"]
GET_CODECS_TOOL_NAME = TOOL_REGISTRY["get_codecs"]["tool_name"]
GET_PUBLIC_NO_TOOL_NAME = TOOL_REGISTRY["get_public_no"]["tool_name"]
GET_PUBLIC_NO_POLL_TOOL_NAME = TOOL_REGISTRY["get_public_no_poll"]["tool_name"]
GET_CALL_RULES_OUT_TOOL_NAME = TOOL_REGISTRY["get_call_rules_out"]["tool_name"]
GET_CALL_RULES_OUT_GROUP_TOOL_NAME = TOOL_REGISTRY["get_call_rules_out_group"]["tool_name"]
GET_CHANNEL_GROUP_POLL_TOOL_NAME = TOOL_REGISTRY["get_channel_group_poll"]["tool_name"]
GET_CHANNEL_GROUPS_TOOL_NAME = TOOL_REGISTRY["get_channel_groups"]["tool_name"]

# Tool schemas for backwards compatibility
GET_CHANNELS_TOOL_SCHEMA = TOOL_SCHEMAS["get_channels"]
GET_CODECS_TOOL_SCHEMA = TOOL_SCHEMAS["get_codecs"]
GET_PUBLIC_NO_TOOL_SCHEMA = TOOL_SCHEMAS["get_public_no"]
GET_PUBLIC_NO_POLL_TOOL_SCHEMA = TOOL_SCHEMAS["get_public_no_poll"]
GET_CALL_RULES_OUT_TOOL_SCHEMA = TOOL_SCHEMAS["get_call_rules_out"]
GET_CALL_RULES_OUT_GROUP_TOOL_SCHEMA = TOOL_SCHEMAS["get_call_rules_out_group"]
GET_CHANNEL_GROUP_POLL_TOOL_SCHEMA = TOOL_SCHEMAS["get_channel_group_poll"]
GET_CHANNEL_GROUPS_TOOL_SCHEMA = TOOL_SCHEMAS["get_channel_groups"]


async def get_channels(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve channels.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_channels"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CHANNELS_TOOL_SCHEMA,
        TYPE
    )


async def get_codecs(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve codecs.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_codecs"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CODECS_TOOL_SCHEMA,
        TYPE
    )


async def get_public_no(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve public no.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_public_no"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_PUBLIC_NO_TOOL_SCHEMA,
        TYPE
    )


async def get_public_no_poll(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve public no poll.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_public_no_poll"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_PUBLIC_NO_POLL_TOOL_SCHEMA,
        TYPE
    )


async def get_call_rules_out(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve call rules out.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_call_rules_out"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CALL_RULES_OUT_TOOL_SCHEMA,
        TYPE
    )


async def get_call_rules_out_group(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve call rules out group.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_call_rules_out_group"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CALL_RULES_OUT_GROUP_TOOL_SCHEMA,
        TYPE
    )


async def get_channel_group_poll(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve channel group poll.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_channel_group_poll"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CHANNEL_GROUP_POLL_TOOL_SCHEMA,
        TYPE
    )


async def get_channel_groups(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve channel groups.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_channel_groups"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CHANNEL_GROUPS_TOOL_SCHEMA,
        TYPE
    )
