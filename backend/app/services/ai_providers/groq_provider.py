from openai import AsyncOpenAI
from loguru import logger
from app.core.config import settings
from .base import AIProvider, sanitize_error
from typing import Dict, Any, Optional

def is_valid_groq_key(key: Optional[str]) -> bool:
    """Validates whether a Groq API key is present, non-empty, and structurally valid."""
    if not key or not isinstance(key, str):
        return False
    k = key.strip()
    if not k or k.lower() in ("none", "null", "undefined", "false", "your-groq-key", "placeholder", "gsk_placeholder"):
        return False
    if not k.startswith("gsk_") or len(k) < 20:
        return False
    return True

class GroqProvider(AIProvider):
    # Supported default model replacing deprecated llama-3.3-70b-versatile
    DEFAULT_MODEL = "openai/gpt-oss-120b"

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key.strip() if api_key else ""
        raw_model = (model or getattr(settings, "GROQ_MODEL", None) or self.DEFAULT_MODEL).strip()

        # Replace deprecated or invalid models with supported default
        if not raw_model or raw_model == "llama-3.3-70b-versatile":
            logger.warning(
                f"GroqProvider: configured model '{raw_model}' is deprecated or missing access; "
                f"defaulting to '{self.DEFAULT_MODEL}'."
            )
            self.model = self.DEFAULT_MODEL
        else:
            self.model = raw_model

        self.client: Optional[AsyncOpenAI] = None

        if not is_valid_groq_key(self.api_key):
            logger.warning("GroqProvider not initialized: missing or invalid GROQ_API_KEY (must start with 'gsk_' and have valid length).")
            return

        try:
            self.client = AsyncOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=self.api_key,
                timeout=60.0,
            )
            logger.info(f"GroqProvider initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize GroqProvider: {sanitize_error(e)}")
            self.client = None

    def is_available(self) -> bool:
        return self.client is not None and bool(self.api_key) and bool(self.model)

    async def refine_analysis(self, findings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.is_available():
            return None
        
        try:
            prompt = self._get_prompt(findings)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
            return self._parse_json(content)
        except Exception as e:
            logger.warning(f"Groq refinement failed ({type(e).__name__}): {sanitize_error(e)}")
            return None

    async def chat(self, message: str) -> Optional[str]:
        if not self.is_available():
            return None

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI Deployment Assistant. Answer user queries about web deployment, code analysis, and DevOps correctly and concisely."},
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"Groq chat failed ({type(e).__name__}): {sanitize_error(e)}")
            return None

    async def generate_dockerfile(self, prompt: str) -> Optional[str]:
        if not self.is_available():
            return None

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert DevOps engineer. Output ONLY the raw content of the requested Dockerfile. Do not use Markdown formatting blocks or explanations."},
                    {"role": "user", "content": prompt}
                ]
            )
            text = response.choices[0].message.content.strip()
            # Strip markdown code blocks just in case
            if text.startswith("```"):
                lines = text.split("\n")
                if len(lines) > 1 and lines[-1].startswith("```"):
                    text = "\n".join(lines[1:-1])
            return text
        except Exception as e:
            logger.warning(f"Groq Dockerfile generation failed ({type(e).__name__}): {sanitize_error(e)}")
            return None
