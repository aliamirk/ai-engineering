"""Tool registry for managing and filtering tools by user role."""

from typing import Any, Dict, List, Optional, Union
from strands_agent.core.api_client import GatePassAPIClient
from strands_agent.tools.hr_tools import get_hr_tools
from strands_agent.tools.admin_tools import get_admin_tools
from strands_agent.tools.gate_tools import get_gate_tools
from strands_agent.tools.notification_qr_tools import (
    get_notification_tools,
    get_qr_code_tools
)


class ToolRegistry:
    """Central registry for all gate pass management tools.
    
    This class manages all tool definitions and provides role-based filtering
    to ensure users only have access to tools authorized for their role.
    """
    
    def __init__(self, api_client: GatePassAPIClient):
        """Initialize the tool registry with all available tools.
        
        Args:
            api_client: GatePassAPIClient instance for making API requests
        """
        self.api_client = api_client
        self._tools: Dict[str, Any] = {}
        self._register_all_tools()
    
    def _register_all_tools(self) -> None:
        """Register all tools from HR, Admin, Gate, Notification, and QR Code modules."""
        # Register HR tools
        for tool in get_hr_tools(self.api_client):
            self._tools[tool.name] = tool
        
        # Register Admin tools
        for tool in get_admin_tools(self.api_client):
            self._tools[tool.name] = tool
        
        # Register Gate tools
        for tool in get_gate_tools(self.api_client):
            self._tools[tool.name] = tool
        
        # Register Notification tools
        for tool in get_notification_tools(self.api_client):
            self._tools[tool.name] = tool
        
        # Register QR Code tools
        for tool in get_qr_code_tools(self.api_client):
            self._tools[tool.name] = tool
    
    def get_tools_for_role(self, user_role: str) -> List[Any]:
        """Filter tools by user role.
        
        Args:
            user_role: The user's role (HR_User, Admin_User, or Gate_User)
            
        Returns:
            List of tool instances authorized for the given role
        """
        authorized_tools = []
        
        for tool in self._tools.values():
            # Get the required role(s) for this tool
            required_role = tool.required_role
            
            # Handle tools that allow multiple roles (like mark_notification_read)
            if isinstance(required_role, list):
                if user_role in required_role:
                    authorized_tools.append(tool)
            # Handle tools available to all roles
            elif required_role == "All":
                authorized_tools.append(tool)
            # Handle tools with a specific role requirement
            elif required_role == user_role:
                authorized_tools.append(tool)
        
        return authorized_tools
    
    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Retrieve a specific tool by name.
        
        Args:
            tool_name: The name of the tool to retrieve
            
        Returns:
            The tool instance if found, None otherwise
        """
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, Any]:
        """Get all registered tools.
        
        Returns:
            Dictionary mapping tool names to tool instances
        """
        return self._tools.copy()
