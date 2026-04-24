# MASTER_ARCHITECTURE.md — 10D Sniper V110.173
# Fonte da Verdade Arquitetural — Sincronizado com RULES.md

## 🚀 ROADMAP DE VERSÕES & MARCOS TÉCNICOS

*   **V110.174: SELECTIVE INTELLIGENCE UPGRADE — VANGUARD [APR 24]**
    - **Asset Trend Guard**: Implementação de trava obrigatória para alinhar trades com a tendência H4 em ativos de volatilidade EXTREME.
    - **Spring Directionality**: Restrição do bypass de mola para seguir rigorosamente a tendência principal do ativo.
    - **Macro Shield**: Elevação da régua de Macro Score para ativos propensos a armadilhas (Trap-Prone).

*   **V110.173: ELITE FLEET EXPANSION — TOP 40 🌸 [APR 23]**
    - **Elite-40 Fleet**: Expansão do monitoramento de ativos `Spring Elite` de 20 para 40 pares, dobrando a capacidade de busca por setups explosivos.
    - **Spring Shield Bypass**: Consolidação do mecanismo de bypass que permite entradas em ativos `Trap-Prone` estritamente quando marcados como `MOLA` pelo Bibliotecário.
    - **UI Synchronization**: Alinhamento do Radar e Slots para exibir corretamente as badges BLITZ e SWING. Inclusão do selo `🧬 GENESIS: ID` com fallback para `order_id` para garantir rastreabilidade total.
    - **Estado Zero Global**: Re-inicialização completa do sistema para garantir integridade após a expansão da frota.

*   **V110.172: GENESIS IRON LOCK — RACE CONDITION FIX 🔒 [APR 22]**
    - **Atomic Genesis ID:** O `genesis_id` agora é gerado APÓS a confirmação da Exchange, usando o `orderId` Bybit como chave primária (`BLZ-<BYBIT_ORDER_ID>-<SYM>`). Colisões de ID entre ordens simultâneas são matematicamente impossíveis.
    - **Global In-Memory Lock:** O `CaptainAgent._process_single_signal` agora verifica `bankroll_manager.pending_slots` antes de qualquer processamento. Se o símbolo já está em transição, o sinal duplicado é descartado com `[GLOBAL IN-MEMORY LOCK]`.
    - **Paper Desync Guard:** `can_open_new_slot` e `get_specific_empty_slot` agora consultam `bybit_rest_service.paper_positions` em memória antes de ceder um slot vago no Firestore. Evita overwrite silencioso de posições ativas quando Firebase e memória estão fora de sincronia.
    - **Estado Zero V110.172:** Nuclear Reset completo — slots, trade_history, orders_genesis, banca ($100) e paper_storage.

*   **V110.171: SEAMLESS PREMIUM — UI PURGE ✨ [APR 22]**
    - **Seamless Design Protocol:** Remoção absoluta de bordas horizontais e verticais entre Header, Sidebar e Main Content.
    - **Glassmorphism Continuity:** Refinamento dos filtros de blur e opacidade para transições suaves entre componentes fixos.
    - **Visual Cleanup:** Eliminação de artefatos brancos (border-white) que degradavam a estética Grayscale Premium.
    - **Genesis Visibility:** Integração e renderização proeminente do Genesis ID nas ordens ativas (SlotCards), garantindo conformidade com a regra V110.160.

*   **V110.170: BLITZ RECOVERY — MOMENTO MOLA 🌸 [APR 22]**
    - **Blitz Recovery Protocol:** Restauração da execução Blitz com foco total em ativos Elite Mola.
    - **Whale Trap Reversal:** Inversão automática de ordens ao detectar armadilhas institucionais.
    - **Phantom Fix:** Removido bloqueio crítico no CaptainAgent que impedia ordens em tendências de alta.
    - **Radar Visibility:** Forçada a injeção de sinais `spring_elite_list` no RTDB para o Cockpit.

