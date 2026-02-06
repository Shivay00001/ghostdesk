import logging
import pyttsx3
import threading
from typing import List, Any
from .base import BaseSkill, SkillResult

logger = logging.getLogger(__name__)

class VoiceSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="Voice",
            description="Text-to-Speech capabilities using local engine"
        )
        # Initialize engine in a way that doesn't block (threading issues with comtypes on Windows sometimes)
        # Ideally, TTS should run in its own thread loop or process.
        # For PoC, we initialize on demand or keep a global reference carefully.
        self.engine = None 

    @property
    def actions(self) -> List[str]:
        return ["SPEAK"]

    def _speak_thread(self, text: str):
        try:
            # Re-init engine per thread to avoid COM limits on Windows
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS Error: {e}")

    def execute(self, action: str, params: Any, context: Any = None) -> SkillResult:
        if action == "SPEAK":
            text = str(params)
            # Run in thread to not block the brain
            t = threading.Thread(target=self._speak_thread, args=(text,))
            t.start()
            return SkillResult(success=True, message=f"Speaking: {text[:20]}...")
            
        return SkillResult(success=False, message=f"Action {action} not supported")
