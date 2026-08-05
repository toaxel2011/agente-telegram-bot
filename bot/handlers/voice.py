import os
import tempfile
import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.middleware import solo_autorizados
from services.groq_service import groq_service
from core.agent import agente_ia

logger = logging.getLogger(__name__)

@solo_autorizados
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    voice = update.message.voice or update.message.audio

    if not voice:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    temp_path = None
    try:
        # 1. Descargar el archivo de audio enviado por Telegram
        tg_file = await context.bot.get_file(voice.file_id)
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            temp_path = tmp.name

        await tg_file.download_to_drive(custom_path=temp_path)

        # 2. Transcribir con Whisper Large v3
        texto_transcrito = await groq_service.transcribir_audio(temp_path)
        logger.info(f"🎙️ Transcripción para usuario {user_id}: '{texto_transcrito}'")

        if not texto_transcrito.strip():
            await update.message.reply_text("🔇 No logré escuchar ningún mensaje en la nota de voz.")
            return

        # Notificar al usuario lo que la IA entendió de su voz
        await update.message.reply_text(f"🎙️ _Entendí:_ \"{texto_transcrito}\"", parse_mode="Markdown")

        # 3. Procesar el texto resultante con el Agente IA
        respuesta_ia = await agente_ia.procesar_mensaje(user_id, texto_transcrito)
        await update.message.reply_text(respuesta_ia, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error procesando nota de voz: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ocurrió un error al procesar tu nota de voz.")
    finally:
        # Limpieza de archivo temporal
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)