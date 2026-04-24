import logging
import asyncio
import time
import httpx
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
        raw_key = settings.OPENROUTER_API_KEY.strip() if settings.OPENROUTER_API_KEY else None
        if raw_key and not raw_key.startswith("sk-or-v1-"):
            self.openrouter_key = f"sk-or-v1-{raw_key}"
        else:
            self.openrouter_key = raw_key
        self._setup_ai()

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
