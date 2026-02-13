from mcp.server.lowlevel import Server
import os
import mcp.types as types
import json
import argparse
import signal
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import requests
from typing import Awaitable, Callable, Dict, List

# Import the local utils
import utils.server
import utils.token
import utils.logger
import utils.tool_registry

# ----------------------------------------------------------------------------
# Custom Exceptions
# ----------------------------------------------------------------------------

class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

# keys
required_keys = ["appId", "appSecret", "voipnowHost", "voipnowTokenFile"]
allowed_keys = required_keys + ["authTokenMCP", "logLevel", "insecure"]

TOKEN_CHECK_INTERVAL_SECONDS = 300  # 5 minutes
INITIAL_TOKEN_CHECK_DELAY_SECONDS = 10  # Avoid race conditions on startup

# Type alias for tool handlers
ToolHandler = Callable[[dict, dict, "utils.logger.logging.Logger"], Awaitable[List[types.TextContent | types.ImageContent | types.EmbeddedResource]]]

def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the MCP server."""
    parser = argparse.ArgumentParser(description="MCP server options for VoipNow Provisioning")
    parser.add_argument("-c", "--config", type=str, help="Path to configuration file", required=True)
    parser.add_argument("-p", "--port", type=int, help="Port to listen on for SSE", default=8000)
    parser.add_argument("-a", "--address", type=str, help="Address to listen on", default="localhost")
    parser.add_argument(
        "-t",
        "--transport",
        type=str,
        help="Transport type",
        default="stdio",
        choices=["stdio", "streamable-http", "sse"],
    )
    parser.add_argument("-s", "--secure", help="Enable authentication", action="store_true", default=False)
    parser.add_argument("-l", "--log_transport", type=str, help="Type of log transport", default="console", choices=["console", "syslog"])
    return parser.parse_args()

args = parse_args()

def build_tool_schemas() -> list[types.Tool]:
    """Return all exposed tool schemas for the MCP server (dynamically discovered)."""
    return utils.tool_registry.get_tool_schemas()

def build_tool_handlers() -> Dict[str, ToolHandler]:
    """Map tool names to their async handler callables (dynamically discovered)."""
    return utils.tool_registry.get_tool_handlers()

# Build once at import time for fast lookups (now dynamic)
TOOL_HANDLERS: Dict[str, ToolHandler] = build_tool_handlers()

# ConfigManager Class
class ConfigManager:
    """Manage loading, validating, and watching the main configuration.

    Also derives and refreshes the VoipNow token and computed config values.
    """

    def __init__(self, config_file):
        self.config_file = os.path.abspath(config_file)
        self.config_data = {}
        self.voipnow_token = None
        self.voipnow_config = {}
        self.lock = threading.Lock()
        self._token_checker = None  # Will hold TokenExpirationChecker instance
        self.logger = utils.logger.get_logger("mcp-voipnow-provisioning", "INFO", args.log_transport)
        self.load_config()

    def load_config(self):
        """Load configuration from disk, validate, and refresh derived values."""
        with self.lock:
            try:
                # Read new config from file
                with open(self.config_file, 'r') as f:
                    new_config_mcp = json.load(f)

                # Check if config file is valid
                missing_keys = [key for key in required_keys if key not in new_config_mcp]
                if not self.config_data and missing_keys:
                    # This is the first load and keys are missing
                    error_msg = f"Missing keys in config file during initial load: {', '.join(missing_keys)}"
                    self.logger.error(error_msg)
                    raise ConfigurationError(error_msg)
                elif missing_keys:
                    utils.logger.log_warning(self.logger, f"Skipping config reload due to missing keys: {', '.join(missing_keys)}")
                    return  # Skip updating config

                # Check if extra keys are present
                extra_keys = [key for key in new_config_mcp if key not in allowed_keys]
                if not self.config_data and extra_keys:
                    # This is the first load and extra keys present
                    error_msg = f"Extra keys in config file during initial load: {', '.join(extra_keys)}"
                    self.logger.error(error_msg)
                    raise ConfigurationError(error_msg)
                elif extra_keys:
                    utils.logger.log_warning(self.logger, f"Skipping config reload due to extra keys: {', '.join(extra_keys)}")
                    return  # Skip updating config
                  
                # Update logger level (no re-initialization)
                log_level = new_config_mcp.get("logLevel", "INFO")
                utils.logger.set_log_level(self.logger, log_level)

                # Check if URL is valid
                if not new_config_mcp.get("voipnowHost", "").startswith("https://") and not new_config_mcp.get("voipnowHost", "").startswith("http://"):
                    error_msg = "Invalid URL format. Please provide a valid URL in the format 'https://voipnow.com' or 'http://voipnow.com'."
                    self.logger.error(error_msg)
                    raise ConfigurationError(error_msg)

                # Check authTokenMCP if in secure mode
                if args.secure:
                    if 'authTokenMCP' not in new_config_mcp:
                        if not self.config_data:
                            # This is the first load and token is missing
                            error_msg = "authTokenMCP is missing in config file. Please set authTokenMCP when using --secure flag."
                            self.logger.error(error_msg)
                            raise ConfigurationError(error_msg)
                        else:
                            # Subsequent reload and token is missing
                            utils.logger.log_warning(self.logger, "Skipping config reload due to missing authTokenMCP.")
                            return  # Skip updating config

                # Check if token file is provided
                if "voipnowTokenFile" not in new_config_mcp:
                    if not self.config_data:
                        # This is the first load and token file path is missing
                        error_msg = "voipnowTokenFile is missing in config file. Please set voipnowTokenFile."
                        self.logger.error(error_msg)
                        raise ConfigurationError(error_msg)
                    else:
                        # Subsequent reload and token file path is missing
                        utils.logger.log_warning(self.logger, "Skipping config reload due to missing voipnowTokenFile.")
                        return  # Skip updating config

                # Normalize insecure flag to boolean
                if "insecure" in new_config_mcp:
                    new_config_mcp["insecure"] = new_config_mcp["insecure"] is True or new_config_mcp["insecure"] == "true"

                # Update main config data
                self.config_data = new_config_mcp

                # Now handle token file and voipnow config
                # NOTE: All token operations are already protected by self.lock (held above)
                token_file_path = self.config_data.get("voipnowTokenFile")
                if token_file_path:
                    token_path = os.path.abspath(token_file_path)

                    # Check if auth configuration has changed and delete token if needed
                    # This operation is atomic with token regeneration below under the lock
                    config_hash_file = token_path + ".config_hash"
                    config_changed = utils.token.check_config_change(self.config_data, config_hash_file)
                    if config_changed:
                        self.logger.info("Authentication configuration changed. Token file deleted, generating new token...")

                    # Atomically check and regenerate token if missing or expired
                    # No race condition because the entire sequence is under self.lock
                    needs_regeneration = False
                    if not os.path.exists(token_path):
                        if not config_changed:  # Only log if not already logged above
                            self.logger.debug("Token file not found. Generating new token...")
                        needs_regeneration = True
                    else:
                        try:
                            if utils.token.check_token(token_path):
                                if not config_changed:  # Only log if not already logged above
                                    self.logger.debug("Token file expired. Generating new token...")
                                needs_regeneration = True
                        except ValueError as e:
                            # Token file is corrupted
                            # SECURITY: Don't log exception details that might contain token data
                            self.logger.warning("Token file corrupted, regenerating...")
                            needs_regeneration = True

                    # Generate token if needed (still under lock)
                    if needs_regeneration:
                        utils.token.generate_token(self.config_data)

                    # Read token safely (under lock)
                    try:
                        token_data = utils.token._safe_read_token_file(token_path)
                        self.voipnow_token = token_data.split(":")[-1]
                    except ValueError as e:
                        # This shouldn't happen if generation succeeded, but handle it anyway
                        # SECURITY: Don't log exception details that might contain token fragments
                        self.logger.error("Token file still invalid after regeneration")
                        raise RuntimeError("Failed to generate valid token") from e
                else:
                    error_msg = "Token file not specified in config."
                    self.logger.error(error_msg)
                    raise ConfigurationError(error_msg)

                # Update derived config
                self.voipnow_config = {
                    "voipnowUrl": self.config_data.get("voipnowHost", ""),
                    "voipnowToken": self.voipnow_token,
                    "insecure": self.config_data.get("insecure", False),
                }

                self.logger.info("Configuration reloaded.")

                # Start or restart token expiration check
                self.start_token_expiration_check()

            except requests.exceptions.SSLError as e:
                error_msg = f"SSL certificate verification failed: {e}"
                self.logger.error(error_msg)
                if not self.config_data:
                    raise ConfigurationError(error_msg) from e

            except requests.exceptions.HTTPError as e:
                # Handle HTTP errors with specific status codes
                if e.response is not None and e.response.status_code == 401:
                    try:
                        error_data = e.response.json()
                        if error_data.get("error") == "invalid_client":
                            error_msg = "Invalid client credentials (appId/appSecret)"
                            self.logger.error(error_msg)
                            if not self.config_data:
                                raise ConfigurationError(error_msg) from e
                    except (ValueError, KeyError):
                        pass  # Response wasn't JSON or didn't have expected structure

                error_msg = f"HTTP error: {e.response.status_code if e.response else 'unknown'}"
                self.logger.error(error_msg)
                if not self.config_data:
                    raise ConfigurationError(error_msg) from e

            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection error: Cannot connect to VoipNow server: {e}"
                self.logger.error(error_msg)
                if not self.config_data:
                    raise ConfigurationError(error_msg) from e

            except requests.exceptions.Timeout as e:
                error_msg = "Token generation timed out"
                self.logger.error(error_msg)
                if not self.config_data:
                    raise ConfigurationError(error_msg) from e

            except requests.exceptions.RequestException as e:
                error_msg = f"Token generation request failed: {type(e).__name__}"
                self.logger.error(error_msg)
                if not self.config_data:
                    raise ConfigurationError(error_msg) from e

            except (ValueError, KeyError, RuntimeError) as e:
                # Handle token-related errors
                if "token" in str(e).lower() and self.config_data:
                    try:
                        self.logger.warning("Token error detected, attempting to regenerate token...")
                        utils.token.generate_token(self.config_data)
                        # Retry the reload
                        self.load_config()
                        return
                    except (requests.exceptions.RequestException, IOError, ValueError) as regen_error:
                        self.logger.error(f"Failed to regenerate token: {type(regen_error).__name__}")

                self.logger.error("Error reloading config, continuing with previous configuration: %s", type(e).__name__)
                if not self.config_data:
                    raise ConfigurationError(f"Failed to load initial configuration: {type(e).__name__}") from e

            except ConfigurationError:
                # Re-raise configuration errors
                raise

            except (IOError, OSError, json.JSONDecodeError) as e:
                error_msg = f"Failed to load configuration file: {type(e).__name__}"
                self.logger.error(error_msg)
                if not self.config_data:
                    raise ConfigurationError(error_msg) from e

    def get_config(self):
        """Thread-safe accessor for both raw and derived configuration."""
        with self.lock:
            return {
                "main_config": self.config_data,
                "voipnow_config": self.voipnow_config,
            }

    def start_watching(self):
        """Start a watchdog observer to reload config/token file changes."""
        event_handler = ConfigFileHandler(self)
        observer = Observer()
        config_dir = os.path.dirname(self.config_file)
        observer.schedule(event_handler, path=config_dir, recursive=False)
        observer.start()
        self.logger.info("Started watching config and token files for changes.")

        try:
            while not stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            stop_event.set()
        finally:
            observer.stop()
            observer.join()
            self.logger.info("Observer stopped.")
    
    def start_token_expiration_check(self):
        """Schedule or restart the periodic token expiration check."""
        # Stop existing checker if running
        if self._token_checker:
            self._token_checker.stop()

        # Create callback function
        def token_check_callback():
            self.logger.debug("Token is still valid. Callback executed.")

        # Create and start new checker
        self._token_checker = utils.token.TokenExpirationChecker(
            self.config_data,
            self.logger,
            TOKEN_CHECK_INTERVAL_SECONDS,
            token_check_callback
        )
        self._token_checker.start(INITIAL_TOKEN_CHECK_DELAY_SECONDS)


# ConfigFileHandler Class
class ConfigFileHandler(FileSystemEventHandler):
    """Watchdog handler that triggers config reloads on file changes."""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.last_reload_time = {}

    def on_modified(self, event):
        modified_path = os.path.abspath(event.src_path)

        # Get current config to check token file path
        current_config = self.config_manager.get_config()['main_config']
        token_file_path = current_config.get("voipnowTokenFile")
        token_path = os.path.abspath(token_file_path) if token_file_path else None

        config_path = self.config_manager.config_file

        if modified_path == config_path or (token_path and modified_path == token_path):
            # Prevent rapid successive reloads (debounce)
            current_time = time.time()
            if modified_path in self.last_reload_time:
                if current_time - self.last_reload_time[modified_path] < 1.0:  # 1 second debounce
                    return
            
            self.last_reload_time[modified_path] = current_time
            
            # Small delay to ensure file write is complete
            time.sleep(0.1)
            
            self.config_manager.logger.info("Config or token file changed, reloading...")
            self.config_manager.load_config()


# Initialize ConfigManager
config_manager = ConfigManager(args.config)

# Start watching config and token files in a background thread
stop_event = threading.Event()
watcher_thread = threading.Thread(target=config_manager.start_watching, daemon=True)
watcher_thread.start()

# 1. Create an MCP server instance
mcp = Server(
    name="mcp-voipnow-provisioning",
    version="5.7.0",
)


# 2. Define the list of tools
@mcp.list_tools()
async def list_tools() -> list[types.Tool]:
    return build_tool_schemas()


# 3. Implement the tool call logic
@mcp.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Dispatch tool calls to the appropriate async handler.

    Parameters:
        name: The name of the tool to call.
        arguments: The arguments to pass to the tool.

    Returns:
        The tool handler's response content.
    """
    config = config_manager.get_config()
    voipnow_config = config['voipnow_config']
    # Use config_manager.logger
    logger = config_manager.logger
    
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        logger.error(f"Tool not found: {name}")
        raise ValueError(f"Tool not found: {name}")

    try:
        return await handler(arguments, voipnow_config, logger)
    except ValidationError as exc:
        logger.error(f"Tool '{name}' validation failed: {exc}")
        raise ValueError(f"Invalid arguments for tool '{name}'") from exc
    except (KeyError, AttributeError) as exc:
        logger.error(f"Tool '{name}' configuration error: {exc}")
        raise ValueError(f"Tool '{name}' misconfigured") from exc
    except (requests.exceptions.Timeout, TimeoutError) as exc:
        logger.error(f"Tool '{name}' timed out")
        raise RuntimeError(f"Tool '{name}' timed out") from exc
    except requests.exceptions.RequestException as exc:
        logger.error(f"Tool '{name}' network request failed: {type(exc).__name__}")
        raise RuntimeError(f"Failed to execute '{name}': Network error") from exc
    except ValueError as exc:
        # Re-raise ValueError (from validation or SOAP method validation)
        logger.error(f"Tool '{name}' value error: {exc}")
        raise
    except Exception as exc:
        # Catch any unexpected errors but log the type
        logger.error(f"Tool '{name}' unexpected error: {type(exc).__name__}: {exc}")
        raise RuntimeError(f"Tool '{name}' failed unexpectedly") from exc

