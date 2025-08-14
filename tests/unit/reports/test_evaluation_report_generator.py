"""Simple tests for evaluation report generator to boost coverage."""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.reports.generators.evaluation_report_generator import EvaluationReportGenerator


class TestEvaluationReportGenerator(unittest.TestCase):
    """Basic test cases for EvaluationReportGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = EvaluationReportGenerator()
        self.mock_results = {
            "evaluations": [],
            "summary": {"total_plans": 0, "average_score": 0},
            "metadata": {"timestamp": "2025-01-13"},
        }

    def test_generator_initialization(self):
        """Test generator initializes correctly."""
        self.assertIsInstance(self.generator, EvaluationReportGenerator)
        self.assertTrue(hasattr(self.generator, "output_dir"))
        self.assertTrue(hasattr(self.generator, "styles"))

    @patch("src.reports.generators.evaluation_report_generator.SimpleDocTemplate")
    @patch("src.reports.generators.evaluation_report_generator.getSampleStyleSheet")
    def test_generate_pdf_report(self, mock_styles, mock_doc):
        """Test PDF report generation."""
        mock_doc_instance = Mock()
        mock_doc.return_value = mock_doc_instance
        mock_styles.return_value = {"Normal": Mock(), "Heading1": Mock()}

        result = self.generator.generate_pdf_report(self.mock_results)
        self.assertIsInstance(result, Path)

    def test_generate_csv_export(self):
        """Test CSV export generation."""
        result = self.generator.generate_csv_export(self.mock_results)
        self.assertIsInstance(result, Path)

    def test_generate_json_export(self):
        """Test JSON export generation."""
        result = self.generator.generate_json_export(self.mock_results)
        self.assertIsInstance(result, Path)

    def test_generate_executive_summary(self):
        """Test executive summary generation."""
        result = self.generator._generate_executive_summary(self.mock_results)
        self.assertIsInstance(result, Path)

    def test_generate_text_report(self):
        """Test text report generation."""
        test_path = Path("test_report.txt")
        result = self.generator._generate_text_report(self.mock_results, test_path)
        self.assertIsInstance(result, Path)

    def test_generate_detailed_analysis(self):
        """Test detailed analysis generation."""
        result = self.generator._generate_detailed_analysis(self.mock_results)
        self.assertIsInstance(result, Path)

    def test_create_title_page(self):
        """Test title page creation."""
        result = self.generator._create_title_page(self.mock_results, "evaluation")
        self.assertIsInstance(result, list)

    def test_generate_synthesis_recommendations(self):
        """Test synthesis recommendations generation."""
        synthesis_data = {
            "synthesis": {
                "recommendations": ["Recommendation 1", "Recommendation 2"],
                "optimal_approach": "Test approach",
            }
        }
        result = self.generator._create_synthesis_section(synthesis_data)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    def test_pdf_generation_error_fallback(self):
        """Test fallback to text report when PDF generation fails."""
        # Mock SimpleDocTemplate to raise an exception
        with patch(
            "src.reports.generators.evaluation_report_generator.SimpleDocTemplate"
        ) as mock_doc:
            mock_doc.side_effect = Exception("PDF generation failed")

            result = self.generator.generate_pdf_report(self.mock_results)
            self.assertIsInstance(result, Path)
            # Should fallback to .txt extension
            self.assertEqual(result.suffix, ".txt")

    def test_executive_summary_with_empty_plans(self):
        """Test executive summary generation with no plans."""
        empty_results = {"plans": {}, "metadata": {"timestamp": "2025-01-13"}}
        result = self.generator._create_executive_summary(empty_results)
        self.assertIsInstance(result, list)

    def test_executive_summary_with_plans(self):
        """Test executive summary generation with plan data."""
        results_with_plans = {
            "plans": {
                "Plan A": {"overall_score": 8.5, "analysis": "Good plan"},
                "Plan B": {"overall_score": 7.2, "analysis": "Average plan"},
            },
            "metadata": {"timestamp": "2025-01-13"},
        }
        result = self.generator._create_executive_summary(results_with_plans)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    def test_detailed_analysis_with_complete_data(self):
        """Test detailed analysis with complete plan data."""
        complete_results = {
            "plans": {
                "Plan A": {
                    "overall_score": 8.5,
                    "analysis": "Comprehensive analysis",
                    "strengths": ["Strong approach", "Good documentation"],
                    "weaknesses": ["Could improve timeline", "Needs more testing"],
                }
            }
        }
        result = self.generator._create_detailed_analysis(complete_results)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    def test_detailed_analysis_with_minimal_data(self):
        """Test detailed analysis with minimal plan data."""
        minimal_results = {"plans": {"Plan A": {"overall_score": 6.0}}}
        result = self.generator._create_detailed_analysis(minimal_results)
        self.assertIsInstance(result, list)

    def test_synthesis_section_with_recommendations(self):
        """Test synthesis section with recommendations."""
        synthesis_results = {
            "synthesis": {
                "recommendations": [
                    "Use Plan A approach",
                    "Combine with Plan B features",
                ],
                "optimal_approach": "Hybrid solution",
            }
        }
        result = self.generator._create_synthesis_section(synthesis_results)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    def test_text_report_generation(self):
        """Test fallback text report generation."""
        test_results = {
            "plans": {
                "Plan A": {"overall_score": 8.0, "analysis": "Good strategic approach"}
            }
        }
        result = self.generator._generate_text_report(test_results, None)
        self.assertIsInstance(result, Path)
        self.assertEqual(result.suffix, ".txt")

    def test_csv_export_with_complete_data(self):
        """Test CSV export with complete criteria scores."""
        complete_results = {
            "plans": {
                "Plan A": {
                    "overall_score": 8.5,
                    "criteria_scores": {
                        "strategic_prioritization": 9.0,
                        "technical_specificity": 8.0,
                        "comprehensiveness": 8.5,
                        "long_term_vision": 8.0,
                    },
                },
                "Plan B": {
                    "overall_score": 7.0,
                    "criteria_scores": {
                        "strategic_prioritization": 7.5,
                        "technical_specificity": 6.5,
                        "comprehensiveness": 7.0,
                        "long_term_vision": 7.0,
                    },
                },
            }
        }
        result = self.generator.generate_csv_export(complete_results)
        self.assertIsInstance(result, Path)
        self.assertEqual(result.suffix, ".csv")

    def test_csv_export_with_empty_plans(self):
        """Test CSV export with no plans."""
        empty_results = {"plans": {}}
        result = self.generator.generate_csv_export(empty_results)
        self.assertIsInstance(result, Path)
        self.assertEqual(result.suffix, ".csv")

    def test_json_export_with_complex_data(self):
        """Test JSON export with complex evaluation data."""
        complex_results = {
            "plans": {
                "Plan A": {
                    "overall_score": 8.5,
                    "criteria_scores": {"strategic_prioritization": 9.0},
                    "analysis": "Detailed analysis",
                    "strengths": ["Good approach"],
                    "weaknesses": ["Minor issues"],
                }
            },
            "metadata": {"timestamp": "2025-01-13", "evaluator": "test"},
            "synthesis": {"recommendations": ["Use Plan A"]},
        }
        result = self.generator.generate_json_export(complex_results)
        self.assertIsInstance(result, Path)
        self.assertEqual(result.suffix, ".json")

    def test_pdf_generation_with_synthesis(self):
        """Test PDF generation with synthesis data."""
        results_with_synthesis = {
            "plans": {"Plan A": {"overall_score": 8.0}},
            "synthesis": {"recommendations": ["Test recommendation"]},
            "metadata": {"timestamp": "2025-01-13"},
        }

        with patch(
            "src.reports.generators.evaluation_report_generator.SimpleDocTemplate"
        ):
            with patch(
                "src.reports.generators.evaluation_report_generator.getSampleStyleSheet"
            ):
                result = self.generator.generate_pdf_report(results_with_synthesis)
                self.assertIsInstance(result, Path)

    @patch("src.reports.generators.evaluation_report_generator.Path.mkdir")
    def test_complete_report_package_error_handling(self, mock_mkdir):
        """Test error handling in complete report package generation."""
        # Mock an error that will trigger the except block at lines 513-514
        with patch.object(self.generator, "generate_pdf_report") as mock_pdf:
            mock_pdf.side_effect = Exception("PDF generation failed")

            with self.assertRaises(Exception) as context:
                self.generator.generate_complete_report_package(self.mock_results)

            self.assertIn(
                "Failed to generate complete report package", str(context.exception)
            )

    def test_generate_comparison_analysis(self):
        """Test comparison analysis generation."""
        result = self.generator._generate_comparison_analysis(self.mock_results)
        self.assertIsInstance(result, Path)

    def test_generate_complete_report_package(self):
        """Test complete report package generation."""
        result = self.generator.generate_complete_report_package(self.mock_results)
        self.assertIsInstance(result, dict)
        self.assertIn("executive", result)
        self.assertIn("csv", result)
        self.assertIn("json", result)

    def test_create_executive_summary(self):
        """Test create executive summary method."""
        result = self.generator._create_executive_summary(self.mock_results)
        self.assertIsInstance(result, list)

    def test_create_scoring_overview(self):
        """Test create scoring overview method."""
        test_results = {
            "plans": {"Plan A": {"score": 8.5}, "Plan B": {"score": 7.2}},
            "summary": {"average_score": 7.85},
        }
        result = self.generator._create_scoring_overview(test_results)
        self.assertIsInstance(result, list)

    def test_create_synthesis_section(self):
        """Test create synthesis section method."""
        test_results = {
            "optimal_plan": {"name": "Plan A", "rationale": "Best plan"},
            "recommendations": ["Rec 1", "Rec 2"],
        }
        result = self.generator._create_synthesis_section(test_results)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)


if __name__ == "__main__":
    unittest.main()
