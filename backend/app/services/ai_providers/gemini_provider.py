import google.generativeai as genai
import asyncio
from loguru import logger
from app.core.config import settings
from .base import AIProvider
from typing import Dict, Any, Optional
from google.api_core import exceptions

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"GeminiProvider initialized with model: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize GeminiProvider: {e}")
            self.model = None

    async def _call_with_retry(self, func, *args, **kwargs):
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # We use run_in_executor to avoid blocking the event loop if the library call is sync
                # but since we are already in an async method, we can just call it if it's fast.
                # However, for robustness with 429s, we loop here.
                return func(*args, **kwargs)
            except exceptions.ResourceExhausted as e:
                if attempt == max_retries - 1:
                    logger.error(f"Gemini API limit reached after {max_retries} attempts: {e}")
                    raise
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Gemini API rate limit reached. Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
            except exceptions.ServiceUnavailable as e:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Gemini service unavailable. Retrying in {delay}s...")
                await asyncio.sleep(delay)
            except Exception as e:
                # For other exceptions, we don't retry by default
                logger.error(f"Gemini API call failed: {e}")
                raise

    async def refine_analysis(self, findings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.model:
            return None
        
        try:
            prompt = self._get_prompt(findings)
            response = await self._call_with_retry(self.model.generate_content, prompt)
            return self._parse_json(response.text)
        except Exception as e:
            logger.error(f"Gemini refinement failed: {e}")
            return None

    async def chat(self, message: str) -> Optional[str]:
        if not self.model:
            return None

        try:
            prompt = f"You are a helpful AI Deployment Assistant. Answer the following user query directly and concisely.\n\nUser: {message}\nAssistant:"
            response = await self._call_with_retry(self.model.generate_content, prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat failed: {e}")
            return None

    async def generate_dockerfile(self, prompt: str) -> Optional[str]:
        if not self.model:
            return None

        try:
            response = await self._call_with_retry(self.model.generate_content, prompt)
            text = response.text.strip()
            # Strip markdown code blocks if the LLM includes them
            if text.startswith("```"):
                lines = text.split("\n")
                if len(lines) > 1 and lines[-1].startswith("```"):
                    text = "\n".join(lines[1:-1])
            return text
        except Exception as e:
            logger.error(f"Gemini Dockerfile generation failed: {e}")
            return None
