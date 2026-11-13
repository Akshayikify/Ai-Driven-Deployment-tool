from openai import AsyncOpenAI
from loguru import logger
from app.core.config import settings
from .base import AIProvider, sanitize_error
from typing import Dict, Any, Optional

def is_valid_openrouter_key(key: Optional[str]) -> bool:
    """Validates whether an OpenRouter API key is provided and structurally valid."""
    if not key or not isinstance(key, str):
        return False
    k = key.strip()
    if not k or k.lower() in ("none", "null", "undefined", "false", "your-openrouter-key", "placeholder"):
        return False
    if len(k) < 10:
        return False
    return True

class OpenRouterProvider(AIProvider):
    DEFAULT_MODEL = "google/gemini-2.5-flash"

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key.strip() if api_key else ""
        self.model = (model or getattr(settings, "OPENROUTER_MODEL", None) or self.DEFAULT_MODEL).strip()
        self.client: Optional[AsyncOpenAI] = None

        if not is_valid_openrouter_key(self.api_key):
            logger.warning("OpenRouterProvider not initialized: missing or invalid OPENROUTER_API_KEY.")
            return

        try:
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                timeout=120.0,
            )
            logger.info(f"OpenRouterProvider initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouterProvider: {sanitize_error(e)}")
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
                ],
                max_tokens=4096,
                extra_headers={
                    "HTTP-Referer": "https://github.com/Akshayikify/Auto_Deployment_tool",
                    "X-Title": "Auto Deploy AI",
                }
            )
            content = response.choices[0].message.content
            return self._parse_json(content)
        except Exception as e:
            logger.warning(f"OpenRouter refinement failed ({type(e).__name__}): {sanitize_error(e)}")
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
                ],
                max_tokens=4096,
                extra_headers={
                    "HTTP-Referer": "https://github.com/Akshayikify/Auto_Deployment_tool",
                    "X-Title": "Auto Deploy AI",
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"OpenRouter chat failed ({type(e).__name__}): {sanitize_error(e)}")
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
                ],
                max_tokens=4096,
                extra_headers={
                    "HTTP-Referer": "https://github.com/Akshayikify/Auto_Deployment_tool",
                    "X-Title": "Auto Deploy AI",
                }
            )
            text = response.choices[0].message.content.strip()
            # Strip markdown code blocks just in case
            if text.startswith("```"):
                lines = text.split("\n")
                if len(lines) > 1 and lines[-1].startswith("```"):
                    text = "\n".join(lines[1:-1])
            return text
        except Exception as e:
            logger.warning(f"OpenRouter Dockerfile generation failed ({type(e).__name__}): {sanitize_error(e)}")
            return None
