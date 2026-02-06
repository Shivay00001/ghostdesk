import io
import base64
import logging
import pyautogui
from pydantic import BaseModel
from typing import Optional, List
from ..core.types import AgentResult
from ..core.llm import OllamaClient
from .skeletons import BaseAgent

logger = logging.getLogger(__name__)

class ElementCoordinates(BaseModel):
    x: int
    y: int

class VisionAgent(BaseAgent):
    def __init__(self, model: str = "llama3.2-vision"):
        super().__init__("Vision")
        self.llm = OllamaClient()
        self.model = model

    def capture_screen(self) -> str:
        """
        Captures full screen and returns valid file path (temp).
        Also returns base64 string for internal use.
        """
        # For PoC we just return a temp path, but logic needs base64
        # We'll just return "memory" here to signify it's handling it.
        # In a real app we might save it for debugging.
        return "latest_screenshot.png"

    def detect_element(self, screenshot_path_placeholder: str, description: str) -> AgentResult:
        """
        Takes a screenshot, sends to Llama Vision, asks for coordinates.
        """
        try:
            # 1. Capture
            logger.info("Capturing screen...")
            screenshot = pyautogui.screenshot()
            
            # 2. Encode
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # 3. Prompt
            prompt = f"Find the center coordinates of the UI element '{description}'. Return ONLY a JSON array [x, y]. If not found, return empty []."
            
            logger.info(f"Asking {self.model} to find '{description}'...")
            response = self.llm.generate(
                prompt=prompt, 
                model=self.model, 
                images=[img_str]
            )

            # 4. Parse
            import json
            if not response:
                return AgentResult(success=False, message="No response from Vision Model")

            # Cleanup markdown
            clean = response.strip()
            if clean.startswith("```json"): clean = clean[7:]
            if clean.endswith("```"): clean = clean[:-3]
            
            coords = json.loads(clean)
            
            if isinstance(coords, list) and len(coords) == 2:
                # Validate bounds (basic)
                width, height = pyautogui.size()
                x, y = int(coords[0]), int(coords[1])
                
                # Check if reasonable
                if 0 <= x <= width and 0 <= y <= height:
                     return AgentResult(success=True, data={"x": x, "y": y}, message=f"Found at {x},{y}")
                else:
                    return AgentResult(success=False, message=f"Coordinates {x},{y} out of bounds")
            
            return AgentResult(success=False, message="Element not found or invalid format")

        except Exception as e:
            logger.error(f"Vision Error: {e}")
            return AgentResult(success=False, message=str(e))
