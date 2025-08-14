"""
Test suite for agent tools.
Tests all tools in src/agents/tools/
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from src.agents.tools.evaluation_framework import EvaluationFrameworkTool
from src.agents.tools.gap_analyzer import GapAnalyzerTool
from src.agents.tools.plan_comparator import PlanComparatorTool
from src.agents.tools.scoring_calculator import ScoringCalculatorTool


class TestEvaluationFrameworkTool(unittest.TestCase):
    """Test suite for EvaluationFrameworkTool"""

    def setUp(self):
        """Set up test fixtures"""
        self.tool = EvaluationFrameworkTool()

    def test_tool_initialization(self):
        """Test that evaluation framework tool initializes correctly"""
        self.assertEqual(self.tool.name, "evaluation_framework")
        self.assertIsNotNone(self.tool.description)

    def test_tool_run_basic_functionality(self):
        """Test basic tool execution"""
        # This will test the _run method indirectly
        result = self.tool._run(
            plan_name="Test Plan",
            plan_content="Test plan content",
            audit_context="Test audit context",
        )
        self.assertIsInstance(result, str)
        self.assertIn("evaluation", result.lower())

    @patch("src.agents.tools.evaluation_framework.PromptManager")
    def test_load_framework_criteria_success(self, mock_prompt_manager):
        """Test successful loading of framework criteria"""
        # Setup mock to return valid criteria
        mock_instance = Mock()
        mock_instance.extract_evaluation_criteria.return_value = {
            "Strategic": 0.4,
            "Technical": 0.3,
            "Comprehensive": 0.2,
            "Vision": 0.1,
        }
        mock_prompt_manager.return_value = mock_instance

        tool = EvaluationFrameworkTool()

        # Check that criteria were loaded successfully
        self.assertEqual(len(tool.criteria_weights), 4)
        self.assertEqual(tool.criteria_weights["Strategic"], 0.4)

    @patch("src.agents.tools.evaluation_framework.PromptManager")
    def test_load_framework_criteria_fallback(self, mock_prompt_manager):
        """Test fallback criteria when loading fails"""
        # Setup mock to raise exception
        mock_instance = Mock()
        mock_instance.extract_evaluation_criteria.side_effect = Exception("Load failed")
        mock_prompt_manager.return_value = mock_instance

        tool = EvaluationFrameworkTool()

        # Check that fallback criteria were used
        self.assertEqual(len(tool.criteria_weights), 4)
        self.assertIn("Strategic Prioritization", tool.criteria_weights)
        self.assertEqual(tool.criteria_weights["Strategic Prioritization"], 0.4)

    def test_apply_framework_exception_handling(self):
        """Test exception handling in _run method"""
        # Force an exception by providing invalid inputs
        with patch.object(
            self.tool, "_build_evaluation_prompt", side_effect=Exception("Build failed")
        ):
            result = self.tool._run(
                plan_name="Test Plan",
                plan_content="Test content",
                audit_context="Test context",
            )

            self.assertIsInstance(result, str)
            self.assertIn("Error", result)
            self.assertIn("Test Plan", result)

    def test_get_criteria_weights(self):
        """Test get_criteria_weights method"""
        weights = self.tool.get_criteria_weights()

        self.assertIsInstance(weights, dict)
        self.assertGreater(len(weights), 0)
        # Verify that weights sum approximately to 1.0
        total_weight = sum(weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=1)

    def test_criteria_weights_property(self):
        """Test criteria_weights property access"""
        weights = self.tool.criteria_weights

        self.assertIsInstance(weights, dict)
        self.assertGreater(len(weights), 0)
        # Test that it's the same as get_criteria_weights
        self.assertEqual(weights, self.tool.get_criteria_weights())


class TestGapAnalyzerTool(unittest.TestCase):
    """Test suite for GapAnalyzerTool"""

    def setUp(self):
        """Set up test fixtures"""
        self.tool = GapAnalyzerTool()

    def test_tool_initialization(self):
        """Test that gap analyzer tool initializes correctly"""
        self.assertEqual(self.tool.name, "gap_analyzer")
        self.assertIsNotNone(self.tool.description)

    def test_wcag_criteria_loading(self):
        """Test WCAG criteria are loaded correctly"""
        self.assertTrue(hasattr(self.tool, "wcag_criteria"))
        self.assertGreater(len(getattr(self.tool, "wcag_criteria", {})), 0)

    def test_identify_wcag_gaps_basic(self):
        """Test basic WCAG gap identification"""
        plan_content = "Test plan with some accessibility content"
        audit_content = "Test audit with accessibility issues"
        gaps = self.tool._identify_wcag_gaps(plan_content, audit_content)
        self.assertIsInstance(gaps, dict)

    def test_identify_strategic_gaps(self):
        """Test strategic gap identification"""
        coverage = {
            "total_issues": 10,
            "addressed_issues": 7,
            "partially_addressed": 2,
            "unaddressed_issues": ["Issue 1", "Issue 2"],
            "coverage_percentage": 70.0,
        }
        gaps = self.tool._identify_strategic_gaps(coverage)
        self.assertIsInstance(gaps, list)


class TestPlanComparatorTool(unittest.TestCase):
    """Test suite for PlanComparatorTool"""

    def setUp(self):
        """Set up test fixtures"""
        self.tool = PlanComparatorTool()

    def test_tool_initialization(self):
        """Test that plan comparator tool initializes correctly"""
        self.assertEqual(self.tool.name, "plan_comparator")
        self.assertIsNotNone(self.tool.description)

    def test_tool_run_basic_functionality(self):
        """Test basic plan comparison"""
        result = self.tool._run(
            plan_a_name="Plan A",
            plan_a_content="Plan A content",
            plan_b_name="Plan B",
            plan_b_content="Plan B content",
            comparison_criteria=["criteria1", "criteria2"],
        )
        self.assertIsInstance(result, str)


class TestScoringCalculatorTool(unittest.TestCase):
    """Test suite for ScoringCalculatorTool"""

    def setUp(self):
        """Set up test fixtures"""
        self.tool = ScoringCalculatorTool()

    def test_tool_initialization(self):
        """Test that scoring calculator tool initializes correctly"""
        self.assertEqual(self.tool.name, "scoring_calculator")
        self.assertIsNotNone(self.tool.description)

    def test_calculate_weighted_score_basic(self):
        """Test basic weighted score calculation"""
        scores = {"accessibility": 8.0, "usability": 7.0}
        weights = {"accessibility": 0.6, "usability": 0.4}

        result = self.tool._calculate_weighted_score(scores, weights)
        expected = (8.0 * 0.6) + (7.0 * 0.4)
        self.assertEqual(result, expected)

    def test_calculate_weighted_score_zero_weights(self):
        """Test weighted score calculation with zero weights"""
        scores = {"accessibility": 5.0}
        weights = {"accessibility": 0.0}

        result = self.tool._calculate_weighted_score(scores, weights)
        self.assertEqual(result, 0.0)

    def test_comparative_rankings(self):
        """Test comparative ranking generation"""
        scores = {"plan_a": 8.5, "plan_b": 7.0, "plan_c": 8.5}  # Tie with plan_a

        result = self.tool.calculate_comparative_rankings(scores)
        self.assertIsInstance(result, str)
        self.assertIn("plan_a", result)
        self.assertIn("plan_b", result)
        self.assertIn("plan_c", result)

    def test_assess_performance_level(self):
        """Test performance level assessment"""
        # Test different score ranges
        self.assertEqual(self.tool._assess_performance_level(9.5), "Exceptional")
        self.assertEqual(self.tool._assess_performance_level(8.0), "Strong")
        self.assertEqual(self.tool._assess_performance_level(6.0), "Adequate")
        self.assertEqual(self.tool._assess_performance_level(4.0), "Needs Improvement")


if __name__ == "__main__":
    unittest.main()
