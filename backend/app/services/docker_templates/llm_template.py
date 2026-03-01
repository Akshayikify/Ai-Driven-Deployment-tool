from typing import Dict, Any, Optional
from loguru import logger
from app.services.ai_service import ai_service
from .base import DockerTemplate

class LLMDockerTemplate(DockerTemplate):
    async def generate_dockerfile(self, findings: Dict[str, Any]) -> str:
        """
        Dynamically generates a Dockerfile using an LLM.
        This overrides the base class interface by making it async.
        """
        logger.info(f"Using LLM Fallback to generate Dockerfile for {findings.get('language')}")
        content = await ai_service.generate_dockerfile(findings)
        
        if not content:
            logger.error("LLM failed to generate Dockerfile. Falling back to a basic generic template.")
            content = (
                "FROM ubuntu:jammy\n"
                "CMD [\"echo\", \"Placeholder container. LLM generation failed.\"]\n"
            )
            
        return content
