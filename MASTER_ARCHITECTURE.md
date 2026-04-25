# MASTER_ARCHITECTURE.md — 10D Sniper V110.208
# Fonte da Verdade Arquitetural — Sincronizado com RULES.md

## 🚀 ROADMAP DE VERSÕES & MARCOS TÉCNICOS

*   **V110.208: SELF-HEALING & BLACK BOX PERSISTENCE [APR 24]**
    - **Auto-Migration:** Implementação de migração automática de esquema no boot para corrigir divergências de colunas no Postgres.
    - **Black Box Protocol:** Backup de emergência em JSON (`emergency_trades.json`) para garantir 100% de persistência caso o banco falhe.

*   **V110.207: BRANDING RESTORATION & CACHE SHIELD [APR 24]**
    - **Logo Restoration:** Reintegração do logo oficial `logo10DTrasp.png` com transparência nativa.
    - **Cache-Busting V4:** Implementação de sufixos de versão nas imagens para forçar atualização em todos os navegadores.

*   **V110.203: DATA INTEGRITY & ATOMIC ARCHIVAL [APR 24]**
    - **Atomic free_slot:** Refatoração do método de liberação de slots para arquivar obrigatoriamente trades no histórico antes da limpeza.
    - **Zero Data Loss:** Garantia de que ordens encerradas por Auditoria ou Reset de Fábrica sejam preservadas no Vault.

*   **V110.202: BOOT PERSISTENCE & SYNC RELIABILITY [APR 24]**
    - **Forced Boot Sync:** Remoção da lógica de pular sincronia de slots no `main.py`; o robô agora recupera o estado do banco no início.
    - **Persistence Shield:** Proteção contra perda de ordens durante deploys ou reinicializações do servidor Railway.

*   **V110.201: BRANDING SIMPLIFICATION & OPEN ACCESS [APR 24]**
    - **System 10D UI:** Simplificação visual da tela de login para um estilo minimalista.
    - **Access Key:** Configuração da chave padrão `123` para facilitar o acesso livre do administrador.

*   **V110.200: BLINDAGEM PHASE & SOVEREIGN AUTH [APR 24]**
    - **Fortress Auth:** Sistema de login soberano com autenticação JWT/Token no backend e frontend.
    - **Guardian Agent:** Implementação do agente de custódia para manutenção de integridade e segurança.
    - **Scrubbing:** Limpeza de >150 arquivos legados, reduzindo a dívida técnica e poluição do backend.

*   **V110.199: PRODUCTION DOMAIN FINALIZATION [APR 24]**
    - **CORS Hardening:** Inclusão de variantes `www` e domínios de produção no backend para eliminar bloqueios de segurança.
    - **Full Domain Parity:** Sincronização de regras de acesso para `1crypten.space`.

*   **V110.198: DOMAIN & SSL HARDENING [APR 24]**
    - **WSS Protocol Fix:** Inteligência de detecção de protocolo no `cockpit.html` para suportar `wss://` automaticamente em domínios HTTPS.
    - **Custom Domain Ready:** Ajustes de roteamento para garantir conectividade em `1crypten.space`.

*   **V110.197: RUNTIME STABILITY & SCOPE HARDENING [APR 24]**
    - **Execution Fix:** Resolvido `NameError: is_spring_strike` no `BankrollManager` via pré-declaração de variáveis de controle.
    - **Database Sync Fix:** Resolvido `TypeError` de múltiplos valores para o argumento `id` em atualizações de banca e slots.

*   **V110.196: DATABASE HARDENING & RATE LIMIT SHIELD [APR 24]**
    - **SQL Schema Sync:** Modelo `Slot` no Postgres atualizado para suportar 100% dos campos de telemetria e inteligência (margin, leverage, fleet_intel).
    - **CoinGecko Shield:** Implementação de `asyncio.Lock` no `MacroAnalyst` para evitar erros 429 durante picos de análise de sinais.
    - **Nuclear Reset:** Disponibilizado script `nuclear_schema_reset.py` para sincronização forçada de ambiente.

*   **V110.195: ORPHAN GENESIS PROTOCOL [APR 24]**
    - **Genesis Recovery:** Ordens re-adotadas da exchange (órfãs) agora geram automaticamente um `genesis_id` para identificação no Cockpit.
    - **ID Persistence:** Garantia de que o `genesis_id` e o `order_id` sejam preservados durante os ciclos de sincronização real-time do Bankroll.

*   **V110.194: CAPTAIN SCOPE STABILIZATION [APR 24]**
    - **Captain Unbound Fix:** Correção de falha fatal (UnboundLocalError) ao processar sinais SNIPER/Elite; variáveis de escopo (`is_decorrelated`, `is_spring_vanguard`) agora inicializadas corretamente.
    - **Vanguard Stability:** Garantia de que sinais Vanguard passem pelas travas de tendência H4 sem quebras de execução.

*   **V110.193: GHOST-LOCK PURGE & SYMBOL HARDENING [APR 24]**
    - **Ghost-Lock Resolution:** Implementação do protocolo de Database Wipe para limpar estados corrompidos de slots "4/4" sem ordens reais.
    - **Symbol Purgue:** Remoção completa de `PEPEUSDT` (substituído por `1000PEPEUSDT`) em todas as camadas de configuração para evitar erros de subscrição no WebSocket.
    - **Scan Resumption:** Otimização do loop de escaneamento para retomar imediatamente após a limpeza de estado.

