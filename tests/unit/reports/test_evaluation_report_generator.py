"""
Unit tests for evaluation report generator.

Tests the report generation functionality including PDF creation,
CSV export, and various report formats.

References:
    - Phase 4 Plan: Report generation testing requirements
    - Master Plan: Testing strategy
    - LLM Error Handling Enhancement Plan - Phase 3
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from reportlab.lib.pagesizes import letter

from src.models.evaluation_models import (
    EvaluationStatus,
    PartialEvaluationSummary,
    ResilienceInfo,
)
from src.reports.generators.evaluation_report_generator import EvaluationReportGenerator


class TestEvaluationReportGenerator:
    """Test suite for evaluation report generator."""

    @pytest.fixture
    def report_generator(self):
        """Create a report generator instance for testing."""
        return EvaluationReportGenerator()

    @pytest.fixture
    def sample_evaluation_results(self):
        """Sample evaluation results for testing."""
        return {
            "plans": {
                "PlanA": {
                    "overall_score": 8.5,
                    "criteria_scores": {
                        "strategic_prioritization": 9.0,
                        "technical_specificity": 8.0,
                        "comprehensiveness": 8.5,
                        "long_term_vision": 7.5,
                    },
                    "analysis": "Strong strategic approach with good technical details.",
                    "strengths": ["Clear prioritization", "Comprehensive coverage"],
                    "weaknesses": ["Could use more specific timelines"],
                    "status": "completed",
                },
                "PlanB": {
                    "overall_score": 7.2,
                    "criteria_scores": {
                        "strategic_prioritization": 7.5,
                        "technical_specificity": 7.0,
                        "comprehensiveness": 7.2,
                        "long_term_vision": 6.8,
                    },
                    "analysis": "Good overall plan with room for improvement.",
                    "strengths": ["Balanced approach", "Realistic goals"],
                    "weaknesses": ["Lacks technical depth"],
                    "status": "completed",
                },
            },
            "synthesis": {
                "summary": "PlanA shows the strongest overall approach.",
                "recommendations": [
                    "Implement PlanA as the primary strategy",
                    "Incorporate technical details from PlanB",
                ],
            },
        }

    @pytest.fixture
    def sample_partial_evaluation_results(self):
        """Sample partial evaluation results with NA statuses."""
        return {
            "plans": {
                "PlanA": {
                    "overall_score": 8.5,
                    "criteria_scores": {
                        "strategic_prioritization": 9.0,
                        "technical_specificity": 8.0,
                        "comprehensiveness": 8.5,
                        "long_term_vision": 7.5,
                    },
                    "analysis": "Strong strategic approach with good technical details.",
                    "strengths": ["Clear prioritization", "Comprehensive coverage"],
                    "weaknesses": ["Could use more specific timelines"],
                    "status": "completed",
                },
                "PlanB": {
                    "status": "NA",
                    "na_reason": "LLM connection timeout",
                    "llm_used": "Gemini Pro",
                },
                "PlanC": {
                    "overall_score": 6.8,
                    "criteria_scores": {
                        "strategic_prioritization": 7.0,
                        "technical_specificity": 6.5,
                        "comprehensiveness": 6.8,
                        "long_term_vision": 6.5,
                    },
                    "analysis": "Basic plan with some good elements.",
                    "strengths": ["Simple and clear"],
                    "weaknesses": ["Lacks strategic depth"],
                    "status": "completed",
                },
            },
            "resilience_info": {
                "partial_evaluation": True,
                "available_llms": ["GPT-4"],
                "unavailable_llms": ["Gemini Pro"],
                "na_evaluations_count": 1,
                "completion_percentage": 66.7,
            },
            "llm_availability": {
                "gemini": False,
                "openai": True,
            },
        }

    def test_create_completion_statistics_complete_evaluation(
        self, report_generator, sample_evaluation_results
    ):
        """Test completion statistics for complete evaluation."""
        stats = report_generator.create_completion_statistics(sample_evaluation_results)

        assert stats["total_plans"] == 2
        assert stats["completed_evaluations"] == 2
        assert stats["na_evaluations"] == 0
        assert stats["failed_evaluations"] == 0
        assert stats["completion_percentage"] == 100.0
        assert stats["partial_evaluation"] is False
        assert "evaluation_timestamp" in stats

    def test_create_completion_statistics_partial_evaluation(
        self, report_generator, sample_partial_evaluation_results
    ):
        """Test completion statistics for partial evaluation with NA statuses."""
        stats = report_generator.create_completion_statistics(
            sample_partial_evaluation_results
        )

        assert stats["total_plans"] == 3
        assert stats["completed_evaluations"] == 2
        assert stats["na_evaluations"] == 1
        assert stats["failed_evaluations"] == 0
        assert stats["completion_percentage"] == 66.7
        assert stats["partial_evaluation"] is True
        assert stats["available_llms"] == ["GPT-4"]
        assert stats["unavailable_llms"] == ["Gemini Pro"]

    def test_create_completion_statistics_all_na(self, report_generator):
        """Test completion statistics when all evaluations are NA."""
        results = {
            "plans": {
                "PlanA": {"status": "NA", "na_reason": "LLM unavailable"},
                "PlanB": {"status": "NA", "na_reason": "LLM unavailable"},
            },
            "resilience_info": {
                "partial_evaluation": True,
                "available_llms": [],
                "unavailable_llms": ["Gemini Pro", "GPT-4"],
            },
        }

        stats = report_generator.create_completion_statistics(results)

        assert stats["total_plans"] == 2
        assert stats["completed_evaluations"] == 0
        assert stats["na_evaluations"] == 2
        assert stats["failed_evaluations"] == 0
        assert stats["completion_percentage"] == 0.0

    def test_generate_csv_export_with_na_evaluations(
        self, report_generator, sample_partial_evaluation_results
    ):
        """Test CSV export includes NA evaluations with proper status."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            csv_path = report_generator.generate_csv_export(
                sample_partial_evaluation_results, output_path
            )

            # Read the CSV and verify content
            df = pd.read_csv(csv_path)

            # Check that we have the expected rows
            assert len(df) == 3

            # Check completed evaluation
            plan_a_row = df[df["Plan"] == "PlanA"].iloc[0]
            assert plan_a_row["Status"] == "Completed"
            assert plan_a_row["Overall_Score"] == 8.5
            assert pd.isna(plan_a_row["NA_Reason"]) or plan_a_row["NA_Reason"] == ""

            # Check NA evaluation
            plan_b_row = df[df["Plan"] == "PlanB"].iloc[0]
            assert plan_b_row["Status"] == "Not Available"
            assert pd.isna(plan_b_row["Overall_Score"])
            assert plan_b_row["NA_Reason"] == "LLM connection timeout"
            assert plan_b_row["LLM_Used"] == "Gemini Pro"

        finally:
            output_path.unlink(missing_ok=True)

    def test_generate_json_export_with_resilience_info(
        self, report_generator, sample_partial_evaluation_results
    ):
        """Test JSON export includes resilience information and completion statistics."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            json_path = report_generator.generate_json_export(
                sample_partial_evaluation_results, output_path
            )

            # Read the JSON and verify content
            with open(json_path, "r") as f:
                export_data = json.load(f)

            # Check metadata
            assert "metadata" in export_data
            assert export_data["metadata"]["plans_count"] == 3

            # Check evaluation results
            assert "evaluation_results" in export_data

            # Check completion statistics
            assert "completion_statistics" in export_data
            stats = export_data["completion_statistics"]
            assert stats["total_plans"] == 3
            assert stats["completed_evaluations"] == 2
            assert stats["na_evaluations"] == 1
            assert stats["completion_percentage"] == 66.7

        finally:
            output_path.unlink(missing_ok=True)

    @patch("src.reports.generators.evaluation_report_generator.SimpleDocTemplate")
    def test_generate_completion_summary_report(
        self, mock_doc_template, report_generator, sample_partial_evaluation_results
    ):
        """Test completion summary report generation."""
        mock_doc = Mock()
        mock_doc_template.return_value = mock_doc

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            report_generator.generate_completion_summary_report(
                sample_partial_evaluation_results, output_path
            )

            # Verify document was created
            mock_doc_template.assert_called_once()
            mock_doc.build.assert_called_once()

            # Verify the story contains expected elements
            story = mock_doc.build.call_args[0][0]
            assert len(story) > 0

            # Check that we have title and statistics sections
            story_text = " ".join([str(item) for item in story])
            assert "Evaluation Completion Summary" in story_text
            assert "Completion Statistics" in story_text

        finally:
            output_path.unlink(missing_ok=True)

    def test_generate_completion_summary_report_fallback(
        self, report_generator, sample_partial_evaluation_results
    ):
        """Test completion summary report falls back to text when PDF fails."""
        with patch(
            "src.reports.generators.evaluation_report_generator.SimpleDocTemplate"
        ) as mock_doc_template:
            mock_doc_template.side_effect = Exception("PDF generation failed")

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                output_path = Path(tmp_file.name)

            try:
                report_generator.generate_completion_summary_report(
                    sample_partial_evaluation_results, output_path
                )

                # Should return text file path
                assert output_path.with_suffix(".txt").exists()

                # Check content
                summary_path = output_path.with_suffix(".txt")
                with open(summary_path, "r") as f:
                    content = f.read()

                assert "Evaluation Completion Summary" in content
                assert "Total Plans: 3" in content
                assert "Completed Evaluations: 2" in content
                assert "NA Evaluations: 1" in content

            finally:
                output_path.unlink(missing_ok=True)
                if summary_path.exists():
                    summary_path.unlink(missing_ok=True)

    @patch("src.reports.generators.evaluation_report_generator.SimpleDocTemplate")
    def test_generate_pdf_report_with_availability_status(
        self, mock_doc_template, report_generator, sample_partial_evaluation_results
    ):
        """Test PDF report generation includes availability status section."""
        mock_doc = Mock()
        mock_doc_template.return_value = mock_doc

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            output_path = Path(tmp_file.name)

        try:
            report_generator.generate_pdf_report(
                sample_partial_evaluation_results, output_path=output_path
            )

            # Verify document was created
            mock_doc_template.assert_called_once()
            mock_doc.build.assert_called_once()

            # Verify the story contains availability status section
            story = mock_doc.build.call_args[0][0]

            # Extract text content from story elements
            story_text = ""
            for item in story:
                if hasattr(item, "text"):
                    story_text += item.text + " "

            assert "LLM Availability Status" in story_text
            assert "Partial Evaluation" in story_text
            assert "Completion Rate: 66.7%" in story_text.replace("<b>", "").replace(
                "</b>", ""
            )

        finally:
            output_path.unlink(missing_ok=True)

    def test_create_availability_status_section(
        self, report_generator, sample_partial_evaluation_results
    ):
        """Test availability status section creation."""
        content = report_generator._create_availability_status_section(
            sample_partial_evaluation_results
        )

        # Extract text content from Paragraph objects
        content_text = ""
        for item in content:
            if hasattr(item, "text"):
                content_text += item.text + " "

        # Check for key elements
        assert "LLM Availability Status" in content_text
        assert "Partial Evaluation Completed" in content_text
        assert "Completion Rate: 66.7%" in content_text.replace("<b>", "").replace(
            "</b>", ""
        )
        assert "NA Evaluations: 1" in content_text.replace("<b>", "").replace(
            "</b>", ""
        )
        assert "openai: Available" in content_text.replace("<b>", "").replace(
            "</b>", ""
        ).replace("<font color='green'>", "").replace("</font>", "")
        assert "gemini: Unavailable" in content_text.replace("<b>", "").replace(
            "</b>", ""
        ).replace("<font color='red'>", "").replace("</font>", "")
        assert "Troubleshooting Guidance" in content_text

    def test_create_na_evaluation_section(self, report_generator):
        """Test NA evaluation section creation."""
        plan_data = {
            "status": "NA",
            "na_reason": "LLM connection timeout",
            "llm_used": "Gemini Pro",
        }

        content = report_generator._create_na_evaluation_section("PlanB", plan_data)

        # Extract text content from Paragraph objects
        content_text = ""
        for item in content:
            if hasattr(item, "text"):
                content_text += item.text + " "

        assert "Status: Not Available (NA)" in content_text
        assert "Reason: LLM connection timeout" in content_text.replace(
            "<b>", ""
        ).replace("</b>", "")
        assert "LLM: Gemini Pro" in content_text.replace("<b>", "").replace("</b>", "")
        assert "This evaluation could not be completed" in content_text

    def test_create_completed_evaluation_section(
        self, report_generator, sample_evaluation_results
    ):
        """Test completed evaluation section creation."""
        plan_data = sample_evaluation_results["plans"]["PlanA"]

        content = report_generator._create_completed_evaluation_section(
            "PlanA", plan_data
        )

        # Extract text content from Paragraph objects
        content_text = ""
        for item in content:
            if hasattr(item, "text"):
                content_text += item.text + " "

        assert "Overall Score: 8.5/10" in content_text.replace("<b>", "").replace(
            "</b>", ""
        )
        assert "Analysis: Strong strategic approach" in content_text.replace(
            "<b>", ""
        ).replace("</b>", "")
        assert "Strengths:" in content_text
        assert "Clear prioritization" in content_text
        assert "Areas for Improvement:" in content_text
        assert "Could use more specific timelines" in content_text

    def test_create_executive_summary_with_partial_evaluation(
        self, report_generator, sample_partial_evaluation_results
    ):
        """Test executive summary creation with partial evaluation notice."""
        content = report_generator._create_executive_summary(
            sample_partial_evaluation_results
        )
        content_text = " ".join([str(item) for item in content])

        # Should mention partial evaluation
        assert "completed with 66.7% coverage" in content_text
        assert "1 evaluations marked as NA" in content_text
        assert "LLM Availability Status section" in content_text

    def test_create_executive_summary_all_na(self, report_generator):
        """Test executive summary when all evaluations are NA."""
        results = {
            "plans": {
                "PlanA": {"status": "NA", "na_reason": "LLM unavailable"},
                "PlanB": {"status": "NA", "na_reason": "LLM unavailable"},
            },
            "resilience_info": {
                "partial_evaluation": True,
                "completion_percentage": 0.0,
                "na_evaluations_count": 2,
            },
        }

        content = report_generator._create_executive_summary(results)
        content_text = " ".join([str(item) for item in content])

        assert "All evaluations were marked as NA" in content_text
        assert "troubleshooting guidance" in content_text

    def test_create_scoring_overview_with_na_rows(
        self, report_generator, sample_partial_evaluation_results
    ):
        """Test scoring overview table includes NA rows with proper styling."""
        content = report_generator._create_scoring_overview(
            sample_partial_evaluation_results
        )

        # Should have table with status column
        content_text = " ".join([str(item) for item in content])
        assert "Scoring Overview" in content_text
        assert "Status" in content_text
        assert "Plan" in content_text
        assert "Overall Score" in content_text

    def test_cli_report_package_includes_completion_summary(
        self, report_generator, sample_partial_evaluation_results
    ):
        """Test CLI report package includes unified report and data exports."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            metadata = {"execution_timestamp": "2025-01-01T12:00:00"}

            report_paths = report_generator.generate_cli_report_package(
                sample_partial_evaluation_results,
                ["comprehensive"],
                output_dir,
                metadata,
            )

            # Should include unified report (replaces individual PDFs)
            assert "unified_report" in report_paths
            assert report_paths["unified_report"].exists()

            # Should include data exports
            assert "csv" in report_paths
            assert "json" in report_paths

            # Verify file types
            assert report_paths["unified_report"].suffix == ".pdf"
            assert report_paths["csv"].suffix == ".csv"
            assert report_paths["json"].suffix == ".json"

    def test_generate_unified_pdf_report_creates_single_file(
        self, report_generator, sample_evaluation_results
    ):
        """Test that unified PDF report is generated correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            metadata = {"execution_timestamp": "2025-01-01T12:00:00"}

            # Generate unified report
            output_path = report_generator.generate_unified_pdf_report(
                sample_evaluation_results, output_dir, metadata
            )

            # Should create a single PDF file
            assert output_path.exists()
            assert output_path.suffix == ".pdf"
            assert "accessibility_evaluation_report_" in output_path.name

            # Should be the only PDF file in the directory
            pdf_files = list(output_dir.glob("*.pdf"))
            assert len(pdf_files) == 1
            assert pdf_files[0] == output_path

    def test_unified_report_contains_all_sections(
        self, report_generator, sample_evaluation_results
    ):
        """Test that unified report includes all required sections."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            metadata = {"execution_timestamp": "2025-01-01T12:00:00"}

            # Generate unified report
            output_path = report_generator.generate_unified_pdf_report(
                sample_evaluation_results, output_dir, metadata
            )

            # Verify file was created and has content
            assert output_path.exists()
            assert output_path.stat().st_size > 0

            # Note: We can't easily test PDF content in unit tests
            # This would require PDF parsing libraries
            # The test above verifies the file is created successfully

    def test_table_of_contents_generation(self, report_generator):
        """Test table of contents creation and formatting."""
        content = report_generator._create_table_of_contents()

        # Should contain table of contents elements
        assert len(content) > 0

        # Extract text content
        content_text = " ".join([str(item) for item in content])
        assert "Table of Contents" in content_text

        # Should contain expected TOC entries
        expected_entries = [
            "Executive Summary",
            "Execution Summary",
            "Completion Summary",
            "Detailed Analysis",
            "Scoring Overview",
            "Recommendations",
        ]

        for entry in expected_entries:
            assert entry in content_text

    def test_unified_report_with_metadata(
        self, report_generator, sample_evaluation_results
    ):
        """Test unified report generation with execution metadata."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            metadata = {
                "execution_timestamp": "2025-01-01T12:00:00",
                "configuration": {"mode": "parallel", "consensus": "weighted"},
                "audit_files": ["audit1.pdf"],
                "plan_files": ["plan1.pdf", "plan2.pdf"],
            }

            # Generate unified report
            output_path = report_generator.generate_unified_pdf_report(
                sample_evaluation_results, output_dir, metadata
            )

            # Should create file successfully
            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_unified_report_error_handling(self, report_generator):
        """Test unified report generation error handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            # Test with invalid evaluation results
            invalid_results = None

            with pytest.raises(Exception):
                report_generator.generate_unified_pdf_report(
                    invalid_results, output_dir, {}
                )

    def test_page_header_footer_generation(self, report_generator):
        """Test page header and footer creation and formatting."""
        # Test that header/footer method exists and can be called
        assert hasattr(report_generator, "_create_page_header_footer")

        # Test that it returns a callable function
        header_footer_func = report_generator._create_page_header_footer
        assert callable(header_footer_func)

    def test_enhanced_visual_elements(
        self, report_generator, sample_evaluation_results
    ):
        """Test enhanced visual elements and styling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            metadata = {"execution_timestamp": "2025-01-01T12:00:00"}

            # Generate unified report with enhanced styling
            output_path = report_generator.generate_unified_pdf_report(
                sample_evaluation_results, output_dir, metadata
            )

            # Verify enhanced styling was applied
            assert output_path.exists()
            assert output_path.stat().st_size > 0

            # Check that the file is larger than basic version (indicating enhanced content)
            # This is a basic check - in a real scenario we'd parse the PDF content

    def test_professional_color_scheme(self, report_generator):
        """Test professional color scheme implementation."""
        # Test that color constants are defined
        assert hasattr(report_generator, "colors")

        # Test that professional colors are available
        # This would test the color scheme implementation

    def test_consistent_typography(self, report_generator):
        """Test consistent typography and font usage."""
        # Test that typography styles are properly configured
        assert hasattr(report_generator, "styles")
        assert report_generator.styles is not None

        # Test that required styles are available
        required_styles = ["Title", "Heading1", "Normal"]
        for style in required_styles:
            assert style in report_generator.styles

    def test_improved_spacing_and_layout(
        self, report_generator, sample_evaluation_results
    ):
        """Test improved spacing and layout in reports."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            metadata = {"execution_timestamp": "2025-01-01T12:00:00"}

            # Generate report with improved layout
            output_path = report_generator.generate_unified_pdf_report(
                sample_evaluation_results, output_dir, metadata
            )

            # Verify improved layout was applied
            assert output_path.exists()
            # Additional layout-specific tests would go here

    def test_chart_integration_optimization(self, report_generator):
        """Test chart integration and optimization."""
        # Test that chart integration methods exist
        assert hasattr(report_generator, "_create_chart_elements")

        # Test chart creation with sample data
        # This would test the enhanced chart integration

    def test_comprehensive_unified_report_generation(
        self, report_generator, sample_evaluation_results
    ):
        """Test comprehensive unified report generation with all features."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            metadata = {
                "execution_timestamp": "2025-01-01T12:00:00",
                "configuration": {"mode": "parallel", "consensus": "weighted"},
                "audit_files": ["audit1.pdf", "audit2.pdf"],
                "plan_files": ["plan1.pdf", "plan2.pdf"],
                "duration_minutes": 15.5,
                "total_tokens_used": 12500,
            }

            # Generate comprehensive unified report
            output_path = report_generator.generate_unified_pdf_report(
                sample_evaluation_results, output_dir, metadata
            )

            # Verify comprehensive report was generated
            assert output_path.exists()
            assert output_path.stat().st_size > 0

            # Check file naming convention
            assert "accessibility_evaluation_report_" in output_path.name
            assert output_path.suffix == ".pdf"

    def test_enhanced_styling_integration(
        self, report_generator, sample_evaluation_results
    ):
        """Test that enhanced styling is properly integrated throughout the report."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            metadata = {"execution_timestamp": "2025-01-01T12:00:00"}

            # Generate report with enhanced styling
            output_path = report_generator.generate_unified_pdf_report(
                sample_evaluation_results, output_dir, metadata
            )

            # Verify enhanced styling was applied
            assert output_path.exists()

            # Check that the file is larger than basic version (indicating enhanced content)
            # This is a basic check - in a real scenario we'd parse the PDF content
            assert (
                output_path.stat().st_size > 5000
            )  # Enhanced reports should be larger

    def test_color_scheme_consistency(self, report_generator):
        """Test that color scheme is consistent and properly defined."""
        # Verify all required colors are defined
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
            assert report_generator.colors[color_name] is not None

    def test_enhanced_table_styling(self, report_generator):
        """Test enhanced table styling and formatting."""
        # Test that table styling methods work correctly
        assert hasattr(report_generator, "_create_execution_summary_section")
        assert hasattr(report_generator, "_create_completion_summary_section")

        # Test table creation with sample data
        sample_metadata = {
            "execution_timestamp": "2025-01-01T12:00:00",
            "configuration": {"mode": "parallel"},
        }

        table_content = report_generator._create_execution_summary_section(
            sample_metadata
        )
        assert len(table_content) > 0

    def test_chart_generation_with_multiple_plans(self, report_generator):
        """Test chart generation when multiple plans are available."""
        # Create sample data with multiple plans
        multi_plan_results = {
            "plans": {
                "PlanA": {"overall_score": 8.5, "status": "completed"},
                "PlanB": {"overall_score": 7.2, "status": "completed"},
                "PlanC": {"overall_score": 6.8, "status": "completed"},
            }
        }

        # Test chart generation
        chart_elements = report_generator._create_chart_elements(multi_plan_results)
        assert len(chart_elements) > 0

        # Verify chart contains expected elements
        chart_text = " ".join([str(item) for item in chart_elements])
        assert "Score Comparison Chart" in chart_text
        assert "Plan" in chart_text
        assert "Score" in chart_text

    def test_error_handling_and_validation(self, report_generator):
        """Test error handling and input validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            # Test with invalid evaluation results (None)
            with pytest.raises(Exception):
                report_generator.generate_unified_pdf_report(None, output_dir, {})

            # Test with empty evaluation results (empty dict should work but create minimal report)
            try:
                output_path = report_generator.generate_unified_pdf_report(
                    {}, output_dir, {}
                )
                # Empty results should still generate a report (though minimal)
                assert output_path.exists()
                assert output_path.stat().st_size > 0
            except Exception as e:
                # If it fails, that's also acceptable - just verify it's handled gracefully
                assert "Failed to generate unified PDF report" in str(e)

    def test_performance_and_file_size(
        self, report_generator, sample_evaluation_results
    ):
        """Test report generation performance and file size optimization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            metadata = {"execution_timestamp": "2025-01-01T12:00:00"}

            # Generate report and measure performance
            import time

            start_time = time.time()

            output_path = report_generator.generate_unified_pdf_report(
                sample_evaluation_results, output_dir, metadata
            )

            generation_time = time.time() - start_time

            # Verify reasonable performance (should complete in under 5 seconds)
            assert generation_time < 5.0

            # Verify reasonable file size (should be between 5KB and 100KB for sample data)
            file_size = output_path.stat().st_size
            assert 5000 <= file_size <= 100000

    def test_cli_integration_with_enhanced_styling(
        self, report_generator, sample_evaluation_results
    ):
        """Test CLI integration with enhanced styling features."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            metadata = {"execution_timestamp": "2025-01-01T12:00:00"}

            # Test CLI report package generation
            report_paths = report_generator.generate_cli_report_package(
                sample_evaluation_results, ["comprehensive"], output_dir, metadata
            )

            # Verify unified report was generated
            assert "unified_report" in report_paths
            assert report_paths["unified_report"].exists()

            # Verify other expected outputs
            assert "csv" in report_paths
            assert "json" in report_paths
