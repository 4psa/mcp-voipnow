import fs from "fs";
import { logger, logError } from "../logger.js";
import { checkCert } from "../utils.js";
import crypto from "crypto";
import { createRequire } from 'module';

// Helper function to safely read and parse token file
function _safeReadTokenFile(tokenFilePath: string): string {
  try {
    const tokenData = fs.readFileSync(tokenFilePath, "utf8").trim();

    // Handle empty or incomplete token file
    if (!tokenData) {
      throw new Error("Token file is empty");
    }

    const parts = tokenData.split(":");
    if (parts.length !== 3) {
      throw new Error(`Invalid token format: expected exactly 3 parts, got ${parts.length}`);
    }

    const [createdStr, expiresStr, token] = parts;

    // Validate timestamps are numeric
    const created = parseInt(createdStr, 10);
    const expires = parseInt(expiresStr, 10);

    if (isNaN(created) || isNaN(expires)) {
      throw new Error("Invalid timestamp format in token file");
    }

    if (created > expires) {
      throw new Error("Token created timestamp is after expiry timestamp");
    }

    // Validate token is not empty and has reasonable length
    if (!token || token.length < 10) {
      throw new Error("Token is invalid or too short");
    }

    // Basic format validation - tokens should be alphanumeric with some special chars
    if (!/^[A-Za-z0-9_\-\.]+$/.test(token)) {
      throw new Error("Token contains invalid characters");
    }

    return tokenData;
  } catch (error: any) {
    throw new Error(`Failed to read or parse token file: ${error.message}`);
  }
}

// Token and OAuth constants
const OAUTH_CONFIG = {
  GRANT_TYPE: 'client_credentials',
  TYPE: 'unifiedapi',
  TOKEN_ENDPOINT: '/oauth/token.php',
  REDIRECT_PATH: '/ouath/token.php', // Note: keeping original typo for compatibility
} as const;

const TOKEN_SETTINGS = {
  EXPIRATION_BUFFER_MS: 300000, // 5 minutes
  FILE_MODE: 0o600,
} as const;

// Get user agent from package.json
const require = createRequire(import.meta.url);
const packageJson = require('../../package.json');

const HTTP_CONFIG = {
  USER_AGENT: `VoipNow Calls MCP/${packageJson.version}`,
  CONTENT_TYPE: 'application/x-www-form-urlencoded',
} as const;

export async function generateToken(configMCP: any) {
  const params = new URLSearchParams();
  params.append("client_id", configMCP.appId);
  params.append("client_secret", configMCP.appSecret);
  params.append("grant_type", OAUTH_CONFIG.GRANT_TYPE);
  params.append("type", OAUTH_CONFIG.TYPE);
  params.append("redirect_uri", `${configMCP.voipnowHost}${OAUTH_CONFIG.REDIRECT_PATH}`);

  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

  let response: Response;
  try {
    response = await fetch(`${configMCP.voipnowHost}${OAUTH_CONFIG.TOKEN_ENDPOINT}`, {
      method: 'POST',
      headers: {
        "Content-Type": HTTP_CONFIG.CONTENT_TYPE,
        'User-Agent': HTTP_CONFIG.USER_AGENT,
      },
      body: params.toString(),
      signal: controller.signal
    });
    clearTimeout(timeoutId);
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('Token generation request timeout after 30 seconds');
    }
    throw error;
  }

  // Check if the response is successful
  if (!response.ok) {
    const data = await response.json();
    logger.error(`HTTP ${response.status}: ${response.statusText} - ${JSON.stringify(data)}`);
    if (data.error === "invalid_client") {
      logger.error("Invalid client credentials. Please check your appId and appSecret.");
    }
    throw new Error(`HTTP ${response.status}: ${response.statusText} - ${JSON.stringify(data)}`);
  }

  // Parse response
  const data = await response.json();

  // Save the token to a file using atomic write
  const now = Date.now();
  const tokenData = `${now}:${now + data.expires_in * 1000}:${data.access_token}`;

  // Use atomic write with temporary file to prevent race conditions
  const tokenFilePath = configMCP.voipnowTokenFile;
  // Create unique temp file name with PID and random component
  const randomSuffix = crypto.randomBytes(8).toString('hex');
  const tempFilePath = `${tokenFilePath}.tmp.${process.pid}.${randomSuffix}`;

  // Set umask to ensure restrictive permissions from the start
  const oldUmask = process.umask(0o077);
  try {
    // Write to temporary file first with exclusive flag ('wx' fails if file exists)
    fs.writeFileSync(tempFilePath, tokenData, {
      mode: TOKEN_SETTINGS.FILE_MODE,
      flag: 'wx'  // Write + exclusive (fail if exists)
    });

    // Atomically move temp file to final location
    fs.renameSync(tempFilePath, tokenFilePath);
    // Defensive chmod - should already be correct, but ensure it
    fs.chmodSync(tokenFilePath, TOKEN_SETTINGS.FILE_MODE);
  } catch (error) {
    // Clean up temp file if it exists
    if (fs.existsSync(tempFilePath)) {
      try {
        fs.unlinkSync(tempFilePath);
      } catch {}
    }
    throw error;
  } finally {
    // Restore original umask
    process.umask(oldUmask);
  }
}

