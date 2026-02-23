"""Unit tests for ToolRegistry class."""

import pytest
from strands_agent.core.tool_registry import ToolRegistry
from strands_agent.core.api_client import GatePassAPIClient


@pytest.fixture
def api_client():
    """Create a mock API client for testing."""
    return GatePassAPIClient(base_url="http://test.example.com")


@pytest.fixture
def tool_registry(api_client):
    """Create a ToolRegistry instance for testing."""
    return ToolRegistry(api_client)


def test_tool_registry_initialization(tool_registry):
    """Test that ToolRegistry initializes and registers all tools."""
    # Verify that tools are registered
    all_tools = tool_registry.get_all_tools()
    assert len(all_tools) > 0, "ToolRegistry should have registered tools"
    
    # Verify that we have tools from all categories
    tool_names = list(all_tools.keys())
    
    # Check for HR tools
    assert "create_gate_pass" in tool_names
    assert "list_gate_passes" in tool_names
    assert "get_gate_pass_details" in tool_names
    assert "print_gate_pass" in tool_names
    
    # Check for Admin tools
    assert "list_pending_gate_passes" in tool_names
    assert "get_gate_pass_by_number" in tool_names
    assert "approve_gate_pass" in tool_names
    assert "reject_gate_pass" in tool_names
    assert "delete_gate_pass" in tool_names
    assert "list_all_gate_passes_admin" in tool_names
    assert "print_gate_pass_admin" in tool_names
    
    # Check for Gate tools
    assert "scan_exit" in tool_names
    assert "scan_return" in tool_names
    assert "get_gate_pass_by_number_gate" in tool_names
    assert "get_gate_pass_by_id_gate" in tool_names
    assert "get_gate_pass_photos" in tool_names
    
    # Check for Notification tools
    assert "get_admin_notifications" in tool_names
    assert "get_hr_notifications" in tool_names
    assert "mark_notification_read" in tool_names
    
    # Check for QR Code tools
    assert "get_qr_code" in tool_names


def test_get_tools_for_hr_user(tool_registry):
    """Test that HR_User gets only HR tools and shared tools."""
    hr_tools = tool_registry.get_tools_for_role("HR_User")
    hr_tool_names = [tool.name for tool in hr_tools]
    
    # HR should have HR-specific tools
    assert "create_gate_pass" in hr_tool_names
    assert "list_gate_passes" in hr_tool_names
    assert "get_gate_pass_details" in hr_tool_names
    assert "print_gate_pass" in hr_tool_names
    
    # HR should have HR notifications
    assert "get_hr_notifications" in hr_tool_names
    
    # HR should have shared tools
    assert "mark_notification_read" in hr_tool_names
    assert "get_qr_code" in hr_tool_names
    
    # HR should NOT have Admin-specific tools
    assert "approve_gate_pass" not in hr_tool_names
    assert "reject_gate_pass" not in hr_tool_names
    assert "delete_gate_pass" not in hr_tool_names
    assert "get_admin_notifications" not in hr_tool_names
    
    # HR should NOT have Gate-specific tools
    assert "scan_exit" not in hr_tool_names
    assert "scan_return" not in hr_tool_names


def test_get_tools_for_admin_user(tool_registry):
    """Test that Admin_User gets only Admin tools and shared tools."""
    admin_tools = tool_registry.get_tools_for_role("Admin_User")
    admin_tool_names = [tool.name for tool in admin_tools]
    
    # Admin should have Admin-specific tools
    assert "list_pending_gate_passes" in admin_tool_names
    assert "get_gate_pass_by_number" in admin_tool_names
    assert "approve_gate_pass" in admin_tool_names
    assert "reject_gate_pass" in admin_tool_names
    assert "delete_gate_pass" in admin_tool_names
    assert "list_all_gate_passes_admin" in admin_tool_names
    assert "print_gate_pass_admin" in admin_tool_names
    
    # Admin should have Admin notifications
    assert "get_admin_notifications" in admin_tool_names
    
    # Admin should have shared tools
    assert "mark_notification_read" in admin_tool_names
    assert "get_qr_code" in admin_tool_names
    
    # Admin should NOT have HR-specific tools
    assert "create_gate_pass" not in admin_tool_names
    assert "get_hr_notifications" not in admin_tool_names
    
    # Admin should NOT have Gate-specific tools
    assert "scan_exit" not in admin_tool_names
    assert "scan_return" not in admin_tool_names


def test_get_tools_for_gate_user(tool_registry):
    """Test that Gate_User gets only Gate tools and shared tools."""
    gate_tools = tool_registry.get_tools_for_role("Gate_User")
    gate_tool_names = [tool.name for tool in gate_tools]
    
    # Gate should have Gate-specific tools
    assert "scan_exit" in gate_tool_names
    assert "scan_return" in gate_tool_names
    assert "get_gate_pass_by_number_gate" in gate_tool_names
    assert "get_gate_pass_by_id_gate" in gate_tool_names
    assert "get_gate_pass_photos" in gate_tool_names
    
    # Gate should have shared tools (QR code)
    assert "get_qr_code" in gate_tool_names
    
    # Gate should NOT have HR-specific tools
    assert "create_gate_pass" not in gate_tool_names
    assert "get_hr_notifications" not in gate_tool_names
    
    # Gate should NOT have Admin-specific tools
    assert "approve_gate_pass" not in gate_tool_names
    assert "get_admin_notifications" not in gate_tool_names
    
    # Gate should NOT have notification tools (Gate users don't have notifications)
    assert "mark_notification_read" not in gate_tool_names


