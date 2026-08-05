import asyncio
import logging

from config.settings import settings
from database.connection import db_pool
from bot.main import crear_bot_app
from server.health import iniciar_servidor_http

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 Arrancando Agente IA de Productividad...")

    # 1. Inicializar Pool de Conexiones a Base de Datos
    await db_pool.init_pool()

    # 2. Iniciar Servidor HTTP para Render (Keep-Alive)
    await iniciar_servidor_http()

    # 3. Inicializar e Iniciar el Bot de Telegram
    telegram_app = crear_bot_app()
    
    async with telegram_app:
        await telegram_app.start()
        await telegram_app.updater.start_polling(drop_pending_updates=True)
        logger.info("🤖 Bot de Telegram escuchando mensajes...")

        # Mantener el bucle asíncrono corriendo hasta interrupción
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            logger.info("🛑 Deteniendo el servicio...")
        finally:
            await telegram_app.updater.stop()
            await telegram_app.stop()
            await db_pool.close()

if __name__ == "__main__":
    asyncio.run(main())