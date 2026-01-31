import zeep
from zeep.cache import SqliteCache
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import urllib3
from datetime import datetime, time, timezone
from decimal import Decimal
import logging
from jsonschema import validate, ValidationError
import mcp.types as types
import utils.vars as vars
import tempfile
import os

# Custom JSON encoder to handle datetime and decimal objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# Default timeout configuration
DEFAULT_SOAP_TIMEOUT = 30.0  # seconds
DEFAULT_CONNECT_TIMEOUT = 5.0  # seconds

# WSDL caching - use a module-level cache to avoid downloading WSDL on every request
# Cache is stored in temp directory and has 24-hour timeout
_wsdl_cache_dir = os.path.join(tempfile.gettempdir(), "voipnow-mcp-wsdl-cache")
_wsdl_cache = SqliteCache(path=_wsdl_cache_dir, timeout=86400)  # 24 hour cache

def create_soap_session(config: dict) -> Session:
    """
    Create a configured session for SOAP requests with retries, timeouts, and connection pooling.

    Parameters:
        config (dict): Configuration dictionary with optional timeout and retry settings

    Returns:
        Session: Configured requests Session with retry strategy and connection pooling
    """
    session = Session()

    # Configure retry strategy for transient failures
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST", "GET"]
    )

    # Configure adapter with connection pooling
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_maxsize=10,
        pool_block=False
    )

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # Configure SSL verification
    if config.get("insecure", False):
        session.verify = False
        urllib3.disable_warnings()
    else:
        session.verify = True

    return session

def parse_voipnow_date(value):
    """
    Convert VoipNow timestamp format to ISO date string.

    Handles non-standard date formats from VoipNow API that may be timestamps
    instead of standard ISO 8601 date strings.

    Parameters:
        value: The date value to convert (string, int, or float)

    Returns:
        str: ISO formatted date string

    Raises:
        ValueError: If value cannot be parsed as a date or timestamp
    """
    if value is None:
        return None

    # If it's already a datetime object, convert it
    if isinstance(value, datetime):
        return value.date().isoformat()

    # Handle timestamp as string
    if isinstance(value, str):
        if value.isdigit():
            try:
                timestamp = int(value)
                dt = datetime.fromtimestamp(timestamp)
                return dt.date().isoformat()
            except (ValueError, OSError) as e:
                raise ValueError(f"Invalid timestamp value: {value}") from e
        else:
            # Try to parse as ISO date
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.date().isoformat()
            except ValueError as e:
                raise ValueError(f"Invalid date format: {value}") from e

    # Handle timestamp as int or float
    elif isinstance(value, (int, float)):
        try:
            dt = datetime.fromtimestamp(value)
            return dt.date().isoformat()
        except (ValueError, OSError) as e:
            raise ValueError(f"Invalid timestamp value: {value}") from e

    raise ValueError(f"Unsupported date type: {type(value).__name__}")

# Function to create an authentication header
def create_auth_header(config):
    """
    Create an authentication header for SOAP requests.

    Parameters:
    config (dict): Configuration dictionary containing the VoipNow URL and token.

    Returns:
    zeep.xsd.Element: The authentication header element.
    """
    # Define the authentication header element
    header = zeep.xsd.Element(
        "{"
        + config["voipnowUrl"]
        + "/soap2/schema/latest/HeaderData.xsd}userCredentials",
        zeep.xsd.ComplexType(
            [
                zeep.xsd.Element(
                    "{"
                    + config["voipnowUrl"]
                    + "/soap2/schema/latest/HeaderData.xsd}accessToken",
                    zeep.xsd.String(),
                ),
            ]
        ),
    )
    return header(accessToken=config["voipnowToken"])


# Function to create a SOAP client
def create_soap_client(config: dict, schema: str):
    """
    Create a SOAP client for interacting with the VoipNow API with proper timeout, session configuration, and WSDL caching.

    Parameters:
        config (dict): Configuration dictionary containing the VoipNow URL, token, and SSL settings.
        schema (str): The schema name for the SOAP client.

    Returns:
        zeep.Client: The SOAP client object.

    Raises:
        ValueError: If schema is invalid or not in the known schemas list
    """
    # Validate schema is in our known schemas (security check)
    schema_to_entity = {
        vars.SCHEMA_NAME.get(entity): entity
        for entity in vars.SCHEMA_NAME
    }
    if schema not in schema_to_entity:
        raise ValueError(f"Invalid schema: {schema}. Must be one of {list(schema_to_entity.keys())}")

    # Get timeout from config or use defaults
    timeout = config.get("soapTimeout", DEFAULT_SOAP_TIMEOUT)

    # Create session using factory pattern (not global session)
    session = create_soap_session(config)

    # Create transport with timeout configuration and WSDL caching
    transport = zeep.Transport(
        session=session,
        cache=_wsdl_cache,  # Enable WSDL caching to avoid downloading on every request
        timeout=timeout,
        operation_timeout=timeout
    )
    transport.session.headers['User-Agent'] = "VoipNow Provisioning MCP Version/2025.2"

    # Construct WSDL URL
    wsdl_url = config["voipnowUrl"] + f"/soap2/schema/latest/{schema}"

    return zeep.Client(
        wsdl_url,
        transport=transport,
        settings=zeep.Settings(strict=False, xml_huge_tree=True),
        plugins=[],
    )


