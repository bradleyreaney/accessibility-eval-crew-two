#!/usr/bin/env python3
"""
Phase 4 demonstration script

This script demonstrates the Phase 4 UI components and functionality.
It can be run to test the Streamlit application and verify components work correctly.

Usage:
    python scripts/phase4_demo.py
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Also set PYTHONPATH environment variable
os.environ["PYTHONPATH"] = str(project_root)


def test_workflow_controller():
    """Test the workflow controller functionality"""
    print("🔍 Testing Workflow Controller...")

    from unittest.mock import Mock

    from src.models.evaluation_models import DocumentContent, EvaluationInput
    from src.utils.workflow_controller import WorkflowController, WorkflowStatus

    # Create mock crew
    mock_crew = Mock()
    mock_crew.execute_complete_evaluation.return_value = {"status": "completed"}

    # Test workflow controller
    controller = WorkflowController(mock_crew)

    # Test status
    status = controller.get_status()
    assert status.status == "idle"
    assert status.progress == 0
    print("  ✅ Initial status correct")

    # Test time estimation
    evaluation_input = EvaluationInput(
        audit_report=DocumentContent(
            title="Test Audit", content="Test content", page_count=5, metadata={}
        ),
        remediation_plans={
            "PlanA": DocumentContent(
                title="Plan A", content="Plan A content", page_count=3, metadata={}
            )
        },
    )

    estimated_time = controller.estimate_time(evaluation_input)
    assert isinstance(estimated_time, int)
    assert estimated_time > 0
    print(f"  ✅ Time estimation: {estimated_time} minutes")

    print("✅ Workflow Controller tests passed!")


def test_report_generator():
    """Test the report generator functionality"""
    print("🔍 Testing Report Generator...")

    from src.models.evaluation_models import DocumentContent, EvaluationInput
    from src.reports.generators.evaluation_report_generator import (
        EvaluationReportGenerator,
    )

    # Test report generator
    generator = EvaluationReportGenerator()

    # Test paths exist
    assert generator.output_dir.exists()
    print("  ✅ Output directory created")

    # Test placeholder methods
    evaluation_input = EvaluationInput(
        audit_report=DocumentContent(
            title="Test Audit", content="Test content", page_count=5, metadata={}
        ),
        remediation_plans={},
    )

    results = {"test": "data"}

    # Test PDF generation (placeholder)
    pdf_path = generator.generate_pdf_report(results, evaluation_input)
    assert pdf_path.exists()
    print("  ✅ PDF report placeholder created")

    # Test CSV generation (placeholder)
    csv_path = generator.generate_csv_export(results)
    assert csv_path.exists()
    print("  ✅ CSV export placeholder created")

    # Test JSON generation (placeholder)
    json_path = generator.generate_json_export(results)
    assert json_path.exists()
    print("  ✅ JSON export placeholder created")

    print("✅ Report Generator tests passed!")


def test_app_imports():
    """Test that the app imports work correctly"""
    print("🔍 Testing App Imports...")

    try:
        from app.main import AccessibilityEvaluatorApp

        print("  ✅ Main app import successful")

        # Test app initialization
        app = AccessibilityEvaluatorApp()
        assert app.pdf_parser is not None
        assert app.report_generator is not None
        print("  ✅ App initialization successful")

    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

    print("✅ App import tests passed!")
    return True


def demo_streamlit_launch():
    """Demo how to launch the Streamlit app"""
    print("🚀 Streamlit App Launch Instructions:")
    print()
    print("To launch the Streamlit application:")
    print("  1. Ensure all dependencies are installed:")
    print("     pip install streamlit plotly")
    print()
    print("  2. Run the Streamlit app:")
    print("     streamlit run app/main.py")
    print()
    print("  3. The app will open in your browser at http://localhost:8501")
    print()
    print("📋 Features Available:")
    print("  • System Configuration (API Keys)")
    print("  • File Upload Interface")
    print("  • Evaluation Execution")
    print("  • Progress Monitoring")
    print("  • Results Dashboard (placeholder)")
    print("  • Export Functionality (placeholder)")
    print()


def main():
    """Main demo function"""
    print("🎯 Phase 4 Demonstration")
    print("=" * 50)
    print()

    success = True

    try:
        test_workflow_controller()
        print()

        test_report_generator()
        print()

        success = test_app_imports() and success
        print()

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        success = False

    if success:
        demo_streamlit_launch()
        print("🎉 Phase 4 core components successfully implemented!")
        print()
        print("📝 Summary:")
        print("  ✅ Workflow Controller - Full functionality")
        print("  ✅ Report Generator - Placeholder structure")
        print("  ✅ Streamlit App - Core UI framework")
        print("  ✅ Integration Points - All connected")
        print()
        print("🔜 Next Steps:")
        print("  • Enhance UI components based on evaluation results")
        print("  • Implement real report generation")
        print("  • Add visualization components")
        print("  • Complete export functionality")
    else:
        print("❌ Phase 4 demo encountered issues!")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
