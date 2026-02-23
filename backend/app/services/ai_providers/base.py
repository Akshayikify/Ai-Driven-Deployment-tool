from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AIProvider(ABC):
    @abstractmethod
    async def refine_analysis(self, findings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Refines the analysis using the specific AI provider."""
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
