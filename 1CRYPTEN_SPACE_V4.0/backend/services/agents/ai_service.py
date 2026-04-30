import logging
import asyncio
import time
import httpx
import base64
import os
try:
    from zhipuai import ZhipuAI
except Exception:
    ZhipuAI = None

import google.generativeai as genai
from config import settings
from services.sovereign_service import sovereign_service

logger = logging.getLogger("AIService")

class AIService:
    def __init__(self):
        self.glm_client = None
        self.gemini_model = None
        self.openrouter_backoff_until = 0
        self.glm_backoff_until = 0
        self.gemini_backoff_until = 0
        self.vision_model_backoffs = {} # [V4.2] Backoff individual por modelo vision
        self.vision_model_dead = set()    # [V4.2] Modelos que deram 402 (Payment Required)
        self.last_vision_model = "Neural Link - Standby"
        self.vision_requests_count = 0
        self._start_periodic_broadcast()
        raw_key = settings.OPENROUTER_API_KEY.strip() if settings.OPENROUTER_API_KEY else None
        if raw_key and not raw_key.startswith("sk-or-v1-"):
            self.openrouter_key = f"sk-or-v1-{raw_key}"
        else:
            self.openrouter_key = raw_key
        self._setup_ai()
        
    def get_cascade_status(self):
        """[V4.2.1] Retorna o status atual da cascata para a UI."""
        models = [
            "google/gemma-3-27b-it:free",
            "meta-llama/llama-3.2-11b-vision-instruct:free",
            "google/gemini-2.0-flash-exp:free",
            "google/gemma-3-12b-it:free",
            "google/gemma-3-4b-it:free"
        ]
        now = time.time()
        status_list = []
        for m in models:
            state = "ACTIVE"
            if m in self.vision_model_dead: state = "DEAD"
            elif now < self.vision_model_backoffs.get(m, 0): state = "COOLING"
            status_list.append({"model": m, "status": state})
        
        return {
            "last_model": self.last_vision_model,
            "requests": self.vision_requests_count,
            "cascade": status_list
        }

    def _setup_ai(self):
        """Initializes AI clients if keys are present."""
        glm_key = settings.GLM_API_KEY.strip() if settings.GLM_API_KEY else None
        if glm_key:
            try:
                self.glm_client = ZhipuAI(api_key=glm_key)
                logger.info("✅ GLM-4 Client Initialized.")
            except Exception as e:
                logger.error(f"❌ Failed to initialize GLM Client: {e}")
        else:
            logger.warning("⚠️ GLM_API_KEY not found.")

        gemini_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else None
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                # Correcting to a stable model name
                self.gemini_model = genai.GenerativeModel('gemini-flash-latest')
                logger.info("✅ Gemini Backup Initialized (v1.5).")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
        else:
            logger.warning("⚠️ GEMINI_API_KEY not found.")
        
        if self.openrouter_key:
            logger.info("✅ OpenRouter (Primary) Configured.")
        else:
            logger.warning("⚠️ OPENROUTER_API_KEY not found.")

    async def generate_content(self, prompt: str, system_instruction: str = "Você é um assistente de trading de elite."):
        """
        [V110.405] Generates content using Gemini exclusively as requested by the user.
        """
        now = time.time()

        if self.gemini_model and now > self.gemini_backoff_until:
            logger.debug(f"Attempting Native Gemini...")
            models_to_try = [
                'gemini-2.0-flash',
                'gemini-flash-latest',
                'gemini-1.5-flash'
            ]
            
            for m_obj in models_to_try:
                try:
                    full_prompt = f"{system_instruction}\n\n{prompt}"
                    def _gemini_sync():
                        if isinstance(m_obj, str):
                            temp_model = genai.GenerativeModel(m_obj)
                            return temp_model.generate_content(full_prompt)
                        else:
                            return m_obj.generate_content(full_prompt)
                            
                    response = await asyncio.wait_for(asyncio.to_thread(_gemini_sync), timeout=25.0)
                        
                    if response and hasattr(response, 'text'):
                        logger.info(f"✅ Gemini Success using {m_obj}")
                        return response.text.strip()
                except Exception as e:
                    if "404" in str(e): continue
                    logger.warning(f"Gemini error with {m_obj}: {e}")
                    if "429" in str(e):
                        if m_obj == models_to_try[-1]:
                            self.gemini_backoff_until = now + 120
                        continue
        
        logger.error("❌ Gemini failed or is in backoff.")
        return None

    async def generate_vision_content(self, prompt: str, image_path: str, system_instruction: str = "Você é um analista técnico de trading especializado em Visão Computacional."):
        """
        [V110.405] Generates content based on an image and a prompt using Gemini Natively.
        """
        if not os.path.exists(image_path):
            logger.error(f"❌ Image path not found: {image_path}")
            return None

        now = time.time()
        self.vision_requests_count += 1
        self.last_vision_model = "Native Gemini"
        asyncio.create_task(sovereign_service.update_ai_cascade(self.get_cascade_status()))

        if self.gemini_model and now > self.gemini_backoff_until:
            try:
                logger.info("👁️ [VISION] Using Native Gemini Flash...")
                import google.generativeai as genai
                from PIL import Image
                img = Image.open(image_path)
                
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content,
                    [f"{system_instruction}\n\n{prompt}", img]
                )
                if response and hasattr(response, 'text'):
                    logger.info("✅ [VISION] Success using Native Gemini")
                    return response.text.strip()
            except Exception as ge:
                logger.warning(f"❌ [VISION] Native Gemini failed: {ge}")
                if "429" in str(ge) or "quota" in str(ge).lower():
                    self.gemini_backoff_until = now + 3600
                    logger.error("🛑 [VISION] Gemini Quota Exceeded. Cooling down for 1 hour.")

        logger.error("❌ [VISION] Native Gemini failed or in backoff.")
        asyncio.create_task(sovereign_service.update_ai_cascade(self.get_cascade_status()))
        return None


    def _start_periodic_broadcast(self):
        """[V4.2.2] Starts a background task to periodically broadcast AI status."""
        async def broadcast_loop():
            while True:
                try:
                    await asyncio.sleep(60) # Every 60s
                    asyncio.create_task(sovereign_service.update_ai_cascade(self.get_cascade_status()))
                except Exception as e:
                    logger.error(f"AI Cascade Broadcast Error: {e}")
                    await asyncio.sleep(10)
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(broadcast_loop())
        except Exception:
            pass

    async def extract_admiral_facts(self, chat_history: str) -> dict:
        """
        [V15.0] Specialized intelligence to extract life facts about the Admiral.
        Returns a dictionary of facts found in the history.
        """
        system_instr = (
            "FOCO: Nomes de familiares (Fabiana, Pedro Kalel, Lívia), fatos REAIS confirmados. "
            "IGNORAR: Sugestões do próprio JARVIS, planos hipotéticos ('talvez', 'quem sabe'), "
            "comentários sobre o mercado que não sejam fatos pessoais.\n"
            "CRÍTICO: Apenas extraia se for uma afirmação direta do Almirante sobre sua vida ou família.\n"
            "RETORNO: Responda APENAS um JSON puro (sem markdown) no formato: "
            '{"familia": ["nome1", "nome2"], "eventos": ["fato confirmado"], "objetivos": ["meta real"], "outros": []}'
        )
        
        try:
            raw_response = await self.generate_content(
                prompt=f"Histórico de Conversa:\n{chat_history}",
                system_instruction=system_instr
            )
            
            if not raw_response:
                return {}
                
            # Clean possible markdown wrap
            clean_json = raw_response.replace('```json', '').replace('```', '').strip()
            import json
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Error extracting admiral facts: {e}")
            return {}

ai_service = AIService()
