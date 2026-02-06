from .gateway import BaseGateway
from .types import UserCommand
import threading
import sys
import time
import logging

logger = logging.getLogger(__name__)

class CLIGateway(BaseGateway):
    def __init__(self):
        super().__init__("CLI")
        self.running = False

    def start(self):
        self.running = True
        logger.info("CLI Gateway Started. Type your commands below:")
        
        while self.running:
            try:
                text = input("Molt> ")
                if not text: continue
                
                cmd = UserCommand(
                    raw_text=text,
                    sender_id="CLI_USER",
                    platform="cli",
                    timestamp=time.time()
                )
                self.push_command(cmd)
            except EOFError:
                break
            except Exception as e:
                logger.error(f"CLI Error: {e}")

    def send_message(self, recipient_id: str, text: str):
        print(f"\n[AGENT]: {text}\n")
