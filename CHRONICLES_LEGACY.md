# 📜 CHRONICLES LEGACY - 10D Sniper
### O Arquivo Histórico de Evolução Tática (Era Antiga)

Este documento contém o registro de todas as versões anteriores à V110.100 Alpha Revolution. Para o estado operacional ATUAL, consulte o [MASTER_ARCHITECTURE.md](file:///c:/Users/spcom/Desktop/10D-3.0%20-%20Qwen/MASTER_ARCHITECTURE.md).

---

## 🏗️ CHANGELOG LEGACY (V110.23 -> V110.144)

*   **V110.175: RAILWAY SOVEREIGN EMANCIPATION 🚂🛡️ [APR 24]**
    *   **Firebase Purge:** Remoção total do `firebase-admin` e desativação de todas as rotas Firestore/RTDB.
    *   **SovereignService:** Implementação do novo singleton de comunicação e persistência nativa.
    *   **Postgres Native:** Migração de toda a lógica de banca e slots para PostgreSQL local no Railway.
    *   **WebSocket Pulse:** Novo motor de broadcast nativo para o Cockpit UI (`RADAR_PULSE` full support).

*   **V110.144: DAILY GOAL MONITOR & OMNIPRESENCE 🎯⚡ [APR 20]**
    *   **Daily Target Monitor:** Implementação de rastreador de "10 Gains por dia" e PnL 24h injetado no topo do Radar.
    *   **Blitz Omnipresence:** Remoção de travas de contra-tendência (ADX > 30) no BlitzSniper para operação total (Alta/Baixa/Lateral).
    *   **Standard Risk:** Padronização de margem fixa em 10% por ordem para consistência da meta diária de 10 vitórias.
    *   **UI Intelligence:** Injeção de card de progresso (`🎯 OBJETIVO DIÁRIO`) como prioridade 0 no Radar RTDB.

*   **V110.143: DYNAMIC RADAR FOCUS & LATERAL THROTTLE 🧠🛡️ [APR 20]**
    *   **Radar Throttle:** Sistema dinâmico que oculta sinais Swing ordinários (Score < 95) em mercados laterais (ADX < 20) para dar visibilidade total à Blitz.
    *   **Sentinel Blitz-Bypass:** Isenção total da trava lateral para sinais M30, permitindo caçadas agressivas em compressão.
    *   **Agility Optimization:** Redução do intervalo de scan para 120s e remoção de loops redundantes no motor core (main.py).

*   **V110.136: ELITE 30M SNIPER — BLITZ EXPANSION ⚡🏹 [APR 18]**

    *   **BlitzSniper Deployment:** Novo agente focado em reversões no TF 30M (Wick Reclaim, SMA Crossover e Fibonacci Golden Zone).
    *   **Elite 30M Logic:** Slot 1 exclusivo para a estratégia Blitz, operando com alavancagem forçada de **50x** (independente do DNA do ativo).
    *   **Elite Extraction Protocol:** Alvo de saída fixo em **300% ROI** e trava de lucro rápida em **150% ROI** (Stop-Gain). Sem migração para Moonbag.
    *   **Environment Stabilization:** Migração completa para **Python 3.10.11** nativo (`venv_elite`), resolvendo crashes de compilação e instabilidade em dependências críticas (pandas/numpy).
    *   **Critical Bugfixes:**
        *   Correção de `NameError: is_decorrelated` noAgente Capitão.
        *   Tratamento de `KeyError: id` para sinais injetados localmente pelo motor Blitz.
        *   Otimização do loop `scan_and_inject` para varredura automatizada da Elite Watchlist.

*   **V110.135: ADAPTIVE LEVERAGE SHIELD & RISK EQUALIZER 🛡️⚖️ [APR 18]**
    *   **Quartermaster Integration:** Implementação do Agente Intendente para gerenciamento de alavancagem dinâmica.
    *   **Dynamic Scaling:** 50x (Smooth), 20x (Jumpy), 10x (Extreme) baseado em `wick_intensity`.
    *   **Risk Equalization:** Automatização do cálculo de margem para manter o valor notional estável em diferentes alavancagens.
    *   **Unified ROI SL:** Escadinha de 5 degraus recalibrada para ser 100% agnóstica à alavancagem via ROI percentual (30%, 70%, 110%, 150%).
    *   **ADX Wick Guard:** Trava de segurança que bloqueia ativos de alta volatilidade (`wick > 0.7`) se o `ADX < 25`.
    *   **Tactical Intelligence Panel:** Nova interface no cockpit para monitoramento de *Correlation Shield*, *Adaptive Weights* e *Guardian Hedge*.
    *   **Software Shielding:** Blindagem contra erros 500. Implementado cast de tipos SQLite (`float/int`) no motor de backtest e `Row Factory` para acesso nominal resiliente.
    *   **UI Reference Fix:** Correção de falhas de referência no React (`tactical_events` scope), garantindo que a auditoria visual nunca trave.
    *   **CVD WebSocket Fix:** Reparo de escopo tático (`data_snapshot`) no Websocket, restaurando o radar de volume.
    *   **Safe Ranking Key:** Ordenador resiliente no Bibliotecário contra dados de tipo misto.

*   **V110.62: TACTICAL INTELLIGENCE PILLARS 🛡️📊🏹 [APR 12]**
    *   **Correlation Shield:** Implementação de cálculo de correlação de Pearson no Websocket para evitar exposição em ativos "espelhados".
    *   **Librarian Auditor:** Novo agente de feedback loop que ajusta os pesos de confiança (Adaptive Weighting) baseado no Win-Rate real dos sensores.
    *   **Guardian Hedge (Slot Zero):** Ativação de seguro automático (Short BTC) em caso de quedas violentas/flash crashes detectados pelo Oráculo.

*   **V110.61: PROTOCOLO GÊNESE & AMNESIA-GUARD 🧬 [APR 12]**
    *   **Order Genesis:** Implementação da certidão de nascimento imutável para ordens. Persistência total de scores (Librarian/Captain) e metadados táticos antes do disparo.
    *   **Amnesia-Guard (Auto-Recovery):** O motor Paper agora re-adota ordens órfãs do Firestore no boot, tornando o sistema resiliente a reinicializações repentinas do Cloud Run.
    *   **Genesis-Shield:** Blindagem do Ghostbuster. Ordens com Gênese ativa possuem imunidade de 30 minutos contra purgas acidentais.

*   **V110.60: ELITE PROGRESSION & MOONBAG FREEDOM 💎 [APR 12]**
    *   **Relaxed Escadinha:** Degrau de 110% ROI recalibrado para stop em **+70%** (0.8% respiro). Emancipação (150% ROI) agora trava em **+100%**.
    *   **Infinite Profit Strategy:** Desativação do TP atômico por Fibonacci em Moonbags.
    *   **Inertia Shadow Shield:** Saída por inércia expandida para **8h** (28800s).

*   **V110.50: INFRASTRUCTURE RESILIENCE & WATCHDOG 🚀 [APR 12]**
    *   **WebSocket Worker Decoupling:** Migração para processamento via `asyncio.Queue`.
    *   **Connectivity Watchdog:** Reinicialização forçada automática do feed de dados após silêncio >30s.

*   **V110.47: LIBRARIAN-CAPTAIN INTEGRATION ENFORCEMENT ⚓📚 [APR 12]**
    *   **Real-time DNA Audit:** Capitão consulta o `asset_dna` antes de cada entrada.
    *   **Adaptive Ambush Mode:** Ativação automática do estilo `AMBUSH` para ativos `HIGH_RISK`.

*   **V110.42.0: THE COMPASS (O BÚSSOLA) - 100% ROI TELEMETRY 📡 [APR 12]**
    *   **The Compass HUD:** Nova interface de carregamento premium no Intelligence Lab.

*   **V110.41.0: EAGLE VISION V2 — INSTITUTIONAL ANALYSIS SUITE 🦅 [APR 11]**
    *   **Equity Curve Sync:** Gráfico de evolução da banca no cockpit.
    *   **Support/Resistance Zones:** Renderização de Pivot Points.

*   **V110.38.0: ABSOLUTE TRAP SHIELD & NECTAR BYPASS 💀🍯 [APR 10]**
    *   **Absolute Trap Shield:** Bloqueio de ativos `💀 TRAP ZONE`.
    *   **Nectar Elite Bypass:** Ativos `🍯 ELITE NECTAR` ignoram tendência macro se Score >= 95.

*   **V110.30.0: SNIPER BACKTEST LAB (PILOT'S LAB) [APR 07]**
    *   **Simulation Engine V1.0:** Motor processa klines SQLite contra a lógica Sentinel.

*   **V110.25.0: THE SENTINEL PROTOCOL [APR 06]**
    *   Bypass de gas e janelas diplomáticas de SL.

*   **V110.23.0 - V110.23.10**
    *   [Estabilidades Core, Hotfix UI Dashboard, Paper Restore Logic].