def test_get_tool_by_name(tool_registry):
    """Test retrieving a specific tool by name."""
    # Test retrieving an existing tool
    create_tool = tool_registry.get_tool("create_gate_pass")
    assert create_tool is not None
    assert create_tool.name == "create_gate_pass"
    assert create_tool.required_role == "HR_User"
    
    # Test retrieving a non-existent tool
    non_existent = tool_registry.get_tool("non_existent_tool")
    assert non_existent is None


def test_tool_has_required_attributes(tool_registry):
    """Test that all tools have required attributes."""
    all_tools = tool_registry.get_all_tools()
    
    for tool_name, tool in all_tools.items():
        # Verify required attributes exist
        assert hasattr(tool, 'name'), f"Tool {tool_name} missing 'name' attribute"
        assert hasattr(tool, 'description'), f"Tool {tool_name} missing 'description' attribute"
        assert hasattr(tool, 'parameters'), f"Tool {tool_name} missing 'parameters' attribute"
        assert hasattr(tool, 'required_role'), f"Tool {tool_name} missing 'required_role' attribute"
        assert hasattr(tool, 'api_endpoint'), f"Tool {tool_name} missing 'api_endpoint' attribute"
        assert hasattr(tool, 'http_method'), f"Tool {tool_name} missing 'http_method' attribute"
        
        # Verify attribute values are not None
        assert tool.name is not None and len(tool.name) > 0
        assert tool.description is not None and len(tool.description) > 0
        assert tool.parameters is not None
        assert tool.required_role is not None
        assert tool.api_endpoint is not None
        assert tool.http_method in ['GET', 'POST']


def test_tool_parameters_schema(tool_registry):
    """Test that all tools have valid parameter schemas."""
    all_tools = tool_registry.get_all_tools()
    
    for tool_name, tool in all_tools.items():
        params = tool.parameters
        
        # Verify parameters is a dictionary
        assert isinstance(params, dict), f"Tool {tool_name} parameters should be a dict"
        
        # Verify it has the required JSON Schema structure
        assert 'type' in params, f"Tool {tool_name} parameters missing 'type'"
        assert params['type'] == 'object', f"Tool {tool_name} parameters type should be 'object'"
        assert 'properties' in params, f"Tool {tool_name} parameters missing 'properties'"
        assert 'required' in params, f"Tool {tool_name} parameters missing 'required'"
        
        # Verify required is a list
        assert isinstance(params['required'], list), f"Tool {tool_name} required should be a list"


def test_role_based_filtering_completeness(tool_registry):
    """Test that role-based filtering is complete and correct."""
    # Get all tools
    all_tools = tool_registry.get_all_tools()
    
    # Get tools for each role
    hr_tools = set(tool.name for tool in tool_registry.get_tools_for_role("HR_User"))
    admin_tools = set(tool.name for tool in tool_registry.get_tools_for_role("Admin_User"))
    gate_tools = set(tool.name for tool in tool_registry.get_tools_for_role("Gate_User"))
    
    # Verify that each tool is accessible by at least one role
    for tool_name, tool in all_tools.items():
        accessible = tool_name in hr_tools or tool_name in admin_tools or tool_name in gate_tools
        assert accessible, f"Tool {tool_name} is not accessible by any role"
    
    # Verify that shared tools (All role) are accessible by all roles
    qr_tool = tool_registry.get_tool("get_qr_code")
    assert qr_tool.required_role == "All"
    assert "get_qr_code" in hr_tools
    assert "get_qr_code" in admin_tools
    assert "get_qr_code" in gate_tools
    
    # Verify that multi-role tools are accessible by specified roles
    mark_notif_tool = tool_registry.get_tool("mark_notification_read")
    assert isinstance(mark_notif_tool.required_role, list)
    assert "Admin_User" in mark_notif_tool.required_role
    assert "HR_User" in mark_notif_tool.required_role
    assert "mark_notification_read" in hr_tools
    assert "mark_notification_read" in admin_tools
    assert "mark_notification_read" not in gate_tools


def test_check_authorization_hr_user_authorized(tool_registry):
    """Test that HR_User is authorized for HR tools."""
    # HR user should be authorized for HR-specific tools
    is_authorized, error = tool_registry.check_authorization("create_gate_pass", "HR_User")
    assert is_authorized is True
    assert error is None
    
    is_authorized, error = tool_registry.check_authorization("list_gate_passes", "HR_User")
    assert is_authorized is True
    assert error is None


