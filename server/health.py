import logging
from aiohttp import web
from config.settings import settings

logger = logging.getLogger(__name__)

async def health_check(request):
    return web.Response(text="🤖 Agente IA activo y respondiendo.", status=200)

async def iniciar_servidor_http():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', settings.PORT)
    await site.start()
    logger.info(f"🌐 Servidor Health-Check HTTP iniciado en puerto {settings.PORT}.")