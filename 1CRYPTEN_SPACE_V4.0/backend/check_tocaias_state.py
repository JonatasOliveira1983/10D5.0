
import asyncio
from services.sovereign_service import sovereign_service
from services.agents.captain import captain_agent
import json

async def check_tocaias():
    print("--- Verificando Tocaias ---")
    
    # 1. Verificar Tocaias no banco de dados (RTDB)
    try:
        if sovereign_service.db:
            tocaias_ref = sovereign_service.db.reference('tocaias')
            tocaias = tocaias_ref.get()
            print(f"Tocaias no RTDB: {json.dumps(tocaias, indent=2) if tocaias else 'Nenhuma'}")
        else:
            print("Firebase DB não inicializado.")
    except Exception as e:
        print(f"Erro ao buscar tocaias no RTDB: {e}")

    # 2. Verificar estado interno do CaptainAgent
    try:
        active_tocaias = getattr(captain_agent, 'active_tocaias', {})
        print(f"Estado interno do CaptainAgent (active_tocaias): {json.dumps(active_tocaias, indent=2) if active_tocaias else 'Vazio'}")
    except Exception as e:
        print(f"Erro ao acessar active_tocaias no CaptainAgent: {e}")

    # 3. Verificar se o sistema está escaneando
    try:
        slots = await sovereign_service.get_active_slots()
        print(f"Slots ocupados: {sum(1 for s in slots if s.get('symbol'))}")
    except Exception as e:
        print(f"Erro ao buscar slots: {e}")

if __name__ == "__main__":
    asyncio.run(check_tocaias())