# Signal handler
def handle_hup(signum, frame):
    """Reload configuration on SIGHUP."""
    config_manager.logger.info(f"Received {signum}, reloading config...")
    config_manager.load_config()
    
if sys.platform != 'win32':
    signal.signal(signal.SIGHUP, handle_hup)

# 4. Start the MCP server
def main():
    """Main entry point with proper error handling."""
    # Validate configuration file
    if not args.config:
        print("Error: No configuration file provided", file=sys.stderr)
        print("Usage: python main.py -c <config_file> [-t <transport>]", file=sys.stderr)
        return 1

    if not os.path.exists(args.config):
        print(f"Error: Config file {args.config} does not exist", file=sys.stderr)
        return 1

    try:
        # Validate transport
        if args.transport == "stdio":
            utils.server.runLocalServer(mcp, config_manager.logger)
        elif args.transport == "sse":
            utils.server.runSSELocalServer(mcp, args, config_manager.logger)
        elif args.transport == "streamable-http":
            utils.server.runHTTPStreamableServer(mcp, args, config_manager.logger)
        else:
            print(f"Error: Unknown transport: {args.transport}", file=sys.stderr)
            print("Valid transports: stdio, sse, streamable-http", file=sys.stderr)
            return 1

        # Wait for shutdown signal
        try:
            while not stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            config_manager.logger.info("Shutting down...")
            stop_event.set()

        watcher_thread.join()
        config_manager.logger.info("Program terminated.")
        return 0

    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Fatal error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())