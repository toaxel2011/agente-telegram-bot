import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.middleware import solo_autorizados, solo_admin
from database.repositories.user_repo import UserRepository

logger = logging.getLogger(__name__)

@solo_autorizados
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mensaje = (
        f"¡Hola {user.first_name}! 👋 Soy tu **Asistente Personal de Inteligencia Artificial**.\n\n"
        "Puedes pedirme cosas en lenguaje natural o con notas de voz, por ejemplo:\n"
        "• *'Recuérdame pagar el internet mañana a las 3 PM'*\n"
        "• *'¿Qué tareas tengo pendientes?'*\n"
        "• *'¿Cómo está el clima hoy en Caracas?'*\n\n"
        "Usa `/help` para ver la lista de comandos disponibles."
    )
    await update.message.reply_text(mensaje, parse_mode="Markdown")

@solo_autorizados
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ayuda = (
        "🤖 **Comandos Disponibles:**\n\n"
        "⚙️ **Configuración:**\n"
        "• `/resumen_hora HH:MM` - Define la hora de tu resumen diario de tareas (o 'desactivar').\n"
        "• `/ciudad <Nombre>` - Configura tu ciudad para el reporte del clima.\n\n"
        "👑 **Administración:**\n"
        "• `/add_user <user_id>` - Autorizar a un nuevo usuario.\n"
        "• `/del_user <user_id>` - Desautorizar a un usuario.\n"
        "• `/users` - Listar usuarios autorizados."
    )
    await update.message.reply_text(ayuda, parse_mode="Markdown")

@solo_autorizados
async def resumen_hora_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        hora_actual = await UserRepository.obtener_resumen_hora(user_id)
        msg = f"Tu hora de resumen diario está configurada a las `{hora_actual}`." if hora_actual else "No tienes configurada hora de resumen diario."
        await update.message.reply_text(f"{msg}\nUsa `/resumen_hora HH:MM` para modificarla o `/resumen_hora desactivar` para cancelarla.", parse_mode="Markdown")
        return

    arg = context.args[0].lower().strip()
    if arg in ["desactivar", "off", "cancelar"]:
        await UserRepository.actualizar_resumen_hora(user_id, None)
        await update.message.reply_text("🚫 Resumen diario desactivado.")
        return

    # Validar formato HH:MM
    import re
    if re.match(r"^([01]?\d|2[03]):[0-5]\d$", arg):
        hora_formatted = f"{int(arg.split(':')[0]):02d}:{int(arg.split(':')[1]):02d}"
        await UserRepository.actualizar_resumen_hora(user_id, hora_formatted)
        await update.message.reply_text(f"⏰ Resumen diario programado para las `{hora_formatted}` todos los días.", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Formato inválido. Usa HH:MM en formato 24 horas (ejemplo: `/resumen_hora 08:00`).", parse_mode="Markdown")

@solo_autorizados
async def ciudad_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        ciudad = await UserRepository.obtener_ciudad(user_id)
        await update.message.reply_text(f"🏙️ Tu ciudad configurada es: *{ciudad}*. Usa `/ciudad <Nombre>` para cambiarla.", parse_mode="Markdown")
        return

    nueva_ciudad = " ".join(context.args).strip()
    await UserRepository.actualizar_ciudad(user_id, nueva_ciudad)
    await update.message.reply_text(f"✅ Ciudad actualizada a: *{nueva_ciudad}*.", parse_mode="Markdown")

@solo_admin
async def add_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Uso: `/add_user <user_id>`", parse_mode="Markdown")
        return
    
    nuevo_id = int(context.args[0])
    await UserRepository.agregar_usuario(nuevo_id)
    await update.message.reply_text(f"✅ Usuario `{nuevo_id}` agregado y autorizado.", parse_mode="Markdown")

@solo_admin
async def del_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Uso: `/del_user <user_id>`", parse_mode="Markdown")
        return
    
    target_id = int(context.args[0])
    await UserRepository.eliminar_usuario(target_id)
    await update.message.reply_text(f"🗑️ Usuario `{target_id}` eliminado.", parse_mode="Markdown")

@solo_admin
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuarios = await UserRepository.listar_usuarios()
    msg = "👥 **Usuarios Autorizados:**\n"
    for uid, es_adm in usuarios:
        rol = "👑 Admin" if es_adm else "👤 Usuario"
        msg += f"• `{uid}` - {rol}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")