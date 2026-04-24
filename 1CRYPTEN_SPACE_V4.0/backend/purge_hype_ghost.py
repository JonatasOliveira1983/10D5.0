import asyncio
import sys
import os

# Ajustar o path para encontrar as services
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

async def purge_hype():
    print("Iniciando Purga de HYPEUSDT...")
    
    try:
        from services.firebase_service import firebase_service
        await firebase_service.initialize()
        await firebase_service.initialize_db()
        
        # 1. Buscar no Firestore (Moonbags)
        print("Buscando HYPEUSDT no Firestore...")
        moonbags = await firebase_service.get_moonbags()
        hype_moons = [m for m in moonbags if m.get('symbol') == 'HYPEUSDT']
        
        if hype_moons:
            for m in hype_moons:
                m_id = m.get('id')
                print(f"Removendo Moonbag {m_id} de HYPEUSDT...")
                # Usando o método oficial da service
                await firebase_service.remove_moonbag(m_id, reason="PURGE_GHOST_ROI_CORRUPT")
        else:
            print("Nenhuma Moonbag de HYPEUSDT encontrada no Firestore.")

        # 2. Limpar RTDB Outcomes
        if firebase_service.rtdb:
            print("Limpando RTDB outcomes de HYPEUSDT...")
            try:
                outcomes_ref = firebase_service.rtdb.child("signals_v110").child("outcomes")
                all_outcomes = outcomes_ref.get()
                if all_outcomes:
                    for key, val in all_outcomes.items():
                        if val.get('symbol') == 'HYPEUSDT':
                            print(f"Deletando outcome RTDB: {key}")
                            outcomes_ref.child(key).remove()
            except Exception as e:
                print(f"Erro ao limpar RTDB: {e}")

        # 3. Limpar Genesis Registry
        print("Limpando registros Genese...")
        try:
            genesis_ref = firebase_service.db.collection("genesis_orders")
            docs = genesis_ref.where("symbol", "==", "HYPEUSDT").stream()
            count = 0
            for doc in docs:
                doc.reference.delete()
                count += 1
            print(f"OK: {count} registros Genese deletados.")
        except Exception as e:
            print(f"Erro ao limpar Genesis: {e}")

        print("\nPurga Concluida com Sucesso!")

    except Exception as e:
        print(f"Erro Fatal durante a purga: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(purge_hype())
