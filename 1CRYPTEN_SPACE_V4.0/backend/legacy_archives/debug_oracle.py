import asyncio
import sys
import os

# Ajustar o PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.agents.oracle_agent import oracle_agent

async def debug_oracle():
    print("🔮 [ORACLE-DEBUG] Buscando contexto validado...")
    context = oracle_agent.get_validated_context()
    print(f"Status: {context.get('status')}")
    print(f"Regime: {context.get('regime')}")
    print(f"Direção BTC: {context.get('btc_direction')}")
    print(f"ADX BTC: {context.get('btc_adx')}")
    print(f"Remaining Wait: {context.get('remaining_wait')}s")
    print(f"Is Stale: {context.get('is_stale')}")
    print(f"Last Updated: {context.get('last_updated')}")

if __name__ == "__main__":
    asyncio.run(debug_oracle())
