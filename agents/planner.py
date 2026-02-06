import json
import logging
from typing import List
from ..core.types import Step
from ..core.llm import OllamaClient
from .skeletons import BaseAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are the Planner Agent for GhostDesk, a secure desktop automation system.
Your job is to convert a user's natural language request into a sequence of atomic execution steps.

You must reply with VALID JSON ONLY. No markdown, no explanations.

Supported Action Types:
- OPEN_APP (value: app name or path)
- TYPE (value: text to type)
- CLICK (target_element: description of element)
- READ (target_element: description of element)
- PRESS (value: key name like 'enter', 'esc')
- BRIEFING (value: none)
- SPEAK (value: text to speak)
- RENDER_CANVAS (value: none)
- BROWSE_GOTO (value: url)
- BROWSE_READ (value: url)
- RUN_SHELL (value: command)
- FILE_READ (value: path)
- FILE_WRITE (value: path|content)

Example Input: "Open Chrome and search for Cats"
Example Output:
[
  {"description": "Open Google Chrome", "action_type": "OPEN_APP", "value": "chrome.exe"},
  {"description": "Focus search bar", "action_type": "CLICK", "target_element": "Address Bar"},
  {"description": "Type search query", "action_type": "TYPE", "value": "Cats"},
  {"description": "Press Enter", "action_type": "PRESS", "value": "enter"}
]
"""

class PlannerAgent(BaseAgent):
    def __init__(self, model_name: str = "llama3.2"):
        super().__init__("Planner")
        self.llm = OllamaClient()
        self.model = model_name

    def create_plan(self, user_intent: str, context: List[dict] = None) -> List[Step]:
        logger.info(f"Planning task for: {user_intent}")
        
        # Build Context String
        cols = []
        if context:
            cols.append("User Context/History:")
            for item in context:
                cols.append(f"- [{item.get('role', 'unknown')}]: {item.get('content', '')}")
        
        context_str = "\n".join(cols)
        
        full_system_prompt = f"{SYSTEM_PROMPT}\n\n{context_str}"
        
        response = self.llm.generate(
            prompt=user_intent,
            system=full_system_prompt,
            model=self.model
        )

        if not response:
            logger.error("Failed to get plan from Ollama.")
            return []

        try:
            # Clean response if it contains markdown code blocks (even if we asked for JSON)
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]

            data = json.loads(clean_response)
            steps = []
            for item in data:
                steps.append(Step(
                    description=item.get("description", "Unknown Step"),
                    action_type=item.get("action_type", "UNKNOWN"),
                    target_element=item.get("target_element"),
                    value=item.get("value")
                ))
            return steps
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON plan: {response}")
            return []
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return []
