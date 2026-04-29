import logging
import asyncio
import os
from typing import Dict, Any, Optional
from services.agents.ai_service import ai_service
from services.screenshot_service import screenshot_service
from services.chart_renderer import chart_renderer # [V5.0]
from config import settings

logger = logging.getLogger("VisionAgent")

class VisionAgent:
    def __init__(self):
        self.role = "Vision Analyst"
        self.system_instruction = (
            "Você é o Agente Visão 5.7 DUAL OCR, um analista técnico de trading avançado especializado em leitura estrutural automatizada.\n"
            "O gráfico (imagem) que você recebe é dividido em DUAS partes (Dual Timeframe: 30M na esquerda, 4H na direita) e possui anotações de texto cruciais (OCR):\n"
            "1. MARCA D'ÁGUA GIGANTE: No fundo do gráfico, há um texto enorme indicando o viés (ex: 'MACRO: BULLISH' ou 'MACRO: BEARISH').\n"
            "2. PAINEL DE OCR INFERIOR: No canto direito inferior do 4H, existe uma caixa dizendo 'ESPAÇO ATÉ RESIST: X%'.\n"
            "3. CAIXA FANTASMA DE ALVO (30M): No lado esquerdo, existe uma grossa linha VERDE desenhada (+6%) e uma VERMELHA (SL) delimitando a zona do trade.\n\n"
            "SUAS REGRAS DE OURO MÁXIMAS INQUEBRÁVEIS:\n"
            "A. [REGRA DO ESPAÇO OCR]: Se você ler no painel inferior que o espaço é MENOR que 6% (ou se a caixa estiver pintada de Vermelho com risco 'danger'), VOCÊ DEVE REJEITAR O SINAL IMEDIATAMENTE (DECISION: REJECTED). Não arrisque em espaços curtos.\n"
            "B. [REGRA DO ALVO LIVRE]: Olhe para a Linha/Caixa Verde (Target) no gráfico da esquerda (30M). Se houver resistência visível cruzando o meio do caminho entre o Strike (Entrada) e o Target verde, REJEITE. O caminho deve estar desimpedido.\n"
            "C. [CONFLUÊNCIA MACRO]: Se o sinal for de COMPRA (Long), mas a marca d'água no fundo gritar 'MACRO: BEARISH' ou 'TRAP ZONE', classifique como risco extremo ou rejeite.\n"
            "Seja técnico, estóico, direto. Priorize a segurança do Capital."
        )

    async def confirm_entry(self, symbol: str, side: str, signal_score: int, context_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        [V4.2 VISION GATE] Realiza a análise visual final para confirmar uma entrada.
        Otimizado para só agir se houver slots livres e DNA favorável.
        """
        logger.info(f"👁️ [VISION] Starting final visual confirmation for {symbol} {side}...")
        
        # 1. [V4.2] VISION GATE: Verificações de Eficiência
        if context_data:
            # A. Verificação de Slots
            active_slots = context_data.get("active_slots_count", 0)
            if active_slots >= 4:
                logger.info(f"⏭️ [VISION-GATE-SKIP] {symbol}: Todos os 4 slots ocupados. Ignorando análise visual.")
                return {
                    "approved": False,
                    "confidence": 0,
                    "reason": "SLOTS_FULL: Sistema operando em capacidade máxima (4/4).",
                    "thoughts": "Aguardando liberação de slot para nova análise."
                }
            
            # B. Verificação do Bibliotecário (DNA)
            lib_dna = context_data.get("lib_dna", {})
            nectar_seal = lib_dna.get("nectar_seal", "")
            if lib_dna.get("status") == "REJECTED" or "TRAP" in nectar_seal or "QUARANTINE" in nectar_seal:
                logger.info(f"⏭️ [VISION-GATE-SKIP] {symbol}: Bibliotecário já vetou o ativo. Ignorando análise visual.")
                return {
                    "approved": False,
                    "confidence": 0,
                    "reason": f"LIBRARIAN_VETO: {lib_dna.get('reason', 'Ativo não qualificado')}.",
                    "thoughts": "Economizando visão: DNA já rejeitado pelo Bibliotecário."
                }

        # 2. Capture the current chart (Playwright Observatory V5.7 OCR)
        logger.info(f"📸 [VISION-V5.7-OCR] {symbol}: Gerando gráfico DUAL do Observatório Público...")
        try:
            # Force using the live UI to capture the new Dual Timeframe OCR elements
            screenshot_path = await screenshot_service.capture_chart(symbol, interval="30")
        except Exception as e:
            logger.error(f"❌ [VISION-V5.7-OCR] Playwright failed: {e}")
            screenshot_path = ""
        
        if not screenshot_path:
            return {
                "approved": True, # Fallback to true se infra falhar, confia no quant.
                "confidence": 50,
                "reason": "Vision UI Falhou: Infraestrutura do Observatório indisponível.",
                "thoughts": "Falha na captura. Confiando nos dados quantitativos do LIBRARIAN."
            }

        # 2. Prepare the prompt
        side_label = "COMPRA (Long)" if side.lower() == "buy" else "VENDA (Short)"
        is_p3 = context_data.get("trigger_type") == "POINT_3_ELITE" if context_data else False
        
        prompt = (
            f"Analise o screenshot DUAL do Observatório de {symbol} para validar uma operação de {side_label}.\n\n"
            "EXECUTE ESTE PROTOCOLO DE 3 PASSOS NA IMAGEM:\n"
            "1. OCR DO PAINEL DE RISCO: Localize o painel no canto inferior direito que informa o 'ESPAÇO ATÉ RESIST'. Leia o valor em porcentagem.\n"
            "   -> SE o valor for inferior a 6.0% (ou a borda for vermelha), VOCÊ DEVE REJEITAR ESTA ORDEM (DECISION: REJECTED).\n"
            "2. MARCA D'ÁGUA: Leia a palavra gigante escrita no fundo do gráfico. É Bullsih ou Bearish? Está a favor do seu {side_label}?\n"
            "3. CAIXA FANTASMA (Lado Esquerdo): O gráfico desenhou uma linha VERDE GROSSA de alvo. O caminho entre o candle atual e a linha verde está livre de linhas grossas vermelhas horizontais?\n\n"
            "FOCO DO GATILHO: " + ("VALIDAÇÃO DO PONTO 3 (ROI DE ELITE)." if is_p3 else "Rompimento do Ponto 2 (Strike).") + "\n\n"
            "RESPONDA EM JSON FORMATO ESTRITO:\n"
            "{\n"
            '  "decision": "APPROVED" ou "REJECTED",\n'
            '  "confidence": 0-100,\n'
            '  "slot_type": "BLITZ" ou "SWING",\n'
            '  "analysis": "Explicação: qual foi a leitura do OCR e das linhas",\n'
            '  "thoughts": "Seus pensamentos internos sobre o contexto visual"\n'
            "}"
        )

        # 3. Call Vision AI
        try:
            response_text = await ai_service.generate_vision_content(
                prompt=prompt,
                image_path=screenshot_path,
                system_instruction=self.system_instruction
            )
            
            if not response_text:
                # [V4.2] Quando a IA falha (quota esgotada/sem crédito), a ordem é BLOQUEADA.
                # O Visão não pode aprovar sem análise real. Lei Máxima do Pipeline Unificado.
                logger.warning(
                    f"⚠️ [VISION-AI-DOWN] {symbol}: IA Vision indisponível (quota/crédito). "
                    f"Bloqueando entrada por segurança (Lei Máxima V4.2)."
                )
                return {
                    "approved": False,
                    "confidence": 0,
                    "reason": "Vision AI Indisponível: Quota/crédito esgotado. Entrada bloqueada por segurança.",
                    "thoughts": "IA Vision offline. Nenhuma análise visual possível. Aguardar restauração da API."
                }

            # Parse JSON from response
            import json
            import re
            
            try:
                # Clean possible markdown
                clean_json = re.sub(r'```json\s*|\s*```', '', response_text).strip()
                data = json.loads(clean_json)
                is_approved = data.get("decision") == "APPROVED"
            except Exception as parse_err:
                logger.error(f"❌ [VISION-PARSE-ERROR] {symbol}: Failed to parse AI response: {parse_err}")
                return {
                    "approved": False,
                    "confidence": 0,
                    "reason": "Erro de processamento da IA: Resposta mal-formatada.",
                    "thoughts": f"Raw text: {response_text[:100]}..."
                }
            
                # [V110.376] Stability: Wait for filesystem sync before broadcasting URL
                await asyncio.sleep(2.5)

                await sovereign_service.log_event(
                    agent="Vision",
                    message=f"Análise visual de {symbol} concluída.",
                    level="INFO",
                    payload={
                        "symbol": symbol,
                        "decision": data.get("decision"),
                        "confidence": data.get("confidence"),
                        "thoughts": data.get("thoughts"),
                        "analysis": data.get("analysis"),
                        "image_url": relative_url
                    }
                )
            except Exception as le:
                logger.error(f"Erro ao logar evento do Visão: {le}")

            return {
                "approved": is_approved,
                "confidence": data.get("confidence", 50),
                "slot_type": data.get("slot_type", "SWING"),
                "reason": data.get("analysis", "No analysis provided"),
                "thoughts": data.get("thoughts", ""),
                "screenshot_url": relative_url # Agora retorna a URL relativa
            }

        except Exception as e:
            logger.error(f"❌ [VISION-ERROR] Analysis failed: {e}")
            return {"approved": True, "confidence": 50, "reason": f"Vision Error: {e}", "thoughts": "Erro técnico no processamento da visão."}

    async def analyze_market_context(self, symbol: str) -> Dict[str, Any]:
        """
        [LIBRARIAN STUDY] Realiza um estudo visual de contexto usando o Motor V5.
        """
        logger.info(f"📸 [VISION-CONTEXT-V5] Analisando contexto de {symbol}...")
        try:
            # Force UI capture
            screenshot_path = await screenshot_service.capture_chart(symbol, interval="60")
        except Exception as e:
            logger.error(f"❌ [VISION-CONTEXT-V5.7-OCR] Screenshot capture failed: {e}")
            screenshot_path = ""

        if not screenshot_path: return {}

        prompt = (
            f"Descreva o estado visual atual de {symbol} baseado nesta tela do Observatório.\n"
            "O gráfico possui Marca D'água Gigante, Painéis OCR no canto direito, e duas janelas temporais.\n"
            "Responda focando em LER o texto da imagem: O que diz a Marca D'água? O que diz a caixa de ESPAÇO LIVRE no canto?\n"
            "Dê uma etiqueta curta do seu próprio julgamento: CLEAN_TREND, MESSY_RANGE, EXHAUSTION ou 123_REVERSAL."
        )

        try:
            from services.sovereign_service import sovereign_service
            result = await ai_service.generate_vision_content(prompt, screenshot_path, self.system_instruction)
            
            # [V110.376] Stability: Wait for filesystem sync before broadcasting URL
            await asyncio.sleep(2.5)

            # [V1.0] Log de inteligência para o fluxo coletivo
            await sovereign_service.log_event(
                agent="Vision",
                message=f"Contexto visual de {symbol} analisado.",
                payload={
                    "symbol": symbol,
                    "thoughts": result,
                    "image_url": f"/assets/vision_proofs/{os.path.basename(screenshot_path)}"
                }
            )

            # Remove temp file after a small delay to ensure UI can fetch it if needed 
            # (though user said no need to store, for the flow it helps)
            # In production with many users, we might want to store longer, but here it's local.
            # asyncio.create_task(self._delayed_delete(screenshot_path, delay=10))
            
            return {"visual_context": result}
        except Exception as e:
            logger.error(f"Error in vision market context: {e}")
            return {}

    async def _delayed_delete(self, path: str, delay: int = 10):
        await asyncio.sleep(delay)
        if os.path.exists(path):
            try:
                os.remove(path)
                logger.info(f"🗑️ [VISION] Temp screenshot deleted: {path}")
            except: pass

vision_agent = VisionAgent()
