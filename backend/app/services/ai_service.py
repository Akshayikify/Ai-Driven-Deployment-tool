from typing import Dict, Any, List, Optional
from loguru import logger
from app.core.config import settings
from .ai_providers.gemini_provider import GeminiProvider
from .ai_providers.openrouter_provider import OpenRouterProvider
from .ai_providers.groq_provider import GroqProvider
from .ai_providers.base import AIProvider

class AIService:
    def __init__(self):
        self.providers: List[AIProvider] = []
        
        # Initialize providers based on available keys
        # We prioritize Groq for its extreme speed and stability
        if settings.GROQ_API_KEY:
            self.providers.append(GroqProvider(settings.GROQ_API_KEY))
        
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

        VERIFIED DOCKER KNOWLEDGE BASE (Use these specific tags, avoid generic -slim for Temurin):
        - Java (Builder): maven:3-eclipse-temurin-17-alpine, maven:3.8-openjdk-11-slim
        - Java (Runtime): eclipse-temurin:17-jre-alpine, eclipse-temurin:11-jre-focal
        - Node.js: node:18-alpine, node:20-slim, node:16-bullseye-slim
        - Python: python:3.11-slim, python:3.9-alpine, python:3.10-bookworm
        - Go: golang:1.21-alpine, golang:1.20-bookworm
        - PHP: php:8.2-fpm-alpine, php:8.1-apache

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

    async def analyze_build_failure(self, logs: str, repo_url: str, workflow_path: str = None) -> Optional[str]:
        """
        Analyzes failed GitHub Actions logs and provides a strict JSON payload with diagnosis and file fixes.
        """
        if not self.providers:
            return None

        # Truncate logs to avoid massive context window payloads
        truncated_logs = logs[-8000:] if len(logs) > 8000 else logs

        context_hint = f" The original workflow filename was identified as: {workflow_path}." if workflow_path else ""

        prompt = rf"""
        You are an expert DevOps engineer and AI assistant. The following are the raw terminal logs from a failed GitHub Actions CI/CD pipeline run for the repository: {repo_url}.{context_hint}
        
        <logs>
        {truncated_logs}
        </logs>
        
        Please analyze these logs and determine exactly how to fix the repository code to make the pipeline pass.
        If you are modifying a workflow file, make sure it is the correct filename (e.g., '.github/workflows/deploy.yml' or as specified in the hint).
        
        STRICT DIAGNOSTIC PROTOCOL:
        1. Identify the EXACT failing command (look for 'RUN' steps or 'exit code: 1').
        2. Read the error message IMMEDIATELY following that command. 
        3. Do NOT guess or assume 'protocol' errors (like https vs https\) unless you see a 'Protocol error' or 'SSL error' in the raw log.
        4. If it's a Maven build:
            - If it mentions 'No such file': Check if pom.xml was copied.
            - If it mentions 'Permission denied': Recommend 'chmod +x mvnw'.
            - If it mentions 'mvn: not found': Recommend a 'maven' builder image.
            - If it mentions a weird '$'\r' symbol': It's a Windows line ending issue; recommend 'sed -i 's/\r$//' mvnw'.

        VERIFIED DOCKER KNOWLEDGE BASE (Use these specific tags, avoid generic -slim for Temurin):
        - Java (Builder): maven:3-eclipse-temurin-17-alpine, maven:3.8-openjdk-11-slim
        - Java (Runtime): eclipse-temurin:17-jre-alpine, eclipse-temurin:11-jre-focal
        - Node.js: node:18-alpine, node:20-slim, node:16-bullseye-slim
        - Python: python:3.11-slim, python:3.9-alpine, python:3.10-bookworm
        - Go: golang:1.21-alpine, golang:1.20-bookworm
        - PHP: php:8.2-fpm-alpine, php:8.1-apache

        TIPS FOR DOCKERFILE ERRORS:
        - If 'mvn' not found: Use a 'maven' builder image.
        - If 'mvnw' permission denied: Add 'chmod +x mvnw' before running.
        - If 'javac' not found: Use a 'jdk' image, not 'jre'.

        CRITICAL CONSTRAINTS:
        - NEVER suggest 'fixing the Maven version URL protocol' if the error is a generic 'exit code: 1' during compilation.
        - Always provide the FULL content of any file you create or modify, not just a snippet.
        - Do NOT remove or bypass critical deployment stages such as 'Build and push Docker image', 'Log in to the Container registry', or 'Extract metadata'.
        - If an image tag is 'Not Found', cross-check with the Verified Knowledge Base above and use an alpine or full version.
        
        You MUST respond ONLY with a valid JSON object. No markdown formatting, no conversational text.
        
        The JSON MUST perfectly follow this schema:
        {{
            "diagnosis": "A concise 2-sentence explanation of why it failed and what you are doing to fix it.",
            "actions": [
                {{
                    "action": "create_file",  // or "modify_file"
                    "path": "path/to/file.ext", // relative to repository root
                    "content": "The exact full file contents to write..."
                }}
            ]
        }}
        """

        for provider in self.providers:
            try:
                logger.info(f"Attempting log analysis with {provider.__class__.__name__}...")
                response = await provider.chat(prompt) 
                if response:
                    # Clean up markdown JSON blocks if the LLM ignored instructions
                    cleaned = response.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    if cleaned.startswith("```"):
                        cleaned = cleaned[3:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    return cleaned.strip()
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed log analysis: {e}")
                continue
                
        return None

ai_service = AIService()
