"""Conversation memory management for the Gate Pass AI Agent."""

from typing import Any, Dict, Optional
from .models import ConversationContext


class ConversationMemory:
    """Manages conversation context to enable natural follow-up interactions.
    
    This class stores gate pass references (pass_number, pass_id), tracks the
    last operation, and maintains any pending parameters. The context persists
    during a session and can be cleared on reset.
    
    Attributes:
        _context: The internal conversation context storage
    """
    
    def __init__(self):
        """Initialize empty conversation context."""
        self._context = ConversationContext()
    
    def store_pass_reference(
        self,
        pass_number: Optional[str] = None,
        pass_id: Optional[str] = None
    ) -> None:
        """Save pass_number and pass_id to conversation context.
        
        Args:
            pass_number: The gate pass number (format: GP-YYYY-NNNN)
            pass_id: The gate pass ID
        """
        if pass_number is not None:
            self._context.current_pass_number = pass_number
        if pass_id is not None:
            self._context.current_pass_id = pass_id
    
    def get_current_pass(self) -> Dict[str, Optional[str]]:
        """Retrieve stored pass information.
        
        Returns:
            Dictionary containing current_pass_number and current_pass_id
        """
        return {
            "pass_number": self._context.current_pass_number,
            "pass_id": self._context.current_pass_id
        }
    
    def update_context(
        self,
        last_operation: Optional[str] = None,
        pending_parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update conversation variables.
        
        Args:
            last_operation: The last operation performed
            pending_parameters: Dictionary of parameters being collected
        """
        if last_operation is not None:
            self._context.last_operation = last_operation
        if pending_parameters is not None:
            self._context.pending_parameters = pending_parameters
    
    def clear(self) -> None:
        """Reset conversation context to empty state."""
        self._context = ConversationContext()
