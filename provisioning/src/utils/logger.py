import logging
from logging.handlers import SysLogHandler
import sys


# Function to get a logger instance
def get_logger(name: str, log_level: str, log_transport: str):
    """
    Get a logger instance with the specified name.

    Parameters:
    name (str): The name of the logger.

    Returns:
    logging.Logger: The logger instance.
    """
    # Set application name
    logger = logging.getLogger(name)
    # Set the log level from the configuration
    set_log_level(logger, log_level)

    if log_transport == "syslog":
        # Create a SysLogHandler
        if sys.platform == "darwin":
            handler = SysLogHandler(
                address="/var/run/syslog", facility=SysLogHandler.LOG_LOCAL0
            )
        elif sys.platform == "linux":
            handler = SysLogHandler(
                address="/dev/log", facility=SysLogHandler.LOG_LOCAL0
            )
        elif sys.platform == "win32":
            handler = SysLogHandler(
                address=("127.0.0.1", 514), facility=SysLogHandler.LOG_LOCAL0
            )
        else:
            raise RuntimeError(f"Unsupported platform for syslog: {sys.platform}")
    else:
        # For console transport, log to stderr to avoid protocol interference
        # stderr is by default
        handler = logging.StreamHandler()

    # Reuse the same formatter
    formatter = logging.Formatter(
        "%(name)s: { 'level': '%(levelname)s' , 'message': '%(message)s'}"
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)
    logger.propagate = False  # Prevent logs from being handled by root logger
    logger.name = name
    return logger

def set_log_level(logger, log_level):
    """
    Set the log level for the logger.

    Parameters:
    logger (logging.Logger): The logger instance.
    log_level (str): The log level to set.
    """
    log_level = log_level.upper()
    if log_level in logging._nameToLevel:
        logger.setLevel(logging._nameToLevel[log_level])
    else:
        logger.setLevel(logging.INFO)
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        logger.warning(f"Invalid log level: {log_level} [{', '.join(valid_levels)}], defaulting to 'INFO'")


# Function to set syslog handler
def set_syslog_handler(logger, loggers_to_configure):
    """
    Set the syslog handler for the specified loggers.

    Parameters:
    logger (logging.Logger): The logger instance.
    loggers_to_configure (list): List of loggers to configure.
    """
    # Configure Uvicorn and Starlette loggers to use the same syslog handler
    syslog_handler = logger.handlers[0]  # Reuse the SysLogHandler from your main logger

    # Configure Uvicorn and Starlette loggers to use the same syslog handler
    for logger_name in loggers_to_configure:
        target_logger = logging.getLogger(logger_name)
        target_logger.setLevel(logging.INFO)

        # Remove any existing handlers to prevent duplicate logs
        for handler in target_logger.handlers[:]:
            target_logger.removeHandler(handler)

        # Add the syslog handler
        target_logger.addHandler(syslog_handler)
        target_logger.propagate = (
            False  # Prevent logs from being handled by the root logger
        )


def log_error(logger, error_message):
    """
    Log an error message.

    Note: This function no longer calls sys.exit(). Callers should handle
    exit decisions themselves by raising exceptions or calling sys.exit()
    in the main entry point.
    """
    logger.error(error_message)

def log_stdout(logger, message):
    """Log an info message."""
    logger.info(message)

def log_warning(logger, message):
    """Log a warning message."""
    logger.warning(message)