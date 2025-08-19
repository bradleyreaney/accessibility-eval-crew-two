"""
Tests for the warning_suppression module.
"""

import logging
import os
import warnings
from unittest.mock import patch

import pytest

from src.utils.warning_suppression import (
    configure_quiet_logging,
    configure_silent_environment,
    suppress_all_warnings,
    suppress_warnings,
)


class TestWarningSuppression:
    """Test the warning suppression functionality."""

    def test_environment_variables_set_on_import(self):
        """Test that environment variables are set when module is imported."""
        # Import the module to trigger environment variable setting
        import src.utils.warning_suppression

        # Check that environment variables are set
        assert os.environ.get("PYTHONWARNINGS") is not None
        assert os.environ.get("PYTHONDONTWRITEBYTECODE") == "1"
        assert os.environ.get("TOKENIZERS_PARALLELISM") == "false"
        assert os.environ.get("TRANSFORMERS_VERBOSITY") == "error"

    def test_warning_filters_applied_on_import(self):
        """Test that warning filters are applied when module is imported."""
        # Import the module to trigger warning filter setup
        import src.utils.warning_suppression

        # Check that warning filters are in place
        filters = warnings.filters
        assert len(filters) > 0

    def test_suppress_warnings_context_manager(self):
        """Test the suppress_warnings context manager."""
        # Get initial warning state
        initial_logging_level = logging.getLogger().level

        with suppress_warnings():
            # Check that logging level is set to ERROR
            assert logging.getLogger().level == logging.ERROR

        # Check that original logging level is restored
        assert logging.getLogger().level == initial_logging_level

    def test_suppress_all_warnings_context_manager(self):
        """Test the suppress_all_warnings context manager."""
        # Get initial warning state
        initial_logging_level = logging.getLogger().level

        with suppress_all_warnings():
            # Check that logging level is set to CRITICAL
            assert logging.getLogger().level == logging.CRITICAL

        # Check that original logging level is restored
        assert logging.getLogger().level == initial_logging_level

    def test_suppress_all_warnings_disables_loggers(self):
        """Test that suppress_all_warnings disables specific loggers."""
        # Get initial logger states
        logger_names = [
            "pkg_resources",
            "pydantic",
            "crewai",
            "langchain",
            "crewai_tools",
            "httpx",
            "urllib3",
        ]
        initial_states = {}
        for name in logger_names:
            logger = logging.getLogger(name)
            initial_states[name] = logger.disabled

        with suppress_all_warnings():
            # Check that loggers are disabled
            for name in logger_names:
                logger = logging.getLogger(name)
                assert logger.disabled is True
                assert logger.level == logging.CRITICAL

        # Check that loggers are restored
        for name in logger_names:
            logger = logging.getLogger(name)
            assert logger.disabled == initial_states[name]

    def test_configure_quiet_logging(self):
        """Test the configure_quiet_logging function."""
        # Get initial logger levels
        logger_names = [
            "crewai",
            "langchain",
            "openai",
            "httpx",
            "pkg_resources",
            "pydantic",
            "crewai_tools",
        ]
        initial_levels = {}
        for name in logger_names:
            logger = logging.getLogger(name)
            initial_levels[name] = logger.level

        # Configure quiet logging
        configure_quiet_logging()

        # Check that loggers are set to ERROR level
        for name in logger_names:
            logger = logging.getLogger(name)
            assert logger.level == logging.ERROR

        # Restore original levels
        for name in logger_names:
            logger = logging.getLogger(name)
            logger.setLevel(initial_levels[name])

    def test_configure_silent_environment(self):
        """Test the configure_silent_environment function."""
        # Get initial environment variables
        initial_env = {}
        for key in [
            "TOKENIZERS_PARALLELISM",
            "TRANSFORMERS_VERBOSITY",
            "LANGCHAIN_VERBOSE",
            "CREWAI_VERBOSE",
        ]:
            initial_env[key] = os.environ.get(key)

        # Get initial logger levels
        logger_names = [
            "crewai",
            "langchain",
            "openai",
            "google",
            "httpx",
            "urllib3",
            "pkg_resources",
            "pydantic",
        ]
        initial_levels = {}
        for name in logger_names:
            logger = logging.getLogger(name)
            initial_levels[name] = logger.level

        # Configure silent environment
        configure_silent_environment()

        # Check that environment variables are set
        assert os.environ.get("TOKENIZERS_PARALLELISM") == "false"
        assert os.environ.get("TRANSFORMERS_VERBOSITY") == "error"
        assert os.environ.get("LANGCHAIN_VERBOSE") == "false"
        assert os.environ.get("CREWAI_VERBOSE") == "false"

        # Check that loggers are set to CRITICAL level
        for name in logger_names:
            logger = logging.getLogger(name)
            assert logger.level == logging.CRITICAL

        # Restore original environment and logger levels
        for key, value in initial_env.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)

        for name in logger_names:
            logger = logging.getLogger(name)
            logger.setLevel(initial_levels[name])

    def test_suppress_warnings_exception_handling(self):
        """Test that suppress_warnings handles exceptions gracefully."""
        # Get initial logging level
        initial_logging_level = logging.getLogger().level

        try:
            with suppress_warnings():
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Check that original logging level is restored even after exception
        assert logging.getLogger().level == initial_logging_level

    def test_suppress_all_warnings_exception_handling(self):
        """Test that suppress_all_warnings handles exceptions gracefully."""
        # Get initial logging level
        initial_logging_level = logging.getLogger().level

        try:
            with suppress_all_warnings():
                raise RuntimeError("Test exception")
        except RuntimeError:
            pass

        # Check that original logging level is restored even after exception
        assert logging.getLogger().level == initial_logging_level

    def test_warning_suppression_context_manager_works(self):
        """Test that the warning suppression context managers work without errors."""
        # Test that both context managers can be used without raising exceptions
        with suppress_warnings():
            pass

        with suppress_all_warnings():
            pass

        # If we get here, the context managers work
        assert True

    def test_logging_configuration_functions_work(self):
        """Test that logging configuration functions work without errors."""
        # Test that both configuration functions can be called without raising exceptions
        configure_quiet_logging()
        configure_silent_environment()

        # If we get here, the functions work
        assert True
