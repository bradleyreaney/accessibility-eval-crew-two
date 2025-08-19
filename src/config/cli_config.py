"""
CLI configuration management for the accessibility evaluation system.

This module provides CLI-specific configuration validation and metadata generation
for the command-line interface that replaces the Streamlit web UI.

References:
    - UI Removal Plan: plans/ui-removal-cli-implementation-plan.md
    - Master Plan: Configuration management patterns
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CLIConfiguration:
    """
    Manage CLI-specific configuration and validation.

    This class handles validation of command-line arguments, environment variables,
    and system setup for the CLI-based evaluation system.
    """

    def __init__(self, args: argparse.Namespace):
        """
        Initialize CLI configuration with parsed arguments.

        Args:
            args: Parsed command line arguments from argparse
        """
        self.args = args
        self.validated = False
        self.validation_errors: List[str] = []

    def validate_environment(self) -> bool:
        """
        Validate API keys and environment setup.

        Returns:
            bool: True if environment is valid, False otherwise
        """
        required_vars = ["GOOGLE_API_KEY", "OPENAI_API_KEY"]
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            error_msg = (
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            self.validation_errors.append(error_msg)
            logger.error(error_msg)
            return False

        logger.debug("Environment variables validated successfully")
        return True

    def validate_input_paths(self) -> bool:
        """
        Validate input directory structure and accessibility.

        Returns:
            bool: True if paths are valid, False otherwise
        """
        paths_to_check = [
            ("audit_dir", "Audit reports directory"),
            ("plans_dir", "Remediation plans directory"),
        ]

        for attr_name, description in paths_to_check:
            path = getattr(self.args, attr_name)

            if not path.exists():
                error_msg = f"{description} does not exist: {path}"
                self.validation_errors.append(error_msg)
                logger.error(error_msg)
                return False

            if not path.is_dir():
                error_msg = f"{description} is not a directory: {path}"
                self.validation_errors.append(error_msg)
                logger.error(error_msg)
                return False

            if not os.access(path, os.R_OK):
                error_msg = f"{description} is not readable: {path}"
                self.validation_errors.append(error_msg)
                logger.error(error_msg)
                return False

        logger.debug("Input paths validated successfully")
        return True

    def validate_output_path(self) -> bool:
        """
        Validate output directory and create if necessary.

        Returns:
            bool: True if output path is valid, False otherwise
        """
        output_path = self.args.output

        try:
            # Create output directory if it doesn't exist
            output_path.mkdir(parents=True, exist_ok=True)

            # Test write access
            test_file = output_path / ".write_test"
            test_file.write_text("test")
            test_file.unlink()

            logger.debug(f"Output path validated and ready: {output_path}")
            return True

        except Exception as e:
            error_msg = f"Cannot write to output directory {output_path}: {str(e)}"
            self.validation_errors.append(error_msg)
            logger.error(error_msg)
            return False

    def validate_execution_parameters(self) -> bool:
        """
        Validate execution-related parameters.

        Returns:
            bool: True if parameters are valid, False otherwise
        """
        # Validate timeout
        if self.args.timeout <= 0:
            error_msg = f"Timeout must be positive: {self.args.timeout}"
            self.validation_errors.append(error_msg)
            logger.error(error_msg)
            return False

        if self.args.timeout > 7200:  # 2 hours max
            logger.warning(f"Long timeout specified: {self.args.timeout} seconds")

        # Validate mode
        valid_modes = ["single", "sequential", "parallel"]
        if self.args.mode not in valid_modes:
            error_msg = f"Invalid execution mode: {self.args.mode}"
            self.validation_errors.append(error_msg)
            logger.error(error_msg)
            return False

        logger.debug("Execution parameters validated successfully")
        return True

    def validate_report_configuration(self) -> bool:
        """
        Validate report type configuration.

        Returns:
            bool: True if report configuration is valid, False otherwise
        """
        valid_types = {
            "basic",
            "detailed",
            "comprehensive",
        }

        try:
            requested_type = self.args.reports.lower()
            if requested_type not in valid_types:
                error_msg = (
                    f"Invalid report type: {requested_type}. "
                    f"Valid types: {', '.join(sorted(valid_types))}"
                )
                self.validation_errors.append(error_msg)
                logger.error(error_msg)
                return False

            logger.debug(f"Report type validated: {requested_type}")
            return True

        except Exception as e:
            error_msg = f"Error parsing report types: {str(e)}"
            self.validation_errors.append(error_msg)
            logger.error(error_msg)
            return False

    def validate_all(self) -> bool:
        """
        Run all validation checks.

        Returns:
            bool: True if all validations pass, False otherwise
        """
        self.validation_errors.clear()

        validations = [
            ("Environment", self.validate_environment),
            ("Input paths", self.validate_input_paths),
            ("Output path", self.validate_output_path),
            ("Execution parameters", self.validate_execution_parameters),
            ("Report configuration", self.validate_report_configuration),
        ]

        all_valid = True
        for name, validation_func in validations:
            try:
                if not validation_func():
                    logger.error(f"❌ {name} validation failed")
                    all_valid = False
                else:
                    logger.debug(f"✅ {name} validation passed")
            except Exception as e:
                logger.error(f"❌ {name} validation error: {str(e)}")
                all_valid = False

        self.validated = all_valid

        if not all_valid:
            logger.error("❌ Configuration validation failed:")
            for error in self.validation_errors:
                logger.error(f"   - {error}")
        else:
            logger.info("✅ All configuration validations passed")

        return all_valid

    def create_execution_metadata(self) -> Dict[str, Any]:
        """
        Create metadata about the execution configuration.

        Returns:
            Dict containing execution metadata
        """
        metadata = {
            "cli_version": "1.0.0",
            "execution_timestamp": datetime.now().isoformat(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "cwd": str(Path.cwd()),
            },
            "configuration": {
                "audit_dir": str(self.args.audit_dir),
                "plans_dir": str(self.args.plans_dir),
                "output_dir": str(self.args.output),
                "execution_mode": self.args.mode,
                "consensus_enabled": self.args.consensus,
                "report_types": self.args.reports,
                "timeout_seconds": self.args.timeout,
                "verbose_logging": self.args.verbose,
                "dry_run": self.args.dry_run,
            },
            "environment": {
                "google_api_configured": bool(os.getenv("GOOGLE_API_KEY")),
                "openai_api_configured": bool(os.getenv("OPENAI_API_KEY")),
            },
        }

        return metadata

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of validation results.

        Returns:
            Dict containing validation summary
        """
        return {
            "validated": self.validated,
            "errors": self.validation_errors.copy(),
            "error_count": len(self.validation_errors),
        }
