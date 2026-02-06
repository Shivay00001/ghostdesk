import logging
import subprocess
from typing import List, Any
from .base import BaseSkill, SkillResult
from ..core.permissions import PermissionManager

logger = logging.getLogger(__name__)

class TerminalSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="Terminal",
            description="Executes shell commands on the host machine"
        )

    @property
    def actions(self) -> List[str]:
        return ["RUN_SHELL"]

    def execute(self, action: str, params: Any, context: Any = None) -> SkillResult:
        if action == "RUN_SHELL":
            command = str(params)
            try:
                # Capture output
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                output = result.stdout.strip()
                error = result.stderr.strip()
                
                msg = f"Output:\n{output}"
                if error:
                    msg += f"\nErrors:\n{error}"
                    
                return SkillResult(success=result.returncode == 0, message=msg)
            except Exception as e:
                return SkillResult(success=False, message=str(e))
                
        return SkillResult(success=False, message=f"Action {action} not supported")
