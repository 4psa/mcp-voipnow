import time
import requests
import sys
import logging
import threading
from typing import Callable
import os
import utils.logger

# Platform-specific imports for file locking
if sys.platform == 'win32':
    import msvcrt  # Windows file locking
else:
    import fcntl   # Unix file locking

def _lock_file(file_handle, exclusive=True):
    """Cross-platform file locking"""
    if sys.platform == 'win32':
        # Windows locking
        lock_mode = msvcrt.LK_NBLCK if exclusive else msvcrt.LK_NBRLCK
        try:
            msvcrt.locking(file_handle.fileno(), lock_mode, 1)
        except IOError:
            raise ValueError("Failed to acquire file lock")
    else:
        # Unix locking
        lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        fcntl.flock(file_handle.fileno(), lock_type)

def _unlock_file(file_handle):
    """Cross-platform file unlocking"""
    if sys.platform == 'win32':
        try:
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
        except IOError:
            pass
    else:
        fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)

def _safe_read_token_file(token_file_path: str):
    """
    Safely reads token file with file locking to prevent race conditions.
    Returns the token data as a string, or raises ValueError if file is invalid.

    Note: Exception messages are sanitized to prevent token leakage in logs.
    """
    try:
        with open(token_file_path, "r") as token_file:
            # Acquire shared lock for reading
            _lock_file(token_file, exclusive=False)
            try:
                token_data = token_file.read().strip()
            finally:
                _unlock_file(token_file)

        # Handle empty or incomplete token file
        # SECURITY: Don't include token_data in exception messages
        if not token_data:
            raise ValueError("Token file is empty")

        parts = token_data.split(":")
        if len(parts) < 3:
            # SECURITY: Don't expose actual token parts count or content
            raise ValueError(f"Invalid token format: expected 3 colon-separated parts, got {len(parts)}")

        return token_data
    except (IOError, OSError) as e:
        # SECURITY: Don't propagate file content in error messages
        raise ValueError(f"Failed to read token file: {type(e).__name__}") from e

def generate_token(config_mcp: dict):
    """
    Sends an OAuth client credentials grant request to retrieve a new token.
    Saves the token to a file.
    """
    voipnow_host = config_mcp["voipnowHost"]
    if not voipnow_host.startswith("https://"):
        voipnow_host = "https://" + voipnow_host

    data = {
        "client_id": config_mcp["appId"],
        "client_secret": config_mcp["appSecret"],
        "grant_type": "client_credentials",
        "type": "unifiedapi",
        "redirect_uri": f"{voipnow_host}/oauth/token.php",
    }

    # Configure SSL verification based on insecure flag
    verify_ssl = not config_mcp.get("insecure", False)

    # Disable SSL warnings if in insecure mode
    if config_mcp.get("insecure", False):
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    response = requests.post(
        f"{voipnow_host}/oauth/token.php",
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "VoipNow Provisioning MCP Version/2025.2",
            },
        verify=verify_ssl,
        timeout=30,
    )
    response.raise_for_status()  # Raise error for 4xx/5xx responses

    now = int(time.time())
    token_data = (
        f"{now}:{now + response.json()['expires_in']}:{response.json()['access_token']}"
    )
    
    # Use atomic write with file locking to prevent race conditions
    token_file_path = config_mcp["voipnowTokenFile"]
    temp_file_path = token_file_path + ".tmp"
    
    # Set umask to ensure restrictive permissions from the start
    old_umask = os.umask(0o077)
    try:
        # Write to temporary file first
        with open(temp_file_path, "w") as token_file:
            # Acquire exclusive lock for writing
            _lock_file(token_file, exclusive=True)
            try:
                token_file.write(token_data)
                token_file.flush()
                os.fsync(token_file.fileno())  # Ensure data is written to disk
            finally:
                _unlock_file(token_file)

        # Atomically move temp file to final location
        os.rename(temp_file_path, token_file_path)
        os.chmod(token_file_path, 0o600)  # Defensive chmod
    except IOError as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass
        raise IOError(f"Failed to write token file: {e}") from e
    finally:
        # Restore original umask
        os.umask(old_umask)


