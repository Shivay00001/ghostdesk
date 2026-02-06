from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel
from .config import Config

class Role(str, Enum):
    ADMIN = "ADMIN"        # Full access
    MANAGER = "MANAGER"    # Can approve acts, cannot delete system files
    EMPLOYEE = "EMPLOYEE"  # Standard access, read-only on sensitive folders
    GUEST = "GUEST"        # Very limited access

class UserIdentity(BaseModel):
    user_id: str
    role: Role
    username: Optional[str] = None

class IdentityManager:
    _instance = None
    
    def __init__(self):
        # Mock "Entra ID" - In prod this would query an AD/LDAP service
        # For PoC, we map config ALLOWED_USERS to ADMIN
        self.user_db: Dict[str, Role] = {}
        for uid in Config.ALLOWED_USERS:
            self.user_db[uid] = Role.ADMIN

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = IdentityManager()
        return cls._instance

    def get_identity(self, user_id: str) -> Optional[UserIdentity]:
        role = self.user_db.get(user_id)
        if role:
            return UserIdentity(user_id=user_id, role=role)
        return None  # Unknown user
