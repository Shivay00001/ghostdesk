import time
import logging
import threading
from typing import Dict, Any

from .queue_mgr import CommandQueue
from .types import UserCommand, AgentResult
from .identity import IdentityManager
from .policy import PolicyEngine, Decision
from .access_control import ApprovalService
from .audit import AuditLogger
from ..agents.planner import PlannerAgent
from ..agents.vision import VisionAgent
from ..agents.action import ActionAgent
from ..agents.knowledge import AttributionAgent
from ..agents.skeletons import VerifierAgent

logger = logging.getLogger(__name__)

class Coordinator:
    def __init__(self):
        self.queue = CommandQueue.get_instance()
        self.identity_mgr = IdentityManager.get_instance()
        self.approval_service = ApprovalService.get_instance()
        self.audit_logger = AuditLogger.get_instance()
        
        self.planner = PlannerAgent(model_name="llama3.2")
        self.vision = VisionAgent(model="llama3.2-vision")
        self.attribution = AttributionAgent(model="llama3.2")
        self.action = ActionAgent()
        self.verifier = VerifierAgent()
        
        self.running = False
        self._thread = None
        # In a real app, this would be a message bus to send updates back to adapter
        self.adapter_callback = None 

    def set_callback(self, callback):
        self.adapter_callback = callback

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("Enterprise Coordinator started.")

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()
        logger.info("Coordinator stopped.")

    def _loop(self):
        while self.running:
            command = self.queue.get(timeout=1.0)
            if command:
                self._handle_command(command)
                self.queue.task_done()

    def _handle_command(self, command: UserCommand):
        logger.info(f"Processing command from {command.sender_id}")
        
        # 0. IDENTITY LOOKUP
        identity = self.identity_mgr.get_identity(command.sender_id)
        if not identity:
            logger.error(f"Unknown Identity for {command.sender_id}. Dropping.")
            return

        # Special Case: Handle "APPROVE <ID>" logic (Simplistic for PoC)
        if command.raw_text.upper().startswith("APPROVE "):
            req_id = command.raw_text.split(" ")[1].strip()
            if self.approval_service.approve_request(req_id):
                self._resume_execution(req_id)
            return

        # 1. PLAN
        plan = self.planner.create_plan(command.raw_text)
        if not plan:
            self._notify_user(command, "Could not generate a plan.")
            return

        # 2. PROPOSE (Policy Check)
        decision = PolicyEngine.evaluate_plan(identity, plan)
        logger.info(f"Policy Decision: {decision}")

        if decision == Decision.DENY:
            self._notify_user(command, "Access Denied by Policy.")
            return
        
        if decision == Decision.REQUIRE_APPROVAL:
            req_id = self.approval_service.create_request(command, identity, plan)
            self._notify_user(command, f"⚠️ Approval Required. Reply with 'APPROVE {req_id}' to proceed.")
            # Stop specific execution here, wait for callback
            return

        # 3. ACT (If Allowed)
        self._execute_plan(plan, command)

    def _resume_execution(self, request_id: str):
        req = self.approval_service.get_request(request_id)
        if req:
            self._notify_user(req.command, f"Request {request_id} Approved. Executing...")
            self._execute_plan(req.plan, req.command)

    def _execute_plan(self, plan, command):
        logger.info("Starting Execution Loop...")
        for i, step in enumerate(plan):
            logger.info(f"--- Step {i+1}: {step.description} ---")
            
            # Observe
            screen_path = self.vision.capture_screen()
            target_loc = None
            if step.target_element:
                res = self.vision.detect_element(screen_path, step.target_element)
                target_loc = res.data
            
            # Special: ANSWER/RAG
            if step.action_type == "ANSWER":
                ans = self.attribution.answer_question(command.raw_text)
                self._notify_user(command, f"💡 **Answer**: {ans}")
                self.audit_logger.log_action(command.sender_id, "ANSWER", "RAG", "SUCCESS", "Answered")
                continue

            # Act
            res = self.action.execute(step, context=target_loc)
            
            # AUDIT LOG
            status = "SUCCESS" if res.success else "FAILURE"
            self.audit_logger.log_action(
                user_id=command.sender_id,
                action_type=step.action_type,
                action_value=str(step.value or step.target_element),
                status=status,
                result=res.message
            )

            if not res.success:
                logger.error(f"Action failed: {res.message}")
                self._notify_user(command, f"Step failed: {step.description}")
                break

            # Verify (Mock)
            self.verifier.verify(step, None, None)
        
        self._notify_user(command, "Job Complete.")

    def _notify_user(self, command: UserCommand, message: str):
        if self.adapter_callback:
            self.adapter_callback(command.sender_id, message)
        else:
            logger.info(f"[OUTGOING -> {command.sender_id}] {message}")
