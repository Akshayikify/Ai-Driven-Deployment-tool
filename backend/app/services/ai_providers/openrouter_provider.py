from openai import AsyncOpenAI
from loguru import logger
from .base import AIProvider
from typing import Dict, Any, Optional

class OpenRouterProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
            # Use a reliable free Gemini model as a fallback
            self.model = "google/gemini-2.5-flash:free" 
            logger.info("OpenRouterProvider initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouterProvider: {e}")
            self.client = None

    async def refine_analysis(self, findings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None
        
        try:
            prompt = self._get_prompt(findings)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                extra_headers={
                    "HTTP-Referer": "https://github.com/Akshayikify/Auto_Deployment_tool",
                    "X-Title": "Auto Deploy AI",
                }
            )
            content = response.choices[0].message.content
            return self._parse_json(content)
        except Exception as e:
            logger.error(f"OpenRouter refinement failed: {e}")
            return None

    async def chat(self, message: str) -> Optional[str]:
        if not self.client:
            return None

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI Deployment Assistant. Answer user queries about web deployment, code analysis, and DevOps correctly and concisely."},
                    {"role": "user", "content": message}
                ],
                extra_headers={
                    "HTTP-Referer": "https://github.com/Akshayikify/Auto_Deployment_tool",
                    "X-Title": "Auto Deploy AI",
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenRouter chat failed: {e}")
            return None

    async def generate_dockerfile(self, prompt: str) -> Optional[str]:
        if not self.client:
            return None

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert DevOps engineer. Output ONLY the raw content of the requested Dockerfile. Do not use Markdown formatting blocks or explanations."},
                    {"role": "user", "content": prompt}
                ],
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
            logger.error(f"OpenRouter Dockerfile generation failed: {e}")
            return None
