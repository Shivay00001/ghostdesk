import uuid
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel
from .types import Step, UserCommand
from .identity import UserIdentity

logger = logging.getLogger(__name__)

class ApprovalRequest(BaseModel):
    request_id: str
    command: UserCommand
    identity: UserIdentity
    plan: List[Step]
    status: str = "PENDING" # PENDING, APPROVED, REJECTED

class ApprovalService:
    _instance = None
    
    def __init__(self):
        self._requests: Dict[str, ApprovalRequest] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ApprovalService()
        return cls._instance

    def create_request(self, command: UserCommand, identity: UserIdentity, plan: List[Step]) -> str:
        req_id = str(uuid.uuid4())[:8]
        request = ApprovalRequest(
            request_id=req_id,
            command=command,
            identity=identity,
            plan=plan
        )
        self._requests[req_id] = request
        logger.info(f"Created Approval Request [{req_id}] for user {identity.user_id}")
        return req_id

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        return self._requests.get(request_id)

    def approve_request(self, request_id: str) -> bool:
        req = self._requests.get(request_id)
        if req and req.status == "PENDING":
            req.status = "APPROVED"
            logger.info(f"Request [{request_id}] APPROVED.")
            return True
        return False

    def reject_request(self, request_id: str) -> bool:
        req = self._requests.get(request_id)
        if req and req.status == "PENDING":
            req.status = "REJECTED"
            logger.info(f"Request [{request_id}] REJECTED.")
            return True
        return False
