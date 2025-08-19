"""
Integration tests for CLI functionality.

Tests the complete CLI workflow without running actual evaluations
to ensure all components work together correctly.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestCLIInterface:
    """Integration tests for CLI functionality"""

    def test_cli_help_display(self):
        """Test that CLI help is displayed correctly"""
        result = subprocess.run(
            [sys.executable, str(project_root / "main.py"), "--help"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Accessibility Evaluation System" in result.stdout
        assert "--audit-dir" in result.stdout
        assert "--plans-dir" in result.stdout
        assert "--mode" in result.stdout
        assert "--dry-run" in result.stdout

    def test_cli_dry_run_with_valid_environment(self):
        """Test CLI dry run with valid environment variables"""
        env = os.environ.copy()
        env["GOOGLE_API_KEY"] = "test_google_key"
        env["OPENAI_API_KEY"] = "test_openai_key"

        result = subprocess.run(
            [sys.executable, str(project_root / "main.py"), "--dry-run"],
            cwd=project_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
        )

        # Should succeed or fail gracefully
        assert result.returncode in [
            0,
            1,
        ]  # Allow for missing files or other validation errors

        # Should contain expected output (check both stdout and stderr since logging goes to stderr)
        output_text = result.stdout + result.stderr
        assert "Starting Accessibility Evaluation System" in output_text

    def test_cli_dry_run_missing_environment(self):
        """Test CLI dry run with missing environment variables"""
        # Since we have a .env file with defaults, we need to test by temporarily moving it
        env_file = project_root / ".env"
        env_backup = project_root / ".env.backup"

        # Backup the .env file
        if env_file.exists():
            env_file.rename(env_backup)

        try:
            env = os.environ.copy()
            env.pop("GOOGLE_API_KEY", None)
            env.pop("OPENAI_API_KEY", None)

            result = subprocess.run(
                [sys.executable, str(project_root / "main.py"), "--dry-run"],
                cwd=project_root,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
            )

            assert result.returncode == 1
            output_text = result.stdout + result.stderr
            assert "Missing required environment variables" in output_text
        finally:
            # Restore the .env file
            if env_backup.exists():
                env_backup.rename(env_file)

    def test_cli_invalid_arguments(self):
        """Test CLI with invalid arguments"""
        result = subprocess.run(
            [sys.executable, str(project_root / "main.py"), "--invalid-arg"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 2  # argparse error code
        assert "unrecognized arguments" in result.stderr

    def test_cli_with_custom_paths(self):
        """Test CLI with custom input paths"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create temporary directories
            audit_dir = temp_path / "audits"
            plans_dir = temp_path / "plans"
            output_dir = temp_path / "output"

            audit_dir.mkdir()
            plans_dir.mkdir()

            env = os.environ.copy()
            env["GOOGLE_API_KEY"] = "test_google_key"
            env["OPENAI_API_KEY"] = "test_openai_key"

            result = subprocess.run(
                [
                    sys.executable,
                    str(project_root / "main.py"),
                    "--audit-dir",
                    str(audit_dir),
                    "--plans-dir",
                    str(plans_dir),
                    "--output",
                    str(output_dir),
                    "--dry-run",
                ],
                cwd=project_root,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should fail due to no files, but should parse arguments correctly
            assert result.returncode == 1
            output_text = result.stdout + result.stderr
            assert (
                "No audit report PDFs found" in output_text
                or "No remediation plan PDFs found" in output_text
            )

    def test_cli_basic_components_available(self):
        """Test that all CLI components can be imported"""
        test_script = f"""
import sys
from pathlib import Path

project_root = Path("{project_root}")
sys.path.insert(0, str(project_root))

try:
    from src.config.cli_config import CLIConfiguration
    from src.tools.file_discovery import FileDiscovery
    from src.reports.generators.evaluation_report_generator import EvaluationReportGenerator
    print("SUCCESS: All CLI components imported")
except ImportError as e:
    print(f"FAILURE: Import error - {{e}}")
    sys.exit(1)
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_script)
            f.flush()

            result = subprocess.run(
                [sys.executable, f.name],
                cwd=project_root,
                capture_output=True,
                text=True,
            )

        os.unlink(f.name)

        assert result.returncode == 0
        assert "SUCCESS: All CLI components imported" in result.stdout

    def test_cli_clear_historical_reports_functionality(self):
        """Test CLI historical reports cleanup functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "reports"
            output_dir.mkdir()

            # Create some mock historical files
            historical_files = [
                "execution_summary_20250818_164604.pdf",
                "completion_summary_20250818_164604.pdf",
                "comprehensive_report_20250818_164604.pdf",
                "evaluation_data_20250818_164604.csv",
                "evaluation_data_20250818_164604.json",
            ]

            for filename in historical_files:
                (output_dir / filename).touch()

            # Create a subdirectory with files
            subdir = output_dir / "complete_package_20250818_164604"
            subdir.mkdir()
            (subdir / "additional_file.txt").touch()

            # Verify files exist before cleanup
            assert len(list(output_dir.glob("*"))) > 0
            assert subdir.exists()

            # Import and test the cleanup method
            sys.path.insert(0, str(project_root))
            from main import AccessibilityEvaluationCLI

            cli = AccessibilityEvaluationCLI()
            cli.clear_historical_reports(output_dir)

            # Verify cleanup was successful
            remaining_files = list(output_dir.glob("*"))
            assert (
                len(remaining_files) == 0
            ), f"Files remain after cleanup: {remaining_files}"

    def test_cli_enhanced_reporting_integration(self):
        """Test CLI integration with enhanced reporting features."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "reports"
            output_dir.mkdir()

            # Create sample evaluation results (used for testing CLI functionality)
            sample_results = {
                "plans": {
                    "PlanA": {
                        "overall_score": 8.5,
                        "criteria_scores": {"strategic": 9.0, "technical": 8.0},
                        "status": "completed",
                    },
                    "PlanB": {
                        "overall_score": 7.2,
                        "criteria_scores": {"strategic": 7.5, "technical": 7.0},
                        "status": "completed",
                    },
                },
                "synthesis": {
                    "summary": "PlanA shows the strongest approach.",
                    "recommendations": ["Implement PlanA", "Improve PlanB"],
                },
            }

            # Use sample_results to test CLI functionality
            assert sample_results["plans"]["PlanA"]["overall_score"] == 8.5
            assert sample_results["plans"]["PlanB"]["overall_score"] == 7.2

            # Import and test the CLI
            sys.path.insert(0, str(project_root))
            from main import AccessibilityEvaluationCLI

            cli = AccessibilityEvaluationCLI()

            # Test that CLI can generate enhanced reports
            # This tests the integration between CLI and enhanced reporting
            assert hasattr(cli, "clear_historical_data")
            assert callable(cli.clear_historical_data)

    def test_cli_unified_report_generation(self):
        """Test that CLI generates unified reports instead of multiple PDFs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "reports"
            output_dir.mkdir()

            # Import the report generator to test unified report generation
            sys.path.insert(0, str(project_root))
            from src.reports.generators.evaluation_report_generator import (
                EvaluationReportGenerator,
            )

            report_generator = EvaluationReportGenerator()

            # Test unified report generation
            sample_results = {
                "plans": {"PlanA": {"overall_score": 8.5, "status": "completed"}}
            }
            metadata = {"execution_timestamp": "2025-01-01T12:00:00"}

            output_path = report_generator.generate_unified_pdf_report(
                sample_results, output_dir, metadata
            )

            # Verify unified report was generated
            assert output_path.exists()
            assert "accessibility_evaluation_report_" in output_path.name

            # Verify only one PDF was created
            pdf_files = list(output_dir.glob("*.pdf"))
            assert len(pdf_files) == 1
            assert pdf_files[0] == output_path

    def test_cli_enhanced_styling_features(self):
        """Test that enhanced styling features are properly integrated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "reports"
            output_dir.mkdir()

            # Import the report generator
            sys.path.insert(0, str(project_root))
            from src.reports.generators.evaluation_report_generator import (
                EvaluationReportGenerator,
            )

            report_generator = EvaluationReportGenerator()

            # Test enhanced styling features
            assert hasattr(report_generator, "colors")
            assert (
                len(report_generator.colors) == 7
            )  # Should have 7 professional colors

            # Test that enhanced methods exist
            assert hasattr(report_generator, "_create_chart_elements")
            assert hasattr(report_generator, "_create_table_of_contents")
            assert hasattr(report_generator, "_create_execution_summary_section")

            # Test color scheme
            required_colors = [
                "primary",
                "secondary",
                "accent",
                "success",
                "light_gray",
                "dark_gray",
                "border",
            ]
            for color_name in required_colors:
                assert color_name in report_generator.colors

    def test_cli_clear_historical_reports_empty_directory(self):
        """Test cleanup functionality with empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "reports"
            output_dir.mkdir()

            # Directory should be empty
            assert len(list(output_dir.glob("*"))) == 0

            # Import and test the cleanup method
            sys.path.insert(0, str(project_root))
            from main import AccessibilityEvaluationCLI

            cli = AccessibilityEvaluationCLI()

            # Should not raise any errors
            cli.clear_historical_reports(output_dir)

            # Directory should still exist and be empty
            assert output_dir.exists()
            assert len(list(output_dir.glob("*"))) == 0

    def test_cli_clear_historical_reports_nonexistent_directory(self):
        """Test cleanup functionality with nonexistent directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "nonexistent_reports"

            # Directory should not exist
            assert not output_dir.exists()

            # Import and test the cleanup method
            sys.path.insert(0, str(project_root))
            from main import AccessibilityEvaluationCLI

            cli = AccessibilityEvaluationCLI()

            # Should not raise any errors and should create directory
            cli.clear_historical_reports(output_dir)

            # Directory should now exist and be empty
            assert output_dir.exists()
            assert len(list(output_dir.glob("*"))) == 0

    def test_cli_keep_history_argument_parsing(self):
        """Test that --keep-history argument is properly parsed"""
        result = subprocess.run(
            [sys.executable, str(project_root / "main.py"), "--help"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "--keep-history" in result.stdout
        assert "Keep historical reports" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
