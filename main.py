import logging
import os

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from services.gmail_service import GmailService
from services.ollama_service import OllamaService
from services.state_manager import StateManager
from handlers.command_handlers import CommandHandlers
from handlers.polling_handler import poll_emails

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    user_id = int(os.getenv("TELEGRAM_USER_ID"))
    interval = int(os.getenv("POLLING_INTERVAL_SECONDS", 120))

    state = StateManager()

    gmail = GmailService(
        credentials_file=os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json"),
    )
    ollama = OllamaService(
        host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
    )

    app = Application.builder().token(token).build()

    cmd = CommandHandlers(gmail, ollama, state)
    app.add_handler(CommandHandler("start", cmd.start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd.handle_keyboard))

    async def polling_job(context):
        await poll_emails(context, gmail, ollama, state, user_id)

    app.job_queue.run_repeating(polling_job, interval=interval, first=10)

    logger.info(f"Bot started — polling every {interval}s")
    app.run_polling()


if __name__ == "__main__":
    main()