*   **V110.168: BLUE CHIP ABSOLUTE BLOCK 🛡️ [APR 22]**
    - **Absolute Shield:** Implementada verificação de blocklist no `_process_single_signal` do CaptainAgent.
    - **Blue Chip Purge:** BTC, ETH, SOL e BNB removidos de todas as listas de fallback e bloqueados em todos os agentes.
    - **50x Focus:** Garantia de que o sistema opere apenas em ativos com alavancagem padrão de 50x.

*   **V110.167: STABLECOIN PURGE — VOLATILITY FOCUS 🛡️ [APR 22]**
    - **Stablecoin Blocklist:** USDE, USDC, EURS, DAI, FDUSD adicionados à blocklist.
    - **Volatility Guard:** Garantia de que o Blitz Sniper foque apenas em ativos com flutuação real.

*   **V110.166: SPRING ANTICIPATION — ELITE PULSE 🎯 [APR 22]**
    - **Spring Anticipation Bonus:** Bônus de +20 pts para ativos Elite Mola em compressão.
    - **Strike Execution style:** Força entrada imediata no primeiro pulso após SMA Cross (Bypass de Pullback).
    - **Volume Lenience:** Redução da dependência de volume institucional para entradas "pré-explosão".
*   **V110.165: ELITE SPRING STRATEGY 🌸 [APR 22]**
    - **Librarian Spring Audit:** Backtest de 15 dias (M30) identifica os 20 ativos mais explosivos pós-compressão.
    - **Blitz Focus:** Blitz Sniper restrito à `spring_elite_list` para máxima assertividade.
    - **Elite UI:** Visualização horizontal da lista Top 20 no Radar de Inteligência.
*   **V110.160: REACTIVE SPRING & GENESIS SYNC 🚀 [APR 21]**
    - **Reactive Spring:** Mola detection moved to Blitz Sniper (M30 real-time) for zero-latency execution.
    - **Genesis Observability:** High-visibility Genesis ID display in Cockpit SlotCards.
    - **is_spring_strike persistence:** Atomic tracking of Spring setups for audit and UI feedback.
*   **V110.155: FLEET STRIKE REFINED — GENESIS [APR 21]**
    - **GENESIS ID:** Implementação de ID único (RG da Ordem) para rastreio total do ciclo de vida.
    - **STRIKE DOCTRINE:** Refinamento do bypass de Tocaia para setups de alta compressão (Spring).
    - **Firebase Atomic Sync:** Registro de certidão de nascimento da ordem no Firestore.
*   **V110.150: STRIKE DOCTRINE — ATTACK MODE [APR 21]**
    - **Strike Execution:** Bypass total de pullbacks para sinais Elite (Score > 92).
    - **Blitz Aggression:** Redução de thresholds de scan e cooldowns para ocupação máxima de slots.
    - **Lateral Guillotine Bypass:** Blitz ignora ADX < 20 se houver Whale Consensus.
*   **V110.149: LIBRARIAN RIGOR & LIQUIDITY [APR 20]**
    - **Trap Shield:** Bloqueio sumário de ativos `is_trap_prone`.
    - **Blitz Optimization:** Score mínimo reduzido para 70 para aumentar volume de ordens.
*   **V110.144: RADAR DE INTELIGÊNCIA UNIFICADO [APR 20]**
    - **Dashboard Central:** Integração de Metas Diárias (10 Gains/Dia) no Radar.
    - **Lateral Throttle:** Ocultação de sinais Swing em baixa volatilidade.
*   **V110.141: BLITZ LOOP OPTIMIZATION [APR 20]**
    - **Scan Interval:** Reduzido de 5 min para 2 min.
    - **Priority Queue:** Blitz inyectado com prioridade negativa (execução imediata).
*   **V110.137: GENESIS PROTOCOL — DUAL SLOTS [APR 19]**
    - **Slot Architecture:** Slots 1-2 (Blitz) / Slots 3-4 (Swing).
    - **Collision Guard:** Impede duplicidade de ativos entre slots e moonbags.
    - **Genesis ID:** RG da Ordem gerado no momento da abertura.

(Histórico anterior omitido para brevidade...)

---
*Documento atualizado em: 2026-04-24 (V110.174) Sincronizado*
