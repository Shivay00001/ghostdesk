import time
import threading
import logging
import schedule
from typing import Callable
from .queue_mgr import CommandQueue
from .types import UserCommand

logger = logging.getLogger(__name__)

class Scheduler:
    _instance = None
    
    def __init__(self):
        self.queue = CommandQueue.get_instance()
        self.running = False
        
        # Default jobs
        # In a real app, these come from DB
        self.schedule_job("09:00", self.trigger_daily_briefing)

    def schedule_job(self, time_str: str, func: Callable):
        schedule.every().day.at(time_str).do(func)
        logger.info(f"Scheduled job at {time_str}")

    def start(self):
        self.running = True
        logger.info("Scheduler started.")
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def trigger_daily_briefing(self):
        logger.info("Triggering Daily Briefing...")
        # Inject a command from "SYSTEM"
        cmd = UserCommand(
            raw_text="Run Daily Briefing",
            sender_id="SYSTEM",
            platform="internal",
            timestamp=time.time()
        )
        self.queue.add_command(cmd)
