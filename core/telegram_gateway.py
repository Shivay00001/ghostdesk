import logging
import asyncio
from typing import Optional
from .gateway import BaseGateway
from .types import UserCommand
from .config import Config

logger = logging.getLogger(__name__)

try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

if TELEGRAM_AVAILABLE:
    class TelegramGateway(BaseGateway):
        def __init__(self):
            super().__init__("Telegram")
            self.token = Config.TELEGRAM_TOKEN
            self.allowed_users = Config.ALLOWED_USERS
            self.app = None
            self.loop = None

        def start(self):
            if not self.token:
                logger.error("Telegram Token missing!")
                return

            self.app = ApplicationBuilder().token(self.token).build()
            self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self._handle_message))
            
            logger.info("Telegram Gateway Started Polling...")
            self.app.run_polling()

        async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
            if not update.message or not update.message.text:
                return

            user_id = str(update.effective_user.id)
            if user_id not in self.allowed_users:
                logger.warning(f"Unauthorized access attempt from {user_id}")
                return
                
            logger.info(f"Gateway received: {update.message.text}")
            
            cmd = UserCommand(
                raw_text=update.message.text,
                sender_id=user_id,
                platform="telegram",
                timestamp=update.message.date.timestamp()
            )
            
            self.push_command(cmd)
            
            if not self.loop:
                self.loop = asyncio.get_running_loop()

        def send_message(self, recipient_id: str, text: str):
            if self.app and self.loop:
                 asyncio.run_coroutine_threadsafe(
                    self.app.bot.send_message(chat_id=recipient_id, text=text),
                    self.loop
                )
            else:
                logger.error("Telegram Loop not ready for outbound message.")
else:
    class TelegramGateway(BaseGateway):
        def __init__(self):
            super().__init__("Telegram")
            logger.warning("Telegram dependencies missing. TelegramGateway disabled.")
        def start(self): pass
        def send_message(self, *args): pass
