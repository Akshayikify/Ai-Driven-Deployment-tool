from typing import Dict, Any, List, Optional
from loguru import logger
from app.core.config import settings
from .ai_providers.gemini_provider import GeminiProvider
from .ai_providers.openrouter_provider import OpenRouterProvider
from .ai_providers.base import AIProvider

class AIService:
    def __init__(self):
        self.providers: List[AIProvider] = []
        
        # Initialize providers based on available keys
        # We prioritize OpenRouter if provided, as it's often more flexible
        if settings.OPENROUTER_API_KEY:
            self.providers.append(OpenRouterProvider(settings.OPENROUTER_API_KEY))
        
        if settings.GOOGLE_API_KEY:
            self.providers.append(GeminiProvider(settings.GOOGLE_API_KEY))

        if not self.providers:
            logger.warning("No AI providers configured. Refinement will be disabled.")

    async def refine_analysis(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrates refinement across available AI providers with a fallback mechanism.
        """
        if not self.providers:
            return findings

        for provider in self.providers:
            try:
                logger.info(f"Attempting AI refinement with {provider.__class__.__name__}...")
                ai_data = await provider.refine_analysis(findings)
                
                if ai_data:
                    logger.info(f"Refinement successful using {provider.__class__.__name__}")
                    findings.update(ai_data)
                    findings["ai_refined"] = True
                    findings["ai_provider"] = provider.__class__.__name__
                    return findings
                
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed: {e}")
                continue

        logger.warning("All AI providers failed to refine analysis.")
        return findings

    async def chat_with_agent(self, message: str) -> str:
        """
        Orchestrates generic chat queries across available providers.
        """
        if not self.providers:
            return "I'm currently running in offline mode without an API key, so I can only perform basic static analysis and generic replies."

        for provider in self.providers:
            try:
                response = await provider.chat(message)
                if response:
                    return response
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed during chat: {e}")
                continue
                
        return "I'm sorry, I'm having trouble connecting to my AI backend right now. Please try again later."

    async def generate_dockerfile(self, findings: Dict[str, Any]) -> Optional[str]:
        """
        Orchestrates LLM generation of a fallback Dockerfile for an unrecognized project.
        """
        if not self.providers:
            logger.warning("No AI providers configured. Cannot generate fallback Dockerfile.")
            return None

        file_list = findings.get("file_index", {}).get("all_files", [])[:500]
        prompt = f"""
        Write a production-ready, highly optimized Dockerfile for the following repository.
        The language was detected as: {findings.get('language')}, Framework: {findings.get('framework')}.

        Project Files:
        {", ".join(file_list)}

        Output EXACTLY AND ONLY the raw Dockerfile content. NO explanations, NO markdown code blocks, NO backticks.
        """

        for provider in self.providers:
            try:
                logger.info(f"Attempting Dockerfile generation with {provider.__class__.__name__}...")
                response = await provider.generate_dockerfile(prompt)
                if response:
                    logger.info(f"Generated Dockerfile using {provider.__class__.__name__}")
                    return response
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed Dockerfile gen: {e}")
                continue
                
        logger.warning("All AI providers failed to generate Dockerfile.")
        return None

ai_service = AIService()
