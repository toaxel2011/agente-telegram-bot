import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.middleware import solo_autorizados
from core.agent import agente_ia

logger = logging.getLogger(__name__)

@solo_autorizados
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text

    if not texto:
        return

    # Enviar acción de "escribiendo..." en Telegram
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Procesar con la IA
    respuesta = await agente_ia.procesar_mensaje(user_id, texto)

    await update.message.reply_text(respuesta, parse_mode="Markdown")