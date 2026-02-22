"""HR tool definitions for Gate Pass Management API."""

from typing import Any, Dict, Optional
from strands_agent.core.api_client import GatePassAPIClient
from strands_agent.core.models import APIResponse


class HRToolDefinition:
    """Base class for HR tool definitions."""
    
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
        return "HR_User"
    
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


class CreateGatePassTool(HRToolDefinition):
    """Tool for creating a new gate pass."""
    
    @property
    def name(self) -> str:
        return "create_gate_pass"
    
    @property
    def description(self) -> str:
        return "Create a new gate pass for a person. Requires person name, description of purpose, and whether the person will return."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "person_name": {
                    "type": "string",
                    "description": "Name of the person"
                },
                "description": {
                    "type": "string",
                    "description": "Purpose of the gate pass"
                },
                "is_returnable": {
                    "type": "boolean",
                    "description": "Whether the person will return"
                }
            },
            "required": ["person_name", "description", "is_returnable"]
        }
    
    @property
    def api_endpoint(self) -> str:
        return "/hr/gatepass/create"
    
    @property
    def http_method(self) -> str:
        return "POST"
    
    def execute(self, person_name: str, description: str, is_returnable: bool) -> str:
        """Execute gate pass creation.
        
        Args:
            person_name: Name of the person
            description: Purpose of the gate pass
            is_returnable: Whether the person will return
            
        Returns:
            Formatted response string
        """
        json_data = {
            "person_name": person_name,
            "description": description,
            "is_returnable": is_returnable
        }
        
        response = self.api_client.request(
            method=self.http_method,
            endpoint=self.api_endpoint,
            json_data=json_data
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format gate pass creation response."""
        if not response.success:
            return f"Failed to create gate pass: {response.error}"
        
        data = response.data
        if isinstance(data, dict):
            pass_number = data.get('pass_number', 'N/A')
            person_name = data.get('person_name', 'N/A')
            status = data.get('status', 'N/A')
            return (
                f"Gate pass created successfully!\n"
                f"Pass Number: {pass_number}\n"
                f"Person: {person_name}\n"
                f"Status: {status}"
            )
        
        return "Gate pass created successfully!"


class ListGatePassesTool(HRToolDefinition):
    """Tool for listing gate passes with optional status filtering."""
    
    @property
    def name(self) -> str:
        return "list_gate_passes"
    
    @property
    def description(self) -> str:
        return "List all gate passes with optional status filtering. Status can be 'pending', 'approved', 'rejected', 'exited', or 'returned'."
    
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
        return "/hr/gatepass/list"
    
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


class GetGatePassDetailsTool(HRToolDefinition):
    """Tool for retrieving gate pass details by ID."""
    
    @property
    def name(self) -> str:
        return "get_gate_pass_details"
    
    @property
    def description(self) -> str:
        return "Get detailed information about a specific gate pass using its ID."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pass_id": {
                    "type": "string",
                    "description": "The gate pass ID"
                }
            },
            "required": ["pass_id"]
        }
    
    @property
    def api_endpoint(self) -> str:
        # This will be formatted with pass_id in execute method
        return "/hr/gatepass/{pass_id}"
    
    @property
    def http_method(self) -> str:
        return "GET"
    
    def execute(self, pass_id: str) -> str:
        """Execute gate pass details retrieval.
        
        Args:
            pass_id: The gate pass ID
            
        Returns:
            Formatted response string
        """
        endpoint = f"/hr/gatepass/{pass_id}"
        
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


class PrintGatePassTool(HRToolDefinition):
    """Tool for generating a printable version of a gate pass."""
    
    @property
    def name(self) -> str:
        return "print_gate_pass"
    
    @property
    def description(self) -> str:
        return "Generate a printable version of a gate pass using its pass number (format: GP-YYYY-NNNN)."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pass_number": {
                    "type": "string",
                    "description": "The gate pass number (format: GP-YYYY-NNNN)"
                }
            },
            "required": ["pass_number"]
        }
    
    @property
    def api_endpoint(self) -> str:
        # This will be formatted with pass_number in execute method
        return "/hr/gatepass/{pass_number}/print"
    
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
        endpoint = f"/hr/gatepass/{pass_number}/print"
        
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


def get_hr_tools(api_client: GatePassAPIClient) -> list:
    """Get all HR tool instances.
    
    Args:
        api_client: GatePassAPIClient instance
        
    Returns:
        List of HR tool instances
    """
    return [
        CreateGatePassTool(api_client),
        ListGatePassesTool(api_client),
        GetGatePassDetailsTool(api_client),
        PrintGatePassTool(api_client)
    ]
