import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Define type
TYPE = "Report"

# Tool registry containing all Report tool configurations
TOOL_REGISTRY = {
    "call_costs": {
        "allowed_keys": ["userID", "userIdentifier", "interval", "year", "month", "prepareDelete"],
        "method_type": "CallCosts",
        "tool_name": "call-costs",
        "tool_description": "Retrieve call costs for a specific user",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "userID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Account ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "Account identifier. Alternative to userID."
                },
                "interval": {
                    "type": "object",
                    "properties": {
                        "startDate": {
                            "type": "string",
                            "format": "date",
                            "description": "Start date in format yyyy-mm-dd"
                        },
                        "endDate": {
                            "type": "string",
                            "format": "date",
                            "description": "End date in format yyyy-mm-dd"
                        }
                    },
                    "additionalProperties": False,
                    "description": "Search between startDate and endDate"
                },
                "year": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Search year. Default: current year"
                },
                "month": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Search month. Default: current month"
                },
                "prepareDelete": {
                    "type": "boolean",
                    "description": "Set flag to mark client in state: irreversable suspension"
                }
            },
            "dependencies": {
                "year": ["month"],
                "month": ["year"]
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
                {
                    "not": {
                        "allOf": [
                            {"required": ["interval"]},
                            {"required": ["year", "month"]}
                        ]
                    }
                }
            ]
        }
    },
    "call_report": {
        "allowed_keys": ["userID", "userIdentifier", "interval", "flow", "type", "disposition", "records", "hangupCause", "networkCode"],
        "method_type": "CallReport",
        "tool_name": "call-report",
        "tool_description": "Retrieve call report for a specific user",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "userID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Account ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "Account identifier. Alternative to userID."
                },
                "interval": {
                    "type": "object",
                    "properties": {
                        "startDate": {
                            "type": "string",
                            "format": "date",
                            "description": "Start date in format yyyy-mm-dd"
                        },
                        "endDate": {
                            "type": "string",
                            "format": "date",
                            "description": "End date in format yyyy-mm-dd"
                        }
                    },
                    "additionalProperties": False,
                    "description": "Search between startDate and endDate"
                },
                "flow": {
                    "type": "string",
                    "enum": ["in", "out"],
                    "description": "Call flow: in, out"
                },
                "type": {
                    "type": "string",
                    "enum": ["local", "elocal", "out"],
                    "description": "Call type: local, elocal, out"
                },
                "disposition": {
                    "type": "string",
                    "enum": ["ANSWERED", "BUSY", "FAILED", "NO ANSWER", "UNKNOWN", "NOT ALLOWED"],
                    "description": "Call disposition: ANSWERED, BUSY, FAILED, NO ANSWER, UNKNOWN, NOT ALLOWED"
                },
                "records": {
                    "type": "integer",
                    "default": 1000,
                    "description": "Number of records to be returned. Maximum: 1,000"
                },
                "hangupCause": {
                    "type": "integer",
                    "description": "Filter report by hangup cause"
                },
                "networkCode": {
                    "type": "string",
                    "description": "Filter report by network code"
                }
            },
            "oneOf": [
                {"required": ["userID"]},
                {"required": ["userIdentifier"]}
            ]
        }
    },
    "quick_stats": {
        "allowed_keys": ["userID", "userIdentifier", "login"],
        "method_type": "QuickStats",
        "tool_name": "quick-stats",
        "tool_description": "Retrieve quick stats for a specific entity",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "userID": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Account ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "Account identifier. Alternative to userID."
                },
                "login": {
                    "type": "string",
                    "description": "Account username"
                }
            },
            "oneOf": [
                {"required": ["userID"]},
                {"required": ["userIdentifier"]},
                {"required": ["login"]}
            ]
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
CALL_COSTS_TOOL_NAME = TOOL_REGISTRY["call_costs"]["tool_name"]
CALL_REPORT_TOOL_NAME = TOOL_REGISTRY["call_report"]["tool_name"]
QUICK_STATS_TOOL_NAME = TOOL_REGISTRY["quick_stats"]["tool_name"]

# Tool schemas for backwards compatibility
CALL_COSTS_TOOL_SCHEMA = TOOL_SCHEMAS["call_costs"]
CALL_REPORT_TOOL_SCHEMA = TOOL_SCHEMAS["call_report"]
QUICK_STATS_TOOL_SCHEMA = TOOL_SCHEMAS["quick_stats"]


async def call_costs(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Get call costs for a specific call

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.
        logger (logging.Logger): The logger object.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects.
    """
    tool_config = TOOL_REGISTRY["call_costs"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        CALL_COSTS_TOOL_SCHEMA,
        TYPE
    )


async def call_report(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Get call report for a specific call

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.
        logger (logging.Logger): The logger object.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects.
    """
    tool_config = TOOL_REGISTRY["call_report"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        CALL_REPORT_TOOL_SCHEMA,
        TYPE
    )


async def quick_stats(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Get quick stats for a specific entity

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.
        logger (logging.Logger): The logger object.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects.
    """
    tool_config = TOOL_REGISTRY["quick_stats"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        QUICK_STATS_TOOL_SCHEMA,
        TYPE
    )
