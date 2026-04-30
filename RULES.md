# RULES.md — 10D Sniper V110.406 "Slot Saturation Guard"
# Invariantes Tecnicas Inegociaveis — [PERSISTÊNCIA ABSOLUTA]
# Leia INTEIRO antes de tocar em qualquer arquivo.
# Fonte da verdade: codigo real no Railway e PostgreSQL/WebSocket Nativo.

---

## 🛡️ PROTOCOLO DE BLINDAGEM V4.0 (CRÍTICO)
1. **AUTO-CURA DE BANCO:** O sistema realiza migrações automáticas de esquema no boot. Qualquer divergência de coluna deve ser corrigida via script integrado ao `database_service.py`.
2. **TIMEZONE INTEGRITY (CRÍTICO):** É obrigatório o uso de `datetime.utcnow().replace(tzinfo=None)` ou `datetime.utcnow()` para todas as interações e comparações com o Postgres. **NUNCA** use `datetime.now(timezone.utc)` para comparações diretas com timestamps do banco, pois isso gera erro de "offset-naive vs offset-aware". SSOT: Naive UTC.
3. **ARQUIVAMENTO ATÔMICO:** É terminantemente proibido limpar um slot sem antes garantir o arquivamento no Postgres via `database_service.log_trade`.
4. **PAPER MODE ENFORCEMENT:** Em modo de teste, a variável `BYBIT_EXECUTION_MODE` deve ser injetada como `PAPER` no Railway para garantir o saldo simulado de $100.
5. **META DE LUCRO ROI >= 80% (V110.350):** O contador de progresso diário (Dashboard) e o contador de ciclos do Vault (1/10) agora são baseados em ROI técnico (>= 80%) em vez de lucro fixo em dólar. Isso garante a justiça do ciclo independente do capital (Compound-Ready).
14. **INTEGRIDADE DE FECHAMENTO (V110.360):** É obrigatório que o `BankrollManager` registre todas as ordens detectadas como fechadas (inclusive órfãs) no `trade_history` para garantir paridade absoluta entre a banca e o histórico auditável.
15. **NORMALIZAÇÃO DE SIDE (V110.360):** Todas as comparações de lado de ordem (`side`) no frontend e backend devem ser normalizadas (`toUpperCase()`) para suportar variações de API (Buy/BUY/LONG).
16. **INTELIGÊNCIA DO RADAR (V110.370):** O Radar deve operar de forma contextual. Se não houver slots disponíveis para um determinado tipo de estratégia (Blitz ou Swing), os sinais desse tipo devem ser filtrados na UI para evitar poluição visual e confusão operacional. O cabeçalho do Radar deve exibir a demanda ativa (ex: "VISÃO BUSCANDO 1 SWING").
17. **VISUAL FLOW SENTINEL (V110.371):** A "Linha Vertical" de scan nos gráficos é o indicador visual do agente Flow Sentinel. Ela deve refletir o status do sistema (Verde/Branco = Ativo, Vermelho = Falha de Integridade/Offline). Marcadores de "ENTRY" devem ser baseados no timestamp real (`opened_at`) para garantir precisão absoluta na auditoria visual.

---

## 📜 LEI MÁXIMA DO SISTEMA (V110.406)

## 1. SOBERANIA E INTELIGÊNCIA
- **Motor de IA:** Uso exclusivo do **Google Gemini Nativo** (Custo Zero).
- **Protocolo de Visão:** O Agente Visão atua como o **Gatilho Final (Last Gate)**.
- **Guardião de Slots:** O sistema entra em modo **STANDBY TOTAL** (incluindo Visão e Estudos) quando os 4 slots estão ocupados.
- **Visão-Last Protocol:** Nenhuma análise visual é realizada sem demanda real de slot ou score quantitativo de elite (Score >= 90).

## 2. GESTÃO DE RISCO (BANKROLL)
- **Slots:** 4 Slots simultâneos (2 Blitz + 2 Swing).
- **Alavancagem:** 50x (Padrão Sniper).
- **Risco por Operação:** 1% da Banca.

## 3. PROTOCOLO DE EXECUÇÃO
- **Quantitativo:** Primeiro filtro via SignalGenerator e Captain.
- **Visual:** Segundo filtro via Vision Agent (OCR Dual + Contexto).
- **Aprovação:** Apenas sinais com aprovação dupla (Math + Vision) são executados.
- **Veto:** O Agente Visão tem poder de veto absoluto sobre qualquer sinal.

---

## REGRA 00 — REPOSITÓRIO ÚNICO E OFICIAL
1. **REPO ÚNICO:** O único repositório oficial e absoluto para este sistema é: `https://github.com/JonatasOliveira1983/10D5.0/`.
2. **PUSH OBRIGATÓRIO:** Todo commit deve ser enviado exclusivamente para o branch `main` do repositório `10D5.0` para deploy automático.
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
- **REGRA:** Slots 1 e 2 são EXCLUSIVOS para BlitzSniper (30M). Slots 3 e 4 para Swing e Moonbags.
- **REGRA (MOONBAG EXPANSION):** Se uma Moonbag ocupar um slot de Swing, o sistema libera o slot lógico para um novo par da lista Elite, mantendo sempre o processamento focado nos 20 pares ativos.
- **REGRA (COLLISION GUARD):** Impede o mesmo ativo em mais de um slot simultaneamente via `paper_positions` e Postgres.
- **REGRA (DEMANDA ADAPTATIVA - V110.370):** O sistema monitora as vagas nos slots em tempo real. O Radar agora filtra sinais para exibir apenas os tipos compatíveis com as vagas abertas. Se os 4 slots estiverem cheios, o Radar entra em modo STANDBY automático.

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
1. **Estética:** Grayscale Premium (Preto, Branco, Cinza e Verde Normal `#22c55e`). **PROIBIDO LIMA.**
2. **Glassmorphism:** Uso obrigatório de `backdrop-blur-xl` em todos os painéis.
3. **Labels de Histórico:** Devem seguir o padrão `+R$ 0,00` com vírgula para decimais.
4. **VISUALIZAÇÃO TÉCNICA (ESCADINHA ELITE):** O gráfico do cockpit deve renderizar obrigatoriamente as 5 linhas de alvo da estratégia Sniper: T1(30%), T2(50%), T3(70%), T4(110%) e T5(150%).
5. **PRECISÃO DE PNL:** O cálculo do ROI na interface deve utilizar o feed de preço do WebSocket (BybitWS) para evitar disparidades visuais com o gráfico.

---

## 12. INTELIGÊNCIA COLETIVA E AGENTE VISÃO (V110.406 — SLOT SATURATION GUARD)
1. **Vision Gate Seletivo:** O Agente Visão só captura screenshots e aciona a IA se o sinal tiver **Score >= 95** (Captain) ou **Confidence >= 90** (Librarian). Sinais secundários são processados via quantitativo puro.
2. **Protocolo de Demanda Ativa:** O Bibliotecário e o Visão só iniciam estudos se houver slots livres (filled < 4). Se o sistema estiver 4/4, entra em **Standby de Inteligência Visual**.
3. **Análise de Cache (TTL 15m):** Resultados visuais são memorizados por 15 minutos por ativo. Se o sinal persistir sem mudança estrutural, o sistema reutiliza a decisão anterior para economizar quota.
4. **Veto Obrigatório Universal:** Se o score for >= 95, o Visão tem poder de veto. Inclui backoff de 1h para quota excedida no Gemini.

---

*Versão: V110.406 "Slot Saturation Guard" | Atualizado: 2026-05-01*
*Este arquivo é a ÚNICA FONTE DA VERDADE. Repositório Oficial: 10D5.0.*
