"""
LLM configuration and connection management
References: Master Plan - LLM Integration section
"""

import os
from typing import Optional, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """Configuration for LLM connections"""

    gemini_api_key: str
    openai_api_key: str
    gemini_model: str = "gemini-pro"
    openai_model: str = "gpt-4"
    temperature: float = 0.1  # Low temperature for consistent evaluation
    max_tokens: Optional[int] = None
    timeout_seconds: int = 30
    max_retries: int = 3


class LLMManager:
    """
    Manages connections to judge LLMs
    Provides consistent interface for both Gemini and GPT-4
    """

    def __init__(self, config: LLMConfig):
        """
        Initialize LLM manager with configuration.

        Args:
            config: LLM configuration containing API keys and settings
        """
        self.config = config
        self._gemini_client: Optional[ChatGoogleGenerativeAI] = None
        self._openai_client: Optional[ChatOpenAI] = None

    @property
    def gemini(self) -> ChatGoogleGenerativeAI:
        """Get Gemini Pro client"""
        if self._gemini_client is None:
            # Set environment variable temporarily for LangChain
            os.environ["GOOGLE_API_KEY"] = self.config.gemini_api_key
            self._gemini_client = ChatGoogleGenerativeAI(
                model=self.config.gemini_model, temperature=self.config.temperature
            )
        return self._gemini_client

    @property
    def openai(self) -> ChatOpenAI:
        """Get GPT-4 client"""
        if self._openai_client is None:
            # Set environment variable temporarily for LangChain
            os.environ["OPENAI_API_KEY"] = self.config.openai_api_key
            self._openai_client = ChatOpenAI(
                model=self.config.openai_model,
                temperature=self.config.temperature,
                # max_tokens parameter removed as it's not supported in newer versions
            )
        return self._openai_client

    def test_connections(self) -> Dict[str, bool]:
        """
        Test connections to both LLMs
        Returns success status for each
        """
        results = {}

        # Test Gemini
        try:
            logger.info("Testing Gemini connection...")
            _ = self.gemini.invoke(
                "Hello, this is a connection test. Please respond with 'Connection successful.'"
            )
            results["gemini"] = True
            logger.info("Gemini connection successful")
        except Exception as e:
            logger.error(f"Gemini connection failed: {e}")
            results["gemini"] = False

        # Test OpenAI
        try:
            logger.info("Testing OpenAI connection...")
            _ = self.openai.invoke(
                "Hello, this is a connection test. Please respond with 'Connection successful.'"
            )
            results["openai"] = True
            logger.info("OpenAI connection successful")
        except Exception as e:
            logger.error(f"OpenAI connection failed: {e}")
            results["openai"] = False

        return results

    @classmethod
    def from_environment(cls) -> "LLMManager":
        """Create LLMManager from environment variables"""
        config = LLMConfig(
            gemini_api_key=os.getenv("GOOGLE_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            timeout_seconds=int(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
            max_retries=int(os.getenv("MAX_RETRY_ATTEMPTS", "3")),
        )

        if not config.gemini_api_key:
            logger.warning("GOOGLE_API_KEY not set in environment")
        if not config.openai_api_key:
            logger.warning("OPENAI_API_KEY not set in environment")

        return cls(config)
