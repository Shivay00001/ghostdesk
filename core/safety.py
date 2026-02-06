import logging
from typing import List
from .types import Step

logger = logging.getLogger(__name__)

ALLOWED_ACTION_TYPES = {
    "OPEN_APP",
    "TYPE",
    "CLICK",
    "READ",
    "PRESS",
    "WAIT",
    "ANSWER"
}

FORBIDDEN_APPS = {
    "cmd.exe",
    "powershell.exe",
    "regedit.exe",
    "bash.exe"
}

class SafetyPolicy:
    @staticmethod
    def validate_plan(plan: List[Step]) -> bool:
        """
        Validates a list of steps against safety rules.
        Returns True if safe, False otherwise.
        """
        for step in plan:
            # 1. Check Action Type
            if step.action_type not in ALLOWED_ACTION_TYPES:
                logger.error(f"Safety Violation: Unknown action type '{step.action_type}'")
                return False

            # 2. Check App Allow/Block List (for OPEN_APP)
            if step.action_type == "OPEN_APP" and step.value:
                app_name = step.value.lower()
                if any(forbidden in app_name for forbidden in FORBIDDEN_APPS):
                    logger.error(f"Safety Violation: Launching forbidden app '{step.value}'")
                    return False
        
        return True
