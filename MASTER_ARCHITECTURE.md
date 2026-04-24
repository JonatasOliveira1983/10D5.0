# MASTER_ARCHITECTURE.md — 10D Sniper V110.175
# Fonte da Verdade Arquitetural — Sincronizado com RULES.md

## 🚀 ROADMAP DE VERSÕES & MARCOS TÉCNICOS

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

## 🏗️ ARQUITETURA DE SISTEMA (V110.175)

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

*Documento atualizado em: 2026-04-24 (V110.175) Sincronizado*
*Este documento reflete a migração completa para o ambiente RAILWAY.*
