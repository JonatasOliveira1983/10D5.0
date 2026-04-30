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

## 12. INTELIGÊNCIA COLETIVA E AGENTE VISÃO (V110.406 — SLOT SATURATION GUARD)
1. **Vision Gate Seletivo:** O Agente Visão só captura screenshots e aciona a IA se o sinal tiver **Score >= 95** (Captain) ou **Confidence >= 90** (Librarian). Sinais secundários são processados via quantitativo puro.
2. **Protocolo de Demanda Ativa:** O Bibliotecário e o Visão só iniciam estudos se houver slots livres (filled < 4). Se o sistema estiver 4/4, entra em **Standby de Inteligência Visual**.
3. **Análise de Cache (TTL 15m):** Resultados visuais são memorizados por 15 minutos por ativo. Se o sinal persistir sem mudança estrutural, o sistema reutiliza a decisão anterior para economizar quota.
4. **Veto Obrigatório Universal:** Se o score for >= 95, o Visão tem poder de veto. Inclui backoff de 1h para quota excedida no Gemini.

---

*Versão: V110.406 "Slot Saturation Guard" | Atualizado: 2026-05-01*
*Este arquivo é a ÚNICA FONTE DA VERDADE. Repositório Oficial: 10D5.0.*
