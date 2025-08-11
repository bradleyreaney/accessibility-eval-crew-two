"""
Tests for LLM configuration and connections
"""

import os
from unittest.mock import Mock, patch

import pytest

from src.config.llm_config import LLMConfig, LLMManager


class TestLLMConfig:
    """Test LLM configuration model"""

    def test_llm_config_initialization(self):
        """Test LLMConfig initialization with valid data"""
        config = LLMConfig(
            gemini_api_key="test_gemini_key", openai_api_key="test_openai_key"
        )

        assert config.gemini_api_key == "test_gemini_key"
        assert config.openai_api_key == "test_openai_key"
        assert config.gemini_model == "gemini-pro"
        assert config.openai_model == "gpt-4"
        assert config.temperature == 0.1

    def test_llm_config_custom_values(self):
        """Test LLMConfig with custom values"""
        config = LLMConfig(
            gemini_api_key="test_key_1",
            openai_api_key="test_key_2",
            temperature=0.5,
            timeout_seconds=60,
        )

        assert config.temperature == 0.5
        assert config.timeout_seconds == 60


class TestLLMManager:
    """Test LLM manager functionality"""

    def test_llm_manager_initialization(self, mock_llm_config):
        """Test LLM manager setup"""
        manager = LLMManager(mock_llm_config)

        assert manager.config == mock_llm_config
        assert manager._gemini_client is None
        assert manager._openai_client is None

    @patch("src.config.llm_config.ChatGoogleGenerativeAI")
    def test_gemini_client_creation(self, mock_gemini_class, mock_llm_config):
        """Test Gemini client creation"""
        mock_client = Mock()
        mock_gemini_class.return_value = mock_client

        manager = LLMManager(mock_llm_config)

        # Access the property to trigger client creation
        client = manager.gemini

        assert client == mock_client
        assert manager._gemini_client == mock_client
        mock_gemini_class.assert_called_once()

    @patch("src.config.llm_config.ChatOpenAI")
    def test_openai_client_creation(self, mock_openai_class, mock_llm_config):
        """Test OpenAI client creation"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        manager = LLMManager(mock_llm_config)

        # Access the property to trigger client creation
        client = manager.openai

        assert client == mock_client
        assert manager._openai_client == mock_client
        mock_openai_class.assert_called_once()

    @patch("src.config.llm_config.ChatGoogleGenerativeAI")
    @patch("src.config.llm_config.ChatOpenAI")
    def test_test_connections_success(
        self, mock_openai_class, mock_gemini_class, mock_llm_config
    ):
        """Test successful connection testing"""
        # Setup mocks
        mock_gemini = Mock()
        mock_openai = Mock()
        mock_gemini.invoke.return_value = "Connection successful"
        mock_openai.invoke.return_value = "Connection successful"
        mock_gemini_class.return_value = mock_gemini
        mock_openai_class.return_value = mock_openai

        manager = LLMManager(mock_llm_config)
        results = manager.test_connections()

        assert results["gemini"] is True
        assert results["openai"] is True
        mock_gemini.invoke.assert_called_once()
        mock_openai.invoke.assert_called_once()

    @patch("src.config.llm_config.ChatGoogleGenerativeAI")
    @patch("src.config.llm_config.ChatOpenAI")
    def test_test_connections_failure(
        self, mock_openai_class, mock_gemini_class, mock_llm_config
    ):
        """Test connection failure handling"""
        # Setup mocks to raise exceptions
        mock_gemini = Mock()
        mock_openai = Mock()
        mock_gemini.invoke.side_effect = Exception("Gemini connection failed")
        mock_openai.invoke.side_effect = Exception("OpenAI connection failed")
        mock_gemini_class.return_value = mock_gemini
        mock_openai_class.return_value = mock_openai

        manager = LLMManager(mock_llm_config)
        results = manager.test_connections()

        assert results["gemini"] is False
        assert results["openai"] is False

    @patch.dict(
        os.environ,
        {
            "GOOGLE_API_KEY": "env_gemini_key",
            "OPENAI_API_KEY": "env_openai_key",
            "LLM_TIMEOUT_SECONDS": "45",
        },
    )
    def test_from_environment(self):
        """Test creating LLMManager from environment variables"""
        manager = LLMManager.from_environment()

        assert manager.config.gemini_api_key == "env_gemini_key"
        assert manager.config.openai_api_key == "env_openai_key"
        assert manager.config.timeout_seconds == 45

    def test_from_environment_missing_keys(self):
        """Test environment creation with missing API keys"""
        with patch.dict(os.environ, {}, clear=True):
            manager = LLMManager.from_environment()
            assert manager.config.gemini_api_key == ""
            assert manager.config.openai_api_key == ""


class TestLLMIntegration:
    """Integration tests for LLM connections"""

    @pytest.mark.integration
    @pytest.mark.llm
    def test_real_llm_connections(self):
        """Test connections to real LLM APIs (requires API keys)"""
        # Only run if API keys are available
        gemini_key = os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if (
            not gemini_key
            or not openai_key
            or gemini_key.startswith("test_")
            or openai_key.startswith("test_")
        ):
            pytest.skip("Real API keys not available for integration test")

        config = LLMConfig(gemini_api_key=gemini_key, openai_api_key=openai_key)

        manager = LLMManager(config)
        results = manager.test_connections()

        # At least one should work for integration tests
        assert any(results.values()), f"No LLM connections working: {results}"
