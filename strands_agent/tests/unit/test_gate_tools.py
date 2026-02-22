"""Unit tests for Gate tool definitions."""

import pytest
from unittest.mock import Mock, patch
from strands_agent.tools.gate_tools import (
    ScanExitTool,
    ScanReturnTool,
    GetGatePassByNumberGateTool,
    GetGatePassByIdGateTool,
    GetGatePassPhotosTool,
    get_gate_tools
)
from strands_agent.core.models import APIResponse
from strands_agent.core.api_client import GatePassAPIClient
from strands_agent.core.file_handler import FileValidationError


@pytest.fixture
def mock_api_client():
    """Create a mock API client."""
    return Mock(spec=GatePassAPIClient)


class TestScanExitTool:
    """Tests for ScanExitTool."""
    
    def test_tool_properties(self, mock_api_client):
        """Test that tool has all required properties."""
        tool = ScanExitTool(mock_api_client)
        
        assert tool.name == "scan_exit"
        assert tool.description is not None
        assert len(tool.description) > 0
        assert tool.parameters is not None
        assert tool.required_role == "Gate_User"
        assert tool.api_endpoint == "/gate/scan-exit"
        assert tool.http_method == "POST"
    
    def test_parameters_schema(self, mock_api_client):
        """Test that parameters schema is correctly defined."""
        tool = ScanExitTool(mock_api_client)
        params = tool.parameters
        
        assert params["type"] == "object"
        assert "pass_number" in params["properties"]
        assert "photo" in params["properties"]
        assert set(params["required"]) == {"pass_number", "photo"}
    
    @patch('strands_agent.tools.gate_tools.prepare_multipart_data')
    def test_execute_success(self, mock_prepare, mock_api_client):
        """Test successful exit scan."""
        tool = ScanExitTool(mock_api_client)
        
        # Mock file preparation
        mock_prepare.return_value = (
            {'pass_number': 'GP-2024-0001'},
            {'photo': ('test.jpg', b'fake_image_data', 'image/jpeg')}
        )
        
        # Mock successful API response
        mock_api_client.request.return_value = APIResponse(
            success=True,
            status_code=200,
            data={
                "pass_number": "GP-2024-0001",
                "person_name": "John Doe",
                "exit_time": "2024-01-01T10:00:00"
            }
        )
        
        result = tool.execute(
            pass_number="GP-2024-0001",
            photo="/path/to/photo.jpg"
        )
        
        # Verify file preparation was called
        mock_prepare.assert_called_once_with("GP-2024-0001", "/path/to/photo.jpg")
        
        # Verify API client was called correctly with multipart data
        mock_api_client.request.assert_called_once_with(
            method="POST",
            endpoint="/gate/scan-exit",
            params={'pass_number': 'GP-2024-0001'},
            files={'photo': ('test.jpg', b'fake_image_data', 'image/jpeg')}
        )
        
        # Verify response formatting
        assert "Exit scan successful" in result
        assert "GP-2024-0001" in result
        assert "John Doe" in result
    
    @patch('strands_agent.tools.gate_tools.prepare_multipart_data')
    def test_execute_file_validation_error(self, mock_prepare, mock_api_client):
        """Test exit scan with file validation error."""
        tool = ScanExitTool(mock_api_client)
        
        # Mock file validation error
        mock_prepare.side_effect = FileValidationError("Invalid file format: txt")
        
        result = tool.execute(
            pass_number="GP-2024-0001",
            photo="/path/to/file.txt"
        )
        
        assert "File validation failed" in result
        assert "Invalid file format" in result
    
    def test_execute_api_failure(self, mock_api_client):
        """Test failed exit scan."""
        tool = ScanExitTool(mock_api_client)
        
        with patch('strands_agent.tools.gate_tools.prepare_multipart_data') as mock_prepare:
            mock_prepare.return_value = (
                {'pass_number': 'GP-2024-0001'},
                {'photo': ('test.jpg', b'fake_image_data', 'image/jpeg')}
            )
            
            # Mock failed API response
            mock_api_client.request.return_value = APIResponse(
                success=False,
                status_code=403,
                error="Gate pass not approved"
            )
            
            result = tool.execute(
                pass_number="GP-2024-0001",
                photo="/path/to/photo.jpg"
            )
            
            assert "Failed to scan exit" in result
            assert "Gate pass not approved" in result


class TestScanReturnTool:
    """Tests for ScanReturnTool."""
    
    def test_tool_properties(self, mock_api_client):
        """Test that tool has all required properties."""
        tool = ScanReturnTool(mock_api_client)
        
        assert tool.name == "scan_return"
        assert tool.description is not None
        assert tool.required_role == "Gate_User"
        assert tool.api_endpoint == "/gate/scan-return"
        assert tool.http_method == "POST"
    
    @patch('strands_agent.tools.gate_tools.prepare_multipart_data')
    def test_execute_success(self, mock_prepare, mock_api_client):
        """Test successful return scan."""
        tool = ScanReturnTool(mock_api_client)
        
        # Mock file preparation
        mock_prepare.return_value = (
            {'pass_number': 'GP-2024-0001'},
            {'photo': ('test.jpg', b'fake_image_data', 'image/jpeg')}
        )
        
        # Mock successful API response
        mock_api_client.request.return_value = APIResponse(
            success=True,
            status_code=200,
            data={
                "pass_number": "GP-2024-0001",
                "person_name": "John Doe",
                "return_time": "2024-01-01T18:00:00"
            }
        )
        
        result = tool.execute(
            pass_number="GP-2024-0001",
            photo="/path/to/photo.jpg"
        )
        
        # Verify response formatting
        assert "Return scan successful" in result
        assert "GP-2024-0001" in result
        assert "John Doe" in result


