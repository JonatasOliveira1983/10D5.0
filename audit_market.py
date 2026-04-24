
import asyncio
import sys
import os
import time

# Adiciona o backend ao path
sys.path.insert(0, os.path.join(os.getcwd(), '1CRYPTEN_SPACE_V4.0/backend'))

from services.bybit_rest import bybit_rest_service
from services.signal_generator import signal_generator
from services.firebase_service import firebase_service

async def audit():
    print("--- AUDITORIA TÁTICA SNIPER ---")
    
    # 1. BTC Price & Variation
    btc = await bybit_rest_service.get_tickers('BTCUSDT')
    ticker = btc.get('result', {}).get('list', [{}])[0]
    btc_p = ticker.get('lastPrice', '0')
    btc_24h = ticker.get('price24hPcnt', '0')
    
    # 2. Market Regime (ADX)
    regime_data = await signal_generator.detect_market_regime('BTCUSDT')
    adx = regime_data.get('adx', 0)
    regime_name = regime_data.get('regime', 'N/A')
    
    # 3. Oracle Context (Dominance/Correlation)
    oracle_context = await firebase_service.get_oracle_context()
    if oracle_context:
        dom = oracle_context.get('dominance', 50.0)
        corr = oracle_context.get('btc_correlation', 30)
    else:
        dom = 50.0
        corr = 30
        print("(!) Oracle Context não encontrado no Firestore. Usando defaults.")
    
    print(f"BTC Preço Real: ${float(btc_p):,.2f}")
    print(f"BTC Var 24h: {float(btc_24h):+.2f}%")
    print(f"ADX Atual: {adx:.2f}")
    print(f"Regime: {regime_name}")
    print(f"Dominância: {dom:.1f}%")
    print(f"Correlação BTC: {corr}%")
    
    print("\n--- COMPARAÇÃO COM RELATÓRIO DO ALMIRANTE ---")
    diff_p = abs(float(btc_p) - 70850.00) / 70850.00 * 100
    diff_adx = abs(adx - 58.58)
    
    print(f"Divergência Preço: {diff_p:.2f}%")
    print(f"Divergência ADX: {diff_adx:.2f}")
    print("------------------------------------------")

if __name__ == "__main__":
    asyncio.run(audit())
