import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { randomUUID } from 'node:crypto';
import express, { Request, Response } from 'express';
import { isInitializeRequest } from '@modelcontextprotocol/sdk/types.js';
import { OptionValues } from "commander";
import { Logger } from "winston";
import * as auth from "./auth/auth.js";
import { logError, logStdout, logWarning } from "./logger.js";

// Constants for error codes and messages
const ERROR_CODES = {
  INVALID_SESSION: -32000,
  INTERNAL_ERROR: -32603,
} as const;

const ERROR_MESSAGES = {
  INVALID_SESSION: 'Invalid or missing session ID',
  INTERNAL_ERROR: 'Internal server error',
} as const;

// Utility function to create JSON-RPC error response
function createErrorResponse(code: number, message: string, id: any = null) {
  return {
    jsonrpc: '2.0',
    error: { code, message },
    id,
  };
}

// Utility function to clean up transports
async function cleanupTransports(transports: Record<string, any>, logger: Logger): Promise<void> {
  for (const sessionId in transports) {
    try {
      logger.info(`Closing transport for session ${sessionId}`);
      await transports[sessionId].close();
      delete transports[sessionId];
    } catch (error) {
      logger.error(`Error closing transport for session ${sessionId}:`, error);
    }
  }
}

// Utility function to setup routes with optional authentication
function setupRoutesWithAuth(app: express.Application, routes: Array<{method: 'get'|'post'|'delete', path: string, handler: any}>, options: OptionValues, logger: Logger) {
  const basicAuth = options.secure ? auth.createBasicAuth(logger, options.config) : null;
  
  routes.forEach(({method, path, handler}) => {
    if (basicAuth) {
      app[method](path, basicAuth, handler);
    } else {
      app[method](path, handler);
    }
  });
}

/**
 * Validate port number
 * @param port - Port value to validate
 * @returns Validated port number
 * @throws Error if port is invalid
 */
function validatePort(port: any): number {
    const portNum = parseInt(port, 10);
    if (isNaN(portNum) || portNum < 1 || portNum > 65535) {
        throw new Error(`Invalid port: ${port}. Must be between 1 and 65535`);
    }
    return portNum;
}

/**
 * Validate address
 * @param address - Address to validate
 * @returns Validated address
 * @throws Error if address is invalid
 */
function validateAddress(address: any): string {
    if (!address || typeof address !== 'string' || address.length === 0) {
        throw new Error('Address cannot be empty');
    }

    // Basic validation for IP address format or localhost
    const isValidIP = /^(\d{1,3}\.){3}\d{1,3}$/.test(address);
    const isLocalhost = address === 'localhost';
    const isValidHostname = /^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$/.test(address);

    if (!isValidIP && !isLocalhost && !isValidHostname) {
        throw new Error(`Invalid address: ${address}. Must be a valid IP, hostname, or 'localhost'`);
    }

    return address;
}

export async function runSSELocalServer(server: Server, options: OptionValues, logger: Logger) {
    logWarning("The sse transport is deprecated and has been replaced by streamable-http")
    // Store transports by session ID
    const transports: Record<string, SSEServerTransport> = {};
    const app = express();

    // Health check endpoint
    app.get('/health', (req: Request, res: Response) => {
        res.status(200).json({
            status: 'healthy',
            service: 'voipnow-calls-mcp',
            transport: 'sse',
            timestamp: new Date().toISOString()
        });
    });

    const mcpGetHandler = async (req: Request, res: Response) => {
        try {
            // Create a new SSE transport for the client
            // The endpoint for POST messages is '/messages'
            const transport = new SSEServerTransport('/messages', res);

            // Store the transport by session ID
            const sessionId = transport.sessionId;
            transports[sessionId] = transport;

            // Set up onclose handler to clean up transport when closed
            transport.onclose = () => {
                logger.info(`SSE transport closed for session ${sessionId}`);
                delete transports[sessionId];
            };
            await server.connect(transport);
        } catch (error) {
            logger.error(`Error establishing SSE stream: ${error}`);
            if (!res.headersSent) {
                res.status(500).send('Error establishing SSE stream');
            }
        }
    };

    const mcpPostHandler = async (req: Request, res: Response) => {
        // Extract session ID from URL query parameter
        // In the SSE protocol, this is added by the client based on the endpoint event
        const sessionId = req.query.sessionId as string | undefined;

        if (!sessionId) {
            logger.error('No session ID provided in request URL');
            res.status(400).send('Missing sessionId parameter');
            return;
        }

        const transport = transports[sessionId];
        if (!transport) {
            logger.error(`No active transport found for session ID: ${sessionId}`);
            res.status(404).send('Session not found');
            return;
        }
        try {
            // Handle the POST message with the transport
            transport.handlePostMessage(req, res, req.body);
        } catch (error) {
            logger.error('Error handling request:', error);
            if (!res.headersSent) {
                res.status(500).send('Error handling request');
            }
        }
    };

    // Use utility function for route setup
    setupRoutesWithAuth(app, [
        { method: 'get', path: '/sse', handler: mcpGetHandler },
        { method: 'post', path: '/messages', handler: mcpPostHandler }
    ], options, logger);

    // Validate port and address
    const PORT = validatePort(options.port);
    const ADDRESS = validateAddress(options.address);

    try {
        app.listen(PORT, ADDRESS, () => {
            logStdout(`VoipNow Calls MCP SSE Server listening on http://${ADDRESS}:${PORT}`);
            logStdout(`SSE endpoint: http://${ADDRESS}:${PORT}/sse`);
            logStdout(`Message endpoint: http://${ADDRESS}:${PORT}/messages`);
        });
    } catch (error) {
        logError('Error starting server:', error);
    }

    // Handle server shutdown using utility function
    process.on('SIGINT', async () => {
        logStdout('Shutting down server...');
        await cleanupTransports(transports, logger);
        logStdout('Server shutdown complete');
        process.exit(0);
    });
}

