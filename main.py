#!/usr/bin/env python3
"""
Command-Line Interface for Accessibility Evaluation System

This module provides a comprehensive CLI for evaluating accessibility remediation plans
using CrewAI multi-agent workflows. Replaces the web-based UI with efficient file
discovery and automated PDF report generation.

Features:
    - Automated file discovery in specified directories
    - Multi-agent evaluation using Gemini Pro and GPT-4
    - Comprehensive PDF report generation
    - Environment validation and configuration
    - Dry-run mode for testing

Usage:
    python main.py [options]
    python main.py --dry-run
    python main.py --audit-dir /path/to/audits --plans-dir /path/to/plans

References:
    - Master Plan: CLI Implementation (Phase 1 Complete)
    - Configuration Management: src/config/
    - Evaluation Framework: src/evaluation/
"""

import argparse
import asyncio
import logging
import os
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config.cli_config import CLIConfiguration
from src.config.crew_config import AccessibilityEvaluationCrew
from src.config.llm_config import LLMManager
from src.models.evaluation_models import EvaluationCriteria, EvaluationInput
from src.reports.generators.evaluation_report_generator import EvaluationReportGenerator
from src.tools.file_discovery import FileDiscovery
from src.utils.workflow_controller import WorkflowController

# Apply environment-level suppression immediately
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Comprehensive warning suppression
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")

# Set logging levels for noisy libraries
for logger_name in [
    "crewai",
    "langchain",
    "pydantic",
    "pkg_resources",
    "crewai_tools",
    "httpx",
]:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

# Now use our enhanced suppression system
try:
    from src.utils.warning_suppression import suppress_all_warnings

    suppress_all_warnings()
except ImportError:
    # Fallback if the module isn't available
    pass


