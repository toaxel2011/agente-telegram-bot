import pytz
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    GROQ_API_KEY: str
    DATABASE_URL: str
    ADMIN_ID: int
    PARTNER_ID: int = 0
    
    # Modelos de Groq
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    FALLBACK_MODEL_NAME: str = "llama-3.1-8b-instant"
    WHISPER_MODEL: str = "whisper-large-v3"
    TEMPERATURE: float = 0.2

    # Configuración de Servidor
    PORT: int = 8080
    TIMEZONE_STR: str = "America/Caracas"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def TIMEZONE(self):
        return pytz.timezone(self.TIMEZONE_STR)

settings = Settings()