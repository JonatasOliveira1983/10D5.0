# MASTER_ARCHITECTURE.md — 10D Sniper V110.175
# Fonte da Verdade Arquitetural — Sincronizado com RULES.md

## 🚀 ROADMAP DE VERSÕES & MARCOS TÉCNICOS

*   **V110.175: RAILWAY SOVEREIGN — FIREBASE PURGE 🚂 [APR 24]**
    - **Infrastructure Migration:** Migracao definitiva do ecossistema Google Cloud/Firebase para a infraestrutura nativa do Railway.
    - **Postgres Primary SSOT:** O PostgreSQL do Railway torna-se a fonte primária de verdade para saldos, slots, histórico e Genesis IDs.
    - **Native WebSocket Broadcast:** Implementação de canal WebSocket nativo (`/ws/cockpit`) para transmissão de pulso, radar e atualizações de slot, eliminando a latência e dependência do Firebase RTDB.
    - **Fast Oracle Boot:** Redução do tempo de estabilização do Oráculo de 150s para 30s, otimizado para reinicializações rápidas em contêineres Railway.
    - **Instant Genesis:** Geração de Genesis ID no momento da criação da ordem (Paper e Real) para garantir rastreabilidade 100% na UI.

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
