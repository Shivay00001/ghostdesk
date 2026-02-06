from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field

class UserCommand(BaseModel):
    """Normalized command received from an adapter."""
    raw_text: str
    sender_id: str
    platform: str
    timestamp: datetime = Field(default_factory=datetime.now)
    message_id: str

class AgentResult(BaseModel):
    """Standard result format for any agent action."""
    success: bool
    data: Optional[Any] = None
    message: str = ""

class Step(BaseModel):
    """An atomic step in the execution plan."""
    description: str
    action_type: str  # e.g., "CLICK", "TYPE", "READ"
    target_element: Optional[str] = None
    value: Optional[str] = None
