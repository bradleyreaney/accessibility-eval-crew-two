#!/usr/bin/env python
"""
Phase 1 validation script
Tests all major components to ensure proper setup
"""
import sys
import os
from pathlib import Path
import logging

import sys
import os
from pathlib import Path
import logging

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def test_imports():
    """Test that all core modules can be imported"""
    print("🧪 Testing imports...")

    try:
        from src.tools.pdf_parser import PDFParser
        from src.tools.prompt_manager import PromptManager
        from src.config.llm_config import LLMManager, LLMConfig
        from src.models.evaluation_models import DocumentContent, EvaluationCriteria
        from src.models.report_models import EvaluationReport, ReportMetadata

        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_pdf_parser():
    """Test PDF parser functionality"""
    print("\n🧪 Testing PDF parser...")

    try:
        from src.tools.pdf_parser import PDFParser

        parser = PDFParser()
        print(f"✅ PDF parser initialized with formats: {parser.supported_formats}")

        # Test with real audit report if available
        audit_path = Path("data/audit-reports/AccessibilityReportTOA.pdf")
        if audit_path.exists():
            print(f"📄 Found audit report: {audit_path}")
            try:
                result = parser.parse_audit_report(audit_path)
                print(
                    f"✅ Parsed audit report: {len(result.content)} chars, {result.page_count} pages"
                )
                print(f"   Title: {result.title}")
            except Exception as e:
                print(f"⚠️  Failed to parse audit report: {e}")

        # Test batch parsing of remediation plans
        plans_dir = Path("data/remediation-plans")
        if plans_dir.exists():
            print(f"📁 Found plans directory: {plans_dir}")
            try:
                plans = parser.batch_parse_plans(plans_dir)
                print(f"✅ Parsed {len(plans)} remediation plans: {list(plans.keys())}")
                for plan_name, plan_content in plans.items():
                    print(f"   {plan_name}: {len(plan_content.content)} chars")
            except Exception as e:
                print(f"⚠️  Failed to parse plans: {e}")

        return True
    except Exception as e:
        print(f"❌ PDF parser test failed: {e}")
        return False


def test_prompt_manager():
    """Test prompt manager functionality"""
    print("\n🧪 Testing prompt manager...")

    try:
        from src.tools.prompt_manager import PromptManager

        prompt_path = Path("promt/eval-prompt.md")
        if prompt_path.exists():
            manager = PromptManager(prompt_path)
            print(f"✅ Loaded evaluation prompt: {len(manager.base_prompt)} chars")

            # Test structure validation
            missing = manager.validate_prompt_structure()
            if not missing:
                print("✅ Prompt structure validation passed")
            else:
                print(f"⚠️  Missing prompt sections: {missing}")

            # Test criteria extraction
            criteria = manager.extract_evaluation_criteria()
            print(f"✅ Extracted {len(criteria)} evaluation criteria")
            for criterion, weight in criteria.items():
                print(f"   {criterion}: {weight:.0%}")

            return True
        else:
            print(f"⚠️  Evaluation prompt not found: {prompt_path}")
            return False
    except Exception as e:
        print(f"❌ Prompt manager test failed: {e}")
        return False


def test_llm_config():
    """Test LLM configuration (without actual API calls)"""
    print("\n🧪 Testing LLM configuration...")

    try:
        from src.config.llm_config import LLMManager, LLMConfig

        # Test with mock keys
        config = LLMConfig(gemini_api_key="test_key", openai_api_key="test_key")
        manager = LLMManager(config)
        print(f"✅ LLM manager initialized")
        print(f"   Gemini model: {config.gemini_model}")
        print(f"   OpenAI model: {config.openai_model}")
        print(f"   Temperature: {config.temperature}")

        # Test environment loading
        manager_env = LLMManager.from_environment()
        print("✅ LLM manager from environment created")

        return True
    except Exception as e:
        print(f"❌ LLM config test failed: {e}")
        return False


def test_models():
    """Test data models"""
    print("\n🧪 Testing data models...")

    try:
        from src.models.evaluation_models import (
            DocumentContent,
            EvaluationCriteria,
            JudgmentScore,
        )

        # Test DocumentContent
        doc = DocumentContent(
            title="Test Document",
            content="Test content",
            page_count=1,
            metadata={"test": "value"},
        )
        print("✅ DocumentContent model working")

        # Test EvaluationCriteria
        criteria = EvaluationCriteria()
        criteria.validate_weights_sum()
        print("✅ EvaluationCriteria model working")

        # Test JudgmentScore
        score = JudgmentScore(
            criterion="Test Criterion",
            score=8.5,
            rationale="Test rationale",
            confidence=0.9,
        )
        print("✅ JudgmentScore model working")

        return True
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False


def main():
    """Run all Phase 1 validation tests"""
    print("🚀 Phase 1 Validation Script")
    print("=" * 50)

    setup_logging()

    tests = [
        ("Core Imports", test_imports),
        ("PDF Parser", test_pdf_parser),
        ("Prompt Manager", test_prompt_manager),
        ("LLM Configuration", test_llm_config),
        ("Data Models", test_models),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 Phase 1 foundation is ready!")
        print("   You can now proceed to Phase 2: Agent Development")
    else:
        print("⚠️  Some tests failed. Please fix issues before proceeding.")
        print("   Check the setup guide: docs/development/setup-guide.md")


if __name__ == "__main__":
    main()
