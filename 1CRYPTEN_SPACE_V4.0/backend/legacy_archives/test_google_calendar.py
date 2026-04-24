import asyncio
import logging
from services.google_calendar_service import google_calendar_service
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestCalendar")

async def test_connection():
    logger.info("🕵️ Testando conexão com Google Calendar...")
    events = await google_calendar_service.list_upcoming_events(max_results=5)
    
    if events is not None:
        logger.info(f"✅ Conexão bem-sucedida! Encontrados {len(events)} eventos futuros.")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            logger.info(f"📅 Evento: {event.get('summary')} em {start}")
    else:
        logger.error("❌ Falha na conexão com Google Calendar.")

if __name__ == "__main__":
    asyncio.run(test_connection())
