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

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass

from src.config.cli_config import CLIConfiguration
from src.config.crew_config import AccessibilityEvaluationCrew
from src.config.llm_config import LLMManager
from src.models.evaluation_models import EvaluationCriteria, EvaluationInput
from src.reports.generators.evaluation_report_generator import EvaluationReportGenerator
from src.tools.file_discovery import FileDiscovery
from src.utils.llm_resilience_manager import LLMResilienceManager, ResilienceConfig
from src.utils.workflow_controller import WorkflowController

# Apply environment-level suppression immediately
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Disable telemetry and external services
os.environ["CREWAI_DISABLE_TELEMETRY"] = "1"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_PROJECT"] = ""
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = ""
os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = ""
os.environ["OTEL_TRACES_EXPORTER"] = "none"
os.environ["OTEL_METRICS_EXPORTER"] = "none"
os.environ["OTEL_LOGS_EXPORTER"] = "none"
os.environ["OPENTELEMETRY_PYTHON_DISABLED"] = "true"
os.environ["OTEL_PYTHON_DISABLED"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_TRACES_SAMPLER"] = "always_off"
os.environ["OTEL_METRICS_EXPORTER"] = "none"
os.environ["OTEL_LOGS_EXPORTER"] = "none"
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = ""
os.environ["OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"] = ""
os.environ["OTEL_EXPORTER_OTLP_LOGS_ENDPOINT"] = ""

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
    Enhanced with LLM resilience capabilities for graceful degradation.

    Attributes:
        config: CLI configuration management
        llm_manager: LLM connection and configuration
        resilience_manager: LLM resilience manager for error handling
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
        self.resilience_manager: Optional[LLMResilienceManager] = None
        self.file_discovery = FileDiscovery()
        self.report_generator = EvaluationReportGenerator()
        self.workflow_controller: Optional[WorkflowController] = None

    def clear_historical_data(self, output_dir: Path) -> None:
        """
        Clear all historical reports and data from output directory and related folders.

        Args:
            output_dir: Directory to clean (default: output/reports)

        Raises:
            OSError: If cleanup fails due to file system issues
        """
        try:
            # Always ensure the output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Get the parent output directory to clean related folders
            output_parent = output_dir.parent

            # Clean up reports directory
            if output_dir.exists():
                # Remove all files in reports directory
                for file_path in output_dir.glob("*"):
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        import shutil

                        shutil.rmtree(file_path)

                print(f"🧹 Cleared historical reports from {output_dir}")
            else:
                print(f"📁 Created output directory: {output_dir}")

            # Clean up evaluations directory
            evaluations_dir = output_parent / "evaluations"
            if evaluations_dir.exists():
                for file_path in evaluations_dir.glob("*"):
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        import shutil

                        shutil.rmtree(file_path)
                print(f"🧹 Cleared historical evaluations from {evaluations_dir}")

            # Clean up comparisons directory
            comparisons_dir = output_parent / "comparisons"
            if comparisons_dir.exists():
                for file_path in comparisons_dir.glob("*"):
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        import shutil

                        shutil.rmtree(file_path)
                print(f"🧹 Cleared historical comparisons from {comparisons_dir}")

            # Clean up any other temporary files in output directory
            for temp_file in output_parent.glob(".*"):
                if temp_file.name in [".DS_Store", ".DS_Store?", "._*"]:
                    temp_file.unlink()
                    print(f"🧹 Removed temporary file: {temp_file}")

        except Exception as e:
            raise OSError(f"Failed to clear historical data: {e}")

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
            type=Path,
            default=Path("data/audit-reports"),
            help="Directory containing accessibility audit reports (default: data/audit-reports)",
        )

        parser.add_argument(
            "--plans-dir",
            type=Path,
            default=Path("data/remediation-plans"),
            help="Directory containing remediation plans (default: data/remediation-plans)",
        )

        parser.add_argument(
            "--output",
            type=Path,
            default=Path("output/reports"),
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

        # Historical data management
        parser.add_argument(
            "--keep-history",
            action="store_true",
            help="Keep historical data including reports, evaluations, and comparisons (default: clear all previous data)",
        )

        return parser

    def validate_environment(self) -> bool:
        """
        Validate the environment and LLM configurations.

        Returns:
            True if environment is valid, False otherwise
        """
        try:
            print("🔧 Validating environment configuration...")

            # CLI configuration will be initialized in main() with parsed args
            # For now, just validate LLM components

            # Initialize LLM manager
            self.llm_manager = LLMManager.from_environment()

            # Initialize LLM resilience manager
            resilience_config = ResilienceConfig(
                max_retries=3,
                retry_delay_seconds=2,
                exponential_backoff=True,
                timeout_seconds=30,
                enable_partial_evaluation=True,
                minimum_llm_requirement=1,
                na_reporting_enabled=True,
            )
            self.resilience_manager = LLMResilienceManager(
                self.llm_manager, resilience_config
            )

            # Validate LLM configurations with resilience manager
            print("🔍 Checking LLM availability...")
            availability_status = self.resilience_manager.check_llm_availability()

            available_count = sum(availability_status.values())
            if available_count < resilience_config.minimum_llm_requirement:
                print(
                    f"❌ LLM configuration validation failed - insufficient LLMs available ({available_count})"
                )
                return False

            # Log availability status
            available_llms = [
                llm for llm, status in availability_status.items() if status
            ]
            unavailable_llms = [
                llm for llm, status in availability_status.items() if not status
            ]

            print("✅ LLM availability check complete:")
            print(
                f"   Available: {', '.join(available_llms) if available_llms else 'None'}"
            )
            if unavailable_llms:
                print(f"   Unavailable: {', '.join(unavailable_llms)}")
                print("   ⚠️  System will operate with reduced capability")

            print("✅ Environment validation successful")
            return True

        except Exception as e:
            print(f"❌ Environment validation failed: {str(e)}")
            return False

    def discover_files(self, audit_dir: Path, plans_dir: Path) -> Dict[str, List[Path]]:
        """
        Discover audit reports and remediation plans in specified directories.

        Args:
            audit_dir: Directory containing audit reports
            plans_dir: Directory containing remediation plans

        Returns:
            Dictionary with discovered file paths
        """
        audit_path = audit_dir
        plans_path = plans_dir

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
        Enhanced with LLM resilience capabilities for graceful degradation.

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

        # Create evaluation crew with resilience manager
        crew = AccessibilityEvaluationCrew(self.llm_manager, self.resilience_manager)

        # Validate crew configuration
        if not crew.validate_configuration():
            raise RuntimeError("Crew configuration validation failed")

        # Initialize workflow controller with resilience manager
        self.workflow_controller = WorkflowController(crew, self.resilience_manager)

        print(f"⚡ Starting {mode.title()} Evaluation Workflow")

        # Display resilience status if available
        if self.resilience_manager:
            availability_status = self.resilience_manager.check_llm_availability()
            available_llms = [
                llm for llm, status in availability_status.items() if status
            ]
            unavailable_llms = [
                llm for llm, status in availability_status.items() if not status
            ]

            if unavailable_llms:
                print(
                    f"🛡️  Resilience Mode: Operating with {len(available_llms)} available LLM(s)"
                )
                print(f"   Unavailable: {', '.join(unavailable_llms)}")
            else:
                print("🛡️  Resilience Mode: All LLMs available")

        # Record start time for duration calculation
        from datetime import datetime

        start_time = datetime.now()

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

        # Calculate execution duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60.0  # Convert to minutes

        # Add execution metadata to results
        results["execution_metadata"] = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_minutes": duration,
        }

        # Add resilience information to results if available
        if self.resilience_manager:
            results["resilience_stats"] = (
                self.resilience_manager.get_evaluation_statistics()
            )

        print("✅ Evaluation workflow completed successfully")
        return results

    def generate_report(
        self, evaluation_results: Dict[str, Any], output_dir: Path, report_level: str
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
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create comprehensive execution metadata
        execution_metadata = self.config.create_execution_metadata()

        # Add discovered files to metadata
        if hasattr(self, "discovery_results"):
            execution_metadata["audit_files"] = [
                f.name for f in self.discovery_results.get("audit_files", [])
            ]
            execution_metadata["plan_files"] = [
                f.name for f in self.discovery_results.get("plan_files", [])
            ]

        # Add execution timing information if available
        if "execution_metadata" in evaluation_results:
            exec_meta = evaluation_results["execution_metadata"]
            execution_metadata["execution_timestamp"] = exec_meta.get(
                "start_time", execution_metadata["execution_timestamp"]
            )
            execution_metadata["duration_minutes"] = exec_meta.get(
                "duration_minutes", 0
            )

        # Add report types configuration
        execution_metadata["configuration"]["report_types"] = report_level

        report_paths = self.report_generator.generate_cli_report_package(
            evaluation_results=evaluation_results,
            report_types=[report_level, "pdf", "json"],  # Generate multiple formats
            output_dir=output_dir,
            metadata=execution_metadata,
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
                # Store discovery results for report generation
                self.discovery_results = discovery_results
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

            # Clear historical data unless --keep-history is specified
            if not args.keep_history:
                print("🧹 Clearing previous evaluation data...")
                self.clear_historical_data(args.output)
            else:
                print("📚 Keeping historical data as requested")

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
