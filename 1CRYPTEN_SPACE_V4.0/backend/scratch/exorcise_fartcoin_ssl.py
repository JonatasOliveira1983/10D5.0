import psycopg2
import json
import sys

# Ensure utf-8 output to prevent charmap errors
sys.stdout.reconfigure(encoding='utf-8')

DATABASE_URL = "postgresql://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"

def main():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()

        print("Lendo paper_engine_state da tabela system_state...")
        cur.execute("SELECT data FROM system_state WHERE key = 'paper_engine_state'")
        row = cur.fetchone()
        
        if row and row[0]:
            data = row[0]
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    data = {}
            
            positions = data.get("positions", [])
            moonbags = data.get("moonbags", [])
            
            # Remover FARTCOIN
            new_pos = [p for p in positions if "FARTCOIN" not in p.get("symbol", "")]
            new_moon = [p for p in moonbags if "FARTCOIN" not in p.get("symbol", "")]
            
            if len(new_pos) != len(positions) or len(new_moon) != len(moonbags):
                data["positions"] = new_pos
                data["moonbags"] = new_moon
                
                # Salvar de volta
                update_query = "UPDATE system_state SET data = %s, updated_at = now() WHERE key = 'paper_engine_state'"
                cur.execute(update_query, (json.dumps(data),))
                
                print(f"FARTCOIN removido do paper_engine_state no Postgres! ({len(positions) - len(new_pos)} ordens deletadas)")
            else:
                print("FARTCOIN nao foi encontrado no paper_engine_state.")
        else:
            print("Nenhum paper_engine_state encontrado.")

        # Limpar slots 
        cur.execute("UPDATE slots SET symbol = NULL, status_risco = 'LIVRE', pnl_percent = 0, entry_price = 0, qty = 0, side = NULL, order_id = NULL, genesis_id = NULL WHERE symbol LIKE '%FARTCOIN%'")
        print("Slots limpos!")
        
        # Limpar moonbags
        cur.execute("DELETE FROM moonbags WHERE symbol LIKE '%FARTCOIN%'")
        print("Moonbags limpas!")

        # Limpar trade history
        cur.execute("DELETE FROM trade_history WHERE genesis_id LIKE '%FARTCOIN%' OR symbol LIKE '%FARTCOIN%'")
        print("Trade history limpo!")

        conn.commit()
        cur.close()
        conn.close()
        print("Commit realizado com sucesso.")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
