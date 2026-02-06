from ghostdesk.skills.base import BaseSkill, SkillResult
from ghostdesk.skills.desktop import DesktopSkill
from ghostdesk.skills.system import SystemSkill
from ghostdesk.skills.briefing import DailyBriefingSkill
from ghostdesk.skills.voice import VoiceSkill
from ghostdesk.skills.canvas import CanvasSkill
from ghostdesk.skills.browser import BrowserSkill
from ghostdesk.skills.terminal import TerminalSkill
from ghostdesk.skills.filesystem import FileSkill
from .types import Step
from .permissions import PermissionManager
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SkillEngine:
    """
    Orchestrates the execution of skills.
    Replaces the monolithic ActionAgent.
    """
    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {}
        self.action_map: Dict[str, BaseSkill] = {}
        self.permission_mgr = PermissionManager.get_instance()
        
        # Register default skills
        self.register_skill(DesktopSkill())
        self.register_skill(SystemSkill())
        self.register_skill(DailyBriefingSkill())
        self.register_skill(VoiceSkill())
        self.register_skill(CanvasSkill())
        self.register_skill(BrowserSkill())
        self.register_skill(TerminalSkill())
        self.register_skill(FileSkill())

    def register_skill(self, skill: BaseSkill):
        self.skills[skill.name] = skill
        for action in skill.actions:
            self.action_map[action] = skill
        logger.info(f"Registered Skill: {skill.name} handles {skill.actions}")

    def execute_step(self, step: Step, context: Any = None) -> SkillResult:
        action_type = step.action_type.upper()
        
        skill = self.action_map.get(action_type)
        if not skill:
            return SkillResult(success=False, message=f"No skill registered for action: {action_type}")

        # Permission Check
        params = step.value
        allowed = self.permission_mgr.check_permission(action_type, params)
        
        if not allowed:
            # For Phase 1 PoC, we just fail. Phase 2 (Gateway) will handle "Request Approval".
            return SkillResult(success=False, message=f"PERMISSION DENIED: {action_type} for {params} requires approval.")
            
        # Execute
        return skill.execute(action_type, params, context)