// Helper function to parse token data from file
function parseTokenData(tokenFilePath: string): { created: number; expires: number; token: string } {
  const tokenData = _safeReadTokenFile(tokenFilePath);
  const [createdTimestamp, expirationTimestamp, token] = tokenData.split(":");
  return {
    created: parseInt(createdTimestamp, 10),
    expires: parseInt(expirationTimestamp, 10),
    token: token || '',
  };
}

// Check if the token has expired or is about to expire in the next 5 minutes
export function checkToken(tokenFilePath: string): boolean {
  const { expires } = parseTokenData(tokenFilePath);
  return Date.now() >= expires - TOKEN_SETTINGS.EXPIRATION_BUFFER_MS;
}

// Function to read the expiration timestamp from the .access_token file
function getExpirationTimestamp(tokenFilePath: string): number {
  const { expires } = parseTokenData(tokenFilePath);
  return expires;
}

// Function to check if authentication-related configuration has changed
export function checkConfigChange(configMCP: any, configHashFile: string): boolean {
  
  // Create hash of authentication-related config
  const authConfig = {
    appId: configMCP.appId || "",
    appSecret: configMCP.appSecret || "",
    voipnowHost: configMCP.voipnowHost || ""
  };
  
  const currentHash = crypto.createHash('sha256').update(JSON.stringify(authConfig)).digest('hex');
  
  try {
    const storedHash = fs.readFileSync(configHashFile, 'utf8').trim();
    
    if (storedHash !== currentHash) {
      // Config changed, update hash file and delete token file
      fs.writeFileSync(configHashFile, currentHash, { mode: 0o600 });
      
      // Delete token file so it gets regenerated
      const tokenFile = configMCP.voipnowTokenFile;
      if (tokenFile && fs.existsSync(tokenFile)) {
        fs.unlinkSync(tokenFile);
      }
      
      return true;
    }
    return false;
    
  } catch (error) {
    // First time, create hash file
    fs.writeFileSync(configHashFile, currentHash, { mode: 0o600 });
    return false;
  }
}

// Function to check the expiration time and run a function at regular intervals
export async function checkTokenExpiration(
  configMCP: any,
  interval: number,
  callback: () => void
) {
  // Check if token needs renewal
  if (checkToken(configMCP.voipnowTokenFile)) {
    logger.debug("Token has expired or is about to expire. Generating a new token.");
    await generateToken(configMCP).catch((error: any) => {
      const processedError = checkCert(error);
      logError("Fatal error generating token:", processedError);
    });
  }

  // Calculate next check interval
  const expirationTimestamp = getExpirationTimestamp(configMCP.voipnowTokenFile);
  const currentTime = Date.now();
  const timeUntilExpiration = expirationTimestamp - currentTime;
  
  const nextCheckInterval = (timeUntilExpiration <= 0 || isNaN(timeUntilExpiration)) 
    ? interval 
    : Math.min(timeUntilExpiration, interval);

  logger.debug(`Setting timeout for ${nextCheckInterval} milliseconds.`);
  
  setTimeout(async () => {
    logger.debug("Timeout triggered. Calling callback.");
    callback();
    logger.debug("Callback called. Recursively calling checkTokenExpiration.");
    await checkTokenExpiration(configMCP, interval, callback);
  }, nextCheckInterval);
}
