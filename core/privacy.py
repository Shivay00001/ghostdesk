import re
import logging

logger = logging.getLogger(__name__)

class PrivacyScrubber:
    """
    Enterprise Privacy Guard.
    Scans and redacts PII before it leaves the secure perimeter.
    """
    
    # Regex Patterns (Simplified for PoC)
    PATTERNS = {
        "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "PHONE": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US-centric simple
        "IP_ADDR": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        "API_KEY": r'(sk-[a-zA-Z0-9]{32,})', # Basic OpenAI key det
    }

    @staticmethod
    def scrub(text: str) -> str:
        if not text:
            return text
            
        scrubbed = text
        for label, pattern in PrivacyScrubber.PATTERNS.items():
            scrubbed = re.sub(pattern, f"[REDACTED_{label}]", scrubbed)
        
        if scrubbed != text:
            logger.info("PII detected and redacted from outgoing message.")
            
        return scrubbed
