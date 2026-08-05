import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from database.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)

def solo_autorizados(func):
    """Decorador para restringir el uso del bot a usuarios registrados en la BD."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user:
            return

        autorizado = await UserRepository.usuario_autorizado(user.id)
        if not autorizado:
            logger.warning(f"🚫 Acceso denegado a usuario no autorizado: {user.id} (@{user.username})")
            if update.message:
                await update.message.reply_text("⛔ Lo siento, no estás autorizado para interactuar con este asistente.")
            return

        return await func(update, context, *args, **kwargs)
    return wrapper

def solo_admin(func):
    """Decorador para comandos exclusivos de administradores."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user:
            return

        es_admin = await UserRepository.es_admin(user.id)
        if not es_admin:
            if update.message:
                await update.message.reply_text("⛔ Este comando requiere privilegios de Administrador.")
            return

        return await func(update, context, *args, **kwargs)
    return wrapper