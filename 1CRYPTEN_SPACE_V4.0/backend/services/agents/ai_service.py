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
            "google/gemini-2.0-flash-exp:free",
            "google/gemini-2.0-flash-lite-preview-02-05:free",
            "qwen/qwen2.5-vl-72b-instruct:free",
            "nvidia/llama-3.1-nemotron-nano-vl-8b-v1:free",
            "google/gemma-3-27b-it:free",
            "mistralai/pixtral-12b:free"
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
        Generates content using OpenRouter (DeepSeek) primarily, falling back to GLM/Gemini.
        """
        now = time.time()

        # 1. Primary: OpenRouter Cascade (Free Tier Models)
        if self.openrouter_key and now > self.openrouter_backoff_until:
            logger.debug(f"Attempting OpenRouter Cascade...")
            
            openrouter_models = [
                "deepseek/deepseek-r1:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "mistralai/mistral-small-3.1-24b-instruct:free",
                "qwen/qwen3-next-80b-a3b-instruct:free",
                "nousresearch/hermes-3-llama-3.1-405b:free"
            ]
            
            for or_model in openrouter_models:
                try:
                    logger.debug(f"OpenRouter trying model: {or_model}")
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        response = await client.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {self.openrouter_key}",
                                "HTTP-Referer": "https://1crypten.space", 
                                "X-Title": "1CRYPTEN Space V4.0",
                            },
                            json={
                                "model": or_model,
                                "messages": [
                                    {"role": "system", "content": system_instruction},
                                    {"role": "user", "content": prompt}
                                ],
                                "temperature": 0.7
                            }
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if "error" in data:
                                logger.warning(f"OpenRouter 200 OK Error with {or_model}: {data['error']}")
                                continue
                                
                            text = data.get('choices', [{}])[0].get('message', {}).get('content')
                            if text: 
                                logger.info(f"✅ OpenRouter Success using {or_model}")
                                return text.strip()
                            else:
                                logger.warning(f"OpenRouter 200 OK but empty text from {or_model}. Raw: {data}")
                        else:
                            logger.warning(f"OpenRouter HTTP {response.status_code} with {or_model}: {response.text}")
                            if response.status_code == 429:
                                # Se todos falharem com 429, aplicamos o backoff geral no ultimo
                                if or_model == openrouter_models[-1]:
                                    self.openrouter_backoff_until = now + 60
                except Exception as e:
                    logger.warning(f"OpenRouter Exception with {or_model}: {e}")
                    if or_model == openrouter_models[-1]:
                        self.openrouter_backoff_until = now + 60

        # 2. Fallback: GLM
        if self.glm_client and now > self.glm_backoff_until:
            try:
                logger.debug(f"Falling back to GLM...")
                def _glm_sync():
                    return self.glm_client.chat.completions.create(
                        model="glm-4",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt}
                        ]
                    )
                response = await asyncio.to_thread(_glm_sync)
                text = response.choices[0].message.content
                if text: return text.strip()
            except Exception as e:
                logger.warning(f"GLM Fallback failed: {e}")
                if "429" in str(e):
                    self.glm_backoff_until = now + 60

        # 3. Fallback: Gemini
        if self.gemini_model and now > self.gemini_backoff_until:
            logger.debug(f"Falling back to Gemini...")
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
                        # Só entra em backoff se esgotar TUDO
                        if m_obj == models_to_try[-1]:
                            self.gemini_backoff_until = now + 120
                        continue
        
        logger.error("❌ All AI providers failed or are in backoff.")
        return None

    async def generate_vision_content(self, prompt: str, image_path: str, system_instruction: str = "Você é um analista técnico de trading especializado em Visão Computacional."):
        """
        [V4.2 CASCATA FREE] Generates content based on an image and a prompt.
        Uses a cascade of FREE models from OpenRouter to ensure no costs and high availability.
        """
        if not os.path.exists(image_path):
            logger.error(f"❌ Image path not found: {image_path}")
            return None

        now = time.time()
        self.vision_requests_count += 1
        # Broadcast initial "Checking" state
        asyncio.create_task(sovereign_service.update_ai_cascade(self.get_cascade_status()))
        
        # [V4.2] FREE VISION CASCADE MODELS (Ordered by quality)
        # [V110.335] FREE VISION CASCADE MODELS (Updated IDs)
        FREE_VISION_MODELS = [
            "google/gemini-2.0-flash-lite-preview-02-05:free",
            "google/gemma-3-27b-it:free",
            "google/gemma-3-12b-it:free",
            "nvidia/nemotron-nano-12b-v2-vl:free",
            "mistralai/pixtral-12b:free",
            "meta-llama/llama-3.2-11b-vision-instruct:free"
        ]

        if not self.openrouter_key:
            logger.error("❌ No OpenRouter Key found for Vision Cascade.")
            return None

        # Encode image to base64 once
        try:
            with open(image_path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode('utf-8')
            image_url = f"data:image/png;base64,{encoded_image}"
        except Exception as e:
            logger.error(f"❌ Failed to encode image for Vision: {e}")
            return None

        for idx, v_model in enumerate(FREE_VISION_MODELS):
            # Skip if dead or in backoff
            if v_model in self.vision_model_dead:
                continue
            if now < self.vision_model_backoffs.get(v_model, 0):
                continue

            self.last_vision_model = v_model.split('/')[-1]
            asyncio.create_task(sovereign_service.update_ai_cascade(self.get_cascade_status()))

            try:
                logger.info(f"👁️ [VISION-CASCADE] Trying model {idx+1}/{len(FREE_VISION_MODELS)}: {v_model}...")
                
                async with httpx.AsyncClient(timeout=45.0) as client:
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.openrouter_key}",
                            "HTTP-Referer": "https://1crypten.space", 
                            "X-Title": "1CRYPTEN Vision Cascade",
                        },
                        json={
                            "model": v_model,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": f"{system_instruction}\n\n{prompt}"},
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": image_url}
                                        }
                                    ]
                                }
                            ],
                            "temperature": 0.2
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Check for internal OpenRouter error even with 200
                        if "error" in data:
                            err_msg = str(data["error"])
                            logger.warning(f"⚠️ [VISION-CASCADE] Model {v_model} returned error: {err_msg}")
                            if "429" in err_msg or "rate" in err_msg.lower():
                                self.vision_model_backoffs[v_model] = now + 60
                            elif "402" in err_msg or "credit" in err_msg.lower():
                                logger.error(f"💀 [VISION-CASCADE] Model {v_model} requires payment. Marking as DEAD.")
                                self.vision_model_dead.add(v_model)
                            continue

                        text = data.get('choices', [{}])[0].get('message', {}).get('content')
                        if text:
                            logger.info(f"✅ [VISION-CASCADE] Success using {v_model}")
                            return text.strip()
                        else:
                            logger.warning(f"⚠️ [VISION-CASCADE] Model {v_model} returned empty response.")
                    
                    elif response.status_code == 429:
                        logger.warning(f"⏳ [VISION-CASCADE] Rate limit (429) for {v_model}. Cooling down 60s.")
                        self.vision_model_backoffs[v_model] = now + 60
                    
                    elif response.status_code == 402:
                        logger.error(f"💀 [VISION-CASCADE] Payment Required (402) for {v_model}. Marking as DEAD.")
                        self.vision_model_dead.add(v_model)
                    
                    else:
                        logger.warning(f"❌ [VISION-CASCADE] HTTP {response.status_code} for {v_model}: {response.text}")

            except Exception as e:
                logger.warning(f"💥 [VISION-CASCADE] Exception with {v_model}: {e}")
                self.vision_model_backoffs[v_model] = now + 30 # Short backoff on generic error
                continue

        logger.error("❌ [VISION-CASCADE] All free vision models exhausted or in backoff.")
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
