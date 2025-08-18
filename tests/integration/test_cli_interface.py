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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
