"""
Advanced warning suppression for CrewAI and LangChain components.

This module provides comprehensive warning suppression to eliminate noise
from CrewAI callback handlers and other third-party library warnings.

References:
    - CrewAI callback handling issues
    - LangChain warning suppression
    - Runtime warning management
"""

import logging
import os
import warnings
from contextlib import contextmanager
from typing import Any, Dict

# Set environment variables for maximum warning suppression
os.environ["PYTHONWARNINGS"] = (
    "ignore::DeprecationWarning,ignore::UserWarning,ignore::FutureWarning"
)
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

# Apply all warning filters immediately
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")

# Catch specific warnings we're seeing
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Additional filters for specific messages
warnings.filterwarnings("ignore", message=".*pkg_resources.*")
warnings.filterwarnings("ignore", message=".*declare_namespace.*")
warnings.filterwarnings("ignore", message=".*Pydantic.*")
warnings.filterwarnings("ignore", message=".*@validator.*")
warnings.filterwarnings("ignore", message=".*__fields__.*")
warnings.filterwarnings("ignore", message=".*schema.*method.*")
warnings.filterwarnings("ignore", message=".*config.*deprecated.*")
warnings.filterwarnings("ignore", message=".*crewai_tools.*")
warnings.filterwarnings("ignore", message=".*AttributeError.*")

# Module-specific suppressions
warnings.filterwarnings("ignore", module="pkg_resources")
warnings.filterwarnings("ignore", module="crewai")
warnings.filterwarnings("ignore", module="pydantic")
warnings.filterwarnings("ignore", module="google")
warnings.filterwarnings("ignore", module="langchain")
warnings.filterwarnings("ignore", module="crewai_tools")


@contextmanager
def suppress_warnings():
    """
    Context manager to suppress warnings during crew execution.

    Temporarily disables warnings to provide clean output during evaluation.
    """
    # Save current warning state
    old_warnings = list(warnings.filters)
    old_level = logging.getLogger().level

    try:
        # Clear and reset all warning filters
        warnings.resetwarnings()
        warnings.filterwarnings("ignore")

        # Set logging to ERROR level to suppress INFO messages
        logging.getLogger().setLevel(logging.ERROR)
        logging.getLogger("crewai").setLevel(logging.ERROR)
        logging.getLogger("langchain").setLevel(logging.ERROR)
        logging.getLogger("pydantic").setLevel(logging.ERROR)

        yield

    finally:
        # Restore original warning filters safely
        warnings.resetwarnings()
        for filter_item in old_warnings:
            try:
                # Handle different types of filter items
                if len(filter_item) >= 1 and filter_item[0] in (
                    "error",
                    "ignore",
                    "always",
                    "default",
                    "module",
                    "once",
                ):
                    action = filter_item[0]

                    # Handle message parameter - could be string, regex, or None
                    message = filter_item[1] if len(filter_item) > 1 else ""
                    if message is not None and not isinstance(message, str):
                        # Skip non-string messages (like regex objects)
                        continue
                    # Convert None to empty string for warnings.filterwarnings
                    if message is None:
                        message = ""

                    # Handle other parameters with safe defaults
                    category = (
                        filter_item[2]
                        if len(filter_item) > 2 and filter_item[2] is not None
                        else Warning
                    )
                    module = filter_item[3] if len(filter_item) > 3 else ""
                    if module is not None and not isinstance(module, str):
                        # Skip non-string modules (like regex objects)
                        continue
                    # Convert None to empty string for warnings.filterwarnings
                    if module is None:
                        module = ""
                    lineno = (
                        filter_item[4]
                        if len(filter_item) > 4 and filter_item[4] is not None
                        else 0
                    )
                    append = (
                        filter_item[5]
                        if len(filter_item) > 5 and filter_item[5] is not None
                        else False
                    )

                    warnings.filterwarnings(
                        action, message, category, module, lineno, append
                    )
            except (ValueError, TypeError, IndexError):
                # Skip invalid filter items
                continue
        logging.getLogger().setLevel(old_level)


