import logging
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from services.state_manager import StateManager
from services.gmail_service import GmailService
from services.ollama_service import OllamaService

logger = logging.getLogger(__name__)

BTN_HISTORY = "📋 History"


def get_main_keyboard(polling_active: bool = True) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[BTN_HISTORY]],
        resize_keyboard=True,
    )


class CommandHandlers:
    def __init__(self, gmail: GmailService, ollama: OllamaService, state: StateManager):
        self.gmail = gmail
        self.ollama = ollama
        self.state = state

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        active = self.state.is_polling_active()
        await update.message.reply_text(
            "Mail Digest Bot is ready ✓\nAuto-polling is active.",
            reply_markup=get_main_keyboard(active),
        )

    async def handle_keyboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text

        if text == BTN_HISTORY:
            await self._show_history(update)

    async def _show_history(self, update: Update):
        history = self.state.get_history(limit=5)
        if not history:
            await update.message.reply_text(
                "No summary history yet.",
                reply_markup=get_main_keyboard(self.state.is_polling_active()),
            )
            return

        chunks = []
        current = "📋 Recent summaries (last 5)\n"
        for item in reversed(history):
            dt = datetime.fromisoformat(item["time"])
            summary = item["summary"][:400] + "..." if len(item["summary"]) > 400 else item["summary"]
            block = f"\n📮 Gmail — {dt.strftime('%d/%m %H:%M')}\n{summary}\n{'─' * 20}"
            if len(current) + len(block) > 4000:
                chunks.append(current)
                current = block
            else:
                current += block
        chunks.append(current)

        for i, chunk in enumerate(chunks):
            await update.message.reply_text(
                chunk,
                reply_markup=get_main_keyboard(self.state.is_polling_active()) if i == len(chunks) - 1 else None,
            )

