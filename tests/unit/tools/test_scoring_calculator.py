"""Tests for scoring calculator."""

import unittest
from unittest.mock import patch

from src.agents.tools.scoring_calculator import ScoringCalculatorTool


class TestScoringCalculator(unittest.TestCase):
    """Test cases for ScoringCalculator."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool = ScoringCalculatorTool()

    def test_calculate_missing_scores_error(self):
        """Test error handling for missing scores."""
        # Test with empty scores
        result = self.tool._run({}, {}, "TestPlan")
        self.assertIn("Error: Missing scores", result)

    def test_calculate_missing_weights_error(self):
        """Test error handling for missing weights."""
        # Test with scores but empty weights
        scores = {"criterion1": 8.0}
        result = self.tool._run(scores, {}, "TestPlan")
        self.assertIn("Error: Missing scores", result)

    @patch("src.agents.tools.scoring_calculator.logger")
    def test_calculate_exception_handling(self, mock_logger):
        """Test exception handling in _run."""
        # Test with invalid input that causes exception
        with patch.object(
            self.tool, "_calculate_weighted_score", side_effect=Exception("Test error")
        ):
            result = self.tool._run({"test": 5.0}, {"test": 0.5}, "TestPlan")
            self.assertIn("Error: Failed to calculate score", result)
            mock_logger.error.assert_called()

    def test_assess_performance_level_ranges(self):
        """Test all performance level ranges."""
        # Test Exceptional range
        self.assertEqual(self.tool._assess_performance_level(9.0), "Exceptional")
        self.assertEqual(self.tool._assess_performance_level(10.0), "Exceptional")

        # Test Strong range
        self.assertEqual(self.tool._assess_performance_level(7.5), "Strong")
        self.assertEqual(self.tool._assess_performance_level(8.9), "Strong")

        # Test Adequate range
        self.assertEqual(self.tool._assess_performance_level(5.0), "Adequate")
        self.assertEqual(self.tool._assess_performance_level(6.9), "Adequate")

        # Test Needs Improvement range
        self.assertEqual(self.tool._assess_performance_level(3.0), "Needs Improvement")
        self.assertEqual(self.tool._assess_performance_level(4.9), "Needs Improvement")

        # Test Poor range
        self.assertEqual(self.tool._assess_performance_level(0.0), "Poor")
        self.assertEqual(self.tool._assess_performance_level(2.9), "Poor")

    def test_calculate_comparative_rankings_empty(self):
        """Test comparative rankings with empty scores."""
        result = self.tool.calculate_comparative_rankings({})
        self.assertIn("No scores provided", result)

    def test_calculate_comparative_rankings_multiple(self):
        """Test comparative rankings with multiple plans."""
        scores = {"PlanA": 8.5, "PlanB": 6.2, "PlanC": 9.1}
        result = self.tool.calculate_comparative_rankings(scores)

        # Should have rankings header
        self.assertIn("COMPARATIVE RANKINGS", result)

        # Should be sorted by score (PlanC first, then PlanA, then PlanB)
        lines = result.split("\n")
        self.assertIn("1. PlanC: 9.10", lines[2])
        self.assertIn("2. PlanA: 8.50", lines[3])
        self.assertIn("3. PlanB: 6.20", lines[4])

    def test_calculate_weighted_score_direct(self):
        """Test weighted score calculation directly."""
        scores = {"criterion1": 8.0, "criterion2": 6.0}
        weights = {"criterion1": 0.6, "criterion2": 0.4}

        weighted_score = self.tool._calculate_weighted_score(scores, weights)
        expected = (8.0 * 0.6) + (6.0 * 0.4)  # 4.8 + 2.4 = 7.2
        self.assertEqual(weighted_score, expected)

    def test_generate_scoring_analysis_structure(self):
        """Test scoring analysis generation structure."""
        scores = {"criterion1": 8.0}
        weights = {"criterion1": 1.0}

        analysis = self.tool._generate_scoring_analysis(
            scores, weights, 8.0, "TestPlan"
        )

        # Should contain key components
        self.assertIn("SCORING ANALYSIS", analysis)
        self.assertIn("TestPlan", analysis)
        self.assertIn("Overall Weighted Score: 8.00", analysis)

    def test_scoring_calculator_zero_weight_edge_case(self):
        """Test scoring calculator zero weight edge case."""
        # Test with weights that are zero using the actual method
        scores = {"accessibility": 5.0}
        weights = {"accessibility": 0.0}  # Zero weight

        # This should handle zero weights gracefully
        result = self.tool._calculate_weighted_score(scores, weights)
        self.assertEqual(result, 0.0)

    def test_scoring_calculator_ranking_ties(self):
        """Test scoring calculator ranking with tied scores."""
        # Test scores with ties using the actual method
        scores = {"plan_a": 8.5, "plan_b": 8.5, "plan_c": 7.0}  # Same score

        # Should handle ties appropriately
        rankings = self.tool.calculate_comparative_rankings(scores)
        self.assertIsInstance(rankings, str)
        self.assertIn("plan_a", rankings)
        self.assertIn("plan_b", rankings)


if __name__ == "__main__":
    unittest.main()
