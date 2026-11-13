from typing import Dict, Any, List, Optional
from loguru import logger
from app.core.config import settings
from .ai_providers.gemini_provider import GeminiProvider
from .ai_providers.openrouter_provider import OpenRouterProvider
from .ai_providers.groq_provider import GroqProvider
from .ai_providers.base import AIProvider, sanitize_error

class AIService:
    def __init__(self):
        self.providers: List[AIProvider] = []
        self.load_providers()

    def load_providers(self):
        """
        Initializes AI providers in strict priority order:
          1. OpenRouter (Primary)
          2. Google Gemini (Fallback)
          3. Groq (Optional tertiary, only if explicitly enabled with a valid key and model)
        """
        self.providers = []

        # Priority 1: OpenRouter (Primary)
        openrouter_key = getattr(settings, "OPENROUTER_API_KEY", None)
        if openrouter_key and openrouter_key.strip():
            openrouter = OpenRouterProvider(openrouter_key)
            if openrouter.is_available():
                self.providers.append(openrouter)

        # Priority 2: Google Gemini (Fallback)
        gemini_key = getattr(settings, "GOOGLE_API_KEY", None)
        if gemini_key and gemini_key.strip():
            gemini = GeminiProvider(gemini_key)
            if gemini.is_available():
                self.providers.append(gemini)

        # Priority 3: Groq (Optional tertiary - only if explicitly provided with a valid key and model)
        groq_key = getattr(settings, "GROQ_API_KEY", None)
        if groq_key and groq_key.strip():
            groq = GroqProvider(groq_key)
            if groq.is_available():
                self.providers.append(groq)

        if self.providers:
            provider_names = [p.provider_name for p in self.providers]
            logger.info(f"AI Service initialized. Active providers in priority order: {provider_names}")
        else:
            logger.warning("No active AI providers configured. AI features will run in degraded/offline mode.")

    async def refine_analysis(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrates refinement across available AI providers with a fallback mechanism.
        """
        if not self.providers:
            return findings

        for i, provider in enumerate(self.providers):
            provider_name = provider.provider_name
            try:
                logger.info(f"Attempting AI refinement with {provider_name} (priority {i + 1}/{len(self.providers)})...")
                ai_data = await provider.refine_analysis(findings)
                
                if ai_data:
                    logger.info(f"Refinement successful using {provider_name}")
                    findings.update(ai_data)
                    findings["ai_refined"] = True
                    findings["ai_provider"] = provider_name
                    return findings
                else:
                    logger.warning(f"Provider {provider_name} returned empty refinement data. Attempting fallback...")
                
            except Exception as e:
                safe_err = sanitize_error(e)
                logger.warning(f"Provider {provider_name} failed during refinement: {safe_err}. Attempting fallback...")
                continue

        logger.warning("All AI providers failed to refine analysis.")
        return findings

    async def chat_with_agent(self, message: str) -> str:
        """
        Orchestrates generic chat queries across available providers in priority order.
        Falls back to the next provider if the current provider fails.
        """
        if not self.providers:
            logger.warning("Chat requested but no AI providers are available.")
            return "I'm currently running in offline mode without an API key, so I can only perform basic static analysis and generic replies."

        for i, provider in enumerate(self.providers):
            provider_name = provider.provider_name
            try:
                logger.info(f"Attempting chat with {provider_name} (priority {i + 1}/{len(self.providers)})...")
                response = await provider.chat(message)
                if response and isinstance(response, str) and response.strip():
                    logger.info(f"Chat response successfully generated using {provider_name}")
                    return response.strip()
                else:
                    logger.warning(f"Provider {provider_name} returned empty response. Attempting fallback...")
            except Exception as e:
                safe_err = sanitize_error(e)
                logger.warning(f"Provider {provider_name} encountered error during chat: {safe_err}. Attempting fallback...")
                continue
                
        logger.error("All available AI providers failed to generate a chat response.")
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

        for i, provider in enumerate(self.providers):
            provider_name = provider.provider_name
            try:
                logger.info(f"Attempting Dockerfile generation with {provider_name} (priority {i + 1}/{len(self.providers)})...")
                response = await provider.generate_dockerfile(prompt)
                if response:
                    logger.info(f"Generated Dockerfile using {provider_name}")
                    return response
                else:
                    logger.warning(f"Provider {provider_name} returned empty Dockerfile. Attempting fallback...")
            except Exception as e:
                safe_err = sanitize_error(e)
                logger.warning(f"Provider {provider_name} failed Dockerfile gen: {safe_err}. Attempting fallback...")
                continue
                
        logger.warning("All AI providers failed to generate Dockerfile.")
        return None

    async def analyze_build_failure(
        self,
        logs: str,
        repo_url: str,
        workflow_path: str = None,
        file_contexts: Optional[Dict[str, str]] = None,
        context_hint: str = ""
    ) -> Optional[str]:
        """
        Analyzes failed GitHub Actions logs and provides a strict JSON payload with diagnosis and file fixes.
        """
        if not self.providers:
            return None

        # Truncate logs to avoid massive context window payloads
        truncated_logs = logs[-8000:] if len(logs) > 8000 else logs

        extra_hint = f" The original workflow filename was identified as: {workflow_path}." if workflow_path else ""
        context_hint = extra_hint + (context_hint or "")

        files_context_str = ""
        if file_contexts:
            files_context_str = "\nOriginal file contents currently in repository:\n"
            for path, content in file_contexts.items():
                files_context_str += f"\nFile: `{path}`\n```\n{content}\n```\n"

        prompt = rf"""
        You are an expert DevOps engineer and AI assistant. The following are the raw terminal logs from a failed GitHub Actions CI/CD pipeline run for the repository: {repo_url}.{context_hint}
        
        <logs>
        {truncated_logs}
        </logs>
        {files_context_str}
        
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
        - Python: python:3.11-slim, python:3.10-slim (NEVER use alpine for Python web applications)
        - Go: golang:1.21-alpine, golang:1.20-bookworm
        - PHP: php:8.2-fpm-alpine, php:8.1-apache

        TIPS FOR DOCKERFILE ERRORS:
        - If 'mvn' not found: Use a 'maven' builder image.
        - If 'mvnw' permission denied: Add 'chmod +x mvnw' before running.
        - If 'javac' not found: Use a 'jdk' image, not 'jre'.
        - If 'gunicorn: not found' or 'No module named <pkg>': Ensure the package is installed via 'pip install' in Dockerfile or listed in requirements.txt. Retain the existing WSGI/ASGI module from the original Dockerfile.

        CRITICAL CONSTRAINTS:
        - NEVER suggest 'fixing the Maven version URL protocol' if the error is a generic 'exit code: 1' during compilation.
        - For Python apps: NEVER use alpine images (they lack glibc/C headers). Always use 'python:3.11-slim'.
        - If requirements.txt is not in the repository, DO NOT use 'COPY requirements.txt .' in Dockerfile without also creating requirements.txt via action 'create_file'.
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

        for i, provider in enumerate(self.providers):
            provider_name = provider.provider_name
            try:
                logger.info(f"Attempting log analysis with {provider_name} (priority {i + 1}/{len(self.providers)})...")
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
                    logger.info(f"Log analysis successful using {provider_name}")
                    return cleaned.strip()
                else:
                    logger.warning(f"Provider {provider_name} returned empty log analysis. Attempting fallback...")
            except Exception as e:
                safe_err = sanitize_error(e)
                logger.warning(f"Provider {provider_name} failed log analysis: {safe_err}. Attempting fallback...")
                continue
                
        logger.error("All AI providers failed to analyze build failure.")
        return None

ai_service = AIService()
