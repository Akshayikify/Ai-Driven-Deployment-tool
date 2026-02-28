import google.generativeai as genai
from loguru import logger
from .base import AIProvider
from typing import Dict, Any, Optional

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("GeminiProvider initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize GeminiProvider: {e}")
            self.model = None

    async def refine_analysis(self, findings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.model:
            return None
        
        try:
            prompt = self._get_prompt(findings)
            response = self.model.generate_content(prompt)
            return self._parse_json(response.text)
        except Exception as e:
            logger.error(f"Gemini refinement failed: {e}")
            return None

    async def chat(self, message: str) -> Optional[str]:
        if not self.model:
            return None

        try:
            prompt = f"You are a helpful AI Deployment Assistant. Answer the following user query directly and concisely.\n\nUser: {message}\nAssistant:"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat failed: {e}")
            return None
