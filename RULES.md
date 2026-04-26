# RULES.md — 10D Sniper V4.0 "Adaptive Intelligence"
# Invariantes Tecnicas Inegociaveis — [PERSISTÊNCIA ABSOLUTA]
# Leia INTEIRO antes de tocar em qualquer arquivo.
# Fonte da verdade: codigo real no Railway e PostgreSQL/WebSocket Nativo.

---

## 🛡️ PROTOCOLO DE BLINDAGEM V4.0 (CRÍTICO)
1. **AUTO-CURA DE BANCO:** O sistema realiza migrações automáticas de esquema no boot. Qualquer divergência de coluna deve ser corrigida via script integrado ao `database_service.py`.
2. **TIMEZONE INTEGRITY (CRÍTICO):** É obrigatório o uso de `datetime.utcnow().replace(tzinfo=None)` ou `datetime.utcnow()` para todas as interações e comparações com o Postgres. **NUNCA** use `datetime.now(timezone.utc)` para comparações diretas com timestamps do banco, pois isso gera erro de "offset-naive vs offset-aware". SSOT: Naive UTC.
3. **ARQUIVAMENTO ATÔMICO:** É terminantemente proibido limpar um slot sem antes garantir o arquivamento no Postgres via `database_service.log_trade`.
4. **PAPER MODE ENFORCEMENT:** Em modo de teste, a variável `BYBIT_EXECUTION_MODE` deve ser injetada como `PAPER` no Railway para garantir o saldo simulado de $100.
5. **META DE LUCRO 10/10 (V4.0):** O contador de progresso diário (Dashboard) e o contador de ciclos do Vault (1/10) só incrementam se o lucro líquido da ordem (PNL) for **>= $10.00**.

---

## ⚡ 10D BYBITY REAL 4.0 — PROTOCOLO DE ELITE
## REGRA 00 — REPOSITÓRIO ÚNICO E OFICIAL
1. **REPO ÚNICO:** O único repositório oficial para este sistema é: `https://github.com/JonatasOliveira1983/10D5.0/`.
2. **PUSH OBRIGATÓRIO:** Todo commit deve ser enviado para o branch `main` deste repositório para deploy automático no Railway.
3. **URL DE COMANDO:** A UI oficial é acessível via `https://1crypten.space/`.

---

## REGRA 0 — PROTOCOLO DE INFRAESTRUTURA RAILWAY (SOVEREIGN)
1. **SSOT (Source of Truth):** O banco de dados primário é o **PostgreSQL (Railway)**. O `SovereignService` é o único orquestrador autorizado de persistência.
2. **BROADCAST:** Toda comunicação com a UI é feita via **WebSocket Nativo (/ws/cockpit)**.
3. **VAULT HISTORY:** O histórico de trades deve ser recuperado via `database_service` e exposto pela API `/api/history`. Retornar listas vazias na UI por falha de serviço soberano é inaceitável.
4. **EMANCIPAÇÃO TOTAL:** O uso de Firebase/Firestore/RTDB foi **EXTINTO**. O sistema opera de forma 100% autônoma.

---

## 1. SISTEMA DE SLOTS — ATRIBUICAO FIXA
| Slot | Tipo       | Estrategia   | Moonbag?                     | Leverage      |
|------|------------|--------------|------------------------------|---------------|
| 1    | BLITZ_30M  | BlitzSniper  | Condicional (pos 300% ROI)   | 50x fixo      |
| 2    | BLITZ_30M  | BlitzSniper  | Condicional (pos 300% ROI)   | 50x fixo      |
| 3    | SWING      | Harvester    | SIM (emancipa em 150% ROI)   | 50x fixo      |
| 4    | SWING      | Harvester    | SIM (emancipa em 150% ROI)   | 50x fixo      |

- **REGRA:** Alavancagem de 50x é OBRIGATÓRIA para todos os slots para maximizar o potencial da banca Sniper.
- **REGRA:** Slots 1 e 2 são EXCLUSIVOS para BlitzSniper. Nunca atribua outro tipo.
- **REGRA:** Collision Guard impede o mesmo ativo em mais de um slot simultaneamente via `paper_positions` e Postgres.

---

## 2. GENESIS ID — PASSAPORTE DA ORDEM
- **Geração Instantânea:** O `genesis_id` é gerado no momento do nascimento da ordem, inclusive em Paper Mode.
- **Formato Atômico:** `BLZ-{UUID6}-{SYM4}` (Blitz) / `SWG-{UUID6}-{SYM4}` (Swing)
- **REGRA:** O `genesis_id` é persistido no **PostgreSQL** e transmitido via **WebSocket** imediatamente.
- **REGRA:** genesis_id deve acompanhar a ordem até o fechamento.

