import google.generativeai as genai
import asyncio
from loguru import logger
from app.core.config import settings
from .base import AIProvider, sanitize_error
from typing import Dict, Any, Optional
from google.api_core import exceptions

def is_valid_gemini_key(key: Optional[str]) -> bool:
    """Validates whether a Google Gemini API key is present and structurally valid."""
    if not key or not isinstance(key, str):
        return False
    k = key.strip()
    if not k or k.lower() in ("none", "null", "undefined", "false", "your-gemini-key", "placeholder"):
        return False
    if len(k) < 10:
        return False
    return True

class GeminiProvider(AIProvider):
    DEFAULT_MODEL = "gemini-flash-latest"

    def __init__(self, api_key: str, model_name: Optional[str] = None):
        self.api_key = api_key.strip() if api_key else ""
        self.model_name = (model_name or getattr(settings, "GEMINI_MODEL", None) or self.DEFAULT_MODEL).strip()
        self.model = None

        if not is_valid_gemini_key(self.api_key):
            logger.warning("GeminiProvider not initialized: missing or invalid GOOGLE_API_KEY.")
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"GeminiProvider initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize GeminiProvider: {sanitize_error(e)}")
            self.model = None

    def is_available(self) -> bool:
        return self.model is not None and bool(self.api_key)

    async def _call_with_retry(self, func, *args, **kwargs):
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except exceptions.ResourceExhausted as e:
                if attempt == max_retries - 1:
                    logger.error(f"Gemini API limit reached after {max_retries} attempts: {sanitize_error(e)}")
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
                logger.error(f"Gemini API call failed: {sanitize_error(e)}")
                raise

    async def refine_analysis(self, findings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.is_available():
            return None
        
        try:
            prompt = self._get_prompt(findings)
            response = await self._call_with_retry(self.model.generate_content, prompt)
            return self._parse_json(response.text)
        except Exception as e:
            logger.warning(f"Gemini refinement failed ({type(e).__name__}): {sanitize_error(e)}")
            return None

    async def chat(self, message: str) -> Optional[str]:
        if not self.is_available():
            return None

        try:
            prompt = f"You are a helpful AI Deployment Assistant. Answer the following user query directly and concisely.\n\nUser: {message}\nAssistant:"
            response = await self._call_with_retry(self.model.generate_content, prompt)
            return response.text
        except Exception as e:
            logger.warning(f"Gemini chat failed ({type(e).__name__}): {sanitize_error(e)}")
            return None

    async def generate_dockerfile(self, prompt: str) -> Optional[str]:
        if not self.is_available():
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
            logger.warning(f"Gemini Dockerfile generation failed ({type(e).__name__}): {sanitize_error(e)}")
            return None
