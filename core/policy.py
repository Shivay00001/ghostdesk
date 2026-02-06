import logging
from enum import Enum
from typing import List
from .types import Step
from .identity import Role, UserIdentity

logger = logging.getLogger(__name__)

class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"

class PolicyEngine:
    """
    Enterprise Governance Engine.
    Decides if an action plan is allowed based on the User's Role.
    """

    CRITICAL_APPS = {"cmd", "powershell", "regedit", "format"}
    SENSITIVE_ACTIONS = {"DELETE", "WRITE", "UPLOAD"}

    @staticmethod
    def evaluate_plan(identity: UserIdentity, plan: List[Step]) -> Decision:
        # Default decision
        decision = Decision.ALLOW

        for step in plan:
            # 1. ADMINS are trusted but destructive actions still need sanity check (optional)
            if identity.role == Role.ADMIN:
                # Even for admins, we might want approval for "format c:" types of things
                if PolicyEngine._is_destructive(step):
                    return Decision.REQUIRE_APPROVAL
                continue

            # 2. MANAGERS
            if identity.role == Role.MANAGER:
                if PolicyEngine._is_destructive(step):
                    return Decision.REQUIRE_APPROVAL
                if PolicyEngine._is_system_critical(step):
                    return Decision.DENY
                continue

            # 3. EMPLOYEES
            if identity.role == Role.EMPLOYEE:
                if PolicyEngine._is_destructive(step) or PolicyEngine._is_system_critical(step):
                    return Decision.DENY
                continue

        return decision

    @staticmethod
    def _is_destructive(step: Step) -> bool:
        # Heuristic for destructive actions
        if step.action_type in ["DELETE", "PRESS"]: # PRESS might be "Delete" key
            return True
        # Check for dangerous CLI commands if typing
        if step.action_type == "TYPE" and "del " in (step.value or "").lower():
            return True
        return False

    @staticmethod
    def _is_system_critical(step: Step) -> bool:
        if step.action_type == "OPEN_APP":
            app = (step.value or "").lower()
            if any(crit in app for crit in PolicyEngine.CRITICAL_APPS):
                return True
        return False
