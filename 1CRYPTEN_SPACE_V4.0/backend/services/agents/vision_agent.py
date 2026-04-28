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
            "Você é o Agente Visão 5.0, um analista técnico de trading especializado em SMC (Smart Money Concepts).\n"
            "O gráfico que você recebe é anotado com indicadores e zonas institucionais:\n"
            "1. SMA 21 (Branca) e SMA 100 (Amarela): Confirmam a tendência e pontos de suporte dinâmico.\n"
            "2. CAIXAS/LINHAS: Representam Order Blocks (Zonas de baleias) e FVGs.\n"
            "DIRETRIZES DE ANÁLISE:\n"
            "A. Rejeição: O preço deve mostrar pavios longos ou falha de rompimento em uma das SMAs ou Blocos.\n"
            "B. Liquidez: Identifique se o movimento atual busca capturar liquidez acima/abaixo dos pavios.\n"
            "C. Veredito: Seja técnico, direto e estóico."
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

        # 2. Capture the current chart (Pure Python Renderer [V5.0])
        logger.info(f"📸 [VISION-V5] {symbol}: Gerando gráfico anotado via Python Engine...")
        try:
            from services.agents.librarian import librarian_agent
            visual_data = await librarian_agent.get_visual_data(symbol, interval="1h") # Usamos 1h para melhor definição de OB
            
            if visual_data and not visual_data['df'].empty:
                screenshot_path = chart_renderer.render_chart(
                    symbol=symbol, 
                    df=visual_data['df'], 
                    obs=visual_data['obs'], 
                    fvgs=visual_data['fvgs'],
                    pattern_123=visual_data.get('pattern_123')
                )
            else:
                # Fallback to screenshot service if no data
                logger.warning(f"⚠️ [VISION-V5] No local data for {symbol}. Falling back to ScreenshotService.")
                screenshot_path = await screenshot_service.capture_chart(symbol, interval="30")
        except Exception as e:
            logger.error(f"❌ [VISION-V5] Pure Renderer failed: {e}")
            screenshot_path = await screenshot_service.capture_chart(symbol, interval="30")
        
        if not screenshot_path:
            return {
                "approved": True, # Fallback to true if capture fails but signal is strong
                "confidence": 50,
                "reason": "Vision Engine Failed: Infraestrutura indisponível.",
                "thoughts": "Falha na captura. Confiando nos dados quantitativos."
            }

        # 2. Prepare the prompt
        side_label = "COMPRA (Long)" if side.lower() == "buy" else "VENDA (Short)"
        prompt = (
            f"Analise este gráfico de {symbol} para uma operação de {side_label}.\n"
            "O gráfico foi pré-anotado com o Motor de Visão 5.0:\n"
            "- LINHA BRANCA: SMA 21 (Tendência de curto prazo).\n"
            "- LINHA AMARELA: SMA 100 (Tendência de médio prazo).\n"
            "- CAIXAS COLORIDAS: Zonas de Order Block (Institucional).\n"
            "- MARCADORES (1), (2), (3): Estratégia de Reversão 1-2-3. (2) é a exaustão, (3) é a confirmação.\n"
            "PERGUNTA: O preço está respeitando as zonas e o padrão 1-2-3? Existe confluência visual para a entrada?\n"
            "RESPONDA EM JSON:\n"
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
        [LIBRARIAN STUDY] Realiza um estudo visual de contexto usando o Motor V5.
        """
        logger.info(f"📸 [VISION-CONTEXT-V5] Analisando contexto de {symbol}...")
        try:
            from services.agents.librarian import librarian_agent
            visual_data = await librarian_agent.get_visual_data(symbol, interval="1h")
            
            if visual_data and not visual_data['df'].empty:
                screenshot_path = chart_renderer.render_chart(
                    symbol=symbol, 
                    df=visual_data['df'], 
                    obs=visual_data['obs'], 
                    fvgs=visual_data['fvgs'],
                    pattern_123=visual_data.get('pattern_123')
                )
            else:
                screenshot_path = await screenshot_service.capture_chart(symbol, interval="60")
        except Exception as e:
            logger.error(f"❌ [VISION-CONTEXT-V5] Pure Renderer failed: {e}")
            screenshot_path = await screenshot_service.capture_chart(symbol, interval="60")

        if not screenshot_path: return {}

        prompt = (
            f"Descreva o estado visual atual de {symbol}.\n"
            "O gráfico possui médias móveis, zonas de Order Block e marcadores 1-2-3 anotados.\n"
            "Dê uma etiqueta curta: CLEAN_TREND, MESSY_RANGE, EXHAUSTION ou 123_REVERSAL.\n"
            "Analise se o preço está sendo repelido pelas zonas ou confirmando o padrão 1-2-3."
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
