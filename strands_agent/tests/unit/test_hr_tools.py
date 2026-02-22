"""Unit tests for HR tool definitions."""

import pytest
from unittest.mock import Mock, MagicMock
from strands_agent.tools.hr_tools import (
    CreateGatePassTool,
    ListGatePassesTool,
    GetGatePassDetailsTool,
    PrintGatePassTool,
    get_hr_tools
)
from strands_agent.core.models import APIResponse
from strands_agent.core.api_client import GatePassAPIClient


@pytest.fixture
def mock_api_client():
    """Create a mock API client."""
    return Mock(spec=GatePassAPIClient)


class TestCreateGatePassTool:
    """Tests for CreateGatePassTool."""
    
    def test_tool_properties(self, mock_api_client):
        """Test that tool has all required properties."""
        tool = CreateGatePassTool(mock_api_client)
        
        assert tool.name == "create_gate_pass"
        assert tool.description is not None
        assert len(tool.description) > 0
        assert tool.parameters is not None
        assert tool.required_role == "HR_User"
        assert tool.api_endpoint == "/hr/gatepass/create"
        assert tool.http_method == "POST"
    
    def test_parameters_schema(self, mock_api_client):
        """Test that parameters schema is correctly defined."""
        tool = CreateGatePassTool(mock_api_client)
        params = tool.parameters
        
        assert params["type"] == "object"
        assert "person_name" in params["properties"]
        assert "description" in params["properties"]
        assert "is_returnable" in params["properties"]
        assert set(params["required"]) == {"person_name", "description", "is_returnable"}
    
    def test_execute_success(self, mock_api_client):
        """Test successful gate pass creation."""
        tool = CreateGatePassTool(mock_api_client)
        
        # Mock successful API response
        mock_api_client.request.return_value = APIResponse(
            success=True,
            status_code=200,
            data={
                "pass_number": "GP-2024-0001",
                "person_name": "John Doe",
                "status": "pending"
            }
        )
        
        result = tool.execute(
            person_name="John Doe",
            description="Business meeting",
            is_returnable=True
        )
        
        # Verify API client was called correctly
        mock_api_client.request.assert_called_once_with(
            method="POST",
            endpoint="/hr/gatepass/create",
            json_data={
                "person_name": "John Doe",
                "description": "Business meeting",
                "is_returnable": True
            }
        )
        
        # Verify response formatting
        assert "Gate pass created successfully" in result
        assert "GP-2024-0001" in result
        assert "John Doe" in result
    
    def test_execute_failure(self, mock_api_client):
        """Test failed gate pass creation."""
        tool = CreateGatePassTool(mock_api_client)
        
        # Mock failed API response
        mock_api_client.request.return_value = APIResponse(
            success=False,
            status_code=422,
            error="Validation error: person_name is required"
        )
        
        result = tool.execute(
            person_name="",
            description="Business meeting",
            is_returnable=True
        )
        
        assert "Failed to create gate pass" in result
        assert "Validation error" in result


class TestListGatePassesTool:
    """Tests for ListGatePassesTool."""
    
    def test_tool_properties(self, mock_api_client):
        """Test that tool has all required properties."""
        tool = ListGatePassesTool(mock_api_client)
        
        assert tool.name == "list_gate_passes"
        assert tool.description is not None
        assert tool.required_role == "HR_User"
        assert tool.api_endpoint == "/hr/gatepass/list"
        assert tool.http_method == "GET"
    
    def test_execute_with_status_filter(self, mock_api_client):
        """Test listing gate passes with status filter."""
        tool = ListGatePassesTool(mock_api_client)
        
        # Mock successful API response
        mock_api_client.request.return_value = APIResponse(
            success=True,
            status_code=200,
            data=[
                {
                    "pass_number": "GP-2024-0001",
                    "person_name": "John Doe",
                    "status": "pending",
                    "created_at": "2024-01-01T10:00:00"
                }
            ]
        )
        
        result = tool.execute(status="pending")
        
        # Verify API client was called with status parameter
        mock_api_client.request.assert_called_once_with(
            method="GET",
            endpoint="/hr/gatepass/list",
            params={"status": "pending"}
        )
        
        assert "Found 1 gate pass" in result
        assert "GP-2024-0001" in result
    
    def test_execute_without_filter(self, mock_api_client):
        """Test listing all gate passes without filter."""
        tool = ListGatePassesTool(mock_api_client)
        
        mock_api_client.request.return_value = APIResponse(
            success=True,
            status_code=200,
            data=[]
        )
        
        result = tool.execute()
        
        # Verify API client was called without parameters
        mock_api_client.request.assert_called_once_with(
            method="GET",
            endpoint="/hr/gatepass/list",
            params={}
        )
        
        assert "No gate passes found" in result


