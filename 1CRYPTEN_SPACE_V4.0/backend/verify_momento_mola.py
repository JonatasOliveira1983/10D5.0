
import asyncio
import logging
import sys
import os

# Adiciona o diretório backend ao sys.path para importações
sys.path.append(os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend"))

from services.agents.librarian import librarian_agent

async def test_mola_logic():
    print("🔍 Testando Lógica de Momento Mola no Bibliotecário...")
    
    # Mock de klines (100 klines)
    # Cenário de compressão: as últimas 20 barras têm desvio padrão baixo
    klines_compressed = []
    for i in range(80):
        klines_compressed.append([0, 0, 0, 100 + (i % 5), 0]) # Long term vol ~1.4
    for i in range(20):
        klines_compressed.append([0, 0, 0, 102, 0]) # Short term vol 0
        
    # Injetando mock no cache do bibliotecário (precisamos acessar o cache ou simular a função)
    # Como a lógica está dentro de perform_full_market_study, vamos testar uma extração isolada se possível
    # ou rodar o estudo para um par real e ver o log.
    
    symbol = "SUIUSDT"
    print(f"📡 Buscando DNA para {symbol}...")
    dna = await librarian_agent.get_asset_dna(symbol)
    
    print(f"📊 DNA Resultado:")
    print(f"   - Is Spring Moment: {dna.get('is_spring_moment')}")
    print(f"   - Compression Score: {dna.get('compression_score')}")
    print(f"   - Nectar Seal: {dna.get('nectar_seal')}")
    
    if "compression_score" in dna:
        print("✅ Coluna de compressão detectada no DNA.")
    else:
        print("❌ Coluna de compressão AUSENTE no DNA.")

if __name__ == "__main__":
    asyncio.run(test_mola_logic())
