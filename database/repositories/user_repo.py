import logging
from typing import Optional, List, Tuple
from database.connection import db_pool

logger = logging.getLogger(__name__)

class UserRepository:

    @staticmethod
    async def usuario_autorizado(user_id: int) -> bool:
        query = "SELECT user_id FROM usuarios WHERE user_id = $1;"
        async with db_pool.pool.acquire() as conn:
            val = await conn.fetchval(query, user_id)
            return val is not None

    @staticmethod
    async def es_admin(user_id: int) -> bool:
        query = "SELECT es_admin FROM usuarios WHERE user_id = $1;"
        async with db_pool.pool.acquire() as conn:
            return bool(await conn.fetchval(query, user_id))

    @staticmethod
    async def agregar_usuario(user_id: int) -> None:
        query = "INSERT INTO usuarios (user_id, es_admin) VALUES ($1, FALSE) ON CONFLICT DO NOTHING;"
        async with db_pool.pool.acquire() as conn:
            await conn.execute(query, user_id)

    @staticmethod
    async def eliminar_usuario(user_id: int) -> None:
        query = "DELETE FROM usuarios WHERE user_id = $1 AND es_admin = FALSE;"
        async with db_pool.pool.acquire() as conn:
            await conn.execute(query, user_id)

    @staticmethod
    async def listar_usuarios() -> List[Tuple[int, bool]]:
        query = "SELECT user_id, es_admin FROM usuarios ORDER BY user_id;"
        async with db_pool.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [(r["user_id"], r["es_admin"]) for r in rows]

    @staticmethod
    async def actualizar_resumen_hora(user_id: int, hora: Optional[str]) -> None:
        query = "UPDATE usuarios SET resumen_hora = $1 WHERE user_id = $2;"
        async with db_pool.pool.acquire() as conn:
            await conn.execute(query, hora, user_id)

    @staticmethod
    async def obtener_resumen_hora(user_id: int) -> Optional[str]:
        query = "SELECT resumen_hora FROM usuarios WHERE user_id = $1;"
        async with db_pool.pool.acquire() as conn:
            return await conn.fetchval(query, user_id)

    @staticmethod
    async def actualizar_ciudad(user_id: int, ciudad: str) -> None:
        query = "UPDATE usuarios SET ciudad = $1 WHERE user_id = $2;"
        async with db_pool.pool.acquire() as conn:
            await conn.execute(query, ciudad, user_id)

    @staticmethod
    async def obtener_ciudad(user_id: int) -> str:
        query = "SELECT ciudad FROM usuarios WHERE user_id = $1;"
        async with db_pool.pool.acquire() as conn:
            ciudad = await conn.fetchval(query, user_id)
            return ciudad if ciudad else "Punto Fijo"