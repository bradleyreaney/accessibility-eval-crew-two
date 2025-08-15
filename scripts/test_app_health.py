#!/usr/bin/env python3
"""
Test script to verify the app runs without critical errors
Tests the main app components without launching the full Streamlit interface
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import warning suppression (which auto-applies when imported)
import src.utils.suppress_warnings


def test_app_imports():
    """Test that all app modules can be imported"""
    print("🧪 Testing app imports...")

    try:
        from app.main import AccessibilityEvaluatorApp

        print("✅ Main app module imports successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_app_instantiation():
    """Test that the app can be instantiated"""
    print("🧪 Testing app instantiation...")

    try:
        from app.main import AccessibilityEvaluatorApp

        app = AccessibilityEvaluatorApp()
        print("✅ App instantiation successful")
        return True
    except Exception as e:
        print(f"❌ Instantiation error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_core_modules():
    """Test that core modules can be imported"""
    print("🧪 Testing core module imports...")

    modules_to_test = [
        "src.config.llm_config",
        "src.models.evaluation_models",
        "src.tools.pdf_parser",
        "src.tools.prompt_manager",
        "src.utils.suppress_warnings",
    ]

    success_count = 0
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
            success_count += 1
        except Exception as e:
            print(f"❌ {module}: {e}")

    return success_count == len(modules_to_test)


def main():
    """Run all tests"""
    print("🚀 Starting app error verification tests...\n")

    tests = [
        ("Core modules", test_core_modules),
        ("App imports", test_app_imports),
        ("App instantiation", test_app_instantiation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! The app should run without critical errors.")
        print(
            "💡 Note: Deprecation warnings from dependencies are suppressed but harmless."
        )
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
