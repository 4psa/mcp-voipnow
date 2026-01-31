import anyio
import uvicorn
from collections.abc import AsyncIterator
import contextlib
import logging

from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware import Middleware
from starlette.types import Receive, Scope, Send

import auth.auth as auth
import utils.logger


class ClosedResourceErrorFilter(logging.Filter):
    """Filter to suppress ClosedResourceError exceptions from MCP library.
    
    These errors occur when clients disconnect before the message router
    finishes reading from the stream. This is a normal condition and the
    request has already been processed successfully.
    """
    def filter(self, record):
        # Check if this is an error log about ClosedResourceError
        if record.levelno >= logging.ERROR:
            # Check if the message contains ClosedResourceError
            if hasattr(record, 'exc_info') and record.exc_info:
                exc_type = record.exc_info[0]
                if exc_type is not None and 'ClosedResourceError' in str(exc_type):
                    return False
            # Also check the message text
            if 'ClosedResourceError' in str(record.getMessage()):
                return False
        return True

def runLocalServer(mcp, logger):

    async def arun():

        utils.logger.log_stdout(logger, "VoipNow Provisioning MCP Server running on stdio")
        async with stdio_server() as streams:
            await mcp.run(
                streams[0], streams[1], 
                mcp.create_initialization_options()
            )

    anyio.run(arun)

def _create_middleware(args, logger):
    """Create middleware configuration based on security settings."""
    if args.secure:
        return [
            Middleware(
                AuthenticationMiddleware,
                backend=auth.BasicAuthBackend(logger, args.config),
            )
        ]
    return []

def _create_shutdown_handler(logger):
    """Create a shutdown handler function."""
    def shutdown_handler():
        utils.logger.log_stdout(logger, "Shutting down MCP server gracefully")
    return shutdown_handler

def _setup_logging_handlers(logger):
    """Set up syslog handlers for uvicorn and starlette."""
    utils.logger.set_syslog_handler(
        logger,
        loggers_to_configure=[
            "uvicorn",
            "uvicorn.access",
            "uvicorn.error",
            "starlette",
        ],
    )
    
    # Add filter to suppress ClosedResourceError exceptions from MCP library
    # These occur when clients disconnect and are normal behavior
    closed_resource_filter = ClosedResourceErrorFilter()
    
    # Apply filter to MCP library loggers
    mcp_logger = logging.getLogger("mcp.server.streamable_http")
    mcp_logger.addFilter(closed_resource_filter)
    
    # Also apply to uvicorn.error logger since errors might propagate there
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.addFilter(closed_resource_filter)

def runSSELocalServer(mcp, args, logger):
    utils.logger.log_warning(
        logger,
        "The sse transport is deprecated and has been replaced by streamable-http"
    )

    sse = SseServerTransport("/messages/")

    # Set up logging and middleware
    _setup_logging_handlers(logger)
    middleware = _create_middleware(args, logger)

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp.run(
                streams[0], streams[1], 
                mcp.create_initialization_options()
            )
        return Response()

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ],
        on_shutdown=[_create_shutdown_handler(logger)],
        middleware=middleware,
    )
    utils.logger.log_stdout(logger, "VoipNow Provisioning MCP Server running on sse")
    uvicorn.run(starlette_app, host=args.address, port=args.port, log_config=None)

def runHTTPStreamableServer(mcp, args, logger):

    # Create the session manager with true stateless mode
    session_manager = StreamableHTTPSessionManager(
        app=mcp,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    # Set up logging and middleware
    middleware = _create_middleware(args, logger)
    _setup_logging_handlers(logger)

    # ASGI handler for streamable HTTP connections
    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        try:
            await session_manager.handle_request(scope, receive, send)
        except anyio.ClosedResourceError:
            # This is a normal condition when clients disconnect before
            # the message router finishes reading from the stream.
            # The request has already been processed successfully (200 status),
            # so we can safely ignore this error.
            logger.debug("Client disconnected during stream processing (normal)")
        except Exception as e:
            # Log other unexpected errors but don't crash the server
            logger.error(f"Unexpected error in streamable HTTP handler: {type(e).__name__}: {e}")
            raise

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
        middleware=middleware,
    )

    utils.logger.log_stdout(logger, "VoipNow Provisioning MCP Server running on streamable-http")
    uvicorn.run(starlette_app, host=args.address, port=args.port, log_config=None)
