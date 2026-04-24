import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.signal_generator import signal_generator

async def test_trap_logic():
    print("--- Testando Lógica Trap Pivot & Pullback Sniper ---")
    
    # Simular candidatos saindo do Estágio 1
    candidates = [
        {
            'symbol': 'BULL_TRAP_COIN',
            'side_label': 'Long', # Sardinhas comprando
            'cvd_val': 200000,
            'abs_cvd': 200000,
            'preliminary_score': 60,
            # Mockar a resposta da API para retornar 'sweep_and_reclaim_short'
            'mock_pattern': 'sweep_and_reclaim_short',
            'mock_trend': 'bullish'
        },
        {
            'symbol': 'BEAR_TRAP_COIN',
            'side_label': 'Short', # Sardinhas vendendo
            'cvd_val': -250000,
            'abs_cvd': 250000,
            'preliminary_score': 65,
            # Mockar a resposta da API para retornar 'sweep_and_reclaim_long'
            'mock_pattern': 'sweep_and_reclaim_long',
            'mock_trend': 'bearish'
        },
        {
            'symbol': 'PULLBACK_COIN',
            'side_label': 'Long',
            'cvd_val': 100000,
            'abs_cvd': 100000,
            'preliminary_score': 55,
            'mock_pattern': 'pullback_bounce',
            'mock_trend': 'bullish'
        },
        {
            'symbol': 'TRASH_COIN',
            'side_label': 'Long',
            'cvd_val': 50000,
            'abs_cvd': 50000,
            'preliminary_score': 45,
            'mock_pattern': 'none', # Rompimento falso/seco
            'mock_trend': 'sideways'
        }
    ]
    
    # Fazer um patching temporário na função de análise 1H para retornar nossos mocks
    original_get_1h = signal_generator.get_1h_trend_analysis
    
    async def mock_get_1h(symbol):
        for c in candidates:
            if c['symbol'] == symbol:
                return {'trend': c['mock_trend'], 'pattern': c['mock_pattern']}
        return {'trend': 'sideways', 'pattern': 'none'}
        
    signal_generator.get_1h_trend_analysis = mock_get_1h
    
    # Patch scalp 1m
    original_scalp = signal_generator.get_1m_scalp_analysis
    async def mock_scalp(symbol):
        return {'scalp_valid': False, 'rsi_1m': 50}
    signal_generator.get_1m_scalp_analysis = mock_scalp
    
    # Extrair e testar a função stage2_analyze (já que ela está empacotada no monitor_and_generate)
    # Como Stage2 é inner, recriamos a lógica aqui para o teste
    
    for candidate in candidates:
        trend_data = await signal_generator.get_1h_trend_analysis(candidate['symbol'])
        trend = trend_data['trend']
        pattern = trend_data['pattern']
        side_label = candidate['side_label']
        
        trend_bonus = 0
        pattern_bonus = 0
        trap_exploited = False
        pullback_sniped = False
        
        # Copiando a exata lógica implementada no signal_generator.py:
        if (side_label == "Long" and trend == "bullish") or (side_label == "Short" and trend == "bearish"):
            trend_bonus = 15
        elif trend == "sideways":
            trend_bonus = 0
        else:
            trend_bonus = -20
            
        if side_label == "Long" and pattern == 'sweep_and_reclaim_short':
            side_label = "Short"
            pattern_bonus = 40
            trap_exploited = True
            trend_bonus = 15 if trend == "bearish" else 0
        elif side_label == "Short" and pattern == 'sweep_and_reclaim_long':
            side_label = "Long"
            pattern_bonus = 40
            trap_exploited = True
            trend_bonus = 15 if trend == "bullish" else 0
        elif (side_label == "Long" and pattern == 'pullback_bounce') or \
             (side_label == "Short" and pattern == 'pullback_rejection'):
            pattern_bonus = 35
            pullback_sniped = True
        elif pattern in ['sweep_and_reclaim_long', 'sweep_and_reclaim_short']:
            pattern_bonus = 30
        elif pattern in signal_generator.valid_entry_patterns:
            pattern_bonus = 10
        elif pattern in ['none', 'unknown']:
            pattern_bonus = -30
            
        tactical_score = candidate['preliminary_score'] + trend_bonus + pattern_bonus
        
        print(f"\n[{candidate['symbol']}]")
        print(f"Original Side: {candidate['side_label']} | Pattern: {pattern}")
        print(f"Final Side...: {side_label} (Trap Pivot: {trap_exploited})")
        print(f"Bonus Padrão.: {pattern_bonus} (Pullback Sniped: {pullback_sniped})")
        print(f"Score Tático.: {tactical_score}")
        if tactical_score < 30:
            print("Status.......: ❌ REJEITADO (Pontuação < 30 no funil)")
        else:
            print("Status.......: ✅ APROVADO PARA ESTÁGIO 3")

    # Restore
    signal_generator.get_1h_trend_analysis = original_get_1h
    signal_generator.get_1m_scalp_analysis = original_scalp

if __name__ == "__main__":
    asyncio.run(test_trap_logic())