class AccessibilityEvaluationCLI:
    """
    Command-line interface for the accessibility evaluation system.

    Provides comprehensive CLI functionality for automated evaluation of
    accessibility remediation plans using multi-agent workflows.

    Attributes:
        config: CLI configuration management
        llm_manager: LLM connection and configuration
        file_discovery: Automated file discovery system
        report_generator: PDF report generation
        workflow_controller: Evaluation workflow orchestration
    """

    def __init__(self):
        """Initialize the CLI with all necessary components."""
        print("🚀 Starting Accessibility Evaluation System")

        # Initialize core components that don't need arguments
        self.config: Optional[CLIConfiguration] = None
        self.llm_manager: Optional[LLMManager] = None
        self.file_discovery = FileDiscovery()
        self.report_generator = EvaluationReportGenerator()
        self.workflow_controller: Optional[WorkflowController] = None

    def setup_argument_parser(self) -> argparse.ArgumentParser:
        """
        Configure and return the argument parser for CLI options.

        Returns:
            Configured ArgumentParser instance with all CLI options
        """
        parser = argparse.ArgumentParser(
            description="Accessibility Evaluation System - Multi-agent remediation plan analysis",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python main.py --dry-run                    # Test configuration without running evaluation
  python main.py                              # Run with default directories (data/audit-reports, data/remediation-plans)
  python main.py --audit-dir /custom/audits   # Use custom audit reports directory
  python main.py --plans-dir /custom/plans    # Use custom remediation plans directory
  python main.py --output /custom/output      # Use custom output directory
  python main.py --mode single               # Single evaluation mode
  python main.py --consensus threshold       # Use threshold consensus algorithm
  python main.py --reports detailed          # Generate detailed reports
  python main.py --timeout 300               # Set custom timeout (seconds)
            """,
        )

        # Core directory options
        parser.add_argument(
            "--audit-dir",
            type=str,
            default="data/audit-reports",
            help="Directory containing accessibility audit reports (default: data/audit-reports)",
        )

        parser.add_argument(
            "--plans-dir",
            type=str,
            default="data/remediation-plans",
            help="Directory containing remediation plans (default: data/remediation-plans)",
        )

        parser.add_argument(
            "--output",
            type=str,
            default="output/reports",
            help="Output directory for generated reports (default: output/reports)",
        )

        # Evaluation configuration
        parser.add_argument(
            "--mode",
            choices=["single", "parallel", "sequential"],
            default="parallel",
            help="Evaluation mode: single (one plan), parallel (all plans simultaneously), sequential (one by one)",
        )

        parser.add_argument(
            "--consensus",
            choices=["simple", "weighted", "threshold", "advanced"],
            default="weighted",
            help="Consensus algorithm for multi-judge evaluation",
        )

        parser.add_argument(
            "--reports",
            choices=["basic", "detailed", "comprehensive"],
            default="comprehensive",
            help="Level of detail in generated reports",
        )

        # Operational options
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output (note: some library warnings may still appear)",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate configuration and file discovery without running evaluation",
        )

        parser.add_argument(
            "--timeout",
            type=int,
            default=300,
            help="Timeout for evaluation operations in seconds (default: 300)",
        )

        return parser

    def validate_environment(self) -> bool:
        """
        Validate that all required environment variables and configurations are present.

        Returns:
            True if environment is valid, False otherwise
        """
        print("🔍 Validating Environment Configuration")

        try:
            # Initialize LLM manager to validate API keys
            self.llm_manager = LLMManager.from_environment()

            # Validate LLM configurations
            connection_results = self.llm_manager.test_connections()
            if not any(connection_results.values()):
                print(
                    "❌ LLM configuration validation failed - no connections available"
                )
                return False

            print("✅ Environment validation successful")
            return True

        except Exception as e:
            print(f"❌ Environment validation failed: {str(e)}")
            return False

    def discover_files(self, audit_dir: str, plans_dir: str) -> Dict[str, List[Path]]:
        """
        Discover audit reports and remediation plans in specified directories.

        Args:
            audit_dir: Directory containing audit reports
            plans_dir: Directory containing remediation plans

        Returns:
            Dictionary with discovered file paths
        """
        from pathlib import Path

        audit_path = Path(audit_dir)
        plans_path = Path(plans_dir)

        print("🔍 Discovering files...")
        print(f"   📁 Audit reports directory: {audit_path}")
        print(f"   📁 Remediation plans directory: {plans_path}")

        try:
            audit_files = self.file_discovery.discover_audit_reports(audit_path)
            plan_files = self.file_discovery.discover_remediation_plans(plans_path)

            print(f"   ✅ Found {len(audit_files)} audit reports")
            print(f"   ✅ Found {len(plan_files)} remediation plans")

            if not audit_files:
                raise FileNotFoundError(f"No audit reports found in {audit_dir}")

            if not plan_files:
                raise FileNotFoundError(f"No remediation plans found in {plans_dir}")

            return {"audit_files": audit_files, "plan_files": plan_files}

        except Exception as e:
            raise FileNotFoundError(f"File discovery failed: {str(e)}")

    async def run_evaluation(
        self, evaluation_input: EvaluationInput, mode: str
    ) -> Dict[str, Any]:
        """
        Execute the complete evaluation workflow using CrewAI agents.

        Args:
            evaluation_input: Structured input for evaluation
            mode: Evaluation mode (single, parallel, sequential)

        Returns:
            Dictionary containing evaluation results and metadata
        """
        if not self.llm_manager:
            raise RuntimeError(
                "LLM manager not initialized. Call validate_environment() first."
            )

        print("🤖 Initializing Multi-Agent Evaluation Crew")

        # Create evaluation crew
        crew = AccessibilityEvaluationCrew(self.llm_manager)

        # Validate crew configuration
        if not crew.validate_configuration():
            raise RuntimeError("Crew configuration validation failed")

        # Initialize workflow controller
        self.workflow_controller = WorkflowController(crew)

        print(f"⚡ Starting {mode.title()} Evaluation Workflow")

        # Execute evaluation based on mode
        if mode == "single":
            results = await self.workflow_controller.start_evaluation(
                evaluation_input, mode, False
            )
        elif mode == "parallel":
            results = await self.workflow_controller.start_evaluation(
                evaluation_input, mode, False
            )
        elif mode == "sequential":
            results = await self.workflow_controller.start_evaluation(
                evaluation_input, mode, False
            )
        else:
            raise ValueError(f"Unsupported evaluation mode: {mode}")

        print("✅ Evaluation workflow completed successfully")
        return results

    def generate_report(
        self, evaluation_results: Dict[str, Any], output_dir: str, report_level: str
    ) -> str:
        """
        Generate comprehensive PDF report from evaluation results.

        Args:
            evaluation_results: Results from evaluation workflow
            output_dir: Directory to save the generated report
            report_level: Level of detail (basic, detailed, comprehensive)

        Returns:
            Path to the generated report file
        """
        print(f"📄 Generating {report_level.title()} PDF Report")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate report
        from datetime import datetime
        from pathlib import Path

        report_paths = self.report_generator.generate_cli_report_package(
            evaluation_results=evaluation_results,
            report_types=[report_level, "pdf", "json"],  # Generate multiple formats
            output_dir=Path(output_dir),
            metadata={
                "execution_time": datetime.now().isoformat(),
                "report_level": report_level,
                "cli_version": "1.0.0",
            },
        )

        # Return the primary PDF report path as string
        primary_report = report_paths.get("pdf", list(report_paths.values())[0])
        report_path = str(primary_report)

        print(f"📊 Report Generated: {report_path}")
        return report_path

    async def main(self) -> None:
        """
        Main CLI execution flow with comprehensive error handling.

        Coordinates all aspects of the evaluation process from argument parsing
        through file discovery, evaluation execution, and report generation.
        """
        try:
            # Parse command line arguments
            parser = self.setup_argument_parser()
            args = parser.parse_args()

            # Initialize configuration with parsed arguments
            self.config = CLIConfiguration(args)

            # Configure verbose logging if requested
            if args.verbose:
                logging.basicConfig(level=logging.INFO)
                print("🔊 Verbose mode enabled")
            else:
                # Ensure quiet operation
                logging.basicConfig(level=logging.ERROR)

            # Validate environment configuration
            if not self.validate_environment():
                print(
                    "❌ Environment validation failed. Please check your configuration."
                )
                sys.exit(1)

            # Discover input files
            try:
                discovery_results = self.discover_files(args.audit_dir, args.plans_dir)
            except FileNotFoundError as e:
                print(f"❌ File discovery failed: {str(e)}")
                sys.exit(1)

            # Handle dry-run mode
            if args.dry_run:
                print(
                    "🧪 Dry-run mode: Configuration and file discovery completed successfully"
                )
                print("✅ System ready for evaluation")
                return

            # Prepare evaluation input
            # Create evaluation input from discovered files
            evaluation_input = self.file_discovery.create_evaluation_input(
                discovery_results["audit_files"], discovery_results["plan_files"]
            )

            # Execute evaluation workflow with warning suppression
            print("🎯 Starting Accessibility Evaluation Process")

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                evaluation_results = await self.run_evaluation(
                    evaluation_input, args.mode
                )

            # Generate comprehensive report
            report_path = self.generate_report(
                evaluation_results=evaluation_results,
                output_dir=args.output,
                report_level=args.reports,
            )

            # Display completion summary
            print("\n🎉 Evaluation Complete!")
            print(f"📁 Report Location: {report_path}")
            print(f"📊 Evaluation Mode: {args.mode.title()}")
            print(f"🔬 Consensus Algorithm: {args.consensus.title()}")
            print(f"📄 Report Level: {args.reports.title()}")

        except KeyboardInterrupt:
            print("\n⚠️  Evaluation interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            if args.verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)


def main():
    """Entry point for the CLI application."""
    cli = AccessibilityEvaluationCLI()
    asyncio.run(cli.main())


if __name__ == "__main__":
    main()
