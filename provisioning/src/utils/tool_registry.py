"""
Dynamic tool discovery and registration system for MCP VoipNow Provisioning.

This module automatically discovers and registers tools from the tools directory,
eliminating the need for manual imports and registrations in main.py.
"""

import sys
import importlib
import pkgutil
from typing import Dict, List, Callable, Awaitable
import mcp.types as types
import logging
import re

# Type alias for tool handlers
ToolHandler = Callable[[dict, dict, logging.Logger], Awaitable[List[types.TextContent | types.ImageContent | types.EmbeddedResource]]]


class DynamicToolRegistry:
    """
    Dynamically discovers and registers tools from the tools directory.
    
    This class scans the tools directory structure and automatically imports
    modules that contain tool definitions, extracting their schemas and handlers.
    """
    
    def __init__(self, tools_package_path: str = "tools"):
        """
        Initialize the dynamic tool registry.
        
        Args:
            tools_package_path: The package path to the tools directory (e.g., "tools")
        """
        self.tools_package_path = tools_package_path
        self.tool_schemas: List[types.Tool] = []
        self.tool_handlers: Dict[str, ToolHandler] = {}
        self._discovered_modules = set()
        self.logger = logging.getLogger(__name__)
        
    def discover_and_register_tools(self) -> None:
        """
        Discover and register all tools from the tools directory.
        
        This method:
        1. Walks through the tools directory structure
        2. Imports each Python module
        3. Extracts TOOL_REGISTRY configurations
        4. Builds tool schemas and handlers
        """
        self.tool_schemas.clear()
        self.tool_handlers.clear()
        self._discovered_modules.clear()
        
        # Get the tools package
        try:
            tools_package = importlib.import_module(self.tools_package_path)
        except ImportError as e:
            raise ImportError(f"Could not import tools package '{self.tools_package_path}': {e}")
        
        # Walk through all modules in the tools package
        self._walk_package(tools_package)
        
        self.logger.debug(f"Dynamically discovered {len(self.tool_schemas)} tools from {len(self._discovered_modules)} modules")
    
    def _walk_package(self, package) -> None:
        """
        Recursively walk through a package and discover tools.
        
        Args:
            package: The package to walk through
        """
        package_path = package.__path__
        package_name = package.__name__
        
        # Walk through all modules in the package
        for importer, modname, ispkg in pkgutil.iter_modules(package_path, package_name + "."):
            # Validate module name pattern
            if not re.match(r'^tools\.[a-z_]+(?:\.[a-z_]+)*$', modname):
                self.logger.warning(f"Skipping suspicious module name: {modname}")
                continue
            try:
                # Import the module
                module = importlib.import_module(modname)
                self._discovered_modules.add(modname)
                
                # Check if it's a subpackage and recurse
                if ispkg:
                    self._walk_package(module)
                else:
                    # Process the module for tools
                    self._process_module(module, modname)
                    
            except Exception as e:
                self.logger.debug(f"Could not import module '{modname}': {e}")
                continue
    
    def _process_module(self, module, module_name: str) -> None:
        """
        Process a module to extract tool definitions.
        
        Args:
            module: The imported module
            module_name: The name of the module
        """
        # Check if module has TOOL_REGISTRY
        if not hasattr(module, 'TOOL_REGISTRY'):
            return
            
        tool_registry = getattr(module, 'TOOL_REGISTRY')
        if not isinstance(tool_registry, dict):
            return
            
        self.logger.debug(f"Processing tools from module: {module_name}")
        
        # Process each tool in the registry
        for tool_func_name, tool_config in tool_registry.items():
            try:
                # Create tool schema
                schema = self._create_tool_schema(tool_config)
                self.tool_schemas.append(schema)
                
                # Find and register the handler function
                handler_func = getattr(module, tool_func_name, None)
                if handler_func and callable(handler_func):
                    tool_name = tool_config.get("tool_name", tool_func_name)
                    self.tool_handlers[tool_name] = handler_func
                    self.logger.debug(f"Registered tool: {tool_name} (handler: {tool_func_name})")
                else:
                    self.logger.debug(f"Handler function '{tool_func_name}' not found in {module_name}")
                    
            except Exception as e:
                self.logger.debug(f"Error processing tool '{tool_func_name}' in {module_name}: {e}")
                continue
    
    def _create_tool_schema(self, tool_config: dict) -> types.Tool:
        """
        Create a tool schema from tool configuration.
        
        Args:
            tool_config: The tool configuration dictionary
            
        Returns:
            types.Tool: The MCP tool schema
        """
        return types.Tool(
            name=tool_config["tool_name"],
            description=tool_config["tool_description"],
            inputSchema=tool_config["input_schema"]
        )
    
    def get_tool_schemas(self) -> List[types.Tool]:
        """
        Get all discovered tool schemas.
        
        Returns:
            List[types.Tool]: List of all tool schemas
        """
        return self.tool_schemas.copy()
    
    def get_tool_handlers(self) -> Dict[str, ToolHandler]:
        """
        Get all discovered tool handlers.
        
        Returns:
            Dict[str, ToolHandler]: Dictionary mapping tool names to their handlers
        """
        return self.tool_handlers.copy()
    
    def get_tool_handler(self, tool_name: str) -> ToolHandler:
        """
        Get a specific tool handler by name.
        
        Args:
            tool_name: The name of the tool
            
        Returns:
            ToolHandler: The tool handler function
            
        Raises:
            KeyError: If the tool is not found
        """
        if tool_name not in self.tool_handlers:
            raise KeyError(f"Tool '{tool_name}' not found in registry")
        return self.tool_handlers[tool_name]
    
    def refresh(self) -> None:
        """
        Refresh the tool registry by re-discovering all tools.
        
        This is useful when tools are added, removed, or modified at runtime.
        """
        # Clear the module cache for tools package to ensure fresh imports
        modules_to_remove = [name for name in sys.modules.keys() 
                           if name.startswith(self.tools_package_path)]
        for module_name in modules_to_remove:
            if module_name != self.tools_package_path:  # Keep the root package
                del sys.modules[module_name]
        
        # Re-discover tools
        self.discover_and_register_tools()


# Global instance for easy access
_global_registry = None


def get_registry(tools_package_path: str = "tools") -> DynamicToolRegistry:
    """
    Get the global tool registry instance.
    
    Args:
        tools_package_path: The package path to the tools directory
        
    Returns:
        DynamicToolRegistry: The global registry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = DynamicToolRegistry(tools_package_path)
        _global_registry.discover_and_register_tools()
    return _global_registry


def refresh_registry() -> None:
    """
    Refresh the global tool registry.
    """
    global _global_registry
    if _global_registry is not None:
        _global_registry.refresh()


def get_tool_schemas() -> List[types.Tool]:
    """
    Get all tool schemas from the global registry.
    
    Returns:
        List[types.Tool]: List of all tool schemas
    """
    return get_registry().get_tool_schemas()


def get_tool_handlers() -> Dict[str, ToolHandler]:
    """
    Get all tool handlers from the global registry.
    
    Returns:
        Dict[str, ToolHandler]: Dictionary mapping tool names to their handlers
    """
    return get_registry().get_tool_handlers()


def get_tool_handler(tool_name: str) -> ToolHandler:
    """
    Get a specific tool handler by name from the global registry.
    
    Args:
        tool_name: The name of the tool
        
    Returns:
        ToolHandler: The tool handler function
        
    Raises:
        KeyError: If the tool is not found
    """
    return get_registry().get_tool_handler(tool_name)
