import logging
from datetime import datetime
from database.connection import db_pool

logger = logging.getLogger(__name__)

class TaskRepository:

    @staticmethod
    async def crear_tarea(
        user_id: int, 
        titulo: str, 
        fecha_hora: datetime, 
        notificar_a: str = '', 
        recurrencia: str = None, 
        prioridad: str = 'normal',
        primer_recordatorio: datetime = None
    ):
        """Crea una nueva tarea para un usuario."""
        query = """
            INSERT INTO tareas (user_id, titulo, fecha_hora, notificar_a, recurrencia, prioridad, primer_recordatorio)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, user_id, titulo, fecha_hora, completada, notificada, notificar_a, recurrencia, prioridad;
        """
        # Aseguramos que los datetimes sean naive (sin tzinfo) para asyncpg
        if fecha_hora and hasattr(fecha_hora, 'tzinfo') and fecha_hora.tzinfo is not None:
            fecha_hora = fecha_hora.replace(tzinfo=None)
            
        if primer_recordatorio and hasattr(primer_recordatorio, 'tzinfo') and primer_recordatorio.tzinfo is not None:
            primer_recordatorio = primer_recordatorio.replace(tzinfo=None)

        async with db_pool.pool.acquire() as conn:
            row = await conn.fetchrow(
                query, user_id, titulo, fecha_hora, notificar_a, recurrencia, prioridad, primer_recordatorio
            )
            return dict(row) if row else None

    @staticmethod
    async def obtener_tareas_pendientes(user_id: int):
        """Obtiene todas las tareas no completadas de un usuario."""
        query = """
            SELECT * FROM tareas
            WHERE user_id = $1 AND completada = FALSE
            ORDER BY fecha_hora ASC;
        """
        async with db_pool.pool.acquire() as conn:
            rows = await conn.fetch(query, user_id)
            return [dict(row) for row in rows]

    @staticmethod
    async def obtener_recordatorios_pendientes(ahora: datetime):
        """
        Obtiene todas las tareas cuya fecha sea menor o igual a 'ahora'
        y que aún no hayan sido completadas ni notificadas.
        """
        # Limpiamos tzinfo para evitar el error de asyncpg
        if hasattr(ahora, 'tzinfo') and ahora.tzinfo is not None:
            ahora = ahora.replace(tzinfo=None)

        query = """
            SELECT * FROM tareas
            WHERE fecha_hora <= $1
              AND completada = FALSE
              AND notificada = FALSE;
        """
        async with db_pool.pool.acquire() as conn:
            rows = await conn.fetch(query, ahora)
            return [dict(row) for row in rows]

    @staticmethod
    async def marcar_notificada(tarea_id: int):
        """Marca una tarea como notificada."""
        query = """
            UPDATE tareas
            SET notificada = TRUE
            WHERE id = $1
            RETURNING id, notificada;
        """
        async with db_pool.pool.acquire() as conn:
            row = await conn.fetchrow(query, tarea_id)
            return dict(row) if row else None

    @staticmethod
    async def marcar_completada(tarea_id: int, user_id: int):
        """Marca una tarea como completada."""
        query = """
            UPDATE tareas
            SET completada = TRUE
            WHERE id = $1 AND user_id = $2
            RETURNING id, completada;
        """
        async with db_pool.pool.acquire() as conn:
            row = await conn.fetchrow(query, tarea_id, user_id)
            return dict(row) if row else None

    @staticmethod
    async def eliminar_tarea(tarea_id: int, user_id: int):
        """Elimina una tarea de la base de datos."""
        query = """
            DELETE FROM tareas
            WHERE id = $1 AND user_id = $2
            RETURNING id;
        """
        async with db_pool.pool.acquire() as conn:
            row = await conn.fetchrow(query, tarea_id, user_id)
            return dict(row) if row else None