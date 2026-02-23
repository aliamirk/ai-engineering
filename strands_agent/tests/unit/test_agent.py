"""Unit tests for GatePassAgent."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import HumanMessage
from strands_agent.core.agent import GatePassAgent
from strands_agent.core.models import APIResponse


class TestGatePassAgentInitialization:
    """Test GatePassAgent initialization."""
    
    def test_init_with_valid_hr_role(self):
        """Test agent initialization with HR_User role."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        assert agent.user_role == "HR_User"
        assert agent.api_client is not None
        assert agent.tool_registry is not None
        assert agent.conversation_memory is not None
        assert agent.llm is not None
        assert agent.tools is not None
    
    def test_init_with_valid_admin_role(self):
        """Test agent initialization with Admin_User role."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="Admin_User"
        )
        
        assert agent.user_role == "Admin_User"
        assert agent.api_client is not None
        assert agent.tool_registry is not None
        assert agent.conversation_memory is not None
        assert agent.llm is not None
        assert agent.tools is not None
    
    def test_init_with_valid_gate_role(self):
        """Test agent initialization with Gate_User role."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="Gate_User"
        )
        
        assert agent.user_role == "Gate_User"
        assert agent.api_client is not None
        assert agent.tool_registry is not None
        assert agent.conversation_memory is not None
        assert agent.llm is not None
        assert agent.tools is not None
    
    def test_init_with_invalid_role(self):
        """Test agent initialization with invalid role raises ValueError."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        with pytest.raises(ValueError) as exc_info:
            GatePassAgent(
                api_base_url="http://localhost:8000",
                llm=mock_llm,
                user_role="InvalidRole"
            )
        
        assert "Invalid user_role" in str(exc_info.value)
        assert "InvalidRole" in str(exc_info.value)
    
    def test_api_client_initialized_with_base_url(self):
        """Test that API client is initialized with correct base URL."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        assert agent.api_client.base_url == "http://localhost:8000"
    
    def test_tool_registry_filters_by_role(self):
        """Test that tool registry filters tools based on user role."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        # Create HR agent
        hr_agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Get HR tools
        hr_tools = hr_agent.tool_registry.get_tools_for_role("HR_User")
        hr_tool_names = [tool.name for tool in hr_tools]
        
        # Verify HR tools are present
        assert "create_gate_pass" in hr_tool_names
        assert "list_gate_passes" in hr_tool_names
        
        # Verify Admin-only tools are not present
        assert "approve_gate_pass" not in hr_tool_names
        assert "reject_gate_pass" not in hr_tool_names
    
    def test_conversation_memory_initialized(self):
        """Test that conversation memory is initialized."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Verify conversation memory is initialized
        assert agent.conversation_memory is not None
        
        # Verify it starts with empty context
        current_pass = agent.conversation_memory.get_current_pass()
        assert current_pass["pass_number"] is None
        assert current_pass["pass_id"] is None


class TestGatePassAgentMethods:
    """Test GatePassAgent methods."""
    
    def test_reset_context_clears_memory(self):
        """Test that reset_context clears both conversation and chat history."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Store some context
        agent.conversation_memory.store_pass_reference(
            pass_number="GP-2024-0001",
            pass_id="123"
        )
        
        # Add some chat history
        agent.chat_history.append(HumanMessage(content="Test message"))
        
        # Verify context is stored
        current_pass = agent.conversation_memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0001"
        assert current_pass["pass_id"] == "123"
        assert len(agent.chat_history) > 0
        
        # Reset context
        agent.reset_context()
        
        # Verify context is cleared
        current_pass = agent.conversation_memory.get_current_pass()
        assert current_pass["pass_number"] is None
        assert current_pass["pass_id"] is None
        assert len(agent.chat_history) == 0
    
    def test_chat_handles_exceptions_gracefully(self):
        """Test that chat method handles exceptions gracefully."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        mock_llm.invoke = Mock(side_effect=Exception("Test error"))
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Call chat and verify it returns error message instead of crashing
        response = agent.chat("Create a gate pass")
        
        assert "error" in response.lower()
        assert "Test error" in response
    
    def test_system_prompt_includes_role(self):
        """Test that system prompt includes user role information."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        system_prompt = agent._get_system_prompt()
        
        assert "HR_User" in system_prompt
        assert "Create new gate passes" in system_prompt
    
    def test_system_prompt_different_for_each_role(self):
        """Test that system prompt is different for each role."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        hr_agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        admin_agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="Admin_User"
        )
        
        gate_agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="Gate_User"
        )
        
        hr_prompt = hr_agent._get_system_prompt()
        admin_prompt = admin_agent._get_system_prompt()
        gate_prompt = gate_agent._get_system_prompt()
        
        # Verify each prompt is unique
        assert hr_prompt != admin_prompt
        assert admin_prompt != gate_prompt
        assert hr_prompt != gate_prompt
        
        # Verify role-specific content
        assert "Create new gate passes" in hr_prompt
        assert "Approve or reject" in admin_prompt
        assert "Scan people exiting" in gate_prompt


class TestGatePassAgentIntegration:
    """Integration tests for GatePassAgent with requirements validation."""
    
    def test_agent_initializes_with_api_client_tool_registry_and_memory(self):
        """Validates Requirements 6.1, 8.1, 12.1, 12.2, 12.3.
        
        Test that agent initializes with all required components:
        - API client for making requests
        - Tool registry for managing tools
        - Conversation memory for context
        - Filtered tools based on user role
        """
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Verify API client is initialized (Requirement 12.1)
        assert agent.api_client is not None
        assert isinstance(agent.api_client.base_url, str)
        
        # Verify tool registry is initialized (Requirement 12.2)
        assert agent.tool_registry is not None
        
        # Verify conversation memory is initialized (Requirement 12.3)
        assert agent.conversation_memory is not None
        
        # Verify tools are filtered by role (Requirement 8.1)
        hr_tools = agent.tool_registry.get_tools_for_role("HR_User")
        assert len(hr_tools) > 0
        
        # Verify LangChain integration is created (Requirement 6.1)
        assert agent.llm is not None
        assert agent.tools is not None
    
    def test_agent_filters_tools_by_role_during_initialization(self):
        """Validates Requirement 8.1.
        
        Test that agent only has access to tools authorized for its role.
        """
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        # Test HR role
        hr_agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        hr_tools = hr_agent.tool_registry.get_tools_for_role("HR_User")
        hr_tool_names = [tool.name for tool in hr_tools]
        
        # HR should have create_gate_pass
        assert "create_gate_pass" in hr_tool_names
        
        # HR should NOT have approve_gate_pass (Admin only)
        assert "approve_gate_pass" not in hr_tool_names
        
        # Test Admin role
        admin_agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="Admin_User"
        )
        
        admin_tools = admin_agent.tool_registry.get_tools_for_role("Admin_User")
        admin_tool_names = [tool.name for tool in admin_tools]
        
        # Admin should have approve_gate_pass
        assert "approve_gate_pass" in admin_tool_names
        
        # Admin should NOT have create_gate_pass (HR only)
        assert "create_gate_pass" not in admin_tool_names
