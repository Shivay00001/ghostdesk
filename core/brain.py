import logging
import time
from .queue_mgr import CommandQueue
from .memory import MemoryManager
from .types import UserCommand
from ..agents.planner import PlannerAgent
from ..agents.vision import VisionAgent
from .skill_engine import SkillEngine
from .intent import IntentParser
# from ..agents.knowledge import AttributionAgent # RAG

logger = logging.getLogger(__name__)

class Brain:
    """
    The Central Intelligence of LocalMolt.
    """
    
    def __init__(self):
        self.queue = CommandQueue.get_instance()
        self.memory = MemoryManager.get_instance()
        self.intent_parser = IntentParser(model="llama3.2")
        
        # New: Load identity
        self.agent_name = self.memory.recall("agent_name") or "LocalMolt"
        
        # Agents
        self.planner = PlannerAgent(model_name="llama3.2")
        self.vision = VisionAgent(model="llama3.2-vision")
        self.skill_engine = SkillEngine()
        # self.attribution = AttributionAgent() # Logic bringing logic here later
        
        self.running = False

    def start(self):
        self.running = True
        logger.info(f"{self.agent_name} Brain is active. Waiting for input...")
        
        while self.running:
            try:
                command = self.queue.get_command(timeout=1.0)
                if command:
                    self._process_command(command)
            except Exception as e:
                # queue empty
                pass

    def _process_command(self, command: UserCommand):
        logger.info(f"Processing: {command.raw_text}")
        
        # 1. Memory Log (User)
        self.memory.log_interaction("user", command.raw_text)
        
        # 2. Context Retrieval
        history = self.memory.get_recent_history(limit=5)
        
        # 3. Intent Parsing
        intent = self.intent_parser.parse(command.raw_text)
        logger.info(f"Detected Intent: {intent}")
        
        if intent == "CHAT":
            # Simple conversational reply (Mock for now, can use LLM)
            self._respond(command.sender_id, f"I heard you say: {command.raw_text} (Chat Mode)")
            
        elif intent == "QUERY":
            # Delegate to RAG (Placeholder logic, implementing next)
            self._respond(command.sender_id, "I need to check the Knowledge Base for that. (Query Mode)")
            
        elif intent == "TASK":
            self._execute_task_pipeline(command, history)

    def _execute_task_pipeline(self, command: UserCommand, context: list):
        plan = self.planner.create_plan(command.raw_text, context=context)
        
        if not plan:
            self._respond(command.sender_id, "I couldn't come up with a plan.")
            return

        self._respond(command.sender_id, f"🧠 Planning {len(plan.steps)} steps...")
        
        for step in plan.steps:
            # Action
            result = self.skill_engine.execute_step(step, context=None) # Passing None context for now as Vision linkage needs refactor
            
            # Memory Log (System)
            self.memory.log_interaction("system", f"Executed {step.action_type}: {result.message}")
            
            if not result.success:
                self._respond(command.sender_id, f"❌ Failed: {result.message}")
                break
        
        self._respond(command.sender_id, "✅ Done.")

    def _respond(self, chat_id, text):
        logger.info(f"RESPONSE to {chat_id}: {text}")
        self.memory.log_interaction("assistant", text)
        
        if hasattr(self, 'gateway') and self.gateway:
            self.gateway.send_message(chat_id, text)
        else:
            logger.warning("No Gateway attached to Brain. Cannot reply.")
