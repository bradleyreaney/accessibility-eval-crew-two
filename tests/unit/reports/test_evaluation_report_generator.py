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
        """Test CLI report package includes completion summary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            metadata = {"execution_timestamp": "2025-01-01T12:00:00"}

            report_paths = report_generator.generate_cli_report_package(
                sample_partial_evaluation_results,
                ["comprehensive"],
                output_dir,
                metadata,
            )

            # Should include completion summary
            assert "completion_summary" in report_paths
            assert report_paths["completion_summary"].exists()

            # Should include other expected reports
            assert "execution_summary" in report_paths
            assert "comprehensive" in report_paths
            assert "csv" in report_paths
            assert "json" in report_paths
