# 10D Sniper Operational Rules (V110.405)

## 1. Integridade de Timezone
- **SSOT (Single Source of Truth):** Todas as datas e horários devem usar `datetime.now(datetime.timezone.utc)`.
- **Naive Dates Proibidos:** O banco de dados Postgres (Railway) armazena datas sem fuso horário. O `BankrollManager` deve converter para UTC antes de qualquer comparação.

## 2. Prevenção de Duplicidade (Iron Locks)
- **Camada 1: Captain active_tocaias:** Bloqueia o processamento de sinais redundantes para o mesmo símbolo.
- **Camada 2: Captain processing_lock:** Trava atômica no nível de processamento de sinal (normalizado).
- **Camada 3: Bankroll execution_lock:** Garante que apenas uma ordem seja enviada por vez.
- **Camada 4: Collision Guard:** Verifica `paper_positions` e `slots_cache` (com `force_refresh=True`) antes de abrir qualquer posição.
- **Normalização Obrigatória:** Símbolos devem ser sempre limpos (`.replace(".P", "").upper()`) antes de serem usados como chaves de trava.

## 3. WebSocket Resilience
- **Blocklist Shield:** Ativos em manutenção ou com dados corrompidos (ex: `BONKUSDT`) devem ser ignorados no loop do WebSocket para evitar crash do serviço.
- **Auto-Recovery:** Se a conexão cair, o `BybitWS` deve reconstruir o estado de ADX e CVD em no máximo 10 segundos.

## 4. Reset Nuclear (Maintenance)
- **Protocolo de Limpeza:** Resets devem ser feitos via SQL (`nuclear_reset.sql`) ou scripts de wipe (`clear_paper_engine.py`) para garantir que o estado em memória e no banco sejam sincronizados.
- **Bankroll Sync:** Após o reset, o loop de sincronização do `BankrollManager` deve ser o primeiro a rodar para limpar slots fantasmas remanescentes na UI.

## 5. Gestão de IA e Visão (Funil de Custo Zero)
- **Filtro de Funil (Final Gate):** O Agente Visão deve ser sempre a última etapa de aprovação. O Capitão só invoca a IA Visual se todos os critérios algorítmicos (DNA, Macro, ADX) forem aprovados.
- **Soberania Gemini:** O sistema deve priorizar o uso nativo do Google Gemini (SDK `google.generativeai`) para todas as tarefas, minimizando o uso de intermediários como OpenRouter para reduzir custos e latência.

## 6. Git & Push
- **Repositório Oficial:** `JonatasOliveira1983/10D5.0`
- **Branch:** `main`
- **Push Obrigatório:** Toda correção de estabilidade deve ser commitada e enviada imediatamente.
