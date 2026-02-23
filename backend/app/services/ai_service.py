import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from loguru import logger
from app.core.config import settings

class AIService:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
            logger.warning("GOOGLE_API_KEY (settings) not found. AIService will be disabled.")

    async def refine_analysis(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses AI to refine analysis findings when rule-based confidence is low.
        """
        if not self.model:
            logger.info("AI Refinement skipped: No API key provided.")
            return findings

        try:
            # Prepare a compact representation of the file structure
            file_list = findings.get("file_index", {}).get("all_files", [])[:100] # Cap for context
            prompt = f"""
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
            
            response = self.model.generate_content(prompt)
            # Basic JSON extraction logic
            import json
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            
            ai_data = json.loads(text)
            logger.info(f"AI refinement received: {ai_data}")
            
            # Update findings
            findings.update(ai_data)
            findings["ai_refined"] = True
            
        except Exception as e:
            logger.error(f"AI Refinement failed: {e}")
            
        return findings

ai_service = AIService()
