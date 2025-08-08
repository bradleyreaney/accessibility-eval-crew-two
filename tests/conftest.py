"""
PyTest configuration and fixtures for comprehensive TDD implementation
References: TDD Strategy - Test Foundation
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch
from src.models.evaluation_models import DocumentContent
from src.config.llm_config import LLMConfig


@pytest.fixture(scope="session")
def project_root():
    """Project root directory fixture"""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_audit_content():
    """Sample audit report content for testing"""
    return DocumentContent(
        title="Test Accessibility Audit Report",
        content="Sample audit content with accessibility findings...",
        page_count=5,
        metadata={"author": "Test Auditor", "date": "2025-01-01"},
    )


@pytest.fixture
def sample_plan_content():
    """Sample remediation plan content for testing"""
    return DocumentContent(
        title="Remediation Plan A",
        content="Sample plan content with remediation steps...",
        page_count=3,
        metadata={"author": "Test Planner", "plan": "A"},
    )


@pytest.fixture
def mock_llm_config():
    """Mock LLM configuration for testing without API calls"""
    return LLMConfig(
        gemini_api_key="test_gemini_key_123", openai_api_key="test_openai_key_456"
    )


@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a temporary PDF file for testing"""
    pdf_file = tmp_path / "test_document.pdf"
    # Create a minimal PDF content (this would need a real PDF for integration tests)
    pdf_file.write_bytes(
        b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
    )
    return pdf_file


@pytest.fixture
def sample_eval_prompt():
    """Sample evaluation prompt content that matches real format"""
    return """
### PERSONA
You are an expert accessibility consultant.

### CORE TASK
Evaluate remediation plans.

### CONTEXT: ACCESSIBILITY AUDIT FINDINGS
Accessibility issues found in audit.

### CANDIDATE REMEDIATION PLANS
#### PlanA:
Sample plan content

### EVALUATION FRAMEWORK & OUTPUT STRUCTURE
**(1) Strategic Prioritization (Weight: 40%):**
**(2) Technical Specificity & Correctness (Weight: 30%):**
**(3) Comprehensiveness & Structure (Weight: 20%):**
**(4) Long-Term Vision (Weight: 10%):**
"""


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    env_vars = {
        "GOOGLE_API_KEY": "test_google_key",
        "OPENAI_API_KEY": "test_openai_key",
        "PROJECT_ROOT": "/test/project",
        "DEBUG_MODE": "True",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars
