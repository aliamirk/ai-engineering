"""Notification and QR Code tool definitions for Gate Pass Management API."""

from typing import Any, Dict, List, Union
from strands_agent.core.api_client import GatePassAPIClient
from strands_agent.core.models import APIResponse


class NotificationToolDefinition:
    """Base class for Notification tool definitions."""
    
    def __init__(self, api_client: GatePassAPIClient):
        """Initialize tool with API client.
        
        Args:
            api_client: GatePassAPIClient instance for making API requests
        """
        self.api_client = api_client
    
    @property
    def name(self) -> str:
        """Tool name identifier."""
        raise NotImplementedError
    
    @property
    def description(self) -> str:
        """Natural language description for LLM."""
        raise NotImplementedError
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema for tool parameters."""
        raise NotImplementedError
    
    @property
    def required_role(self) -> Union[str, List[str]]:
        """Role(s) required to access this tool."""
        raise NotImplementedError
    
    @property
    def api_endpoint(self) -> str:
        """API endpoint to call."""
        raise NotImplementedError
    
    @property
    def http_method(self) -> str:
        """HTTP method (GET or POST)."""
        raise NotImplementedError
    
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Formatted response string
        """
        raise NotImplementedError
    
    def format_response(self, response: APIResponse) -> str:
        """Format API response into natural language.
        
        Args:
            response: APIResponse object from API client
            
        Returns:
            User-friendly formatted response string
        """
        raise NotImplementedError