---

## 3. BLITZ SNIPER & DNA SPECIALIST (V4.0 ADAPTIVE)
1. **Momento Mola**: Prioridade absoluta para sinais "Mola" identificados pelo Librarian.
2. **Spring Shield (Bypass)**: Sinais de Mola possuem bypass total da Guilhotina Lateral (ADX < 18) e do Trap-Prone Shield.
3. **Adaptive Respiro (V4.0):** O sistema tolera desvios de até **25% de ROI** abaixo do Stop Loss se o fluxo monetário (CVD) estiver favorável e o ativo for classificado como Especialista.
4. **Breakeven Inteligente (V4.0):** Ativos com histórico de pavios (Retest Heavy) retardam o movimento de Stop Loss para a entrada. O gatilho padrão de 30% ROI sobe para 50-60% para evitar ser ejetado na "violinada" inicial.
5. **Paciência Diplomática (V4.0):** O Sentinela concede até 90 segundos de carência se o fluxo monetário (CVD) sustentar a posição, mesmo com o preço abaixo do Stop técnico.

---

## 4. RADAR DE INTELIGÊNCIA — BROADCAST LOCAL
- **Sincronização:** Os sinais são enviados via WebSocket para a UI em tempo real (`type: radar_pulse`).
- **ESTRUTURA DE DADOS:** O pacote de radar_pulse DEVE ser um objeto completo `{signals, decisions, market_context}`. O frontend rejeita arrays puros para evitar quebra de HUD.

---

## 5. ORÁCULO DE MERCADO — ESTABILIZAÇÃO ÁGIL
- **Boot Time:** Reduzido para **15-30 segundos** no Railway.
- **Fallback ADX:** Se o Oráculo estiver estabilizando, o sistema usa o ADX bruto do WebSocket para não travar o Radar.

---

## 6. GESTÃO DE RISCO — BANKROLL RAILWAY
- **Banca Padrão:** **$100.00** (Simulado/Paper).
- **Margem por slot:** **10% da banca** ($10.00 por ordem).
- **Meta Diária:** Exige lucro de $10.00 por trade para contar no placar 10/10.

---

## 7. HIERARQUIA DE AGENTES (SOBERANIA RAILWAY)
```
Captain (Orquestrador Central)
  ├── BlitzSniper   -> Monitor M30 (Slots 1-2)
  ├── Harvester     -> Monitor H1/H4 (Slots 3-4 - SWING)
  ├── Oracle        -> Inteligencia de Mercado (ADX/BTC Pulse)
  ├── Librarian     -> DNA Specialist (Mola/Trap/Respiro)
  └── WebSocket     -> Broadcast de Estado para o Cockpit UI
```

---

## 8. DESIGN INVARIANTE — SEAMLESS PREMIUM
- **Estética:** Grayscale Premium (Preto, Branco, Cinza e Lima).
- **Glassmorphism:** Uso obrigatório de `backdrop-blur-xl` em todos os painéis.

---

## 9. MAPA DE ESTADO SOBERANO
| Componente | Localização Primária (SSOT) |
|---|---|
| **Slots Ativos** | Tabela `slots` (Postgres) |
| **Moonbags** | Tabela `moonbags` (Postgres) |
| **Histórico Vault** | Tabela `trade_history` (Postgres) |
| **Motor Paper** | Tabela `system_state` (Postgres) |

---

## 10. PROTOCOLO DE EXPURGO DE FANTASMAS & GENESIS GUARD (V4.0)
- **Auto-Purge:** Ativos em erro de subscrição são filtrados na carga do estado Paper.
- **Lixo Visual:** Registros com PNL $0 ou ID de recuperação são expurgados do histórico visual (`RECOVERY-%`).
- **Genesis Guard:** Ordens sem DNA de inteligência (emergência) recebem telemetria padrão para evitar erro de "Relatório Inexistente" na UI.

---

## 11. INTEGRIDADE DE ASSINATURA WEBSOCKET (BYBIT-WS)
1. **Blocklist Guard:** Ativos na `settings.ASSET_BLOCKLIST` são ignorados no WS (exceto BTC).
2. **Type Safety:** Handlers validam se a mensagem é um dicionário antes do processamento.

---

*Versão: V4.0 "Adaptive Intelligence" | Atualizado: 2026-04-26*
*Este arquivo é a ÚNICA FONTE DA VERDADE. Repositório Oficial: 10D5.0.*