def _validate_soap_method(schema: str, method: str) -> None:
    """
    Validate that a SOAP method is allowed for the given schema.

    This prevents arbitrary method invocation on the SOAP client.

    Parameters:
        schema (str): The schema name (e.g., "User/User.wsdl")
        method (str): The method name to validate

    Raises:
        ValueError: If the method is not allowed for this schema
    """
    # Build allowed methods set from vars.METHOD_NAME
    allowed_methods = set()

    # Map schema to entity type
    schema_to_entity = {
        vars.SCHEMA_NAME.get(entity): entity
        for entity in vars.SCHEMA_NAME
    }

    entity_type = schema_to_entity.get(schema)
    if not entity_type:
        raise ValueError(f"Unknown schema: {schema}")

    # Get allowed methods for this entity type
    if entity_type in vars.METHOD_NAME:
        allowed_methods = set(vars.METHOD_NAME[entity_type].values())

    # Validate method is in allowed set
    if method not in allowed_methods:
        raise ValueError(
            f"Method '{method}' not allowed for schema '{schema}'. "
            f"Allowed methods: {sorted(allowed_methods)}"
        )


def make_soap_request(
    config: dict, logger: logging.Logger, schema: str, method: str, arguments: dict, allowed_arguments: list[str] = None
):
    """
    Make a SOAP request to the System API with method validation.

    Parameters:
        config (dict): Configuration dictionary containing the VoipNow URL and token.
        schema (str): The schema name for the SOAP client.
        method (str): The method name for the SOAP request.
        arguments (dict): The arguments for the SOAP request.
        allowed_arguments (list): A list of allowed arguments names. Default is None.

    Returns:
        str: The response body of the SOAP request.

    Raises:
        ValueError: If method is not allowed for the schema
    """
    # Validate method before making the request (security check)
    _validate_soap_method(schema, method)

    # Create a SOAP client
    client = create_soap_client(config, schema)

    parameters = {}
    # Prepare the parameters for the SOAP request by filtering the allowed keys.
    # Only the keys that are allowed and have non-null values are included in the parameters.
    parameters = {
        key: arguments[key]
        for key in arguments
        if key in allowed_arguments and arguments[key] is not None
    }

    logger.debug(
        "Parameters used for method %s with schema %s: %s", method, schema, parameters
    )

    # Make the SOAP request
    # Verify method exists on client before calling (defensive check)
    if not hasattr(client.service, method):
        raise ValueError(f"Method '{method}' not found in SOAP service for schema '{schema}'")

    service_method = getattr(client.service, method)

    if parameters:
        response = service_method(
            **parameters, _soapheaders=[create_auth_header(config)]
        )
    else:
        # Some methods require an empty string parameter
        if method in ['GetPhoneLang', 'GetInterfaceLang', 'GetEquipmentList', 'GetSchemaVersions']:
            response = service_method(
                "", _soapheaders=[create_auth_header(config)]
            )
        else:
            response = service_method(
                _soapheaders=[create_auth_header(config)]
            )

    # Serialize the response to JSON format.
    # This ensures that the response can be easily parsed and used by other parts of the application.
    response_body = json.dumps(
        zeep.helpers.serialize_object(response, dict)["body"],
        cls=DateTimeEncoder
    )

    return response_body

async def _execute_operation(
    arguments: dict, 
    config: dict, 
    logger: logging.Logger,
    method_type: str,
    allowed_keys: list[str],
    tool_schema: types.Tool,
    operation_type: str
) -> list[types.TextContent]:
    """
    Generic function to execute operations via SOAP requests.

    Args:
        arguments (dict): The input arguments
        config (dict): The configuration dictionary containing the VoipNow URL and token
        logger (logging.Logger): Logger instance
        method_type (str): The method type for the SOAP request
        allowed_keys (list[str]): List of allowed keys for the operation
        tool_schema (types.Tool): The tool schema for validation
        operation_type (str): The type of the operation

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects
    """
    try:
        validate(instance=arguments, schema=tool_schema.inputSchema)
    except ValidationError as ve:
        raise ValueError(f"Invalid input: {ve.message}") from ve

    # SOAP request
    response_body = make_soap_request(
        config, logger, 
        vars.SCHEMA_NAME[operation_type], 
        vars.METHOD_NAME[operation_type][method_type], 
        arguments, allowed_keys
    )
    
    # Return the response as a list of TextContent objects
    return [types.TextContent(type="text", text=response_body)]