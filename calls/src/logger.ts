import winston, { createLogger, transports } from 'winston';
import { SyslogTransportOptions, Syslog } from 'winston-syslog';

// Constants
const LOG_LEVELS = ['error', 'warn', 'info', 'debug'] as const;
const LOG_TRANSPORTS = ['console', 'syslog'] as const;
const DEFAULT_LOG_LEVEL = 'info';
const DEFAULT_LOG_TRANSPORT = 'console';
const APP_NAME = 'mcp-voipnow-calls';

// Platform-specific syslog paths
const SYSLOG_PATHS = {
  linux: '/dev/log',
  darwin: '/var/run/syslog',
} as const;

// Base syslog configuration
const BASE_SYSLOG_OPTIONS: Omit<SyslogTransportOptions, 'path' | 'protocol' | 'port' | 'host'> = {
  app_name: APP_NAME,
  facility: 'local0',
  type: 'RFC5424',
};

// Platform-specific syslog configurations
const UNIX_SYSLOG_OPTIONS: SyslogTransportOptions = {
  ...BASE_SYSLOG_OPTIONS,
  protocol: 'unix',
};

const WINDOWS_SYSLOG_OPTIONS: SyslogTransportOptions = {
  ...BASE_SYSLOG_OPTIONS,
  protocol: 'udp',
  port: 514,
  host: '127.0.0.1',
};

export const logger = createLogger({
  levels: winston.config.syslog.levels,
  format: winston.format.combine(
    winston.format.errors({ stack: true }),
    winston.format.json()
  )
});

export function logError(message: string, error?: any): never {
  logger.error(message, error);
  logger.end();

  // Use async exit to allow log flush
  setImmediate(() => {
    process.exitCode = 1;
    // Let the process exit naturally or trigger shutdown handlers
    throw new Error(`Fatal error: ${message}`);
  });

  // Type guard - this function never returns
  throw new Error(`Fatal error: ${message}`);
}

export function logStdout(message: string) {
  logger.info(message);
}

export function logWarning(message: string) {
  logger.warning(message);
}

export function setLogLevel(level: string) {
  if (isValidLogLevel(level)) {
    logger.level = level;
  } else {
    logger.level = DEFAULT_LOG_LEVEL;
    // Use logger with fallback to stderr if logger not initialized
    try {
      logger.warning(`Invalid log level: ${level} [${LOG_LEVELS.join(', ')}], defaulting to '${DEFAULT_LOG_LEVEL}'`);
    } catch {
      // Fallback if logger not initialized
      process.stderr.write(`[WARN] Invalid log level: ${level}, defaulting to '${DEFAULT_LOG_LEVEL}'\n`);
    }
  }
}

function isValidLogLevel(level: string): level is typeof LOG_LEVELS[number] {
  return LOG_LEVELS.includes(level as any);
}

// Helper function to create syslog transport for current platform
function createSyslogTransport() {
  const platform = process.platform;
  
  if (platform === 'linux' || platform === 'darwin') {
    const options = {
      ...UNIX_SYSLOG_OPTIONS,
      path: SYSLOG_PATHS[platform],
    };
    return new Syslog(options);
  } else if (platform === 'win32') {
    return new Syslog(WINDOWS_SYSLOG_OPTIONS);
  } else {
    throw new Error(`Unsupported platform: ${platform}`);
  }
}

export function setLogTransport(logType: string) {
  if (logType === 'syslog') {
    try {
      const syslogTransport = createSyslogTransport();
      logger.add(syslogTransport);
    } catch (error) {
      // Use stderr for errors during logger initialization
      process.stderr.write(`[ERROR] ${error instanceof Error ? error.message : 'Unknown error'}\n`);
      process.exit(1);
    }
  } else {
    if (logType !== DEFAULT_LOG_TRANSPORT) {
      // Use stderr for warnings during logger initialization
      process.stderr.write(`[WARN] Invalid log transport: ${logType} [${LOG_TRANSPORTS.join(', ')}], defaulting to '${DEFAULT_LOG_TRANSPORT}'\n`);
    }
    // For console transport, log to stderr to avoid protocol interference
    const syslogLevels = Object.keys(winston.config.syslog.levels);
    logger.add(new transports.Console({stderrLevels: syslogLevels}));
  }
}