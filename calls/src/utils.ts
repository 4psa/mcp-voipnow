import { fileURLToPath } from 'url';
import path from 'path';
import { OptionValues } from 'commander';
import { logger, logError } from './logger.js'
import { generateToken, checkToken, checkConfigChange } from './token/utils.js'
import fs from 'fs'
import net from 'net'

// Validation constants
const VALIDATION_LIMITS = {
  COUNT_MIN: 1,
  COUNT_MAX: 4999,
  START_INDEX_MIN: 0,
  START_INDEX_MAX: 4999,
} as const;

// Regular expressions for validation
const REGEX_PATTERNS = {
  EXTENSION: /^(?:\d{4}\*\d{3}|\d{3})$/,
  SELF: /^@self$/,
  CALLER_ID: /^[A-Za-z\s]+<[0-9*+]+>$/,
  PHONE_NUMBER: /^\+?\d+$/,
} as const;

// Validation error messages grouped by category
export const VALIDATION_ERRORS = {
  COUNT: "Invalid count value. Count must be between 1 and 4999.",
  START_INDEX: "Invalid startIndex value. startIndex must be between 0 and 4999",
  EXTENSION: "Invalid extension format. Please provide a valid extension in the format '1234*123', '123' or '@self'.",
  EXTENSION_SELF: "For this tool, '@self' is not a valid extension format. Please provide a valid extension in the format '1234*123', '123'.",
  CALLER_ID: "Invalid caller ID format. Please provide a valid caller ID in the format 'John Doe <12343432>', 'John Doe <0003*001>', 'John Doe <001>', or 'John Doe <+12343432>'.",
  PHONE_NUMBER: "Invalid phone number format. Please provide a valid phone number in the format '+1234567890' or '1234567890'.",
  PHONE_NUMBER_OR_EXTENSION: "Invalid phone number or extension format. Please provide a valid phone number or extension in the format '+1234567890', '1234567890', '1234*123', '123' or '@self'.",
  AGENT_ID: "Invalid agent ID format. Please provide a valid agent ID in the format '+1234567890', '1234567890', '1234*123' or '123'.",
} as const;

/**
 * Utility function to properly concatenate base URL and relative path
 * @param baseURL - The base URL (e.g. 'https://api.example.com')
 * @param relativePath - The path to append (e.g. '/api/v1/resource')
 * @returns Properly formatted combined URL
 */
export function createUrl(baseURL: string, relativePath: string): string {
    // Remove trailing slash from base if exists
    const cleanBase = baseURL.endsWith('/')
        ? baseURL.slice(0, -1)
        : baseURL;

    // Remove leading slash from path if exists
    const cleanPath = relativePath.startsWith('/')
        ? relativePath.slice(1)
        : relativePath;

    return `${cleanBase}/${cleanPath}`;
}

/**
 * Utility function to properly generate a random string if nothing is provided
 * @returns A unique string
 */
export function generateNonce() {
    var time = process.hrtime();
    var pid = process.pid;
    var buf = Buffer.from("" + (time[0] ^ time[1] ^ pid));

    return toUriSafeBase64(buf.toString('base64'));
}

