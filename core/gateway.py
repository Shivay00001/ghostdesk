import logging
from abc import ABC, abstractmethod
from .queue_mgr import CommandQueue
from .types import UserCommand

logger = logging.getLogger(__name__)

class BaseGateway(ABC):
    def __init__(self, name: str):
        self.name = name
        self.queue = CommandQueue.get_instance()
    
    @abstractmethod
    def start(self):
        """Start the listener loop."""
        pass
    
    @abstractmethod
    def send_message(self, recipient_id: str, text: str):
        """Send a message out."""
        pass

    def push_command(self, cmd: UserCommand):
        """Standard way to push to Brain."""
        self.queue.add_command(cmd)
