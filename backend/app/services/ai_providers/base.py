import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

def sanitize_error(err: Any) -> str:
    """
    Strips potential API keys, auth headers, and tokens from error strings
    to ensure secrets are never leaked in application logs.
    """
    msg = str(err)
    # Redact Authorization: Bearer tokens first (before raw key patterns)
    msg = re.sub(r'Bearer\s+[a-zA-Z0-9_\.\-\+/=]+', 'Bearer [REDACTED_TOKEN]', msg)
    # Redact common key prefixes and tokens
    msg = re.sub(r'(gsk_|sk-or-v1-|sk-|AIzaSy)[a-zA-Z0-9_\-]{6,}', '[REDACTED_KEY]', msg)
    msg = re.sub(r'key=[a-zA-Z0-9_\-]+', 'key=[REDACTED]', msg)
    # Safety normalization if Bearer was ever followed by [REDACTED_KEY]
    msg = re.sub(r'Bearer\s+\[REDACTED_KEY\]', 'Bearer [REDACTED_TOKEN]', msg)
    return msg

class AIProvider(ABC):
    @property
    def provider_name(self) -> str:
        return self.__class__.__name__

    def is_available(self) -> bool:
        """Indicates whether this provider has a valid client and configuration."""
        return True

    @abstractmethod
    async def refine_analysis(self, findings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Refines the analysis using the specific AI provider."""
        pass

    @abstractmethod
    async def chat(self, message: str) -> Optional[str]:
        """Generates a conversational response based on the user's message."""
        pass

    @abstractmethod
    async def generate_dockerfile(self, prompt: str) -> Optional[str]:
        """Generates a raw Dockerfile string from a prompt."""
        pass

    def _get_prompt(self, findings: Dict[str, Any]) -> str:
        file_list = findings.get("file_index", {}).get("all_files", [])[:100]
        return f"""
        Analyze the following project file structure and suggest the main programming language, 
        framework, and the best entry point for a Docker container.
        
        Files:
        {", ".join(file_list)}
        
        Current Findings:
        Language: {findings.get('language')}
        Framework: {findings.get('framework')}
        
        Respond ONLY in JSON format like:
        {{
            "language": "...",
            "framework": "...",
            "entry_point": "...",
            "confidence": 0.9
        }}
        """

    def _parse_json(self, text: str) -> Dict[str, Any]:
        import json
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].strip()
        return json.loads(text)
