import queue
from typing import Optional
from .types import UserCommand

class CommandQueue:
    _instance = None
    
    def __init__(self):
        self._queue = queue.Queue()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CommandQueue()
        return cls._instance

    def put(self, command: UserCommand):
        self._queue.put(command)

    def get(self, block=True, timeout=None) -> Optional[UserCommand]:
        try:
            return self._queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
            
    def task_done(self):
        self._queue.task_done()
