import logging
import asyncio
import os
from typing import Dict, Any, Optional
from services.agents.ai_service import ai_service
from services.screenshot_service import screenshot_service
from config import settings

logger = logging.getLogger("VisionAgent")

class VisionAgent:
    def __init__(self):
        self.role = "Vision Analyst"
        self.system_instruction = (
            "Você é o Agente Visão, um analista técnico de trading de elite especializado em padrões visuais e SMC (Smart Money Concepts).\n"
            "Sua especialidade é identificar armadilhas de liquidez e confirmar pullbacks em médias móveis (SMA 21/100).\n"
            "DIRETRIZES:\n"
            "1. Procure por exaustão: Pavios longos no topo de uma subida (em Short) ou no fundo de uma queda (em Long).\n"
            "2. Confirmação de SMA: O preço deve cruzar ou testar a SMA 21 com corpo de candle decisivo.\n"
            "3. Contexto: Diferencie um 'pulo' para liquidar stops de uma tendência real.\n"
            "4. Respostas: Seja técnico, estóico e direto."
        )

    async def confirm_entry(self, symbol: str, side: str, signal_score: int) -> Dict[str, Any]:
        """
        Realiza a análise visual final para confirmar uma entrada.
        """
        logger.info(f"👁️ [VISION] Starting final visual confirmation for {symbol} {side}...")
        
        # 1. Capture the current chart (30m interval as preferred by user)
        screenshot_path = await screenshot_service.capture_chart(symbol, interval="30")
        
        if not screenshot_path:
            return {
                "approved": True, # Fallback to true if vision fails (don't block system)
                "confidence": 50,
                "reason": "Vision Capture Failed: Procedendo com cautela baseada em dados numéricos.",
                "thoughts": "Falha na captura visual. Confiando nos indicadores do Captain."
            }

        # 2. Prepare the prompt
        side_label = "COMPRA (Long)" if side.lower() == "buy" else "VENDA (Short)"
        prompt = (
            f"Analise este gráfico de {symbol} para uma possível operação de {side_label}.\n"
            f"O sinal matemático tem score de {signal_score}/100.\n"
            "FOCO: Olhe para a SMA 21 (mais curta) e a SMA 100.\n"
            "PERGUNTA: O preço está fazendo um pullback real ou é apenas um 'wick' (pavio) de liquidação de stops?\n"
            "RESPONDA NO FORMATO JSON:\n"
            "{\n"
            '  "decision": "APPROVED" ou "REJECTED",\n'
            '  "confidence": 0-100,\n'
            '  "analysis": "Sua explicação técnica curta",\n'
            '  "thoughts": "Seus pensamentos internos sobre o movimento"\n'
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
            
            # Clean possible markdown
            clean_json = re.sub(r'```json\s*|\s*```', '', response_text).strip()
            data = json.loads(clean_json)
            
            is_approved = data.get("decision") == "APPROVED"
            
            # [V1.0] Broadcast de Inteligência para a UI
            try:
                from services.sovereign_service import sovereign_service
                # Converter path absoluto em URL relativa para a UI
                # screenshot_path: .../backend/assets/vision_proofs/file.png
                # URL: /assets/vision_proofs/file.png
                relative_url = f"/assets/vision_proofs/{os.path.basename(screenshot_path)}"
                
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
                "reason": data.get("analysis", "No analysis provided"),
                "thoughts": data.get("thoughts", ""),
                "screenshot_url": relative_url # Agora retorna a URL relativa
            }

        except Exception as e:
            logger.error(f"❌ [VISION-ERROR] Analysis failed: {e}")
            return {"approved": True, "confidence": 50, "reason": f"Vision Error: {e}", "thoughts": "Erro técnico no processamento da visão."}

    async def analyze_market_context(self, symbol: str) -> Dict[str, Any]:
        """
        [LIBRARIAN STUDY] Realiza um estudo visual de contexto.
        """
        screenshot_path = await screenshot_service.capture_chart(symbol, interval="60") # Contexto em 1h
        if not screenshot_path: return {}

        prompt = (
            f"Descreva o estado visual atual de {symbol} em 1 hora.\n"
            "Ele está em uma tendência limpa, em um range lateral feio, ou perto de uma reversão na média?\n"
            "Dê uma etiqueta curta: CLEAN_TREND, MESSY_RANGE, EXHAUSTION ou REVERSAL.\n"
            "Justifique em uma frase curta."
        )

        try:
            from services.sovereign_service import sovereign_service
            result = await ai_service.generate_vision_content(prompt, screenshot_path, self.system_instruction)
            
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