class GetAdminNotificationsTool(NotificationToolDefinition):
    """Tool for retrieving admin notifications."""
    
    @property
    def name(self) -> str:
        return "get_admin_notifications"
    
    @property
    def description(self) -> str:
        return "Retrieve notifications for admin users."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    @property
    def required_role(self) -> str:
        return "Admin_User"
    
    @property
    def api_endpoint(self) -> str:
        return "/notifications/admin"
    
    @property
    def http_method(self) -> str:
        return "GET"
    
    def execute(self) -> str:
        """Execute admin notifications retrieval.
        
        Returns:
            Formatted response string
        """
        response = self.api_client.request(
            method=self.http_method,
            endpoint=self.api_endpoint
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format admin notifications response."""
        if not response.success:
            return f"Failed to retrieve admin notifications: {response.error}"
        
        data = response.data
        if isinstance(data, list):
            if len(data) == 0:
                return "No notifications found."
            
            result = f"You have {len(data)} notification(s):\n\n"
            for idx, notification in enumerate(data, 1):
                notif_id = notification.get('id', 'N/A')
                message = notification.get('message', 'N/A')
                notif_type = notification.get('type', 'N/A')
                created_at = notification.get('created_at', 'N/A')
                is_read = notification.get('is_read', False)
                read_status = "Read" if is_read else "Unread"
                
                result += f"{idx}. [{read_status}] {message}\n"
                result += f"   Type: {notif_type} | Created: {created_at} | ID: {notif_id}\n\n"
            
            return result
        
        return "Admin notifications retrieved successfully!"


class GetHRNotificationsTool(NotificationToolDefinition):
    """Tool for retrieving HR notifications."""
    
    @property
    def name(self) -> str:
        return "get_hr_notifications"
    
    @property
    def description(self) -> str:
        return "Retrieve notifications for HR users."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    @property
    def required_role(self) -> str:
        return "HR_User"
    
    @property
    def api_endpoint(self) -> str:
        return "/notifications/hr"
    
    @property
    def http_method(self) -> str:
        return "GET"
    
    def execute(self) -> str:
        """Execute HR notifications retrieval.
        
        Returns:
            Formatted response string
        """
        response = self.api_client.request(
            method=self.http_method,
            endpoint=self.api_endpoint
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format HR notifications response."""
        if not response.success:
            return f"Failed to retrieve HR notifications: {response.error}"
        
        data = response.data
        if isinstance(data, list):
            if len(data) == 0:
                return "No notifications found."
            
            result = f"You have {len(data)} notification(s):\n\n"
            for idx, notification in enumerate(data, 1):
                notif_id = notification.get('id', 'N/A')
                message = notification.get('message', 'N/A')
                notif_type = notification.get('type', 'N/A')
                created_at = notification.get('created_at', 'N/A')
                is_read = notification.get('is_read', False)
                read_status = "Read" if is_read else "Unread"
                
                result += f"{idx}. [{read_status}] {message}\n"
                result += f"   Type: {notif_type} | Created: {created_at} | ID: {notif_id}\n\n"
            
            return result
        
        return "HR notifications retrieved successfully!"


class MarkNotificationReadTool(NotificationToolDefinition):
    """Tool for marking a notification as read."""
    
    @property
    def name(self) -> str:
        return "mark_notification_read"
    
    @property
    def description(self) -> str:
        return "Mark a notification as read."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "notification_id": {
                    "type": "string",
                    "description": "The notification ID"
                }
            },
            "required": ["notification_id"]
        }
    
    @property
    def required_role(self) -> List[str]:
        return ["Admin_User", "HR_User"]
    
    @property
    def api_endpoint(self) -> str:
        # This will be formatted with notification_id in execute method
        return "/notifications/mark-read/{notification_id}"
    
    @property
    def http_method(self) -> str:
        return "GET"
    
    def execute(self, notification_id: str) -> str:
        """Execute mark notification as read.
        
        Args:
            notification_id: The notification ID
            
        Returns:
            Formatted response string
        """
        endpoint = f"/notifications/mark-read/{notification_id}"
        
        response = self.api_client.request(
            method=self.http_method,
            endpoint=endpoint
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format mark notification read response."""
        if not response.success:
            return f"Failed to mark notification as read: {response.error}"
        
        data = response.data
        if isinstance(data, dict):
            notif_id = data.get('id', 'N/A')
            message = data.get('message', 'N/A')
            return (
                f"Notification marked as read successfully!\n"
                f"ID: {notif_id}\n"
                f"Message: {message}"
            )
        
        return "Notification marked as read successfully!"


class QRCodeToolDefinition:
    """Base class for QR Code tool definitions."""
    
    def __init__(self, api_client: GatePassAPIClient):
        """Initialize tool with API client.
        
        Args:
            api_client: GatePassAPIClient instance for making API requests
        """
        self.api_client = api_client
    
    @property
    def name(self) -> str:
        """Tool name identifier."""
        raise NotImplementedError
    
    @property
    def description(self) -> str:
        """Natural language description for LLM."""
        raise NotImplementedError
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema for tool parameters."""
        raise NotImplementedError
    
    @property
    def required_role(self) -> str:
        """Role required to access this tool."""
        return "All"
    
    @property
    def api_endpoint(self) -> str:
        """API endpoint to call."""
        raise NotImplementedError
    
    @property
    def http_method(self) -> str:
        """HTTP method (GET or POST)."""
        raise NotImplementedError
    
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Formatted response string
        """
        raise NotImplementedError
    
    def format_response(self, response: APIResponse) -> str:
        """Format API response into natural language.
        
        Args:
            response: APIResponse object from API client
            
        Returns:
            User-friendly formatted response string
        """
        raise NotImplementedError


class GetQRCodeTool(QRCodeToolDefinition):
    """Tool for generating a QR code for a gate pass."""
    
    @property
    def name(self) -> str:
        return "get_qr_code"
    
    @property
    def description(self) -> str:
        return "Generate a QR code for a gate pass."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pass_number": {
                    "type": "string",
                    "description": "The gate pass number"
                }
            },
            "required": ["pass_number"]
        }
    
    @property
    def api_endpoint(self) -> str:
        # This will be formatted with pass_number in execute method
        return "/qr/{pass_number}"
    
    @property
    def http_method(self) -> str:
        return "GET"
    
    def execute(self, pass_number: str) -> str:
        """Execute QR code generation.
        
        Args:
            pass_number: The gate pass number
            
        Returns:
            Formatted response string
        """
        endpoint = f"/qr/{pass_number}"
        
        response = self.api_client.request(
            method=self.http_method,
            endpoint=endpoint
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format QR code response.
        
        Note: QR code image data is returned without modification as per requirement 5.3.
        """
        if not response.success:
            return f"Failed to generate QR code: {response.error}"
        
        # Return QR code data without modification (Requirement 5.3)
        data = response.data
        if isinstance(data, dict):
            qr_code_url = data.get('qr_code_url', None)
            qr_code_data = data.get('qr_code_data', None)
            
            if qr_code_url:
                return f"QR code generated successfully! URL: {qr_code_url}"
            elif qr_code_data:
                # Return the raw QR code data without modification
                return f"QR code generated successfully! Data: {qr_code_data}"
        
        # If response.data is raw image data, return it as-is
        return response.data if response.data else "QR code generated successfully!"


def get_notification_tools(api_client: GatePassAPIClient) -> list:
    """Get all Notification tool instances.
    
    Args:
        api_client: GatePassAPIClient instance
        
    Returns:
        List of Notification tool instances
    """
    return [
        GetAdminNotificationsTool(api_client),
        GetHRNotificationsTool(api_client),
        MarkNotificationReadTool(api_client)
    ]


def get_qr_code_tools(api_client: GatePassAPIClient) -> list:
    """Get all QR Code tool instances.
    
    Args:
        api_client: GatePassAPIClient instance
        
    Returns:
        List of QR Code tool instances
    """
    return [
        GetQRCodeTool(api_client)
    ]
