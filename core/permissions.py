import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

class PermissionManager:
    _instance = None
    
    # Default Policies
    SAFE_ACTIONS = {"WAIT", "READ", "BRIEFING", "SPEAK", "RENDER_CANVAS", "BROWSE_READ", "BROWSE_GOTO", "FILE_READ"}
    RISKY_ACTIONS = {"CLICK", "TYPE", "PRESS", "FILE_WRITE"}
    DANGEROUS_ACTIONS = {"OPEN_APP", "DELETE_FILE", "RUN_SHELL"}

    def __init__(self):
        # In a real app, load this from config/db
        self.whitelisted_apps = {"notepad", "calculator", "calc", "chrome"}
        self.auto_approve_risky = True # For PoC usability. In prod, this should be False.

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PermissionManager()
        return cls._instance

    def check_permission(self, action_type: str, params: any) -> bool:
        """
        Returns True if allowed allowed to run automatically.
        Returns False if requires User Confirmation.
        Raises Exception if Strictly Forbidden.
        """
        action = action_type.upper()
        
        if action in self.SAFE_ACTIONS:
            return True
            
        if action in self.RISKY_ACTIONS:
            if self.auto_approve_risky:
                return True
            return False # Needs confirm
            
        if action in self.DANGEROUS_ACTIONS:
            # Special logic for apps
            if action == "OPEN_APP":
                app_name = str(params).lower()
                for safe_app in self.whitelisted_apps:
                    if safe_app in app_name:
                        return True
                logger.warning(f"Blocked launch of unknown app: {app_name}")
                return False # Unknown app requires confirm
            
            return False # Default dangerous = confirm
            
        return False # Unknown action = confirm
