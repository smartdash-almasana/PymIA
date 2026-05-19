from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

ENGINE_DIR = Path(__file__).resolve().parent
REPO_ROOT = ENGINE_DIR.parent
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from main import _cli_message_from_args, run_message  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("pymia.telegram")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.effective_message is None:
        return
    await update.effective_message.reply_text(
        "PymIA listo. Contame qué querés revisar del negocio."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    message = update.effective_message
    if message is None or message.text is None:
        return

    exit_code, normalized_message, error = _cli_message_from_args(message.text.split())
    if error is not None:
        await message.reply_text(error)
        return

    try:
        reply = run_message(normalized_message)
    except Exception:
        logger.exception("Telegram message processing failed")
        await message.reply_text("No pude procesar el mensaje ahora. Revisemos el servicio.")
        return

    if not reply:
        reply = "No pude avanzar con esa señal. Contame qué área querés revisar: margen, caja, stock, ventas o costos."

    await message.reply_text(str(reply))


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Missing required environment variable TELEGRAM_BOT_TOKEN")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Starting PymIA Telegram polling")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
