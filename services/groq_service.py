import logging
from groq import AsyncGroq
from config.settings import settings

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def transcribir_audio(self, file_path: str) -> str:
        """Transcribe notas de voz asíncronamente con Whisper Large v3."""
        try:
            with open(file_path, "rb") as audio_file:
                transcription = await self.client.audio.transcriptions.create(
                    model=settings.WHISPER_MODEL,
                    file=audio_file,
                    language="es",
                    response_format="text"
                )
            return transcription.strip()
        except Exception as e:
            logger.error(f"Error en transcripción Whisper: {e}")
            raise e

groq_service = GroqService()