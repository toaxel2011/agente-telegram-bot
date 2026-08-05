import logging
from datetime import datetime
from telegram.ext import ContextTypes
from config.settings import settings
from database.connection import db_pool
from database.repositories.task_repo import TaskRepository
from database.repositories.user_repo import UserRepository
from services.weather_service import obtener_clima_async

logger = logging.getLogger(__name__)

async def daily_summary_job(context: ContextTypes.DEFAULT_TYPE):
    """Job que se ejecuta cada minuto para verificar a qué usuario le toca el resumen diario."""
    ahora_hora = datetime.now(settings.TIMEZONE).strftime("%H:%M")

    async with db_pool.pool.acquire() as conn:
        # Seleccionar usuarios cuya resumen_hora coincida con la hora actual
        usuarios = await conn.fetch("SELECT user_id, ciudad FROM usuarios WHERE resumen_hora = $1;", ahora_hora)

        for u in usuarios:
            uid = u["user_id"]
            ciudad = u["ciudad"] or "Punto Fijo"

            # 1. Obtener clima
            clima_text = await obtener_clima_async(ciudad)

            # 2. Obtener tareas pendientes
            tareas = await TaskRepository.obtener_tareas_pendientes(uid)

            resumen = f"🌅 **¡Buenos días! Tu Resumen del Día**\n\n{clima_text}\n\n"
            if tareas:
                resumen += "📋 **Tareas Pendientes:**\n"
                for t in tareas:
                    prio = "🔺" if t["prioridad"] == "alta" else "⏳"
                    f_str = t["fecha_hora"].strftime("%Y-%m-%d %H:%M")
                    resumen += f"  • #{t['id']} - {t['titulo']} ({f_str}) {prio}\n"
            else:
                resumen += "🎉 ¡No tienes tareas pendientes para hoy!"

            try:
                await context.bot.send_message(chat_id=uid, text=resumen, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Error enviando resumen diario a {uid}: {e}")