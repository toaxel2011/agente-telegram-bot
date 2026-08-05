import asyncio
import logging
from config.settings import settings
from database.connection import db_pool
from core.agent import agente_ia

logging.basicConfig(level=logging.INFO)

async def test_flujo_agente():
    print("🚀 Inicializando pool de prueba...")
    await db_pool.init_pool()

    test_user_id = settings.ADMIN_ID

    print("\n--- TEST 1: Crear Tarea ---")
    prompt_1 = "Recuérdame pagar el servicio de internet mañana a las 3 PM"
    print(f"Usuario: {prompt_1}")
    resp_1 = await agente_ia.procesar_mensaje(test_user_id, prompt_1)
    print(f"Agente: {resp_1}\n")

    print("--- TEST 2: Listar Tareas ---")
    prompt_2 = "¿Cuáles son mis tareas pendientes?"
    print(f"Usuario: {prompt_2}")
    resp_2 = await agente_ia.procesar_mensaje(test_user_id, prompt_2)
    print(f"Agente: {resp_2}\n")

    print("--- TEST 3: Consultar Clima ---")
    prompt_3 = "¿Cómo está el clima hoy en Caracas?"
    print(f"Usuario: {prompt_3}")
    resp_3 = await agente_ia.procesar_mensaje(test_user_id, prompt_3)
    print(f"Agente: {resp_3}\n")

    await db_pool.close()
    print("✅ Prueba finalizada con éxito.")

if __name__ == "__main__":
    asyncio.run(test_flujo_agente())