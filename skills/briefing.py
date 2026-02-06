import logging
import platform
import datetime
from typing import List, Any
from .base import BaseSkill, SkillResult
from ..core.memory import MemoryManager

logger = logging.getLogger(__name__)

class DailyBriefingSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="DailyBriefing",
            description="Generates and sends a daily status report"
        )
        self.memory = MemoryManager.get_instance()

    @property
    def actions(self) -> List[str]:
        return ["BRIEFING"]

    def execute(self, action: str, params: Any, context: Any = None) -> SkillResult:
        try:
            # Gather Info
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            sys_info = f"{platform.system()} {platform.release()}"
            
            # Get recent actions count/highlights
            # (Mock for now, would query memory)
            recent_history = self.memory.get_recent_history(limit=5)
            
            briefing = f"""
🌤️ **Daily Briefing**
📅 {now}
💻 System: {sys_info}

**Recent Memory Context:**
"""
            for item in recent_history:
                briefing += f"- {item['role']}: {item['content'][:50]}...\n"

            briefing += "\nReady for your commands, User."
            
            # The result message will be sent back by the Brain
            return SkillResult(success=True, message=briefing)

        except Exception as e:
            return SkillResult(success=False, message=str(e))
