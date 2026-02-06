import logging
import asyncio
from typing import Optional
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from ..core.config import Config
from ..core.types import UserCommand
from ..core.queue_mgr import CommandQueue
from ..core.gateway import SecurityGateway
from ..core.privacy import PrivacyScrubber

logger = logging.getLogger(__name__)

class TelegramAdapter:
    def __init__(self, coordinator=None):
        self.app = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()
        self.queue = CommandQueue.get_instance()
        self.coordinator = coordinator
        self.bot: Optional[Bot] = None

        if self.coordinator:
            # Register callback so Coordinator can send messages properly
            self.coordinator.set_callback(self.send_message_sync)

        # Add Handlers
        handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
        self.app.add_handler(handler)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return

        # Capture bot instance for later use in callbacks
        if not self.bot:
            self.bot = context.bot

        sender_id = str(update.effective_user.id)
        text = update.message.text
        msg_id = str(update.message.message_id)

        # Log connection
        logger.info(f"Incoming: {text} from {sender_id}")

        command = UserCommand(
            raw_text=text,
            sender_id=sender_id,
            platform="telegram",
            message_id=msg_id
        )

        # Gateway Check
        if SecurityGateway.validate_command(command):
            self.queue.put(command)
            # Don't auto-reply here; let Coordinator handle logic
        else:
            await update.message.reply_text("⛔ Access Denied.")

    def send_message_sync(self, chat_id: str, text: str):
        """
        Thread-safe wrapper to send message from Coordinator thread back to Telegram.
        """
        # PRIVACY GUARD: Redact PII
        clean_text = PrivacyScrubber.scrub(text)

        if self.app and self.app.loop:
            asyncio.run_coroutine_threadsafe(
                self.app.bot.send_message(chat_id=chat_id, text=clean_text),
                self.app.loop
            )
        else:
            logger.error("Telegram App Loop not available for sending message.")

    def run(self):
        logger.info("Starting Telegram Adapter polling...")
        self.app.run_polling()