def test_check_authorization_hr_user_unauthorized(tool_registry):
    """Test that HR_User is not authorized for Admin or Gate tools."""
    # HR user should NOT be authorized for Admin tools
    is_authorized, error = tool_registry.check_authorization("approve_gate_pass", "HR_User")
    assert is_authorized is False
    assert error is not None
    assert "Access denied" in error
    assert "approve_gate_pass" in error
    assert "Admin_User" in error
    
    # HR user should NOT be authorized for Gate tools
    is_authorized, error = tool_registry.check_authorization("scan_exit", "HR_User")
    assert is_authorized is False
    assert error is not None
    assert "Access denied" in error
    assert "scan_exit" in error
    assert "Gate_User" in error


def test_check_authorization_admin_user_authorized(tool_registry):
    """Test that Admin_User is authorized for Admin tools."""
    # Admin user should be authorized for Admin-specific tools
    is_authorized, error = tool_registry.check_authorization("approve_gate_pass", "Admin_User")
    assert is_authorized is True
    assert error is None
    
    is_authorized, error = tool_registry.check_authorization("reject_gate_pass", "Admin_User")
    assert is_authorized is True
    assert error is None


def test_check_authorization_admin_user_unauthorized(tool_registry):
    """Test that Admin_User is not authorized for HR or Gate tools."""
    # Admin user should NOT be authorized for HR tools
    is_authorized, error = tool_registry.check_authorization("create_gate_pass", "Admin_User")
    assert is_authorized is False
    assert error is not None
    assert "Access denied" in error
    assert "create_gate_pass" in error
    assert "HR_User" in error
    
    # Admin user should NOT be authorized for Gate tools
    is_authorized, error = tool_registry.check_authorization("scan_exit", "Admin_User")
    assert is_authorized is False
    assert error is not None
    assert "Access denied" in error


def test_check_authorization_gate_user_authorized(tool_registry):
    """Test that Gate_User is authorized for Gate tools."""
    # Gate user should be authorized for Gate-specific tools
    is_authorized, error = tool_registry.check_authorization("scan_exit", "Gate_User")
    assert is_authorized is True
    assert error is None
    
    is_authorized, error = tool_registry.check_authorization("scan_return", "Gate_User")
    assert is_authorized is True
    assert error is None


def test_check_authorization_gate_user_unauthorized(tool_registry):
    """Test that Gate_User is not authorized for HR or Admin tools."""
    # Gate user should NOT be authorized for HR tools
    is_authorized, error = tool_registry.check_authorization("create_gate_pass", "Gate_User")
    assert is_authorized is False
    assert error is not None
    assert "Access denied" in error
    
    # Gate user should NOT be authorized for Admin tools
    is_authorized, error = tool_registry.check_authorization("approve_gate_pass", "Gate_User")
    assert is_authorized is False
    assert error is not None
    assert "Access denied" in error


def test_check_authorization_all_roles_tool(tool_registry):
    """Test that tools with 'All' role are authorized for all users."""
    # QR code tool should be accessible by all roles
    is_authorized, error = tool_registry.check_authorization("get_qr_code", "HR_User")
    assert is_authorized is True
    assert error is None
    
    is_authorized, error = tool_registry.check_authorization("get_qr_code", "Admin_User")
    assert is_authorized is True
    assert error is None
    
    is_authorized, error = tool_registry.check_authorization("get_qr_code", "Gate_User")
    assert is_authorized is True
    assert error is None


def test_check_authorization_multi_role_tool(tool_registry):
    """Test that tools with multiple roles are authorized for specified roles."""
    # mark_notification_read should be accessible by HR and Admin, but not Gate
    is_authorized, error = tool_registry.check_authorization("mark_notification_read", "HR_User")
    assert is_authorized is True
    assert error is None
    
    is_authorized, error = tool_registry.check_authorization("mark_notification_read", "Admin_User")
    assert is_authorized is True
    assert error is None
    
    is_authorized, error = tool_registry.check_authorization("mark_notification_read", "Gate_User")
    assert is_authorized is False
    assert error is not None
    assert "Access denied" in error
    assert "Admin_User" in error and "HR_User" in error


def test_check_authorization_nonexistent_tool(tool_registry):
    """Test that authorization check fails for non-existent tools."""
    is_authorized, error = tool_registry.check_authorization("nonexistent_tool", "HR_User")
    assert is_authorized is False
    assert error is not None
    assert "not found" in error
    assert "nonexistent_tool" in error


def test_check_authorization_blocks_before_api_call(tool_registry):
    """Test that authorization check happens before any API call."""
    # This test verifies that check_authorization doesn't make API calls
    # by checking that it only examines tool metadata
    
    # Attempt to authorize an HR user for an Admin tool
    is_authorized, error = tool_registry.check_authorization("approve_gate_pass", "HR_User")
    
    # Should be blocked immediately without any API interaction
    assert is_authorized is False
    assert error is not None
    
    # The error should be about authorization, not about API failures
    assert "Access denied" in error
    assert "requires role" in error