function toUriSafeBase64(str: string) {
    return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/**
 * Interface for query parameters
 */
export interface QueryParam {
    name: string;
    value: any;
    validate?: (value: string) => boolean;
    errorMessage?: string;
}

/**
 * Function to check count value
 * @param value - The value to check
 * @returns True if the count is valid
 */
export function validateCount(value: string): boolean {
    const num = parseInt(value, 10);
    return num >= VALIDATION_LIMITS.COUNT_MIN && num <= VALIDATION_LIMITS.COUNT_MAX;
}
export const errorMessageCount = VALIDATION_ERRORS.COUNT;

/**
 * Function to check startIndex value
 * @param value - The value to check
 * @returns True if the startIndex is valid
 */
export function validateStartIndex(value: string): boolean {
    const num = parseInt(value, 10);
    return num >= VALIDATION_LIMITS.START_INDEX_MIN && num <= VALIDATION_LIMITS.START_INDEX_MAX;
}
export const errorStartIndex = VALIDATION_ERRORS.START_INDEX;

/**
 * Function to check extension format    
 * @param variable - The variable to check
 * @returns True if the extension is valid
 */
export function validateExtension(variable: string): boolean {
    // Accepted formats: "1234*123", "123" or "@self"
    return REGEX_PATTERNS.EXTENSION.test(variable) || REGEX_PATTERNS.SELF.test(variable);
}
export const errorMessageExtension = VALIDATION_ERRORS.EXTENSION;
export const errorMessageExtensionSelf = VALIDATION_ERRORS.EXTENSION_SELF;

/**
 * Function to check caller ID format    
 * @param variable - The variable to check
 * @returns True if the caller ID is valid
 */
export function validateCallerID(variable: string): boolean {
    // Accepted formats: "John Doe <12343432>", "John Doe <0003*001>", "John Doe <001>", or "John Doe <+12343432>"
    return REGEX_PATTERNS.CALLER_ID.test(variable);
}
export const errorMessageCallerID = VALIDATION_ERRORS.CALLER_ID;

/**
 * Function to check Phone Number format    
 * @param variable - The variable to check
 * @returns True if the phone number is valid
 */
export function validatePhoneNumber(variable: string): boolean {
    // Accepted formats: "+1234567890" or "1234567890"
    return REGEX_PATTERNS.PHONE_NUMBER.test(variable);
}
export const errorMessagePhoneNumber = VALIDATION_ERRORS.PHONE_NUMBER;

export function validatePhoneNumberOrExtension(variable: string): boolean {
    return validatePhoneNumber(variable) || validateExtension(variable);
}
export const errorMessagePhoneNumberOrExtension = VALIDATION_ERRORS.PHONE_NUMBER_OR_EXTENSION;

/**
 * Function to check Agent ID format    
 * @param variable - The variable to check
 * @returns True if the agent ID is valid
 */
export function validateAgentID(variable: string): boolean {
    // Accepted formats: "+1234567890", "1234567890", "1234*123" or "123"
    return validatePhoneNumber(variable) || validateExtension(variable);
}
export const errorMessageAgentID = VALIDATION_ERRORS.AGENT_ID;

/**
 * Get script directory
 * @returns Script directory
 */
export const getScriptDirectory = () => {
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = path.dirname(__filename);
    return __dirname
}

// Configuration constants
const CONFIG_KEYS = {
  REQUIRED: ["appId", "appSecret", "voipnowHost", "voipnowTokenFile"] as const,
  OPTIONAL: ["authTokenMCP", "logLevel","insecure"] as const,
} as const;

const requiredKeys = CONFIG_KEYS.REQUIRED as readonly string[];
const allowedKeys = [...CONFIG_KEYS.REQUIRED, ...CONFIG_KEYS.OPTIONAL] as readonly string[];

/**
 * Function to checks configuration
 * @param options - Command line options
 * @param configMCP - Configuration file
 */
export async function checks(options: OptionValues, configMCP: any) {
    // Check if config file is valid
    const missingKeys = requiredKeys.filter(key => !(key in configMCP));
    if (missingKeys.length > 0) {
        logError(`Missing keys in config file: ${missingKeys.join(', ')}`, "");
    }
    const extraKeys = Object.keys(configMCP).filter(key => !allowedKeys.includes(key));
    if (extraKeys.length > 0) {
        logError(`Extra keys in config file: ${extraKeys.join(', ')}`, "");
    }

    // Check if auth token is set
    if (options.secure && (configMCP.authTokenMCP === undefined || configMCP.authTokenMCP === '')) {
      logError('Please set auth token in config file', "");
    }

    // Check if URL is valid
    if (!configMCP.voipnowHost.startsWith("https://") && !configMCP.voipnowHost.startsWith("http://")) {
        logError('Invalid URL format. Please provide a valid URL in the format "https://voipnow.com" or "http://voipnow.com".', "");
    }

    // Check if token file is provided
    if (configMCP.voipnowTokenFile === undefined || configMCP.voipnowTokenFile === '') {
      logError('Please set token file in config file', "");
    }

    // Validate parent directory exists and is writable
    const tokenDir = path.dirname(configMCP.voipnowTokenFile);
    try {
      if (!fs.existsSync(tokenDir)) {
        logError(`Token file directory does not exist: ${tokenDir}`, "");
      }

      // Test write permissions by creating a temp file
      const testFile = path.join(tokenDir, '.write_test_' + Date.now());
      fs.writeFileSync(testFile, 'test');
      fs.unlinkSync(testFile);
    } catch (error: any) {
      logError(`Token file directory is not writable: ${tokenDir} - ${error.message}`, "");
    }

    // Check if auth configuration has changed and delete token if needed
    const configHashFile = configMCP.voipnowTokenFile + '.config_hash';
    const configChanged = checkConfigChange(configMCP, configHashFile);
    if (configChanged) {
      logger.info('Authentication configuration changed. Token file deleted, generating new token...');
    }

    // Check if token file exist, if not generate it or
    // check if token is valid
    if (!fs.existsSync(configMCP.voipnowTokenFile) || checkToken(configMCP.voipnowTokenFile) ) {
      if (!configChanged) {  // Only log if not already logged above
        if (!fs.existsSync(configMCP.voipnowTokenFile)) {
          logger.debug('Token file not found. Generating new token...');
        } else {
          logger.debug('Token file expired. Generating new token...');
        }
      }
      await generateToken(configMCP).catch((error: any) => {
        error = checkCert(error);
        logError('Fatal error generating token:', error);
      })
    }
}

export function checkCert(error: any): Error {
  // Check for various SSL/TLS error patterns
  const sslErrorCodes = [
    'CERT_HAS_EXPIRED',
    'UNABLE_TO_VERIFY_LEAF_SIGNATURE',
    'SELF_SIGNED_CERT_IN_CHAIN',
    'DEPTH_ZERO_SELF_SIGNED_CERT',
    'UNABLE_TO_GET_ISSUER_CERT'
  ];

  // Check error.cause.cert pattern
  if (error.cause?.cert) {
    const errorMessage = `SSL Certificate Error ${error.cause.code}: ${error.cause.reason}\n` +
      `Certificate: ${error.cause.cert.subject?.CN || 'unknown'}\n` +
      `Issuer: ${error.cause.cert.issuer?.CN || 'unknown'}\n` +
      `Valid from: ${error.cause.cert.valid_from} to ${error.cause.cert.valid_to}\n\n` +
      `To bypass certificate validation (NOT RECOMMENDED for production), set "insecure": true in config.json`;
    return new Error(errorMessage);
  }

  // Check for SSL error in code or message
  if (error.code && sslErrorCodes.includes(error.code)) {
    return new Error(`SSL Certificate Error: ${error.code} - ${error.message}\n` +
      `To bypass certificate validation (NOT RECOMMENDED for production), set "insecure": true in config.json`);
  }

  // Check message for SSL keywords
  if (error.message && /certificate|ssl|tls/i.test(error.message)) {
    return new Error(`Possible SSL/TLS Error: ${error.message}\n` +
      `If this is a certificate issue, you can set "insecure": true in config.json (NOT RECOMMENDED for production)`);
  }

  return error;
}

export function checkPort (port: number, host: string) {
  return new Promise((resolve, reject) => {
    const server = net.createServer().listen(port, host);
    server.on('listening', () => {
      server.close();
      resolve(true);
    });
    server.on('error', (err: NodeJS.ErrnoException) => {
      if (err.code === 'EADDRINUSE') {
        resolve(false);
      } else {
        reject(err);
      }
    });
  });
};

/**
 * HTTP request configuration
 */
export interface HttpRequestConfig {
  method: string;
  headers: Record<string, string>;
  body?: string;
  redirect?: RequestRedirect;
  timeout?: number; // milliseconds
}

/**
 * Make an HTTP request with timeout support
 * @param url - The URL to request
 * @param config - Request configuration
 * @returns The fetch Response
 * @throws Error on timeout or network failure
 */
export async function fetchWithTimeout(url: string, config: HttpRequestConfig): Promise<Response> {
  const timeoutMs = config.timeout || 30000; // Default 30 seconds
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      method: config.method,
      headers: config.headers,
      body: config.body,
      redirect: config.redirect || 'manual',
      signal: controller.signal
    });

    clearTimeout(timeoutId);
    return response;
  } catch (error: any) {
    clearTimeout(timeoutId);

    // Check if the error was due to abort (timeout)
    if (error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeoutMs}ms`);
    }

    // Re-throw other errors
    throw error;
  }
}

/**
 * Sanitized error response for API errors
 */
export interface SanitizedError {
  error: string;
  status: number;
}

/**
 * Sanitize API error responses to prevent information disclosure
 * @param response - The HTTP response
 * @param errorData - The error data from response body
 * @param logger - Logger instance
 * @returns Sanitized error object
 */
export function sanitizeApiError(
  response: Response,
  errorData: any,
  logger: typeof import('./logger.js').logger
): SanitizedError {
  // Map HTTP status codes to user-friendly messages
  const userMessages: Record<number, string> = {
    400: 'Invalid request parameters',
    401: 'Authentication failed',
    403: 'Permission denied',
    404: 'Resource not found',
    409: 'Resource conflict',
    422: 'Validation error',
    429: 'Too many requests',
    500: 'Server error occurred',
    502: 'Bad gateway',
    503: 'Service unavailable',
    504: 'Gateway timeout'
  };

  const userMessage = userMessages[response.status] || 'Request failed';

  // Log detailed error for debugging (without exposing to user)
  logger.error('API request failed', {
    status: response.status,
    statusText: response.statusText,
    code: errorData?.error?.code,
    message: errorData?.error?.message,
    // Never log the full URL which might contain sensitive params
    endpoint: response.url ? new URL(response.url).pathname : 'unknown'
  });

  // Return sanitized error to user
  return {
    error: userMessage,
    status: response.status
  };
}
