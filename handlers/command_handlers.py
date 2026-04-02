import logging
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from services.state_manager import StateManager
from services.gmail_service import GmailService
from services.ollama_service import OllamaService

logger = logging.getLogger(__name__)

BTN_STOP = "⏸ Pause"
BTN_START = "▶️ Resume"
BTN_STATUS = "ℹ️ Status"
BTN_SNOOZE = "🔕 Snooze"
BTN_HISTORY = "📋 History"


def get_main_keyboard(polling_active: bool) -> ReplyKeyboardMarkup:
    toggle = BTN_STOP if polling_active else BTN_START
    return ReplyKeyboardMarkup(
        [[toggle, BTN_STATUS], [BTN_SNOOZE, BTN_HISTORY]],
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

        if text in (BTN_STOP, BTN_START):
            await self._toggle_polling(update)
        elif text == BTN_STATUS:
            await self._show_status(update)
        elif text == BTN_SNOOZE:
            await self._show_snooze_options(update)
        elif text == BTN_HISTORY:
            await self._show_history(update)

    async def _toggle_polling(self, update: Update):
        currently_active = self.state.is_polling_active()
        self.state.set_polling_active(not currently_active)
        new_active = not currently_active

        msg = "▶️ Polling resumed." if new_active else "⏸ Polling paused."
        await update.message.reply_text(msg, reply_markup=get_main_keyboard(new_active))

    async def _show_status(self, update: Update):
        active = self.state.is_polling_active()
        last_poll = self.state.get_last_poll_time()
        snoozed_until = self.state.get_snoozed_until()

        status_icon = "🟢" if active else "🔴"
        status_text = "Running" if active else "Paused"

        lines = [f"Status: {status_icon} {status_text}"]
        if snoozed_until:
            lines.append(f"🔕 Snoozed until: {snoozed_until}")
        if last_poll:
            lines.append(f"Last checked: {last_poll}")
        else:
            lines.append("Not checked yet.")

        await update.message.reply_text("\n".join(lines), reply_markup=get_main_keyboard(active))

    async def _show_snooze_options(self, update: Update):
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("1 hour", callback_data="snooze_1"),
                InlineKeyboardButton("3 hours", callback_data="snooze_3"),
            ],
            [
                InlineKeyboardButton("8 hours", callback_data="snooze_8"),
                InlineKeyboardButton("Cancel", callback_data="snooze_cancel"),
            ],
        ])
        await update.message.reply_text("Select snooze duration:", reply_markup=keyboard)

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

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        data = query.data
        if not data.startswith("snooze_"):
            return

        hours_str = data.replace("snooze_", "")
        if hours_str == "cancel":
            await query.edit_message_text("Snooze cancelled.")
            return

        hours = int(hours_str)
        self.state.snooze(hours)
        await query.edit_message_text(
            f"🔕 Snoozed for {hours} hour{'s' if hours > 1 else ''}.\nPolling will resume automatically."
        )
