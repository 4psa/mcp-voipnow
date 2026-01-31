import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Define type
TYPE = "Billing"

# Tool registry containing all Billing tool configurations
TOOL_REGISTRY = {
    "get_charging_plans": {
        "allowed_keys": ["userID", "userIdentifier", "filter", "default"],
        "method_type": "GetChargingPlans",
        "tool_name": "get-charging-plans",
        "tool_description": "Retrieve charging plans.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "userID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Account ID"
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "Account identifier. Alternative to userID.",
                },
                "filter": {
                    "type": "string",
                    "description": "The filter for the entity",
                    "enum": ["name", "company", "email", "login"],
                },
                "default": {
                    "type": "boolean",
                    "description": "Set to filter default charging plan",
                },
            },
            "required": [],
            "allOf": [
                {
                    "not": {
                        "allOf": [
                            {"required": ["userID"]},
                            {"required": ["userIdentifier"]}
                        ]
                    }
                }
            ]
        }
    },
    "get_charging_packages": {
        "allowed_keys": ["chargingPlanID"],
        "method_type": "GetChargingPackages",
        "tool_name": "get-charging-packages",
        "tool_description": "Retrieve charging packages.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "chargingPlanID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Charging plan ID",
                },
            },
            "required": ["chargingPlanID"],
        }
    },
    "get_charging_plan_details": {
        "allowed_keys": ["ID", "identifier"],
        "method_type": "GetChargingPlanDetails",
        "tool_name": "get-charging-plan-details",
        "tool_description": "Retrieve charging plan details.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "ID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Charging plan ID",
                },
                "identifier": {
                    "type": "string",
                    "description": "Charging plan identifier. Alternative to ID.",
                },
            },
            "allOf": [{"oneOf": [{"required": ["ID"]}, {"required": ["identifier"]}]}],
        }
    },
    "get_destination_exceptions": {
        "allowed_keys": ["chargingPlanID", "filter"],
        "method_type": "GetDestinationExceptions",
        "tool_name": "get-destination-exceptions",
        "tool_description": "Retrieve destination exceptions.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "chargingPlanID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Charging plan ID",
                },
                "filter": {
                    "type": "string",
                    "description": "Filter destination exception charges list after areaCode, description",
                },
            },
            "required": ["chargingPlanID"],
        }
    },
    "get_recharges": {
        "allowed_keys": ["userID", "userIdentifier"],
        "method_type": "GetRecharges",
        "tool_name": "get-recharges",
        "tool_description": "Retrieve recharges.",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "userID": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Account ID",
                },
                "userIdentifier": {
                    "type": "string",
                    "description": "Account identifier. Alternative to userID.",
                },
            },
            "allOf": [{
                "not": {
                    "allOf": [
                        {"required": ["userID"]},
                        {"required": ["userIdentifier"]}
                    ]
                }
            }
            ],
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
GET_CHARGING_PLANS_TOOL_NAME = TOOL_REGISTRY["get_charging_plans"]["tool_name"]
GET_CHARGING_PACKAGES_TOOL_NAME = TOOL_REGISTRY["get_charging_packages"]["tool_name"]
GET_CHARGING_PLAN_DETAILS_TOOL_NAME = TOOL_REGISTRY["get_charging_plan_details"]["tool_name"]
GET_DESTINATION_EXCEPTIONS_TOOL_NAME = TOOL_REGISTRY["get_destination_exceptions"]["tool_name"]
GET_RECHARGES_TOOL_NAME = TOOL_REGISTRY["get_recharges"]["tool_name"]

# Tool schemas for backwards compatibility
GET_CHARGING_PLANS_TOOL_SCHEMA = TOOL_SCHEMAS["get_charging_plans"]
GET_CHARGING_PACKAGES_TOOL_SCHEMA = TOOL_SCHEMAS["get_charging_packages"]
GET_CHARGING_PLAN_DETAILS_TOOL_SCHEMA = TOOL_SCHEMAS["get_charging_plan_details"]
GET_DESTINATION_EXCEPTIONS_TOOL_SCHEMA = TOOL_SCHEMAS["get_destination_exceptions"]
GET_RECHARGES_TOOL_SCHEMA = TOOL_SCHEMAS["get_recharges"]


async def get_charging_plans(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve charging plans.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_charging_plans"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CHARGING_PLANS_TOOL_SCHEMA,
        TYPE
    )


async def get_charging_packages(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve charging packages.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_charging_packages"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CHARGING_PACKAGES_TOOL_SCHEMA,
        TYPE
    )


async def get_charging_plan_details(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve charging plan details.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_charging_plan_details"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_CHARGING_PLAN_DETAILS_TOOL_SCHEMA,
        TYPE
    )


async def get_destination_exceptions(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve destination exceptions.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_destination_exceptions"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_DESTINATION_EXCEPTIONS_TOOL_SCHEMA,
        TYPE
    )


async def get_recharges(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Retrieve recharges.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects containing the retrieved details.
    """
    tool_config = TOOL_REGISTRY["get_recharges"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        GET_RECHARGES_TOOL_SCHEMA,
        TYPE
    )