export async function runHTTPStreamableServer(serverFactory: (() => Server) | Server, options: OptionValues, logger: Logger) {
    const app = express();
    app.use(express.json());
    // Map to store transports and servers by session ID
    const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};
    const servers: { [sessionId: string]: Server } = {};

    // Check if serverFactory is a function or a Server instance (for backward compatibility)
    const isFactory = typeof serverFactory === 'function';
    const legacyServer = !isFactory ? serverFactory as Server : null;

    // Health check endpoint
    app.get('/health', (req: Request, res: Response) => {
        res.status(200).json({
            status: 'healthy',
            service: 'voipnow-calls-mcp',
            transport: 'streamable-http',
            activeSessions: Object.keys(transports).length,
            timestamp: new Date().toISOString()
        });
    });

    const mcpPostHandler = async (req: Request, res: Response) => {
        try {
            const sessionId = req.headers['mcp-session-id'] as string | undefined;
            let transport: StreamableHTTPServerTransport;

            if (sessionId && transports[sessionId]) {
                // Reuse existing transport
                transport = transports[sessionId];
            } else if (!sessionId && req.method === 'POST' && isInitializeRequest(req.body)) {
                // New initialization request - create new server instance for this session
                transport = new StreamableHTTPServerTransport({
                    sessionIdGenerator: () => randomUUID(),
                    onsessioninitialized: (sessionId) => {
                        // Store the transport by session ID when session is initialized
                        // This avoids race conditions where requests might come in before the session is stored
                        transports[sessionId] = transport;
                    }
                });

                // Create a new server instance for this session
                const sessionServer = isFactory ? (serverFactory as () => Server)() : legacyServer!;

                // Set up onclose handler to clean up transport and server when closed
                transport.onclose = () => {
                    const sid = transport.sessionId;
                    if (sid && transports[sid]) {
                        delete transports[sid];
                        delete servers[sid];
                        logger.info(`Cleaned up server and transport for session ${sid}`);
                    }
                };

                // Connect the transport to the MCP server BEFORE handling the request
                // so responses can flow back through the same transport
                logger.info('Creating server instance for new session');
                logger.info('Connecting transport to server');
                await sessionServer.connect(transport);

                // Store the server instance
                const sid = transport.sessionId;
                if (sid) {
                    servers[sid] = sessionServer;
                }

                await transport.handleRequest(req, res, req.body);
                return; // Already handled
            } else {
                res.status(400).json(createErrorResponse(ERROR_CODES.INVALID_SESSION, ERROR_MESSAGES.INVALID_SESSION));
                return;
            }

            await transport.handleRequest(req, res, req.body);
        } catch (error) {
            logger.error('Error handling MCP request:', error);
            if (!res.headersSent) {
                res.status(500).json(createErrorResponse(ERROR_CODES.INTERNAL_ERROR, ERROR_MESSAGES.INTERNAL_ERROR));
            }
        }
    }

    // Handle GET requests for SSE streams (using built-in support from StreamableHTTP)
    const mcpGetHandler = async (req: Request, res: Response) => {
        const sessionId = req.headers['mcp-session-id'] as string | undefined;
        if (!sessionId || !transports[sessionId]) {
            res.status(400).send('Invalid or missing session ID');
            return;
        }

        // Check for Last-Event-ID header for resumability
        const lastEventId = req.headers['last-event-id'] as string | undefined;
        if (lastEventId) {
            logger.info(`Client reconnecting with Last-Event-ID: ${lastEventId}`);
        } else {
            logger.info(`Establishing new SSE stream for session ${sessionId}`);
        }

        const transport = transports[sessionId];
        await transport.handleRequest(req, res);
    };

    // Handle DELETE requests for session termination (according to MCP spec)
    const mcpDeleteHandler = async (req: Request, res: Response) => {
        const sessionId = req.headers['mcp-session-id'] as string | undefined;
        if (!sessionId || !transports[sessionId]) {
            res.status(400).send('Invalid or missing session ID');
            return;
        }

        logger.info(`Received session termination request for session ${sessionId}`);

        try {
            const transport = transports[sessionId];
            await transport.handleRequest(req, res);
        } catch (error) {
            logger.error('Error handling session termination:', error);
            if (!res.headersSent) {
                res.status(500).send('Error processing session termination');
            }
        }
    }

    // Use utility function for route setup
    setupRoutesWithAuth(app, [
        { method: 'post', path: '/mcp', handler: mcpPostHandler },
        { method: 'get', path: '/mcp', handler: mcpGetHandler },
        { method: 'delete', path: '/mcp', handler: mcpDeleteHandler }
    ], options, logger);

    // Validate port and address
    const PORT = validatePort(options.port);
    const ADDRESS = validateAddress(options.address);

    const appServer = app.listen(PORT, ADDRESS, () => {
        logStdout(`VoipNow Calls MCP Streamable HTTP Server listening on  http://${ADDRESS}:${PORT}`);
        logStdout(`Streamable HTTP endpoint: http://${ADDRESS}:${PORT}/mcp`);
    });

    process.on('SIGINT', async () => {
        logStdout('Shutting down server...');
        await cleanupTransports(transports, logger);
        appServer.close(() => {
            logStdout('Server shutdown complete');
            logger.end();
            process.exit(0);
        });
    });
}

export async function runLocalServer(server: Server, logger: Logger) {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    logStdout("VoipNow Calls MCP Server running on stdio");
}
