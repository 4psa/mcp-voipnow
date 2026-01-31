import json
import logging
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
)

AUTH_TYPE = "bearer"


def get_auth_token(file_path: str, logger: logging.Logger) -> str | None:
    logger.debug(f"Reading auth token from {file_path}")
    try:
        with open(file_path, "r") as f:
            config_data = json.load(f)
            if config_data["authTokenMCP"]:
                return config_data["authTokenMCP"]

        logger.error("AUTH TOKEN not found in .config file")
        return None
    except Exception as e:
        logger.error(f"Error reading token from file: {e}")
        return None


class BasicAuthBackend(AuthenticationBackend):
    def __init__(self, logger: logging.Logger, config_file: str):
        self.logger = logger
        self.config_file = config_file

    async def authenticate(self, conn):
        auth = conn.headers.get("Authorization")

        if not auth:
            self.logger.error("Authorization header is missing")
            raise AuthenticationError("Unauthorized")

        try:
            scheme, credentials = auth.split(maxsplit=1)
        except ValueError:
            self.logger.error("Invalid Authorization header format - cannot split")
            raise AuthenticationError("Unauthorized")

        if scheme.lower() != AUTH_TYPE:
            self.logger.error(f"Invalid Authorization scheme: {scheme}")
            raise AuthenticationError("Unauthorized")

        safe_token = get_auth_token(self.config_file, self.logger)
        if not safe_token:
            self.logger.error("No stored token found")
            raise AuthenticationError("Unauthorized")

        if credentials != safe_token:
            self.logger.error("Invalid token provided")
            raise AuthenticationError("Unauthorized")

        self.logger.debug("Token is valid")
        return AuthCredentials(["authenticated"]), SimpleUser("")
