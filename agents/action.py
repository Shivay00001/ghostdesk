import time
import logging
import pyautogui
import subprocess
from typing import Any
from ..core.types import Step, AgentResult
from .skeletons import BaseAgent

logger = logging.getLogger(__name__)

# SAFETY: Slam mouse to corner to abort
pyautogui.FAILSAFE = True

class ActionAgent(BaseAgent):
    def __init__(self):
        super().__init__("Action")

    def execute(self, step: Step, context: Any) -> AgentResult:
        """
        Executes a single step.
        Context usually contains {"x": 123, "y": 456} from VisionAgent.
        """
        try:
            action = step.action_type.upper()
            
            if action == "OPEN_APP":
                return self._open_app(step.value)
            
            elif action == "CLICK":
                if not context or "x" not in context:
                    return AgentResult(success=False, message="Missing coordinates for CLICK")
                return self._click(context["x"], context["y"])
            
            elif action == "TYPE":
                return self._type_text(step.value)
            
            elif action == "PRESS":
                return self._press_key(step.value)
            
            elif action == "WAIT":
                time.sleep(float(step.value or 1.0))
                return AgentResult(success=True, message="Waited")

            else:
                return AgentResult(success=False, message=f"Unknown Action: {action}")

        except pyautogui.FailSafeException:
            logger.critical("FAILSAFE TRIGGERED! User aborted action.")
            return AgentResult(success=False, message="FAILSAFE ABORT")
        except Exception as e:
            logger.error(f"Action Error: {e}")
            return AgentResult(success=False, message=str(e))

    def _open_app(self, app_name: str) -> AgentResult:
        logger.info(f"Opening App: {app_name}")
        # Method 1: PyAutoGUI Win+R (More visual, generic)
        pyautogui.hotkey('win', 'r')
        time.sleep(0.5)
        pyautogui.write(app_name)
        pyautogui.press('enter')
        time.sleep(2.0) # Wait for launch
        return AgentResult(success=True, message=f"Launched {app_name}")

    def _click(self, x: int, y: int) -> AgentResult:
        logger.info(f"Clicking at {x}, {y}")
        pyautogui.moveTo(x, y, duration=0.5) # Human-like movement
        pyautogui.click()
        return AgentResult(success=True, message=f"Clicked {x},{y}")

    def _type_text(self, text: str) -> AgentResult:
        logger.info(f"Typing: {text}")
        pyautogui.write(text, interval=0.05) # Human-like typing
        return AgentResult(success=True, message="Typed text")

    def _press_key(self, key: str) -> AgentResult:
        logger.info(f"Pressing: {key}")
        pyautogui.press(key)
        return AgentResult(success=True, message=f"Pressed {key}")
