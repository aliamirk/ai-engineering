"""Gate tool definitions for Gate Pass Management API."""

from typing import Any, Dict
from strands_agent.core.api_client import GatePassAPIClient
from strands_agent.core.models import APIResponse
from strands_agent.core.file_handler import prepare_multipart_data, FileValidationError


class GateToolDefinition:
    """Base class for Gate tool definitions."""
    
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
        return "Gate_User"
    
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


class ScanExitTool(GateToolDefinition):
    """Tool for recording a person's exit from the facility."""
    
    @property
    def name(self) -> str:
        return "scan_exit"
    
    @property
    def description(self) -> str:
        return "Record a person's exit from the facility. Requires the gate pass number and a photo of the person."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pass_number": {
                    "type": "string",
                    "description": "The gate pass number"
                },
                "photo": {
                    "type": "string",
                    "description": "Path to photo file of the person exiting"
                }
            },
            "required": ["pass_number", "photo"]
        }
    
    @property
    def api_endpoint(self) -> str:
        return "/gate/scan-exit"
    
    @property
    def http_method(self) -> str:
        return "POST"
    
    def execute(self, pass_number: str, photo: str) -> str:
        """Execute exit scan.
        
        Args:
            pass_number: The gate pass number
            photo: Path to photo file
            
        Returns:
            Formatted response string
        """
        try:
            # Validate and prepare multipart data
            data, files = prepare_multipart_data(pass_number, photo)
            
            # Make API request with multipart form data
            response = self.api_client.request(
                method=self.http_method,
                endpoint=self.api_endpoint,
                params=data,
                files=files
            )
            
            return self.format_response(response)
            
        except FileValidationError as e:
            return f"File validation failed: {str(e)}"
        except Exception as e:
            return f"Failed to scan exit: {str(e)}"
    
    def format_response(self, response: APIResponse) -> str:
        """Format exit scan response."""
        if not response.success:
            return f"Failed to scan exit: {response.error}"
        
        data = response.data
        if isinstance(data, dict):
            pass_number = data.get('pass_number', 'N/A')
            person_name = data.get('person_name', 'N/A')
            exit_time = data.get('exit_time', 'N/A')
            return (
                f"Exit scan successful!\n"
                f"Pass Number: {pass_number}\n"
                f"Person: {person_name}\n"
                f"Exit Time: {exit_time}"
            )
        
        return "Exit scan successful!"


class ScanReturnTool(GateToolDefinition):
    """Tool for recording a person's return to the facility."""
    
    @property
    def name(self) -> str:
        return "scan_return"
    
    @property
    def description(self) -> str:
        return "Record a person's return to the facility. Requires the gate pass number and a photo of the person."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pass_number": {
                    "type": "string",
                    "description": "The gate pass number"
                },
                "photo": {
                    "type": "string",
                    "description": "Path to photo file of the person returning"
                }
            },
            "required": ["pass_number", "photo"]
        }
    
    @property
    def api_endpoint(self) -> str:
        return "/gate/scan-return"
    
    @property
    def http_method(self) -> str:
        return "POST"
    
    def execute(self, pass_number: str, photo: str) -> str:
        """Execute return scan.
        
        Args:
            pass_number: The gate pass number
            photo: Path to photo file
            
        Returns:
            Formatted response string
        """
        try:
            # Validate and prepare multipart data
            data, files = prepare_multipart_data(pass_number, photo)
            
            # Make API request with multipart form data
            response = self.api_client.request(
                method=self.http_method,
                endpoint=self.api_endpoint,
                params=data,
                files=files
            )
            
            return self.format_response(response)
            
        except FileValidationError as e:
            return f"File validation failed: {str(e)}"
        except Exception as e:
            return f"Failed to scan return: {str(e)}"
    
    def format_response(self, response: APIResponse) -> str:
        """Format return scan response."""
        if not response.success:
            return f"Failed to scan return: {response.error}"
        
        data = response.data
        if isinstance(data, dict):
            pass_number = data.get('pass_number', 'N/A')
            person_name = data.get('person_name', 'N/A')
            return_time = data.get('return_time', 'N/A')
            return (
                f"Return scan successful!\n"
                f"Pass Number: {pass_number}\n"
                f"Person: {person_name}\n"
                f"Return Time: {return_time}"
            )
        
        return "Return scan successful!"


