import logging
import time
import pyautogui
from typing import List, Any
from .base import BaseSkill, SkillResult

logger = logging.getLogger(__name__)
pyautogui.FAILSAFE = True

class DesktopSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="DesktopControl",
            description="Controls mouse and keyboard via PyAutoGUI"
        )

    @property
    def actions(self) -> List[str]:
        return ["CLICK", "TYPE", "PRESS", "WAIT"]

    def execute(self, action: str, params: Any, context: Any = None) -> SkillResult:
        try:
            if action == "CLICK":
                # Expecting params to be coordinate dict or context to have it?
                # For Phase 1 we assume params might have it or context
                # Re-using the simplified logic:
                x = context.get("x") if context else None
                y = context.get("y") if context else None
                
                if x is None or y is None:
                     return SkillResult(success=False, message="Missing coordinates for CLICK")
                
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
                return SkillResult(success=True, message=f"Clicked {x},{y}")

            elif action == "TYPE":
                text = params if isinstance(params, str) else str(params)
                pyautogui.write(text, interval=0.05)
                return SkillResult(success=True, message=f"Typed: {text}")

            elif action == "PRESS":
                key = params if isinstance(params, str) else str(params)
                pyautogui.press(key)
                return SkillResult(success=True, message=f"Pressed: {key}")

            elif action == "WAIT":
                sec = float(params) if params else 1.0
                time.sleep(sec)
                return SkillResult(success=True, message=f"Waited {sec}s")

            return SkillResult(success=False, message=f"Action {action} not supported by DesktopSkill")

        except pyautogui.FailSafeException:
            return SkillResult(success=False, message="FAILSAFE ABORT TRIGGERED")
        except Exception as e:
            return SkillResult(success=False, message=str(e))
