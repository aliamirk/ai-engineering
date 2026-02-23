"""
Unit tests for ConversationMemory class.
"""

import pytest
from core.conversation_memory import ConversationMemory


class TestConversationMemoryInit:
    """Tests for ConversationMemory initialization."""
    
    def test_init_creates_empty_context(self):
        """Test that __init__ initializes empty context."""
        memory = ConversationMemory()
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] is None
        assert current_pass["pass_id"] is None
    
    def test_init_creates_independent_instances(self):
        """Test that multiple instances have independent contexts."""
        memory1 = ConversationMemory()
        memory2 = ConversationMemory()
        
        memory1.store_pass_reference(pass_number="GP-2024-0001")
        
        # memory2 should not be affected
        current_pass = memory2.get_current_pass()
        assert current_pass["pass_number"] is None


class TestStorePassReference:
    """Tests for store_pass_reference method."""
    
    def test_store_pass_number_only(self):
        """Test storing only pass_number."""
        memory = ConversationMemory()
        memory.store_pass_reference(pass_number="GP-2024-0001")
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0001"
        assert current_pass["pass_id"] is None
    
    def test_store_pass_id_only(self):
        """Test storing only pass_id."""
        memory = ConversationMemory()
        memory.store_pass_reference(pass_id="abc123")
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] is None
        assert current_pass["pass_id"] == "abc123"
    
    def test_store_both_pass_number_and_id(self):
        """Test storing both pass_number and pass_id."""
        memory = ConversationMemory()
        memory.store_pass_reference(
            pass_number="GP-2024-0001",
            pass_id="abc123"
        )
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0001"
        assert current_pass["pass_id"] == "abc123"
    
    def test_store_updates_existing_pass_number(self):
        """Test that storing a new pass_number updates the existing one."""
        memory = ConversationMemory()
        memory.store_pass_reference(pass_number="GP-2024-0001")
        memory.store_pass_reference(pass_number="GP-2024-0002")
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0002"
    
    def test_store_updates_existing_pass_id(self):
        """Test that storing a new pass_id updates the existing one."""
        memory = ConversationMemory()
        memory.store_pass_reference(pass_id="abc123")
        memory.store_pass_reference(pass_id="def456")
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_id"] == "def456"
    
    def test_store_pass_number_preserves_pass_id(self):
        """Test that storing pass_number doesn't clear pass_id."""
        memory = ConversationMemory()
        memory.store_pass_reference(pass_id="abc123")
        memory.store_pass_reference(pass_number="GP-2024-0001")
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0001"
        assert current_pass["pass_id"] == "abc123"
    
    def test_store_pass_id_preserves_pass_number(self):
        """Test that storing pass_id doesn't clear pass_number."""
        memory = ConversationMemory()
        memory.store_pass_reference(pass_number="GP-2024-0001")
        memory.store_pass_reference(pass_id="abc123")
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0001"
        assert current_pass["pass_id"] == "abc123"
    
    def test_store_with_no_arguments(self):
        """Test that calling store_pass_reference with no arguments does nothing."""
        memory = ConversationMemory()
        memory.store_pass_reference(pass_number="GP-2024-0001")
        memory.store_pass_reference()
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0001"


class TestGetCurrentPass:
    """Tests for get_current_pass method."""
    
    def test_get_current_pass_returns_dict(self):
        """Test that get_current_pass returns a dictionary."""
        memory = ConversationMemory()
        current_pass = memory.get_current_pass()
        
        assert isinstance(current_pass, dict)
        assert "pass_number" in current_pass
        assert "pass_id" in current_pass
    
    def test_get_current_pass_empty_context(self):
        """Test retrieving pass info from empty context."""
        memory = ConversationMemory()
        current_pass = memory.get_current_pass()
        
        assert current_pass["pass_number"] is None
        assert current_pass["pass_id"] is None
    
    def test_get_current_pass_with_stored_data(self):
        """Test retrieving stored pass information."""
        memory = ConversationMemory()
        memory.store_pass_reference(
            pass_number="GP-2024-0001",
            pass_id="abc123"
        )
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0001"
        assert current_pass["pass_id"] == "abc123"