class TestGetGatePassByNumberGateTool:
    """Tests for GetGatePassByNumberGateTool."""
    
    def test_tool_properties(self, mock_api_client):
        """Test that tool has all required properties."""
        tool = GetGatePassByNumberGateTool(mock_api_client)
        
        assert tool.name == "get_gate_pass_by_number_gate"
        assert tool.description is not None
        assert tool.required_role == "Gate_User"
        assert tool.http_method == "GET"
    
    def test_execute_success(self, mock_api_client):
        """Test successful gate pass details retrieval."""
        tool = GetGatePassByNumberGateTool(mock_api_client)
        
        # Mock successful API response
        mock_api_client.request.return_value = APIResponse(
            success=True,
            status_code=200,
            data={
                "pass_number": "GP-2024-0001",
                "person_name": "John Doe",
                "description": "Business meeting",
                "status": "exited",
                "is_returnable": True,
                "created_at": "2024-01-01T10:00:00",
                "exit_time": "2024-01-01T12:00:00"
            }
        )
        
        result = tool.execute(pass_number="GP-2024-0001")
        
        # Verify API client was called with correct endpoint
        mock_api_client.request.assert_called_once_with(
            method="GET",
            endpoint="/gate/gatepass/number/GP-2024-0001"
        )
        
        assert "Gate Pass Details" in result
        assert "GP-2024-0001" in result
        assert "John Doe" in result
        assert "exited" in result


class TestGetGatePassByIdGateTool:
    """Tests for GetGatePassByIdGateTool."""
    
    def test_tool_properties(self, mock_api_client):
        """Test that tool has all required properties."""
        tool = GetGatePassByIdGateTool(mock_api_client)
        
        assert tool.name == "get_gate_pass_by_id_gate"
        assert tool.description is not None
        assert tool.required_role == "Gate_User"
        assert tool.http_method == "GET"
    
    def test_execute_success(self, mock_api_client):
        """Test successful gate pass details retrieval by ID."""
        tool = GetGatePassByIdGateTool(mock_api_client)
        
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
                "created_at": "2024-01-01T10:00:00"
            }
        )
        
        result = tool.execute(pass_id="123")
        
        # Verify API client was called with correct endpoint
        mock_api_client.request.assert_called_once_with(
            method="GET",
            endpoint="/gate/gatepass/id/123"
        )
        
        assert "Gate Pass Details" in result
        assert "GP-2024-0001" in result


class TestGetGatePassPhotosTool:
    """Tests for GetGatePassPhotosTool."""
    
    def test_tool_properties(self, mock_api_client):
        """Test that tool has all required properties."""
        tool = GetGatePassPhotosTool(mock_api_client)
        
        assert tool.name == "get_gate_pass_photos"
        assert tool.description is not None
        assert tool.required_role == "Gate_User"
        assert tool.http_method == "GET"
    
    def test_execute_success_with_photos(self, mock_api_client):
        """Test successful gate pass photos retrieval."""
        tool = GetGatePassPhotosTool(mock_api_client)
        
        # Mock successful API response with photos
        mock_api_client.request.return_value = APIResponse(
            success=True,
            status_code=200,
            data={
                "photos": [
                    {
                        "url": "https://example.com/photo1.jpg",
                        "type": "exit",
                        "timestamp": "2024-01-01T12:00:00"
                    },
                    {
                        "url": "https://example.com/photo2.jpg",
                        "type": "return",
                        "timestamp": "2024-01-01T18:00:00"
                    }
                ]
            }
        )
        
        result = tool.execute(pass_number="GP-2024-0001")
        
        # Verify API client was called with correct endpoint
        mock_api_client.request.assert_called_once_with(
            method="GET",
            endpoint="/gate/photos/GP-2024-0001"
        )
        
        assert "Found 2 photo(s)" in result
        assert "exit" in result
        assert "return" in result
    
    def test_execute_success_no_photos(self, mock_api_client):
        """Test gate pass photos retrieval with no photos."""
        tool = GetGatePassPhotosTool(mock_api_client)
        
        # Mock successful API response with no photos
        mock_api_client.request.return_value = APIResponse(
            success=True,
            status_code=200,
            data={"photos": []}
        )
        
        result = tool.execute(pass_number="GP-2024-0001")
        
        assert "No photos found" in result


class TestGetGateTools:
    """Tests for get_gate_tools function."""
    
    def test_returns_all_gate_tools(self, mock_api_client):
        """Test that get_gate_tools returns all Gate tool instances."""
        tools = get_gate_tools(mock_api_client)
        
        assert len(tools) == 5
        assert isinstance(tools[0], ScanExitTool)
        assert isinstance(tools[1], ScanReturnTool)
        assert isinstance(tools[2], GetGatePassByNumberGateTool)
        assert isinstance(tools[3], GetGatePassByIdGateTool)
        assert isinstance(tools[4], GetGatePassPhotosTool)
        
        # Verify all tools have the same API client
        for tool in tools:
            assert tool.api_client == mock_api_client
