import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.settings import settings
from bot.handlers.commands import (
    start_command, help_command, resumen_hora_command,
    ciudad_command, add_user_command, del_user_command, users_command
)
from bot.handlers.chat import handle_text_message
from bot.handlers.voice import handle_voice_message
from bot.jobs.reminders import check_reminders_job
from bot.jobs.daily_summary import daily_summary_job

logger = logging.getLogger(__name__)

def crear_bot_app() -> Application:
    app = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    # Registrar Comandos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("resumen_hora", resumen_hora_command))
    app.add_handler(CommandHandler("ciudad", ciudad_command))
    app.add_handler(CommandHandler("add_user", add_user_command))
    app.add_handler(CommandHandler("del_user", del_user_command))
    app.add_handler(CommandHandler("users", users_command))

    # Registrar Mensajes (Texto y Voz)
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Registrar Jobs en Background
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(check_reminders_job, interval=60, first=10)
        job_queue.run_repeating(daily_summary_job, interval=60, first=15)
        logger.info("⏰ Jobs en background (Recordatorios y Resumen) registrados correctamente.")

    return app