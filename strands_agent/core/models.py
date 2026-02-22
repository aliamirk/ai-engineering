"""Data models for Gate Pass AI Agent."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class GatePass:
    """Gate pass data model representing a digital authorization document."""
    
    id: str
    pass_number: str  # Format: GP-YYYY-NNNN
    person_name: str
    description: str
    is_returnable: bool
    status: str  # pending, approved, rejected, exited, returned
    created_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    exit_time: Optional[datetime] = None
    return_time: Optional[datetime] = None
    qr_code_url: Optional[str] = None


@dataclass
class Notification:
    """Notification data model for gate pass events."""
    
    id: str
    message: str
    type: str
    created_at: datetime
    is_read: bool
    related_pass_id: Optional[str] = None


@dataclass
class APIResponse:
    """Structured API response object."""
    
    success: bool
    status_code: int
    data: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class ConversationContext:
    """Conversation context for maintaining state across interactions."""
    
    current_pass_number: Optional[str] = None
    current_pass_id: Optional[str] = None
    last_operation: Optional[str] = None
    pending_parameters: Dict[str, Any] = field(default_factory=dict)
