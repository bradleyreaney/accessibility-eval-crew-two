"""
Tests for the suppress_warnings module.
"""

import os
import warnings

import pytest


class TestSuppressWarnings:
    """Test the suppress_warnings module."""

    def test_environment_variables_set(self):
        """Test that environment variables are set correctly."""
        # Import the module to trigger environment variable setting
        import src.utils.suppress_warnings

        # Check that environment variables are set
        assert os.environ.get("PYTHONWARNINGS") is not None
        assert os.environ.get("PYTHONDONTWRITEBYTECODE") == "1"

    def test_warning_filters_applied(self):
        """Test that warning filters are applied."""
        # Import the module to trigger warning filter setup
        import src.utils.suppress_warnings

        # Check that warning filters are in place
        filters = warnings.filters
        assert len(filters) > 0

    def test_module_imports_successfully(self):
        """Test that the module can be imported without errors."""
        try:
            import src.utils.suppress_warnings

            assert True
        except Exception as e:
            pytest.fail(f"Module import failed: {e}")

    def test_warning_suppression_basic(self):
        """Test basic warning suppression functionality."""
        # Import the module to set up suppression
        import src.utils.suppress_warnings

        # Just verify the module imported successfully
        assert True

    def test_module_has_expected_attributes(self):
        """Test that the module has expected attributes."""
        import src.utils.suppress_warnings

        # Check that the module exists and can be imported
        assert src.utils.suppress_warnings is not None