class TestUpdateContext:
    """Tests for update_context method."""
    
    def test_update_last_operation_only(self):
        """Test updating only last_operation."""
        memory = ConversationMemory()
        memory.update_context(last_operation="create_gate_pass")
        
        # Verify by checking internal state through clear and re-init
        assert memory._context.last_operation == "create_gate_pass"
    
    def test_update_pending_parameters_only(self):
        """Test updating only pending_parameters."""
        memory = ConversationMemory()
        params = {"person_name": "John Doe"}
        memory.update_context(pending_parameters=params)
        
        assert memory._context.pending_parameters == params
    
    def test_update_both_operation_and_parameters(self):
        """Test updating both last_operation and pending_parameters."""
        memory = ConversationMemory()
        params = {"person_name": "John Doe", "description": "Meeting"}
        memory.update_context(
            last_operation="create_gate_pass",
            pending_parameters=params
        )
        
        assert memory._context.last_operation == "create_gate_pass"
        assert memory._context.pending_parameters == params
    
    def test_update_replaces_existing_operation(self):
        """Test that updating operation replaces the existing one."""
        memory = ConversationMemory()
        memory.update_context(last_operation="create_gate_pass")
        memory.update_context(last_operation="approve_gate_pass")
        
        assert memory._context.last_operation == "approve_gate_pass"
    
    def test_update_replaces_existing_parameters(self):
        """Test that updating parameters replaces the existing ones."""
        memory = ConversationMemory()
        memory.update_context(pending_parameters={"key1": "value1"})
        memory.update_context(pending_parameters={"key2": "value2"})
        
        assert memory._context.pending_parameters == {"key2": "value2"}
    
    def test_update_with_no_arguments(self):
        """Test that calling update_context with no arguments does nothing."""
        memory = ConversationMemory()
        memory.update_context(last_operation="create_gate_pass")
        memory.update_context()
        
        assert memory._context.last_operation == "create_gate_pass"
    
    def test_update_with_empty_dict(self):
        """Test updating with empty dictionary."""
        memory = ConversationMemory()
        memory.update_context(pending_parameters={})
        
        assert memory._context.pending_parameters == {}


class TestClear:
    """Tests for clear method."""
    
    def test_clear_resets_pass_references(self):
        """Test that clear resets pass_number and pass_id."""
        memory = ConversationMemory()
        memory.store_pass_reference(
            pass_number="GP-2024-0001",
            pass_id="abc123"
        )
        memory.clear()
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] is None
        assert current_pass["pass_id"] is None
    
    def test_clear_resets_operation_and_parameters(self):
        """Test that clear resets last_operation and pending_parameters."""
        memory = ConversationMemory()
        memory.update_context(
            last_operation="create_gate_pass",
            pending_parameters={"key": "value"}
        )
        memory.clear()
        
        assert memory._context.last_operation is None
        assert memory._context.pending_parameters == {}
    
    def test_clear_resets_all_context(self):
        """Test that clear resets entire context."""
        memory = ConversationMemory()
        memory.store_pass_reference(
            pass_number="GP-2024-0001",
            pass_id="abc123"
        )
        memory.update_context(
            last_operation="create_gate_pass",
            pending_parameters={"person_name": "John Doe"}
        )
        memory.clear()
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] is None
        assert current_pass["pass_id"] is None
        assert memory._context.last_operation is None
        assert memory._context.pending_parameters == {}
    
    def test_clear_on_empty_context(self):
        """Test that clear works on already empty context."""
        memory = ConversationMemory()
        memory.clear()
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] is None
        assert current_pass["pass_id"] is None
    
    def test_clear_allows_new_data_after_reset(self):
        """Test that new data can be stored after clear."""
        memory = ConversationMemory()
        memory.store_pass_reference(pass_number="GP-2024-0001")
        memory.clear()
        memory.store_pass_reference(pass_number="GP-2024-0002")
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0002"


class TestConversationMemoryIntegration:
    """Integration tests for ConversationMemory."""
    
    def test_typical_conversation_flow(self):
        """Test a typical conversation flow with multiple operations."""
        memory = ConversationMemory()
        
        # User creates a gate pass
        memory.update_context(last_operation="create_gate_pass")
        memory.store_pass_reference(
            pass_number="GP-2024-0001",
            pass_id="abc123"
        )
        
        # User asks about the same pass
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0001"
        
        # User performs another operation on the same pass
        memory.update_context(last_operation="print_gate_pass")
        
        # Pass reference should still be available
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0001"
    
    def test_switching_between_passes(self):
        """Test switching context between different gate passes."""
        memory = ConversationMemory()
        
        # Work with first pass
        memory.store_pass_reference(pass_number="GP-2024-0001")
        memory.update_context(last_operation="create_gate_pass")
        
        # Switch to second pass
        memory.store_pass_reference(pass_number="GP-2024-0002")
        memory.update_context(last_operation="approve_gate_pass")
        
        # Should have second pass in context
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0002"
        assert memory._context.last_operation == "approve_gate_pass"
    
    def test_session_reset_scenario(self):
        """Test resetting context for a new session."""
        memory = ConversationMemory()
        
        # Simulate a complete session
        memory.store_pass_reference(pass_number="GP-2024-0001")
        memory.update_context(
            last_operation="create_gate_pass",
            pending_parameters={"status": "pending"}
        )
        
        # Reset for new session
        memory.clear()
        
        # Start new session
        memory.store_pass_reference(pass_number="GP-2024-0002")
        memory.update_context(last_operation="list_gate_passes")
        
        current_pass = memory.get_current_pass()
        assert current_pass["pass_number"] == "GP-2024-0002"
        assert memory._context.last_operation == "list_gate_passes"
        assert memory._context.pending_parameters == {}
