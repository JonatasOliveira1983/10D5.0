import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.execution_protocol import execution_protocol

async def main():
    print("--- Simulando SL Hit Bug ---")
    
    # Exemplo: ONDOUSDT
    # Entry: 0.9632 (Long)
    # Target: 0.9824 (+2% price = +100% ROI @ 50x)
    # SL Inicial: 0.9487 (-1.5% price = -75% ROI @ 50x)
    
    # Simular Preço subindo para 0.9680 (ROI positivo, +24.9%)
    slot_data_buy = {
        "symbol": "ONDOUSDT",
        "side": "Buy",
        "entry_price": 0.9632,
        "current_stop": 0.9487,
        "structural_target": 0.9824,
        "slot_type": "TREND" # V15 usa TREND por padrão nas simulações
    }
    current_price_buy = 0.9680
    roi_buy = execution_protocol.calculate_roi(slot_data_buy["entry_price"], current_price_buy, "Buy")
    print(f"[BUY] Preço foi de {slot_data_buy['entry_price']} para {current_price_buy}. ROI = {roi_buy:.2f}%")
    close_b, reason_b, sl_b = await execution_protocol.process_order_logic(slot_data_buy, current_price_buy)
    print(f"-> Deveria fechar? {close_b} | Reason: {reason_b} | Novo SL: {sl_b}")


    # Exemplo: WLDUSDT.P Price=0.4205 | SL=0.423164 (Log do cliente)
    # O SL dele é MAIOR que o preço. Isso indica que é um SHORT / Sell.
    slot_data_sell = {
        "symbol": "WLDUSDT",
        "side": "Sell",
        "entry_price": 0.4180, # Entrada simulada abaixo do SL reportado
        "current_stop": 0.423164, # SL do log (acima do entry e acima do market)
        "structural_target": 0.4096,
        "slot_type": "TREND"
    }
    
    # No log, o preço atual lido era 0.4205 (que subiu contra o short e tá se aproximando do SL)
    current_price_sell = 0.4205
    roi_sell = execution_protocol.calculate_roi(slot_data_sell["entry_price"], current_price_sell, "Sell")
    print(f"\n[SELL] Preço foi de {slot_data_sell['entry_price']} para {current_price_sell}. ROI = {roi_sell:.2f}%")
    close_s, reason_s, sl_s = await execution_protocol.process_order_logic(slot_data_sell, current_price_sell)
    print(f"-> Deveria fechar? {close_s} | Reason: {reason_s} | Novo SL: {sl_s}")
    

if __name__ == "__main__":
    asyncio.run(main())