class GetGatePassByNumberGateTool(GateToolDefinition):
    """Tool for retrieving gate pass details by pass number."""
    
    @property
    def name(self) -> str:
        return "get_gate_pass_by_number_gate"
    
    @property
    def description(self) -> str:
        return "Get gate pass details using the pass number."
    
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
        return "/gate/gatepass/number/{pass_number}"
    
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
        endpoint = f"/gate/gatepass/number/{pass_number}"
        
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
            exit_time = data.get('exit_time', 'N/A')
            return_time = data.get('return_time', 'N/A')
            
            result = (
                f"Gate Pass Details:\n"
                f"Pass Number: {pass_number}\n"
                f"Person: {person_name}\n"
                f"Description: {description}\n"
                f"Status: {status}\n"
                f"Returnable: {'Yes' if is_returnable else 'No'}\n"
                f"Created: {created_at}\n"
            )
            
            if exit_time != 'N/A':
                result += f"Exit Time: {exit_time}\n"
            if return_time != 'N/A':
                result += f"Return Time: {return_time}\n"
            
            return result
        
        return "Gate pass details retrieved successfully!"


class GetGatePassByIdGateTool(GateToolDefinition):
    """Tool for retrieving gate pass details by pass ID."""
    
    @property
    def name(self) -> str:
        return "get_gate_pass_by_id_gate"
    
    @property
    def description(self) -> str:
        return "Get gate pass details using the pass ID."
    
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
        return "/gate/gatepass/id/{pass_id}"
    
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
        endpoint = f"/gate/gatepass/id/{pass_id}"
        
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
            exit_time = data.get('exit_time', 'N/A')
            return_time = data.get('return_time', 'N/A')
            
            result = (
                f"Gate Pass Details:\n"
                f"Pass Number: {pass_number}\n"
                f"Person: {person_name}\n"
                f"Description: {description}\n"
                f"Status: {status}\n"
                f"Returnable: {'Yes' if is_returnable else 'No'}\n"
                f"Created: {created_at}\n"
            )
            
            if exit_time != 'N/A':
                result += f"Exit Time: {exit_time}\n"
            if return_time != 'N/A':
                result += f"Return Time: {return_time}\n"
            
            return result
        
        return "Gate pass details retrieved successfully!"


class GetGatePassPhotosTool(GateToolDefinition):
    """Tool for retrieving photos associated with a gate pass."""
    
    @property
    def name(self) -> str:
        return "get_gate_pass_photos"
    
    @property
    def description(self) -> str:
        return "Retrieve photos associated with a gate pass."
    
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
        return "/gate/photos/{pass_number}"
    
    @property
    def http_method(self) -> str:
        return "GET"
    
    def execute(self, pass_number: str) -> str:
        """Execute gate pass photos retrieval.
        
        Args:
            pass_number: The gate pass number
            
        Returns:
            Formatted response string
        """
        endpoint = f"/gate/photos/{pass_number}"
        
        response = self.api_client.request(
            method=self.http_method,
            endpoint=endpoint
        )
        
        return self.format_response(response)
    
    def format_response(self, response: APIResponse) -> str:
        """Format gate pass photos response."""
        if not response.success:
            return f"Failed to retrieve gate pass photos: {response.error}"
        
        data = response.data
        if isinstance(data, dict):
            photos = data.get('photos', [])
            if isinstance(photos, list):
                if len(photos) == 0:
                    return "No photos found for this gate pass."
                
                result = f"Found {len(photos)} photo(s) for gate pass:\n\n"
                for idx, photo in enumerate(photos, 1):
                    photo_url = photo.get('url', 'N/A')
                    photo_type = photo.get('type', 'N/A')
                    timestamp = photo.get('timestamp', 'N/A')
                    result += f"{idx}. Type: {photo_type}, Timestamp: {timestamp}\n   URL: {photo_url}\n"
                
                return result
        
        return "Gate pass photos retrieved successfully!"


def get_gate_tools(api_client: GatePassAPIClient) -> list:
    """Get all Gate tool instances.
    
    Args:
        api_client: GatePassAPIClient instance
        
    Returns:
        List of Gate tool instances
    """
    return [
        ScanExitTool(api_client),
        ScanReturnTool(api_client),
        GetGatePassByNumberGateTool(api_client),
        GetGatePassByIdGateTool(api_client),
        GetGatePassPhotosTool(api_client)
    ]
