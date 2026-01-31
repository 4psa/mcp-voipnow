/**
 * Dynamic tool discovery and registration system for MCP VoipNow Calls.
 * 
 * This module automatically discovers and registers tools from the tools directory,
 * eliminating the need for manual imports and registrations in index.ts.
 */

import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { Logger } from "winston";
import { readdir, stat } from 'fs/promises';
import fs from 'fs';
import { join, dirname, extname } from "path";
import { fileURLToPath, pathToFileURL } from "url";
import path from 'path';
import { ZodSchema } from "zod";

// Constants for file extensions and naming patterns
const FILE_EXTENSIONS = {
  TYPESCRIPT: '.ts',
  JAVASCRIPT: '.js',
  DECLARATION_TS: '.d.ts',
  DECLARATION_JS: '.d.js',
} as const;

const TOOL_NAMING_PATTERNS = {
  TOOL_SUFFIX: '_TOOL',
  NAME_SUFFIX: 'ToolName',
  DESCRIPTION_SUFFIX: 'ToolDescription',  
  RUNNER_PREFIX: 'run',
  RUNNER_SUFFIX: 'Tool',
  SCHEMA_SUFFIX: 'ToolSchema',
} as const;

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Type definitions for tool modules
export interface ToolModule {
  [key: string]: Tool | string | ToolHandler | ZodSchema<any>;
}

export interface ToolDefinition {
  name: string;
  description: string;
  tool: Tool;
  runner: ToolHandler;
  schema: ZodSchema<any>;
}

export interface ToolHandler {
  (args: any, userAgent: string, config: { voipnowUrl: string; voipnowToken: string; }, logger: Logger): Promise<any>;
}

/**
 * Dynamic tool registry that discovers and manages tools automatically.
 */
export class DynamicToolRegistry {
  private toolDefinitions: ToolDefinition[] = [];
  private toolHandlers: Map<string, ToolHandler> = new Map();
  private logger: Logger;
  private toolsDirectory: string;

  constructor(toolsDirectory: string = "tools", logger?: Logger) {
    // Sanitize and validate the tools directory
    const normalizedDir = path.normalize(toolsDirectory);
    if (normalizedDir.includes('..') || path.isAbsolute(normalizedDir)) {
        throw new Error('Invalid tools directory: must be a relative path without parent directory references');
    }

    const candidatePath = path.join(__dirname, normalizedDir);

    // Verify the directory exists and resolve symlinks
    try {
      const realToolsPath = fs.realpathSync(candidatePath);
      const expectedBase = fs.realpathSync(__dirname);

      // Ensure the real path is within the application directory
      if (!realToolsPath.startsWith(expectedBase + path.sep) && realToolsPath !== expectedBase) {
        throw new Error('Tools directory must be within the application directory');
      }

      // Store the real path for subsequent checks
      this.toolsDirectory = realToolsPath;
    } catch (error: any) {
      throw new Error(`Failed to validate tools directory: ${error.message}`);
    }

    this.logger = logger || console as any;
  }

