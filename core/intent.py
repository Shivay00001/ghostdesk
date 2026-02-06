import logging
import json
from typing import Literal
from ..core.llm import OllamaClient

logger = logging.getLogger(__name__)

IntentType = Literal["CHAT", "TASK", "QUERY"]

class IntentParser:
    def __init__(self, model: str = "llama3.2"):
        self.llm = OllamaClient()
        self.model = model

    def parse(self, text: str) -> IntentType:
        """
        Classifies the user input into CHAT, TASK, or QUERY.
        """
        prompt = f"""
        Classify the following message into one of these categories:
        - TASK: Requires performing actions on the computer (e.g. "Open Chrome", "Type hello", "Delete file").
        - QUERY: Requires looking up information from Knowledge Base (e.g. "What is in the policy?", "Summarize this PDF").
        - CHAT: General conversation, greeting, or question about yourself (e.g. "Hi", "Who are you?").
        
        Message: "{text}"
        
        Return ONLY the category name.
        """
        
        response = self.llm.generate(prompt, model=self.model, system="")
        if not response:
            return "CHAT" # Default
            
        cleaned = response.strip().upper()
        if "TASK" in cleaned:
            return "TASK"
        elif "QUERY" in cleaned:
            return "QUERY"
        else:
            return "CHAT"