def check_token(token_file_path: str):
    """
    Checks if the token has expired or is about to expire in the next 5 minutes.
    """
    try:
        token_data = _safe_read_token_file(token_file_path)
        parts = token_data.split(":")
        expiration_timestamp = parts[1]
        return int(time.time()) >= int(expiration_timestamp) - 300
    except (IndexError, ValueError) as e:
        raise ValueError(f"Failed to read or parse token file: {e}") from e


def get_expiration_timestamp(token_file_path: str):
    """
    Returns the expiration timestamp of the token from the .access_token file.
    """
    try:
        token_data = _safe_read_token_file(token_file_path)
        parts = token_data.split(":")
        expiration_timestamp = parts[1]
        return int(expiration_timestamp)
    except (IndexError, ValueError) as e:
        raise ValueError(f"Failed to read or parse token file: {e}") from e


def check_config_change(config_mcp: dict, config_hash_file: str):
    """
    Checks if the authentication-related configuration has changed.
    If changed, deletes the token file so it gets regenerated.
    Returns True if configuration has changed.

    Uses secure file creation with umask and atomic writes to prevent
    information disclosure through world-readable file permissions.
    """
    import hashlib

    # Create hash of authentication-related config
    auth_config = {
        "appId": config_mcp.get("appId", ""),
        "appSecret": config_mcp.get("appSecret", ""),
        "voipnowHost": config_mcp.get("voipnowHost", "")
    }

    current_hash = hashlib.sha256(str(auth_config).encode()).hexdigest()

    try:
        with open(config_hash_file, 'r') as f:
            stored_hash = f.read().strip()

        if stored_hash != current_hash:
            # Config changed, update hash file atomically with secure permissions
            temp_file = config_hash_file + ".tmp"
            old_umask = os.umask(0o077)  # Ensure restrictive permissions from creation
            try:
                with open(temp_file, 'w') as f:
                    f.write(current_hash)
                    f.flush()
                    os.fsync(f.fileno())  # Ensure data is written to disk

                # Atomically replace the hash file
                os.rename(temp_file, config_hash_file)
                os.chmod(config_hash_file, 0o600)  # Defensive chmod
            finally:
                os.umask(old_umask)  # Restore original umask
                # Clean up temp file if it still exists
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except OSError:
                        pass

            # Delete token file so it gets regenerated
            token_file = config_mcp.get("voipnowTokenFile")
            if token_file and os.path.exists(token_file):
                os.remove(token_file)

            return True
        return False

    except FileNotFoundError:
        # First time, create hash file with secure permissions
        old_umask = os.umask(0o077)  # Ensure restrictive permissions from creation
        try:
            with open(config_hash_file, 'w') as f:
                f.write(current_hash)
                f.flush()
                os.fsync(f.fileno())
            os.chmod(config_hash_file, 0o600)  # Defensive chmod
        finally:
            os.umask(old_umask)  # Restore original umask
        return False


