import asyncpg
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class DatabasePool:
    def __init__(self):
        self.pool: asyncpg.Pool = None

    async def init_pool(self):
        """Inicializa el pool de conexiones asíncrono a PostgreSQL."""
        if not self.pool:
            # Transformar URL de postgres:// a postgresql:// si Render la provee así
            db_url = settings.DATABASE_URL
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)

            self.pool = await asyncpg.create_pool(
                dsn=db_url,
                min_size=2,
                max_size=10,
                timeout=30.0,
                statement_cache_size=0  # <-- 🚀 AGREGA ESTA LÍNEA AQUÍ
            )
            logger.info("✅ Pool de conexiones asíncrono a PostgreSQL inicializado.")
            await self._crear_tablas_iniciales()

    async def _crear_tablas_iniciales(self):
        """Crea las tablas en PostgreSQL con tipos BIGINT para evitar desbordamientos."""
        query_usuarios = """
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id BIGINT PRIMARY KEY,
            es_admin BOOLEAN DEFAULT FALSE,
            resumen_hora VARCHAR(10) DEFAULT '08:00',
            ciudad VARCHAR(100) DEFAULT 'Punto Fijo'
        );
        """
        query_tareas = """
        CREATE TABLE IF NOT EXISTS tareas (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES usuarios(user_id) ON DELETE CASCADE,
            titulo TEXT NOT NULL,
            fecha_hora TIMESTAMP NOT NULL,
            completada BOOLEAN DEFAULT FALSE,
            notificada BOOLEAN DEFAULT FALSE,
            notificar_a TEXT DEFAULT '',
            recurrencia TEXT,
            prioridad VARCHAR(10) DEFAULT 'normal',
            primer_recordatorio TIMESTAMP,
            nag_contador INT DEFAULT 0
        );
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query_usuarios)
            await conn.execute(query_tareas)
            
            # Insertar Administrador por defecto si no existe
            await conn.execute(
                "INSERT INTO usuarios (user_id, es_admin) VALUES ($1, TRUE) ON CONFLICT DO NOTHING;",
                settings.ADMIN_ID
            )
            if settings.PARTNER_ID > 0:
                await conn.execute(
                    "INSERT INTO usuarios (user_id, es_admin) VALUES ($1, FALSE) ON CONFLICT DO NOTHING;",
                    settings.PARTNER_ID
                )
            logger.info("✅ Esquema de Base de Datos verificado e inicializado.")

    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("🔒 Pool de conexiones cerrado.")

db_pool = DatabasePool()