*   **V110.192: SOVEREIGN STABILIZATION & RADAR SYNC [APR 24]**
    - **Radar Sync Fix:** Correção da dessincronização de payload no frontend; o Radar agora recebe o objeto completo `{signals, decisions, market_context}`.
    - **Bybit WS Hardening:** Remoção definitiva de ativos com símbolos inválidos (ex: `PEPEUSDT.P`) que causavam o crash cíclico do WebSocket.
    - **ML Feedback Loop Restoration:** Implementação do método `get_vault_history` no `SovereignService`, permitindo que o Librarian processe o pós-mortem de ML.
    - **Memory & Lifecycle Safety:** Eliminação de `UnboundLocalError` no gerador de sinais e `KeyError` no gerenciamento de conexões WebSocket.

*   **V110.181: SOVEREIGN ENGINE & WS RECOVERY [APR 24]**
    - **Sovereign Engine Deployment:** Ativação do motor de sincronização WebSocket centralizado no frontend.
    - **Universal Bridge Sync:** Correção de sincronização em tempo real para indicadores críticos (BTC Price, Equity) via `cockpit.html`.
    - **Placeholder Purge:** Eliminação definitiva dos estados "---" no Cockpit HUD.
    - **Backend-Frontend Handshake:** Estabilização do fluxo de pacotes `system_state` e `banca_status` via `/ws/cockpit`.

*   **V110.176: SOVEREIGN REFINEMENT — BUG FIX & VAULT MIGRATION [APR 24]**
    - **Vault Postgres Migration:** Migração completa da lógica de ciclos e retiradas do Firestore para tabelas relacionais no Postgres.
    - **AttributeError Purge:** Limpeza total de referências ao `rtdb` e `db` do Firebase em todo o backend.
    - **Sovereign Interface Expansion:** Implementação de métodos de compatibilidade (`get_radar_pulse`, `get_chat_status`, etc.) no `SovereignService`.

*   **V110.175: RAILWAY SOVEREIGN — EMANCIPAÇÃO TOTAL 🚂 [APR 24]**
    - **SovereignService Deployment:** Introdução do `SovereignService` como o orquestrador central de persistência e comunicação, eliminando 100% dos resíduos do SDK do Firebase.
    - **Postgres Primary SSOT:** O PostgreSQL do Railway torna-se a fonte primária de verdade para saldos, slots, histórico e Genesis IDs, gerenciado localmente.
    - **Native WebSocket Broadcast:** Transmissão de sinais, pulso e estados de slot via WebSocket nativo (`/ws/cockpit`), garantindo latência ultra-baixa para o Cockpit UI.
    - **Fast Oracle Boot:** Otimização do tempo de estabilização do Oráculo para 30s, permitindo reinicializações ágeis e resilientes.

*   **V110.174: SELECTIVE INTELLIGENCE UPGRADE — VANGUARD [APR 24]**
    - **Asset Trend Guard**: Implementação de trava obrigatória para alinhar trades com a tendência H4 em ativos de volatilidade EXTREME.
    - **Spring Directionality**: Restrição do bypass de mola para seguir rigorosamente a tendência principal do ativo.
    - **Macro Shield**: Elevação da régua de Macro Score para ativos propensos a armadilhas (Trap-Prone).

*   **V110.173: ELITE FLEET EXPANSION — TOP 40 🌸 [APR 23]**
    - **Elite-40 Fleet**: Expansão do monitoramento de ativos `Spring Elite` de 20 para 40 pares.
    - **Spring Shield Bypass**: Consolidação do mecanismo de bypass para ativos `MOLA`.
    - **UI Synchronization**: Inclusão do selo `🧬 GENESIS: ID` com fallback para `order_id`.

*   **V110.172: GENESIS IRON LOCK — RACE CONDITION FIX 🔒 [APR 22]**
    - **Atomic Genesis ID:** O `genesis_id` gerado APÓS a confirmação da Exchange.
    - **Global In-Memory Lock:** Bloqueio de transição de slots para evitar ordens duplicadas.
    - **Paper Desync Guard:** Sincronização entre memória local e banco de dados para evitar overwrite de slots.

---

## 🏗️ ARQUITETURA DE SISTEMA (V110.176)

### 1. Camada de Dados (Persistência)
- **Primary DB:** PostgreSQL (Railway) — Armazena banca, histórico e registros permanentes.
- **In-Memory Store:** `paper_positions` e `slots_cache` — Gerenciamento de estado de ultra-baixa latência.

### 2. Camada de Comunicação (Real-time)
- **WebSocket Gateway:** FastAPI WebSockets — Broadcast de sinais, pulso de mercado e atualizações de UI.
- **Integrity Guard:** O sistema detecta a ausência de chaves API e entra automaticamente em modo PAPER, garantindo segurança operacional.

### 3. Motor de Execução (Agentes)
- **Captain:** Orquestrador central de sinais e proteção de banca.
- **BlitzSniper:** Motor de alta frequência para TFs curtos (M30).
- **Harvester:** Motor de Swing trading e colheita de Moonbags.
- **Oracle:** Validador de integridade e regime de mercado.

---

*Documento atualizado em: 2026-04-24 (V110.201) Sincronizado*
*Este documento reflete a migração completa e estabilizada para o ambiente RAILWAY.*
