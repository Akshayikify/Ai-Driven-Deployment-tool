"""
Unit tests for AI Provider selection, missing API keys, model validation,
error sanitization, and graceful fallback behavior.
"""
import unittest
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.config import settings
from app.services.ai_providers.base import sanitize_error
from app.services.ai_providers.groq_provider import GroqProvider, is_valid_groq_key
from app.services.ai_providers.openrouter_provider import OpenRouterProvider, is_valid_openrouter_key
from app.services.ai_providers.gemini_provider import GeminiProvider, is_valid_gemini_key
from app.services.ai_service import AIService


class TestAIProviders(unittest.IsolatedAsyncioTestCase):

    def test_key_validators(self):
        """Test API key validation logic across providers."""
        # Groq key validation
        self.assertFalse(is_valid_groq_key(None))
        self.assertFalse(is_valid_groq_key(""))
        self.assertFalse(is_valid_groq_key("   "))
        self.assertFalse(is_valid_groq_key("placeholder"))
        self.assertFalse(is_valid_groq_key("sk-invalid-prefix-1234567890"))
        self.assertFalse(is_valid_groq_key("gsk_tooshort"))
        self.assertTrue(is_valid_groq_key("gsk_validprefixlongkey1234567890"))

        # OpenRouter key validation
        self.assertFalse(is_valid_openrouter_key(None))
        self.assertFalse(is_valid_openrouter_key(""))
        self.assertFalse(is_valid_openrouter_key("short"))
        self.assertTrue(is_valid_openrouter_key("sk-or-v1-abcdefghijklmnopqrstuvwxyz123456"))

        # Gemini key validation
        self.assertFalse(is_valid_gemini_key(None))
        self.assertFalse(is_valid_gemini_key(""))
        self.assertFalse(is_valid_gemini_key("short"))
        self.assertTrue(is_valid_gemini_key("AIzaSyAbcdefghijklmnopqrstuvwxyz123456"))

    def test_error_sanitization(self):
        """Verify that secret keys and authorization tokens are redacted from error messages."""
        groq_err = Exception("404 Error with key gsk_secretkey1234567890123456 at https://api.groq.com")
        sanitized = sanitize_error(groq_err)
        self.assertNotIn("gsk_secretkey1234567890123456", sanitized)
        self.assertIn("[REDACTED_KEY]", sanitized)

        bearer_err = Exception("Authorization failed: Bearer sk-or-v1-supersecrettoken12345678")
        sanitized_bearer = sanitize_error(bearer_err)
        self.assertNotIn("sk-or-v1-supersecrettoken12345678", sanitized_bearer)
        self.assertIn("Bearer [REDACTED_TOKEN]", sanitized_bearer)

    def test_groq_model_replacement(self):
        """Ensure deprecated llama-3.3-70b-versatile is automatically replaced with supported default."""
        with patch.object(settings, "GROQ_API_KEY", "gsk_testvalidkey12345678901234"):
            # When initialized with deprecated model
            provider = GroqProvider("gsk_testvalidkey12345678901234", model="llama-3.3-70b-versatile")
            self.assertEqual(provider.model, "openai/gpt-oss-120b")

            # When initialized with custom model
            provider_custom = GroqProvider("gsk_testvalidkey12345678901234", model="custom-groq-model")
            self.assertEqual(provider_custom.model, "custom-groq-model")

    def test_groq_not_selected_when_key_missing(self):
        """Verify Groq is not instantiated or selected when GROQ_API_KEY is empty or missing."""
        with patch.object(settings, "GROQ_API_KEY", ""):
            with patch.object(settings, "OPENROUTER_API_KEY", "sk-or-v1-validkey1234567890"):
                with patch.object(settings, "GOOGLE_API_KEY", "AIzaSyValidGeminiKey123456"):
                    service = AIService()
                    provider_classes = [p.__class__.__name__ for p in service.providers]
                    self.assertNotIn("GroqProvider", provider_classes)
                    self.assertIn("OpenRouterProvider", provider_classes)
                    self.assertIn("GeminiProvider", provider_classes)

    def test_provider_priority_openrouter_primary_gemini_fallback(self):
        """Verify OpenRouter is priority 1, Gemini is priority 2, and Groq is priority 3."""
        with patch.object(settings, "OPENROUTER_API_KEY", "sk-or-v1-validkey1234567890"):
            with patch.object(settings, "GOOGLE_API_KEY", "AIzaSyValidGeminiKey123456"):
                with patch.object(settings, "GROQ_API_KEY", "gsk_testvalidkey12345678901234"):
                    service = AIService()
                    provider_classes = [p.__class__.__name__ for p in service.providers]
                    self.assertEqual(provider_classes[0], "OpenRouterProvider")
                    self.assertEqual(provider_classes[1], "GeminiProvider")
                    self.assertEqual(provider_classes[2], "GroqProvider")

    async def test_chat_fallback_on_model_not_found(self):
        """
        Simulate primary provider returning 404 model_not_found error.
        Verify that AIService gracefully falls back to secondary provider.
        """
        service = AIService()
        
        # Create mock primary provider that raises 404 model_not_found
        primary_mock = MagicMock()
        primary_mock.provider_name = "MockPrimaryProvider"
        primary_mock.chat = AsyncMock(side_effect=Exception("404 model_not_found: The model does not exist"))

        # Create mock fallback provider that succeeds
        fallback_mock = MagicMock()
        fallback_mock.provider_name = "MockFallbackProvider"
        fallback_mock.chat = AsyncMock(return_value="Hello from fallback provider!")

        service.providers = [primary_mock, fallback_mock]

        response = await service.chat_with_agent("How do I deploy with Docker?")
        self.assertEqual(response, "Hello from fallback provider!")
        primary_mock.chat.assert_awaited_once_with("How do I deploy with Docker?")
        fallback_mock.chat.assert_awaited_once_with("How do I deploy with Docker?")

    async def test_chat_all_providers_fail(self):
        """When all providers fail, return graceful fallback message without 500 error."""
        service = AIService()

        failing_mock = MagicMock()
        failing_mock.provider_name = "FailingProvider"
        failing_mock.chat = AsyncMock(side_effect=Exception("Connection timed out"))

        service.providers = [failing_mock]

        response = await service.chat_with_agent("Hello")
        self.assertIn("trouble connecting to my AI backend", response)

    async def test_chat_no_providers_configured(self):
        """When no providers are configured, return offline message."""
        service = AIService()
        service.providers = []

        response = await service.chat_with_agent("Hello")
        self.assertIn("offline mode", response)


if __name__ == "__main__":
    unittest.main()

