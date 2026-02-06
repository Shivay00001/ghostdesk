import logging
import subprocess
import platform
import pyautogui
from typing import List, Any
from .base import BaseSkill, SkillResult

logger = logging.getLogger(__name__)

class SystemSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="SystemControl",
            description="OS level operations like opening apps"
        )

    @property
    def actions(self) -> List[str]:
        return ["OPEN_APP"]

    def execute(self, action: str, params: Any, context: Any = None) -> SkillResult:
        try:
            if action == "OPEN_APP":
                app_name = str(params)
                # Method 1: Win+R (Universalish)
                pyautogui.hotkey('win', 'r')
                pyautogui.sleep(0.5)
                pyautogui.write(app_name)
                pyautogui.press('enter')
                pyautogui.sleep(2.0)
                return SkillResult(success=True, message=f"Launched {app_name}")
            
            return SkillResult(success=False, message=f"Action {action} not supported by SystemSkill")

        except Exception as e:
            return SkillResult(success=False, message=str(e))
