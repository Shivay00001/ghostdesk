import requests
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.generate_endpoint = f"{base_url}/api/generate"

    def generate(self, prompt: str, model: str = "llama3.2", system: str = "", images: list = None) -> Optional[str]:
        """
        Generates text using the local Ollama instance.
        Supports images for multimodal models (base64 encoded strings).
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json"  # Force JSON output mode if supported by model/Ollama version
        }
        
        if system:
            payload["system"] = system
            
        if images:
            payload["images"] = images

        try:
            response = requests.post(self.generate_endpoint, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama Connection Error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Ollama Invalid Response: {e}")
            return None
