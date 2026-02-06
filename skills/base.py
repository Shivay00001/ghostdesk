from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class SkillResult(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class BaseSkill(ABC):
    """
    Abstract Base Class for all LocalMolt Skills.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @property
    @abstractmethod
    def actions(self) -> List[str]:
        """List of action verbs this skill handles (e.g. ['CLICK', 'TYPE'])"""
        pass

    @abstractmethod
    def execute(self, action: str, params: Any, context: Any = None) -> SkillResult:
        """Execute the skill logic."""
        pass
