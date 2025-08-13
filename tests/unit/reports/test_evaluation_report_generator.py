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
        result = self.generator._generate_synthesis_recommendations(self.mock_results)
        self.assertIsInstance(result, Path)

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
