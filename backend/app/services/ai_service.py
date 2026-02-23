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

ai_service = AIService()