@contextmanager
def suppress_all_warnings():
    """
    Context manager to suppress all warnings during execution.

    This includes CrewAI callbacks, deprecation warnings, and runtime warnings.
    """
    # Save current warning state
    old_warnings = list(warnings.filters)
    old_logging_level = logging.getLogger().level

    try:
        # Suppress all warnings completely
        warnings.resetwarnings()
        warnings.filterwarnings("ignore")
        warnings.simplefilter("ignore")

        # Set logging level to CRITICAL to suppress everything
        logging.getLogger().setLevel(logging.CRITICAL)

        # Suppress specific loggers completely
        logger_names = [
            "pkg_resources",
            "pydantic",
            "crewai",
            "langchain",
            "crewai_tools",
            "httpx",
            "urllib3",
        ]
        disabled_loggers = []

        for logger_name in logger_names:
            logger = logging.getLogger(logger_name)
            if not logger.disabled:
                disabled_loggers.append(logger_name)
                logger.setLevel(logging.CRITICAL)
                logger.disabled = True

        yield

    finally:
        # Restore warning state safely
        warnings.resetwarnings()
        for filter_item in old_warnings:
            try:
                # Handle different types of filter items
                if len(filter_item) >= 1 and filter_item[0] in (
                    "error",
                    "ignore",
                    "always",
                    "default",
                    "module",
                    "once",
                ):
                    action = filter_item[0]

                    # Handle message parameter - could be string, regex, or None
                    message = filter_item[1] if len(filter_item) > 1 else ""
                    if message is not None and not isinstance(message, str):
                        # Skip non-string messages (like regex objects)
                        continue
                    # Convert None to empty string for warnings.filterwarnings
                    if message is None:
                        message = ""

                    # Handle other parameters with safe defaults
                    category = (
                        filter_item[2]
                        if len(filter_item) > 2 and filter_item[2] is not None
                        else Warning
                    )
                    module = filter_item[3] if len(filter_item) > 3 else ""
                    if module is not None and not isinstance(module, str):
                        # Skip non-string modules (like regex objects)
                        continue
                    # Convert None to empty string for warnings.filterwarnings
                    if module is None:
                        module = ""
                    lineno = (
                        filter_item[4]
                        if len(filter_item) > 4 and filter_item[4] is not None
                        else 0
                    )
                    append = (
                        filter_item[5]
                        if len(filter_item) > 5 and filter_item[5] is not None
                        else False
                    )

                    warnings.filterwarnings(
                        action, message, category, module, lineno, append
                    )
            except (ValueError, TypeError, IndexError):
                # Skip invalid filter items
                continue
        logging.getLogger().setLevel(old_logging_level)

        # Re-enable loggers that we disabled
        for logger_name in disabled_loggers:
            logging.getLogger(logger_name).disabled = False


def configure_quiet_logging():
    """Configure logging to suppress verbose outputs from dependencies."""
    # Suppress specific library loggers
    logger_names = [
        "crewai",
        "langchain",
        "openai",
        "httpx",
        "pkg_resources",
        "pydantic",
        "crewai_tools",
    ]
    for logger_name in logger_names:
        logging.getLogger(logger_name).setLevel(logging.ERROR)

    # General suppression of deprecation warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)


def configure_silent_environment():
    """
    Configure the environment for silent operation.

    This sets environment variables and logging levels to minimize
    all output from third-party libraries.
    """
    # Environment variables to suppress various outputs
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["TRANSFORMERS_VERBOSITY"] = "error"
    os.environ["LANGCHAIN_VERBOSE"] = "false"
    os.environ["CREWAI_VERBOSE"] = "false"

    # Configure logging
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
    for logger_name in logger_names:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)

    # Suppress warnings globally
    warnings.filterwarnings("ignore")