class TestGetGatePassDetailsTool:
    """Tests for GetGatePassDetailsTool."""
    
    def test_tool_properties(self, mock_api_client):
        """Test that tool has all required properties."""
        tool = GetGatePassDetailsTool(mock_api_client)
        
        assert tool.name == "get_gate_pass_details"
        assert tool.description is not None
        assert tool.required_role == "HR_User"
        assert tool.http_method == "GET"
    
    def test_execute_success(self, mock_api_client):
        """Test successful gate pass details retrieval."""
        tool = GetGatePassDetailsTool(mock_api_client)
        
        # Mock successful API response
        mock_api_client.request.return_value = APIResponse(
            success=True,
            status_code=200,
            data={
                "pass_number": "GP-2024-0001",
                "person_name": "John Doe",
                "description": "Business meeting",
                "status": "approved",
                "is_returnable": True,
                "created_at": "2024-01-01T10:00:00",
                "approved_at": "2024-01-01T11:00:00",
                "approved_by": "Admin User"
            }
        )
        
        result = tool.execute(pass_id="123")
        
        # Verify API client was called with correct endpoint
        mock_api_client.request.assert_called_once_with(
            method="GET",
            endpoint="/hr/gatepass/123"
        )
        
        assert "Gate Pass Details" in result
        assert "GP-2024-0001" in result
        assert "John Doe" in result
        assert "approved" in result


class TestPrintGatePassTool:
    """Tests for PrintGatePassTool."""
    
    def test_tool_properties(self, mock_api_client):
        """Test that tool has all required properties."""
        tool = PrintGatePassTool(mock_api_client)
        
        assert tool.name == "print_gate_pass"
        assert tool.description is not None
        assert tool.required_role == "HR_User"
        assert tool.http_method == "GET"
    
    def test_execute_success(self, mock_api_client):
        """Test successful gate pass printing."""
        tool = PrintGatePassTool(mock_api_client)
        
        # Mock successful API response
        mock_api_client.request.return_value = APIResponse(
            success=True,
            status_code=200,
            data={"print_url": "https://example.com/print/GP-2024-0001"}
        )
        
        result = tool.execute(pass_number="GP-2024-0001")
        
        # Verify API client was called with correct endpoint
        mock_api_client.request.assert_called_once_with(
            method="GET",
            endpoint="/hr/gatepass/GP-2024-0001/print"
        )
        
        assert "Printable gate pass generated successfully" in result


class TestGetHRTools:
    """Tests for get_hr_tools function."""
    
    def test_returns_all_hr_tools(self, mock_api_client):
        """Test that get_hr_tools returns all HR tool instances."""
        tools = get_hr_tools(mock_api_client)
        
        assert len(tools) == 4
        assert isinstance(tools[0], CreateGatePassTool)
        assert isinstance(tools[1], ListGatePassesTool)
        assert isinstance(tools[2], GetGatePassDetailsTool)
        assert isinstance(tools[3], PrintGatePassTool)
        
        # Verify all tools have the same API client
        for tool in tools:
            assert tool.api_client == mock_api_client
