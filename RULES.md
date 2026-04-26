# RULES.md — 10D Sniper V4.0 "Adaptive Intelligence"
# Invariantes Tecnicas Inegociaveis — [PERSISTÊNCIA ABSOLUTA]
# Leia INTEIRO antes de tocar em qualquer arquivo.
# Fonte da verdade: codigo real no Railway e PostgreSQL/WebSocket Nativo.

---

## 🛡️ PROTOCOLO DE BLINDAGEM V4.0 (CRÍTICO)
1. **AUTO-CURA DE BANCO:** O sistema realiza migrações automáticas de esquema no boot. Qualquer divergência de coluna deve ser corrigida via script integrado ao `database_service.py`.
2. **TIMEZONE INTEGRITY (CRÍTICO):** É obrigatório o uso de `datetime.utcnow().replace(tzinfo=None)` ou `datetime.utcnow()` para todas as interações e comparações com o Postgres. **NUNCA** use `datetime.now(timezone.utc)` para comparações diretas com timestamps do banco.
3. **ARQUIVAMENTO ATÔMICO:** É terminantemente proibido limpar um slot sem antes garantir o arquivamento no Postgres via `database_service.log_trade`.
4. **META DE LUCRO 10/10:** O contador de progresso diário (Dashboard) e o contador de ciclos do Vault só incrementam se o lucro líquido da ordem (PNL) for **>= $10.00**.

---

## ⚡ 10D BYBITY REAL 4.0 — PROTOCOLO DE ELITE
## REGRA 00 — REPOSITÓRIO ÚNICO E OFICIAL
1. **REPO ÚNICO:** O único repositório oficial para este sistema é: `https://github.com/JonatasOliveira1983/10DBybityREAL/`. (Nota: O usuário solicitou o push para `https://github.com/JonatasOliveira1983/10DBybityREAL/commits/main/`)
2. **PUSH OBRIGATÓRIO:** Todo commit deve ser enviado para o branch `main` deste repositório para deploy automático no Railway.
3. **URL DE COMANDO:** A UI oficial é acessível via `https://1crypten.space/`.

---

## 1. SISTEMA DE SLOTS — ATRIBUICAO FIXA
| Slot | Tipo       | Estrategia   | Moonbag?                     | Leverage      |
|------|------------|--------------|------------------------------|---------------|
| 1    | BLITZ_30M  | BlitzSniper  | Condicional (pos 300% ROI)   | 50x fixo      |
| 2    | BLITZ_30M  | BlitzSniper  | Condicional (pos 300% ROI)   | 50x fixo      |
| 3    | SWING      | Harvester    | SIM (emancipa em 150% ROI)   | 50x fixo      |
| 4    | SWING      | Harvester    | SIM (emancipa em 150% ROI)   | 50x fixo      |

---

## 2. DNA SPECIALIST & RESPIRO ADAPTATIVO (NOVO V4.0)
1. **DNA Specialist:** O Bibliotecário (`Librarian`) analisa a intensidade de pavios (Wick Intensity) e a propensão de reteste.
2. **Respiro de ROI:** Ativos "nervosos" possuem um buffer de respiro de até **25% de ROI**. O sistema não fecha a ordem imediatamente ao tocar o Stop se o Gás (CVD) estiver favorável e o desvio estiver dentro do buffer.
3. **Breakeven Inteligente:** O gatilho para mover o Stop para a entrada (Risk-Free) é retardado em ativos com pavios longos. Em vez de 30% ROI, o sistema espera 50-60% ROI para evitar ser ejetado na "violinada" inicial.
4. **Paciência Diplomática:** O Sentinela concede até 90 segundos de carência se o fluxo monetário sustentar a posição, mesmo com o preço abaixo do Stop técnico.

---

## 10. PROTOCOLO DE EXPURGO DE FANTASMAS (GHOST PURGE)
- **Regra 10:** Registros com PNL $0 são filtrados do histórico da Vault para manter a limpeza visual.
- **Genesis Guard:** Ordens de emergência (RECOVERY) recebem automaticamente um relatório de telemetria padrão: "Protocolo de Emergência - Ordem sem DNA de Inteligência".

---

*Versão: V4.0 "Adaptive Intelligence" | Atualizado: 2026-04-26*
*Este arquivo é a ÚNICA FONTE DA VERDADE.*
