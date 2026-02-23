"""Unit tests for GatePassAgent context management enhancements."""

import pytest
from unittest.mock import Mock, MagicMock
from strands_agent.core.agent import GatePassAgent


class TestAgentContextExtraction:
    """Test context extraction and management in chat method."""
    
    def test_extract_pass_references_from_pass_number(self):
        """Test extraction of pass_number from text."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Test pass_number extraction
        text = "Gate pass GP-2024-0001 has been created successfully."
        result = agent._extract_pass_references(text)
        
        assert result["pass_number"] == "GP-2024-0001"
    
    def test_extract_pass_references_from_json_response(self):
        """Test extraction of pass_id from JSON-like text."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Test pass_id extraction from JSON
        text = '{"id": "abc123", "pass_number": "GP-2024-0001"}'
        result = agent._extract_pass_references(text)
        
        assert result["pass_id"] == "abc123"
        assert result["pass_number"] == "GP-2024-0001"
    
    def test_extract_pass_references_no_matches(self):
        """Test extraction when no pass references are present."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Test with text that has no pass references
        text = "Hello, how can I help you today?"
        result = agent._extract_pass_references(text)
        
        assert result["pass_number"] is None
        assert result["pass_id"] is None
    
    def test_update_context_from_tool_call_with_pass_number(self):
        """Test that context is updated when tool is called with pass_number."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="Admin_User"
        )
        
        # Simulate tool call with pass_number
        tool_name = "approve_gate_pass"
        tool_args = {"pass_number": "GP-2024-0001", "name": "Admin User"}
        result = "Gate pass GP-2024-0001 has been approved."
        
        agent._update_context_from_tool_call(tool_name, tool_args, result)
        
        # Verify context was updated
        current_pass = agent.conversation_memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0001"
    
    def test_update_context_from_tool_call_with_pass_id(self):
        """Test that context is updated when tool is called with pass_id."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Simulate tool call with pass_id
        tool_name = "get_gate_pass_details"
        tool_args = {"pass_id": "abc123"}
        result = '{"id": "abc123", "pass_number": "GP-2024-0001", "person_name": "John Doe"}'
        
        agent._update_context_from_tool_call(tool_name, tool_args, result)
        
        # Verify context was updated with both pass_id and pass_number
        current_pass = agent.conversation_memory.get_current_pass()
        assert current_pass["pass_id"] == "abc123"
        assert current_pass["pass_number"] == "GP-2024-0001"
    
    def test_update_context_stores_last_operation(self):
        """Test that last operation is stored in context."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Simulate tool call
        tool_name = "create_gate_pass"
        tool_args = {"person_name": "John Doe", "description": "Meeting", "is_returnable": True}
        result = "Gate pass GP-2024-0001 created successfully."
        
        agent._update_context_from_tool_call(tool_name, tool_args, result)
        
        # Verify last operation was stored
        assert agent.conversation_memory._context.last_operation == "create_gate_pass"
    
    def test_get_context_info_with_pass_number(self):
        """Test that context info is formatted correctly."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Store pass reference
        agent.conversation_memory.store_pass_reference(pass_number="GP-2024-0001")
        
        # Get context info
        context_info = agent._get_context_info()
        
        assert "GP-2024-0001" in context_info
        assert "Current pass number" in context_info
    
    def test_get_context_info_with_both_references(self):
        """Test context info with both pass_number and pass_id."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Store both references
        agent.conversation_memory.store_pass_reference(
            pass_number="GP-2024-0001",
            pass_id="abc123"
        )
        
        # Get context info
        context_info = agent._get_context_info()
        
        assert "GP-2024-0001" in context_info
        assert "abc123" in context_info
        assert "Current pass number" in context_info
        assert "Current pass ID" in context_info
    
    def test_get_context_info_empty(self):
        """Test context info when no context is stored."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Get context info without storing anything
        context_info = agent._get_context_info()
        
        assert context_info == ""
    
    def test_get_available_tools_returns_tool_names(self):
        """Test that get_available_tools returns list of tool names."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Get available tools
        tools = agent.get_available_tools()
        
        # Verify it returns a list of strings
        assert isinstance(tools, list)
        assert all(isinstance(tool, str) for tool in tools)
        
        # Verify HR tools are present
        assert "create_gate_pass" in tools
        assert "list_gate_passes" in tools
    
    def test_get_available_tools_filtered_by_role(self):
        """Test that get_available_tools only returns tools for the user's role."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        # Create HR agent
        hr_agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        # Create Admin agent
        admin_agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="Admin_User"
        )
        
        hr_tools = hr_agent.get_available_tools()
        admin_tools = admin_agent.get_available_tools()
        
        # Verify HR has create_gate_pass but not approve_gate_pass
        assert "create_gate_pass" in hr_tools
        assert "approve_gate_pass" not in hr_tools
        
        # Verify Admin has approve_gate_pass but not create_gate_pass
        assert "approve_gate_pass" in admin_tools
        assert "create_gate_pass" not in admin_tools


class TestAgentSystemPromptEnhancements:
    """Test enhanced system prompt with parameter extraction guidance."""
    
    def test_system_prompt_includes_parameter_extraction_guidance(self):
        """Test that system prompt includes guidance on parameter extraction."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        system_prompt = agent._get_system_prompt()
        
        # Verify parameter extraction guidance is present
        assert "Extract parameters" in system_prompt
        assert "missing required parameters" in system_prompt.lower()
        assert "clarifying questions" in system_prompt.lower()
    
    def test_system_prompt_includes_context_awareness_guidance(self):
        """Test that system prompt includes guidance on using context."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="Admin_User"
        )
        
        system_prompt = agent._get_system_prompt()
        
        # Verify context awareness guidance is present
        assert "Context Awareness" in system_prompt
        assert "Remember pass numbers" in system_prompt
        assert "stored context" in system_prompt.lower()
    
    def test_system_prompt_includes_required_parameters_for_hr(self):
        """Test that HR system prompt lists required parameters for tools."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="HR_User"
        )
        
        system_prompt = agent._get_system_prompt()
        
        # Verify required parameters are mentioned
        assert "person_name" in system_prompt
        assert "description" in system_prompt
        assert "is_returnable" in system_prompt
        assert "pass_number" in system_prompt
    
    def test_system_prompt_includes_required_parameters_for_admin(self):
        """Test that Admin system prompt lists required parameters for tools."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="Admin_User"
        )
        
        system_prompt = agent._get_system_prompt()
        
        # Verify required parameters are mentioned
        assert "pass_number" in system_prompt
        assert "your name" in system_prompt.lower()
    
    def test_system_prompt_includes_required_parameters_for_gate(self):
        """Test that Gate system prompt lists required parameters for tools."""
        mock_llm = Mock()
        mock_llm.bind_tools = Mock(return_value=mock_llm)
        
        agent = GatePassAgent(
            api_base_url="http://localhost:8000",
            llm=mock_llm,
            user_role="Gate_User"
        )
        
        system_prompt = agent._get_system_prompt()
        
        # Verify required parameters are mentioned
        assert "pass_number" in system_prompt
        assert "photo" in system_prompt
