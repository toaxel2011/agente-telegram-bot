from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from database.repositories.task_repo import TaskRepository
from services.weather_service import obtener_clima_async

# --- ESQUEMAS DE PYDANTIC PARA LAS HERRAMIENTAS ---

class CrearTareaSchema(BaseModel):
    titulo: str = Field(description="Descripción o título breve de la tarea")
    fecha_hora: str = Field(description="Fecha y hora en formato YYYY-MM-DD HH:MM")
    prioridad: str = Field(default="normal", description="Nivel de prioridad: 'normal' o 'alta'")
    notificar_a: Optional[str] = Field(default="", description="IDs extras separados por coma si es compartida")
    recurrencia: Optional[str] = Field(default=None, description="Formato 'diaria_HH:MM' o 'semanal_DIA_HH:MM' si aplica")

class ListarTareasSchema(BaseModel):
    pass

class CompletarTareaSchema(BaseModel):
    tarea_id: int = Field(description="ID numérico de la tarea a marcar como completada")

class ConsultarClimaSchema(BaseModel):
    ciudad: str = Field(default="Punto Fijo", description="Nombre de la ciudad para consultar el clima")

# --- HERRAMIENTAS EJECUTABLES ---

async def tool_crear_tarea(user_id: int, args: dict) -> str:
    try:
        data = CrearTareaSchema(**args)
        from datetime import datetime
        dt = datetime.strptime(data.fecha_hora, "%Y-%m-%d %H:%M")
        
        tarea = await TaskRepository.crear_tarea(
            user_id=user_id,
            titulo=data.titulo,
            fecha_hora=dt,
            notificar_a=data.notificar_a or "",
            recurrencia=data.recurrencia,
            prioridad=data.prioridad
        )
        tarea_id = tarea["id"] if tarea else "?"
        return f"✅ Tarea #{tarea_id} creada exitosamente: '{data.titulo}' para el {data.fecha_hora}."
    except Exception as e:
        return f"❌ Error al crear la tarea: {str(e)}"

async def tool_listar_tareas(user_id: int, args: dict) -> str:
    tareas = await TaskRepository.obtener_tareas_pendientes(user_id)
    if not tareas:
        return "📋 No tienes tareas pendientes actualmente."
    
    res = "📋 **Tus Tareas Pendientes:**\n"
    for t in tareas:
        prio = "🔺" if t['prioridad'] == 'alta' else "⏳"
        fecha_str = t['fecha_hora'].strftime("%Y-%m-%d %H:%M")
        res += f"  • #{t['id']} - {t['titulo']} ({fecha_str}) {prio}\n"
    return res

async def tool_completar_tarea(user_id: int, args: dict) -> str:
    try:
        data = CompletarTareaSchema(**args)
        exito = await TaskRepository.marcar_completada(data.tarea_id, user_id)
        if exito:
            return f"✅ Tarea #{data.tarea_id} marcada como completada."
        return f"⚠️ No se encontró la tarea #{data.tarea_id} o no te pertenece."
    except Exception as e:
        return f"❌ Error al completar la tarea: {str(e)}"

async def tool_consultar_clima(user_id: int, args: dict) -> str:
    data = ConsultarClimaSchema(**args)
    return await obtener_clima_async(data.ciudad)

# DEFINICIÓN JSON DE LAS TOOLS PARA GROQ / OPENAI SDK
TOOLS_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "crear_tarea",
            "description": "Registra una nueva tarea o recordatorio con fecha, hora y prioridad.",
            "parameters": CrearTareaSchema.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_tareas",
            "description": "Obtiene la lista de todas las tareas pendientes del usuario.",
            "parameters": ListarTareasSchema.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "completar_tarea",
            "description": "Marca una tarea existente como completada mediante su ID.",
            "parameters": CompletarTareaSchema.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_clima",
            "description": "Obtiene el pronóstico del clima para una ciudad específica.",
            "parameters": ConsultarClimaSchema.model_json_schema()
        }
    }
]