class TokenExpirationChecker:
    """
    Manages token expiration checking with proper cleanup and error handling.

    Uses a single timer that reschedules itself, with proper cancellation support
    to avoid unbounded thread growth.
    """

    def __init__(self, config_mcp: dict, logger: logging.Logger, interval: float, callback: Callable[[], None]):
        """
        Initialize the token expiration checker.

        Parameters:
            config_mcp (dict): Configuration dictionary
            logger (logging.Logger): Logger instance
            interval (float): Check interval in seconds
            callback (Callable): Function to call when token is still valid
        """
        self.config_mcp = config_mcp
        self.logger = logger
        self.interval = interval
        self.callback = callback
        self._timer = None
        self._running = False

    def start(self, initial_delay: float = 10.0):
        """
        Start the token expiration checker.

        Parameters:
            initial_delay (float): Delay before first check (default 10 seconds)
        """
        if self._running:
            self.logger.warning("Token expiration checker already running")
            return

        self._running = True
        self._schedule_next_check(initial_delay)
        self.logger.debug(f"Token expiration checker started (check every {self.interval}s)")

    def stop(self):
        """Stop the token expiration checker and cancel any pending timer."""
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None
        self.logger.debug("Token expiration checker stopped")

    def _schedule_next_check(self, delay: float):
        """
        Schedule the next token check.

        Parameters:
            delay (float): Delay in seconds before next check
        """
        if not self._running:
            return

        self._timer = threading.Timer(delay, self._check_token)
        self._timer.daemon = True
        self._timer.start()

    def _check_token(self):
        """Check token expiration and schedule next check."""
        if not self._running:
            return

        voipnow_token_file = self.config_mcp.get("voipnowTokenFile")
        if not voipnow_token_file:
            self.logger.error("Token file path not configured")
            return

        # Check if token needs regeneration
        try:
            if check_token(voipnow_token_file):
                self.logger.debug("Token expired or expiring, regenerating...")
                try:
                    generate_token(self.config_mcp)
                    self.logger.debug("Token regenerated successfully")
                except requests.exceptions.HTTPError as e:
                    # Handle HTTP errors with specific status codes
                    if e.response is not None and e.response.status_code == 401:
                        try:
                            error_data = e.response.json()
                            if error_data.get("error") == "invalid_client":
                                self.logger.error("Invalid client credentials (appId/appSecret)")
                                self.stop()  # Stop checker on auth failure
                                return
                        except (ValueError, KeyError):
                            pass
                    self.logger.error(f"HTTP error generating token: {e.response.status_code if e.response else 'unknown'}")
                    # Schedule retry sooner on failure
                    self._schedule_next_check(min(60, self.interval / 5))
                    return

                except requests.exceptions.ConnectionError as e:
                    self.logger.error(f"Cannot connect to OAuth server: {type(e).__name__}")
                    # Schedule retry sooner - might be temporary network issue
                    self._schedule_next_check(min(60, self.interval / 5))
                    return

                except requests.exceptions.Timeout as e:
                    self.logger.error("OAuth request timed out")
                    # Schedule retry sooner
                    self._schedule_next_check(min(60, self.interval / 5))
                    return

                except requests.exceptions.RequestException as e:
                    self.logger.error(f"OAuth request failed: {type(e).__name__}")
                    self._schedule_next_check(min(60, self.interval / 5))
                    return

                except (IOError, OSError) as e:
                    self.logger.error(f"Failed to write token file: {type(e).__name__}")
                    self._schedule_next_check(min(60, self.interval / 5))
                    return

        except ValueError as e:
            self.logger.error(f"Error checking token: {type(e).__name__}")
            self._schedule_next_check(self.interval)
            return

        # Calculate next check interval based on expiration time
        try:
            expiration_timestamp = get_expiration_timestamp(voipnow_token_file)
            current_time = time.time()
            time_until_expiration = expiration_timestamp - current_time

            # Calculate next check interval
            if time_until_expiration > 0:
                next_check = min(time_until_expiration, self.interval)
            else:
                next_check = self.interval

            # Call the callback
            if self.callback:
                try:
                    self.callback()
                except Exception as e:
                    self.logger.warning(f"Token check callback failed: {type(e).__name__}")

            # Schedule next check
            self._schedule_next_check(next_check)

        except ValueError as e:
            self.logger.error(f"Error reading token expiration: {type(e).__name__}")
            self._schedule_next_check(self.interval)


def check_token_expiration(
    config_mcp: dict,
    logger: logging.Logger,
    interval: float,
    callback: Callable[[], None],
):
    """
    Checks if the token has expired or is about to expire. If it has,
    generates a new token. If not, schedules the callback and rechecks
    the token after a calculated interval.

    DEPRECATED: Use TokenExpirationChecker class instead for better management.

    This function is kept for backwards compatibility but creates a
    recursive timer chain. New code should use TokenExpirationChecker.

    Parameters:
        config_mcp (dict): Configuration dictionary containing
        logger (logging.Logger): Logger object for logging messages.
        interval (float): Interval in seconds to wait before next check.
        callback (callable): A function to call when the token is still valid.
    """
    # Create a checker instance and start it
    # Note: This creates a new checker each time which is not ideal
    # Callers should migrate to using TokenExpirationChecker directly
    checker = TokenExpirationChecker(config_mcp, logger, interval, callback)
    checker.start(initial_delay=0)
