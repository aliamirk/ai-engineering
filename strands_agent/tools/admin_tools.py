"""Admin tool definitions for Gate Pass Management API."""

from typing import Any, Dict, Optional
from strands_agent.core.api_client import GatePassAPIClient
from strands_agent.core.models import APIResponse


class AdminToolDefinition:
    """Base class for Admin tool definitions."""
    
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
        return "Admin_User"
    
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


class ListPendingGatePassesTool(AdminToolDefinition):
    """Tool for listing all pending gate passes."""
    
    @property
    def name(self) -> str:
        return "list_pending_gate_passes"
    
    @property
    def description(self) -> str:
        return "List all gate passes that are pending approval."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    @property
    def api_endpoint(self) -> str:
        return "/admin/gatepass/pending"
    
    @property
    def http_method(self) -> str:
        return "GET"
    
    def execute(self) -> str:
        """Execute pending gate passes listing.
        
        Returns:
            Formatted response string
        """
        response = self.api_client.request(
            method=self.http_method,
            endpoint=self.api_endpoint
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format pending gate passes list response."""
        if not response.success:
            return f"Failed to list pending gate passes: {response.error}"
        
        data = response.data
        if isinstance(data, list):
            if len(data) == 0:
                return "No pending gate passes found."
            
            result = f"Found {len(data)} pending gate pass(es):\n\n"
            for idx, gate_pass in enumerate(data, 1):
                pass_number = gate_pass.get('pass_number', 'N/A')
                person_name = gate_pass.get('person_name', 'N/A')
                description = gate_pass.get('description', 'N/A')
                created_at = gate_pass.get('created_at', 'N/A')
                result += f"{idx}. {pass_number} - {person_name}\n   Purpose: {description}\n   Created: {created_at}\n\n"
            
            return result
        
        return "Pending gate passes retrieved successfully!"


class GetGatePassByNumberTool(AdminToolDefinition):
    """Tool for retrieving gate pass details by pass number."""
    
    @property
    def name(self) -> str:
        return "get_gate_pass_by_number"
    
    @property
    def description(self) -> str:
        return "Get detailed information about a gate pass using its pass number."
    
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
        return "/admin/gatepass/{pass_number}"
    
    @property
    def http_method(self) -> str:
        return "GET"
    
    def execute(self, pass_number: str) -> str:
        """Execute gate pass details retrieval.
        
        Args:
            pass_number: The gate pass number
            
        Returns:
            Formatted response string
        """
        endpoint = f"/admin/gatepass/{pass_number}"
        
        response = self.api_client.request(
            method=self.http_method,
            endpoint=endpoint
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format gate pass details response."""
        if not response.success:
            return f"Failed to retrieve gate pass details: {response.error}"
        
        data = response.data
        if isinstance(data, dict):
            pass_number = data.get('pass_number', 'N/A')
            person_name = data.get('person_name', 'N/A')
            description = data.get('description', 'N/A')
            status = data.get('status', 'N/A')
            is_returnable = data.get('is_returnable', False)
            created_at = data.get('created_at', 'N/A')
            approved_at = data.get('approved_at', 'N/A')
            approved_by = data.get('approved_by', 'N/A')
            
            result = (
                f"Gate Pass Details:\n"
                f"Pass Number: {pass_number}\n"
                f"Person: {person_name}\n"
                f"Description: {description}\n"
                f"Status: {status}\n"
                f"Returnable: {'Yes' if is_returnable else 'No'}\n"
                f"Created: {created_at}\n"
            )
            
            if approved_at != 'N/A':
                result += f"Approved: {approved_at}\n"
            if approved_by != 'N/A':
                result += f"Approved By: {approved_by}\n"
            
            return result
        
        return "Gate pass details retrieved successfully!"



class ApproveGatePassTool(AdminToolDefinition):
    """Tool for approving a pending gate pass."""
    
    @property
    def name(self) -> str:
        return "approve_gate_pass"
    
    @property
    def description(self) -> str:
        return "Approve a pending gate pass. Requires the pass number and admin name."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pass_number": {
                    "type": "string",
                    "description": "The gate pass number"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the approving admin"
                }
            },
            "required": ["pass_number", "name"]
        }
    
    @property
    def api_endpoint(self) -> str:
        # This will be formatted with pass_number in execute method
        return "/admin/gatepass/{pass_number}/approve"
    
    @property
    def http_method(self) -> str:
        return "POST"
    
    def execute(self, pass_number: str, name: str) -> str:
        """Execute gate pass approval.
        
        Args:
            pass_number: The gate pass number
            name: Name of the approving admin
            
        Returns:
            Formatted response string
        """
        endpoint = f"/admin/gatepass/{pass_number}/approve"
        json_data = {"name": name}
        
        response = self.api_client.request(
            method=self.http_method,
            endpoint=endpoint,
            json_data=json_data
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format gate pass approval response."""
        if not response.success:
            return f"Failed to approve gate pass: {response.error}"
        
        data = response.data
        if isinstance(data, dict):
            pass_number = data.get('pass_number', 'N/A')
            person_name = data.get('person_name', 'N/A')
            approved_by = data.get('approved_by', 'N/A')
            return (
                f"Gate pass approved successfully!\n"
                f"Pass Number: {pass_number}\n"
                f"Person: {person_name}\n"
                f"Approved By: {approved_by}"
            )
        
        return "Gate pass approved successfully!"


class RejectGatePassTool(AdminToolDefinition):
    """Tool for rejecting a pending gate pass."""
    
    @property
    def name(self) -> str:
        return "reject_gate_pass"
    
    @property
    def description(self) -> str:
        return "Reject a pending gate pass. Requires the pass number and admin name."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pass_number": {
                    "type": "string",
                    "description": "The gate pass number"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the rejecting admin"
                }
            },
            "required": ["pass_number", "name"]
        }
    
    @property
    def api_endpoint(self) -> str:
        # This will be formatted with pass_number in execute method
        return "/admin/gatepass/{pass_number}/reject"
    
    @property
    def http_method(self) -> str:
        return "POST"
    
    def execute(self, pass_number: str, name: str) -> str:
        """Execute gate pass rejection.
        
        Args:
            pass_number: The gate pass number
            name: Name of the rejecting admin
            
        Returns:
            Formatted response string
        """
        endpoint = f"/admin/gatepass/{pass_number}/reject"
        json_data = {"name": name}
        
        response = self.api_client.request(
            method=self.http_method,
            endpoint=endpoint,
            json_data=json_data
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format gate pass rejection response."""
        if not response.success:
            return f"Failed to reject gate pass: {response.error}"
        
        data = response.data
        if isinstance(data, dict):
            pass_number = data.get('pass_number', 'N/A')
            person_name = data.get('person_name', 'N/A')
            rejected_by = data.get('rejected_by', 'N/A')
            return (
                f"Gate pass rejected successfully!\n"
                f"Pass Number: {pass_number}\n"
                f"Person: {person_name}\n"
                f"Rejected By: {rejected_by}"
            )
        
        return "Gate pass rejected successfully!"


class DeleteGatePassTool(AdminToolDefinition):
    """Tool for deleting a gate pass."""
    
    @property
    def name(self) -> str:
        return "delete_gate_pass"
    
    @property
    def description(self) -> str:
        return "Delete a gate pass. Requires the pass number and admin name."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pass_number": {
                    "type": "string",
                    "description": "The gate pass number"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the admin performing deletion"
                }
            },
            "required": ["pass_number", "name"]
        }
    
    @property
    def api_endpoint(self) -> str:
        # This will be formatted with pass_number in execute method
        return "/admin/gatepass/{pass_number}/delete"
    
    @property
    def http_method(self) -> str:
        return "POST"
    
    def execute(self, pass_number: str, name: str) -> str:
        """Execute gate pass deletion.
        
        Args:
            pass_number: The gate pass number
            name: Name of the admin performing deletion
            
        Returns:
            Formatted response string
        """
        endpoint = f"/admin/gatepass/{pass_number}/delete"
        json_data = {"name": name}
        
        response = self.api_client.request(
            method=self.http_method,
            endpoint=endpoint,
            json_data=json_data
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format gate pass deletion response."""
        if not response.success:
            return f"Failed to delete gate pass: {response.error}"
        
        data = response.data
        if isinstance(data, dict):
            pass_number = data.get('pass_number', 'N/A')
            deleted_by = data.get('deleted_by', 'N/A')
            return (
                f"Gate pass deleted successfully!\n"
                f"Pass Number: {pass_number}\n"
                f"Deleted By: {deleted_by}"
            )
        
        return "Gate pass deleted successfully!"


class ListAllGatePassesAdminTool(AdminToolDefinition):
    """Tool for listing all gate passes with optional status filtering."""
    
    @property
    def name(self) -> str:
        return "list_all_gate_passes_admin"
    
    @property
    def description(self) -> str:
        return "List all gate passes with optional status filtering."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter by gate pass status (optional)",
                    "enum": ["pending", "approved", "rejected", "exited", "returned"]
                }
            },
            "required": []
        }
    
    @property
    def api_endpoint(self) -> str:
        return "/admin/gatepass/list"
    
    @property
    def http_method(self) -> str:
        return "GET"
    
    def execute(self, status: Optional[str] = None) -> str:
        """Execute gate pass listing.
        
        Args:
            status: Optional status filter
            
        Returns:
            Formatted response string
        """
        params = {}
        if status:
            params['status'] = status
        
        response = self.api_client.request(
            method=self.http_method,
            endpoint=self.api_endpoint,
            params=params
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format gate pass list response."""
        if not response.success:
            return f"Failed to list gate passes: {response.error}"
        
        data = response.data
        if isinstance(data, list):
            if len(data) == 0:
                return "No gate passes found."
            
            result = f"Found {len(data)} gate pass(es):\n\n"
            for idx, gate_pass in enumerate(data, 1):
                pass_number = gate_pass.get('pass_number', 'N/A')
                person_name = gate_pass.get('person_name', 'N/A')
                status = gate_pass.get('status', 'N/A')
                created_at = gate_pass.get('created_at', 'N/A')
                result += f"{idx}. {pass_number} - {person_name} ({status}) - Created: {created_at}\n"
            
            return result
        
        return "Gate passes retrieved successfully!"


class PrintGatePassAdminTool(AdminToolDefinition):
    """Tool for generating a printable version of a gate pass."""
    
    @property
    def name(self) -> str:
        return "print_gate_pass_admin"
    
    @property
    def description(self) -> str:
        return "Generate a printable version of a gate pass."
    
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
        return "/admin/gatepass/{pass_number}/print"
    
    @property
    def http_method(self) -> str:
        return "GET"
    
    def execute(self, pass_number: str) -> str:
        """Execute gate pass printing.
        
        Args:
            pass_number: The gate pass number
            
        Returns:
            Formatted response string
        """
        endpoint = f"/admin/gatepass/{pass_number}/print"
        
        response = self.api_client.request(
            method=self.http_method,
            endpoint=endpoint
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format gate pass print response."""
        if not response.success:
            return f"Failed to generate printable gate pass: {response.error}"
        
        # The response might contain a URL or file data
        data = response.data
        if isinstance(data, dict):
            print_url = data.get('print_url', None)
            if print_url:
                return f"Printable gate pass generated successfully! URL: {print_url}"
        
        return "Printable gate pass generated successfully!"


def get_admin_tools(api_client: GatePassAPIClient) -> list:
    """Get all Admin tool instances.
    
    Args:
        api_client: GatePassAPIClient instance
        
    Returns:
        List of Admin tool instances
    """
    return [
        ListPendingGatePassesTool(api_client),
        GetGatePassByNumberTool(api_client),
        ApproveGatePassTool(api_client),
        RejectGatePassTool(api_client),
        DeleteGatePassTool(api_client),
        ListAllGatePassesAdminTool(api_client),
        PrintGatePassAdminTool(api_client)
    ]