  /**
   * Discover and register all tools from the tools directory.
   */
  async discoverAndRegisterTools(): Promise<void> {
    this.toolDefinitions = [];
    this.toolHandlers.clear();

    try {
      const toolFiles = await this.findToolFiles(this.toolsDirectory);
      this.logger.debug?.(`Found ${toolFiles.length} tool files`);

      for (const toolFile of toolFiles) {
        try {
          await this.processToolFile(toolFile);
        } catch (error) {
          this.logger.debug?.(`Error processing tool file ${toolFile}: ${error}`);
        }
      }

      this.logger.debug?.(`Dynamically discovered ${this.toolDefinitions.length} tools`);
    } catch (error) {
      throw new Error(`Failed to discover tools in directory '${this.toolsDirectory}': ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Find all TypeScript tool files in the tools directory.
   */
  private async findToolFiles(directory: string): Promise<string[]> {
    const toolFiles: string[] = [];

    try {
      const entries = await readdir(directory);

      for (const entry of entries) {
        const fullPath = join(directory, entry);

        // Verify the path is still within bounds using realpath
        try {
          const realFullPath = fs.realpathSync(fullPath);
          const realToolsDir = fs.realpathSync(this.toolsDirectory);

          // Ensure the file is within the tools directory (prevent symlink escapes)
          if (!realFullPath.startsWith(realToolsDir + path.sep) && realFullPath !== realToolsDir) {
            this.logger.warn?.(`Skipping file outside tools directory: ${entry}`);
            continue;
          }

          const statInfo = await stat(fullPath);

          if (statInfo.isDirectory()) {
            // Recursively search subdirectories
            const subDirectoryFiles = await this.findToolFiles(fullPath);
            toolFiles.push(...subDirectoryFiles);
          } else if (statInfo.isFile()) {
            const ext = extname(entry);
            // Look for .ts files in development or .js files in production
            if ((ext === FILE_EXTENSIONS.TYPESCRIPT && !entry.includes(FILE_EXTENSIONS.DECLARATION_TS)) ||
                (ext === FILE_EXTENSIONS.JAVASCRIPT && !entry.includes(FILE_EXTENSIONS.DECLARATION_JS))) {
              toolFiles.push(fullPath);
            }
          }
        } catch (error) {
          this.logger.debug?.(`Error validating path ${fullPath}: ${error}`);
          continue;
        }
      }
    } catch (error) {
      this.logger.debug?.(`Error reading directory ${directory}: ${error}`);
    }

    return toolFiles;
  }

  /**
   * Process a single tool file and extract tool definitions.
   */
  private async processToolFile(filePath: string): Promise<void> {
    try {
      // Convert file path to file URL for dynamic import
      const fileUrl = pathToFileURL(filePath).href;
      const module: ToolModule = await import(fileUrl);

      // Validate module exports
      if (!this.isValidToolModule(module)) {
        throw new Error(`Invalid tool module structure in ${filePath}`);
      }

      this.logger.debug?.(`Processing tool file: ${filePath}`);

      // Find tool definitions in the module
      const toolDefs = this.extractToolDefinitions(module, filePath);

      for (const toolDef of toolDefs) {
        this.toolDefinitions.push(toolDef);
        this.toolHandlers.set(toolDef.name, toolDef.runner);
        this.logger.debug?.(`Registered tool: ${toolDef.name}`);
      }

    } catch (error) {
      this.logger.debug?.(`Failed to import tool file ${filePath}: ${error}`);
    }
  }

  /**
   * Extract tool definitions from a module by looking for expected patterns.
   */
  private extractToolDefinitions(module: ToolModule, filePath: string): ToolDefinition[] {
    const toolDefs: ToolDefinition[] = [];

    // Look for tool definitions following the naming patterns
    const toolObjects = Object.keys(module).filter(key => 
      key.endsWith(TOOL_NAMING_PATTERNS.TOOL_SUFFIX) && 
      typeof module[key] === 'object' && 
      module[key] !== null &&
      'name' in module[key] &&
      typeof (module[key] as any).name === 'string'
    );

    for (const toolObjectKey of toolObjects) {
      try {
        const toolCandidate = module[toolObjectKey];
        
        // Type guard to ensure this is a Tool object
        if (!this.isValidTool(toolCandidate)) {
          this.logger.debug?.(`Invalid tool object for ${toolObjectKey} in ${filePath}`);
          continue;
        }
        
        const tool = toolCandidate as Tool;
        const toolName = tool.name;

        // Find corresponding name, description, runner, and schema using naming patterns
        const nameKey = Object.keys(module).find(key => 
          key.endsWith(TOOL_NAMING_PATTERNS.NAME_SUFFIX) && 
          typeof module[key] === 'string' &&
          module[key] === toolName
        );
        
        const descriptionKey = Object.keys(module).find(key => 
          key.endsWith(TOOL_NAMING_PATTERNS.DESCRIPTION_SUFFIX) && 
          typeof module[key] === 'string'
        );

        const runnerKey = Object.keys(module).find(key => 
          key.startsWith(TOOL_NAMING_PATTERNS.RUNNER_PREFIX) && 
          key.endsWith(TOOL_NAMING_PATTERNS.RUNNER_SUFFIX) && 
          typeof module[key] === 'function'
        );

        const schemaKey = Object.keys(module).find(key => 
          key.endsWith(TOOL_NAMING_PATTERNS.SCHEMA_SUFFIX) && 
          typeof module[key] === 'object' &&
          module[key] !== null
        );

        if (nameKey && descriptionKey && runnerKey && schemaKey) {
          const name = module[nameKey] as string;
          const description = module[descriptionKey] as string;
          const runner = module[runnerKey] as ToolHandler;
          const schema = module[schemaKey] as ZodSchema<any>;

          const toolDef: ToolDefinition = {
            name,
            description,
            tool,
            runner,
            schema
          };

          toolDefs.push(toolDef);
          this.logger.debug?.(`Extracted tool: ${toolDef.name} from ${filePath}`);
        } else {
          this.logger.debug?.(`Incomplete tool definition for ${toolName} in ${filePath}`);
        }

      } catch (error) {
        this.logger.debug?.(`Error extracting tool from ${toolObjectKey}: ${error}`);
      }
    }

    return toolDefs;
  }

  /**
   * Type guard to validate if an object is a valid Tool.
   */
  private isValidTool(obj: any): obj is Tool {
    return (
      typeof obj === 'object' &&
      obj !== null &&
      typeof obj.name === 'string' &&
      typeof obj.inputSchema === 'object' &&
      obj.inputSchema !== null &&
      typeof obj.inputSchema.type === 'string' &&
      obj.inputSchema.type === 'object'
    );
  }

  /**
   * Validate if a module has valid structure and exports.
   */
  private isValidToolModule(module: any): boolean {
    // Check for required exports and structure
    const hasValidExports = typeof module === 'object' && module !== null;
    const hasNoMaliciousPatterns = !this.containsMaliciousPatterns(module);
    return hasValidExports && hasNoMaliciousPatterns;
  }

  /**
   * Check for potentially malicious patterns in module exports.
   */
  private containsMaliciousPatterns(module: any): boolean {
    const moduleString = JSON.stringify(module);
    const maliciousPatterns = ['eval(', 'Function(', 'require("child_process")', 'exec('];
    return maliciousPatterns.some(pattern => moduleString.includes(pattern));
  }

  /**
   * Get all discovered tool schemas.
   */
  getToolSchemas(): Tool[] {
    return this.toolDefinitions.map(def => def.tool);
  }

  /**
   * Get all discovered tool handlers.
   */
  getToolHandlers(): Map<string, ToolHandler> {
    return new Map(this.toolHandlers);
  }

  /**
   * Get a specific tool handler by name.
   */
  getToolHandler(toolName: string): ToolHandler {
    const handler = this.toolHandlers.get(toolName);
    if (!handler) {
      throw new Error(`Tool '${toolName}' not found in registry`);
    }
    return handler;
  }

  /**
   * Get all tool definitions.
   */
  getToolDefinitions(): ToolDefinition[] {
    return [...this.toolDefinitions];
  }

  /**
   * Refresh the tool registry by re-discovering all tools.
   */
  async refresh(): Promise<void> {
    await this.discoverAndRegisterTools();
  }

  /**
   * Get the number of registered tools.
   */
  getToolCount(): number {
    return this.toolDefinitions.length;
  }
}

// Global registry instance
let globalRegistry: DynamicToolRegistry | null = null;

/**
 * Get the global tool registry instance.
 */
export function getRegistry(toolsDirectory: string = "tools", logger?: Logger): DynamicToolRegistry {
  if (!globalRegistry) {
    globalRegistry = new DynamicToolRegistry(toolsDirectory, logger);
  }
  return globalRegistry;
}

/**
 * Initialize and discover tools using the global registry.
 */
export async function initializeTools(toolsDirectory: string = "tools", logger?: Logger): Promise<DynamicToolRegistry> {
  const registry = getRegistry(toolsDirectory, logger);
  await registry.discoverAndRegisterTools();
  return registry;
}

/**
 * Refresh the global tool registry.
 */
export async function refreshRegistry(): Promise<void> {
  if (globalRegistry) {
    await globalRegistry.refresh();
  }
}

/**
 * Get all tool schemas from the global registry.
 */
export function getToolSchemas(): Tool[] {
  if (!globalRegistry) {
    throw new Error("Tool registry not initialized. Call initializeTools() first.");
  }
  return globalRegistry.getToolSchemas();
}

/**
 * Get all tool handlers from the global registry.
 */
export function getToolHandlers(): Map<string, ToolHandler> {
  if (!globalRegistry) {
    throw new Error("Tool registry not initialized. Call initializeTools() first.");
  }
  return globalRegistry.getToolHandlers();
}

/**
 * Get a specific tool handler by name from the global registry.
 */
export function getToolHandler(toolName: string): ToolHandler {
  if (!globalRegistry) {
    throw new Error("Tool registry not initialized. Call initializeTools() first.");
  }
  return globalRegistry.getToolHandler(toolName);
}
