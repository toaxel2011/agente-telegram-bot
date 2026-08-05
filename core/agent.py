import json
import logging
from typing import List, Dict, Any
from config.settings import settings
from services.groq_service import groq_service
from core.prompts import obtener_prompt_sistema
from core.tools import (
    TOOLS_DEFINITIONS,
    tool_crear_tarea,
    tool_listar_tareas,
    tool_completar_tarea,
    tool_consultar_clima
)

logger = logging.getLogger(__name__)

# Mapeo de nombres de funciones a sus implementaciones en Python
HERRAMIENTAS_MAP = {
    "crear_tarea": tool_crear_tarea,
    "listar_tareas": tool_listar_tareas,
    "completar_tarea": tool_completar_tarea,
    "consultar_clima": tool_consultar_clima
}

class AgenteIA:
    def __init__(self):
        # Almacenamiento simple de memoria conversacional en memoria RAM por usuario (últimos 10 mensajes)
        self.historiales: Dict[int, List[Dict[str, Any]]] = {}

    def _obtener_historial(self, user_id: int) -> List[Dict[str, Any]]:
        if user_id not in self.historiales:
            self.historiales[user_id] = []
        return self.historiales[user_id]

    def _agregar_al_historial(self, user_id: int, rol: str, contenido: str):
        historial = self._obtener_historial(user_id)
        historial.append({"role": rol, "content": contenido})
        # Mantener únicamente los últimos 10 mensajes para ahorrar context window y mantener respuestas veloces
        if len(historial) > 10:
            self.historiales[user_id] = historial[-10:]

    async def procesar_mensaje(self, user_id: int, texto_usuario: str) -> str:
        """Procesa la entrada del usuario usando Llama 3.3 70B y Tool Calling."""
        try:
            # 1. Preparar mensajes con System Prompt dinámico
            system_prompt = obtener_prompt_sistema()
            messages = [{"role": system, "content": system_prompt} for system in ["system"]]
            
            # Recuperar memoria conversacional previa
            historial = self._obtener_historial(user_id)
            messages.extend(historial)
            
            # Agregar el nuevo mensaje del usuario
            messages.append({"role": "user", "content": texto_usuario})

            # 2. Primera llamada al modelo en Groq (usando Llama 3.3 70B)
            response = await groq_service.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=messages,
                tools=TOOLS_DEFINITIONS,
                tool_choice="auto",
                temperature=settings.TEMPERATURE
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # 3. Verificar si el Agente decidió ejecutar una o varias herramientas
            if tool_calls:
                # Registrar la intención del asistente en la cadena de mensajes
                messages.append(response_message)

                # Herramientas cuyo resultado se muestra tal cual (formato determinista),
                # sin dejar que el modelo lo parafrasee en una segunda llamada.
                TOOLS_SALIDA_DIRECTA = {"listar_tareas"}
                respuesta_directa = None

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    logger.info(f"🤖 Agente ejecutando Tool '{function_name}' para usuario {user_id} con args: {function_args}")

                    # Ejecutar la herramienta correspondiente
                    if function_name in HERRAMIENTAS_MAP:
                        tool_func = HERRAMIENTAS_MAP[function_name]
                        resultado_tool = await tool_func(user_id, function_args)
                    else:
                        resultado_tool = f"Error: La herramienta '{function_name}' no existe."

                    if function_name in TOOLS_SALIDA_DIRECTA:
                        respuesta_directa = resultado_tool

                    # Devolver el resultado de la herramienta al modelo
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": resultado_tool,
                    })

                if respuesta_directa is not None:
                    # 4a. Mostrar la lista con su formato exacto, sin reescritura del modelo.
                    respuesta_final = respuesta_directa
                else:
                    # 4b. Segunda llamada al modelo para generar la respuesta final natural.
                    segunda_respuesta = await groq_service.client.chat.completions.create(
                        model=settings.MODEL_NAME,
                        messages=messages,
                        temperature=settings.TEMPERATURE
                    )
                    respuesta_final = segunda_respuesta.choices[0].message.content
            else:
                # Si no requirió herramientas, es una conversación directa
                respuesta_final = response_message.content

            # 5. Guardar la interacción en la memoria conversacional
            self._agregar_al_historial(user_id, "user", texto_usuario)
            self._agregar_al_historial(user_id, "assistant", respuesta_final)

            return respuesta_final

        except Exception as e:
            logger.error(f"Error en AgenteIA procesando mensaje: {e}", exc_info=True)
            
            # Intento de Fallback al modelo de 8B en caso de saturación temporal de API
            try:
                logger.warning("⚠️ Reintentando con modelo de respaldo (Fallback Llama-3.1-8b)...")
                fallback_response = await groq_service.client.chat.completions.create(
                    model=settings.FALLBACK_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": obtener_prompt_sistema()},
                        {"role": "user", "content": texto_usuario}
                    ],
                    temperature=0.3
                )
                return fallback_response.choices[0].message.content
            except Exception as fb_err:
                logger.error(f"Error también en modelo Fallback: {fb_err}")
                return "🤔 Lo siento, tuve un problema interno de conexión con mi cerebro de IA. Por favor, intenta de nuevo en unos segundos."

agente_ia = AgenteIA()