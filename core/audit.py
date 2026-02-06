import json
import logging
import time
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)

class AuditLogger:
    _instance = None
    LOG_FILE = "audit_log.jsonl"

    def __init__(self):
        # Ensure log file exists or create it
        if not os.path.exists(self.LOG_FILE):
             with open(self.LOG_FILE, 'w') as f:
                 pass

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AuditLogger()
        return cls._instance

    def log_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """
        Writes a structured JSON log entry.
        """
        entry = {
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event_type": event_type,
            "user_id": user_id,
            "details": details
        }
        
        try:
            with open(self.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def log_action(self, user_id: str, action_type: str, action_value: str, status: str, result: str):
        self.log_event("ACTION_EXECUTION", user_id, {
            "action": action_type,
            "target": action_value,
            "status": status,
            "result": result
        })
