import logging
from datetime import datetime
from telegram.ext import ContextTypes
from config.settings import settings
from database.repositories.task_repo import TaskRepository

logger = logging.getLogger(__name__)

async def check_reminders_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Tarea programada que revisa cada minuto si hay recordatorios pendientes.
    """
    try:
        # Las tareas se guardan naive en hora local (America/Caracas),
        # así que comparamos contra la hora local, no UTC.
        ahora = datetime.now(settings.TIMEZONE).replace(tzinfo=None)
        tareas = await TaskRepository.obtener_recordatorios_pendientes(ahora)

        for tarea in tareas:
            user_id = tarea.get("user_id")
            titulo = tarea.get("titulo")  # <-- Usar 'titulo'
            tarea_id = tarea.get("id")

            mensaje = f"⏰ **Recordatorio**: {titulo}"
            
            await context.bot.send_message(
                chat_id=user_id,
                text=mensaje,
                parse_mode="Markdown"
            )

            # Marcar como notificada para que no vuelva a enviarla en el próximo minuto
            await TaskRepository.marcar_notificada(tarea_id)
            logger.info(f"Recordatorio enviado para tarea ID {tarea_id} a usuario {user_id}")

    except Exception as e:
        logger.error(f"Error en check_reminders_job: {e}", exc_info=True)