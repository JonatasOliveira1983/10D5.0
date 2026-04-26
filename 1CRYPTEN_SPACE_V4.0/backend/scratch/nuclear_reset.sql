-- 10D Sniper V110.261 NUCLEAR RESET SQL
-- Executa a limpeza total dos slots, histórico e reseta a banca para $100

-- 1. Resetar Slots Ativos
UPDATE slots 
SET symbol = NULL, 
    side = NULL, 
    qty = 0, 
    entry_price = 0, 
    entry_margin = 0, 
    current_stop = 0, 
    initial_stop = 0, 
    target_price = 0, 
    liq_price = 0, 
    pnl_percent = 0, 
    status_risco = 'LIVRE', 
    order_id = NULL, 
    genesis_id = NULL, 
    fleet_intel = NULL, 
    pensamento = NULL,
    symbol_adx = 0,
    market_regime = NULL,
    unified_confidence = 50,
    timestamp_last_intel = 0,
    sentinel_first_hit_at = 0,
    timestamp_last_update = 0,
    opened_at = 0;

-- 2. Limpar Histórico de Trades (Vault)
DELETE FROM trade_history;

-- 3. Resetar Banca para $100
UPDATE banca_status 
SET saldo_total = 100.0, 
    risco_real_percent = 0, 
    slots_disponiveis = 4, 
    status = 'IDLE' 
WHERE id = 1;

-- 4. Limpar Moonbags
DELETE FROM moonbags;

-- 5. Resetar Ciclos da Vault
UPDATE vault_cycles 
SET sniper_wins = 0, 
    cycle_number = 1, 
    cycle_profit = 0, 
    cycle_losses = 0, 
    total_trades_cycle = 0, 
    cycle_gains_count = 0, 
    cycle_losses_count = 0, 
    vault_total = 0, 
    accumulated_vault = 0,
    cycle_start_bankroll = 100.0
WHERE id = 1;

-- 6. Limpar Estado do Motor Paper (Ressurreição Prevent)
DELETE FROM system_state WHERE key = 'paper_engine_state';

-- 7. Limpar Ordem Genesis (Opcional, mas recomendado para reset total)
DELETE FROM order_genesis;
