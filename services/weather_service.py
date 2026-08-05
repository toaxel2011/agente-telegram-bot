import httpx
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# Coordenadas geográficas
COORDENADAS: Dict[str, Tuple[float, float]] = {
    "caracas": (10.4806, -66.9036),
    "maracaibo": (10.6317, -71.6406),
    "valencia": (10.1620, -68.0077),
    "barquisimeto": (10.0739, -69.3228),
    "maracay": (10.2469, -67.5958),
    "ciudad guayana": (8.3518, -62.6410),
    "barcelona": (10.1333, -64.6833),
    "maturín": (9.7457, -63.1833),
    "san cristóbal": (7.7667, -72.2333),
    "merida": (8.6000, -71.1333),
    "punto fijo": (11.7083, -70.1989),
}

CLIMA_CODIGOS: Dict[int, str] = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
    3: "Nublado", 45: "Niebla", 48: "Niebla con escarcha",
    51: "Llovizna ligera", 53: "Llovizna moderada", 55: "Llovizna densa",
    61: "Lluvia ligera", 63: "Lluvia moderada", 65: "Lluvia intensa",
    80: "Chubascos ligeros", 81: "Chubascos moderados", 82: "Chubascos violentos",
    95: "Tormenta", 96: "Tormenta con granizo ligero", 99: "Tormenta con granizo intenso"
}

async def obtener_clima_async(ciudad: str = "Punto Fijo") -> str:
    """Consulta el pronóstico del clima de forma asíncrona mediante la API de Open-Meteo."""
    ciudad_key = ciudad.lower().strip()
    lat, lon = COORDENADAS.get(ciudad_key, COORDENADAS["punto fijo"])
    
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,weathercode"
        f"&timezone=America%2FCaracas&forecast_days=1"
    )
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            daily = data["daily"]
            temp_max = daily["temperature_2m_max"][0]
            temp_min = daily["temperature_2m_min"][0]
            weather_code = daily["weathercode"][0]
            clima_texto = CLIMA_CODIGOS.get(weather_code, "Desconocido")
            
            return f"🌤️ Clima en {ciudad.capitalize()}: {clima_texto}, máx {temp_max}°C / mín {temp_min}°C"
    except Exception as e:
        logger.error(f"Error consultando el clima para {ciudad}: {e}")
        return "⚠️ No se pudo obtener el pronóstico del clima en este momento."