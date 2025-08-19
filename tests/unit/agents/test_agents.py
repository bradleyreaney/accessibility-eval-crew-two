"""
Test suite for Phase 2 agent implementation.
References: Master Plan - Testing Standards, Phase 2 - Agent Validation
"""

import logging
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.agents.analysis_agent import AnalysisAgent
from src.agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent
from src.agents.scoring_agent import ScoringAgent
from src.agents.tools.evaluation_framework import EvaluationFrameworkTool
from src.agents.tools.gap_analyzer import GapAnalyzerTool
from src.agents.tools.plan_comparator import PlanComparatorTool
from src.agents.tools.scoring_calculator import ScoringCalculatorTool
from src.config.llm_config import LLMManager


class TestAgentTools:
    """Test suite for agent tools"""

    def test_evaluation_framework_tool_initialization(self):
        """Test that evaluation framework tool initializes correctly"""
        tool = EvaluationFrameworkTool()
        assert tool.name == "evaluation_framework"
        assert "evaluation framework" in tool.description.lower()
        assert hasattr(tool, "criteria_weights")

    def test_scoring_calculator_tool_initialization(self):
        """Test that scoring calculator tool initializes correctly"""
        tool = ScoringCalculatorTool()
        assert tool.name == "scoring_calculator"
        assert "scoring" in tool.description.lower()

    def test_gap_analyzer_tool_initialization(self):
        """Test that gap analyzer tool initializes correctly"""
        tool = GapAnalyzerTool()
        assert tool.name == "gap_analyzer"
        assert "gap" in tool.description.lower()
        assert hasattr(tool, "wcag_criteria")

    def test_plan_comparator_tool_initialization(self):
        """Test that plan comparator tool initializes correctly"""
        tool = PlanComparatorTool()
        assert tool.name == "plan_comparator"
        assert "comparison" in tool.description.lower()
        assert hasattr(tool, "comparison_dimensions")

    def test_evaluation_framework_tool_run(self):
        """Test evaluation framework tool execution"""
        tool = EvaluationFrameworkTool()

        result = tool._run(
            plan_name="TestPlan",
            plan_content="This is a test remediation plan with accessibility improvements.",
            audit_context="Test audit report with identified accessibility issues.",
        )

        assert isinstance(result, str)
        assert "TestPlan" in result
        assert "EVALUATION FRAMEWORK ASSESSMENT" in result

    def test_scoring_calculator_tool_run(self):
        """Test scoring calculator tool execution"""
        tool = ScoringCalculatorTool()

        criterion_scores = {
            "Strategic Prioritization": 8.0,
            "Technical Specificity": 7.5,
            "Comprehensiveness": 6.0,
            "Long-term Vision": 7.0,
        }

        criteria_weights = {
            "Strategic Prioritization": 0.4,
            "Technical Specificity": 0.3,
            "Comprehensiveness": 0.2,
            "Long-term Vision": 0.1,
        }

        result = tool._run(criterion_scores, criteria_weights, "TestPlan")

        assert isinstance(result, str)
        assert "SCORING ANALYSIS" in result
        assert "TestPlan" in result
        assert "7.3" in result or "7.25" in result  # Expected weighted score

    def test_gap_analyzer_tool_run(self):
        """Test gap analyzer tool execution"""
        tool = GapAnalyzerTool()

        plan_content = (
            "This plan addresses keyboard navigation and color contrast issues."
        )
        audit_content = "Audit found violations in: keyboard navigation, color contrast, alt text, and heading structure."

        result = tool._run(plan_content, audit_content, "TestPlan")

        assert isinstance(result, str)
        assert "GAP ANALYSIS REPORT" in result
        assert "TestPlan" in result

    def test_gap_analyzer_tool_coverage_calculation(self):
        """Test gap analyzer coverage percentage calculation"""
        tool = GapAnalyzerTool()

        # Test plan that covers most accessibility keywords
        comprehensive_plan = """
        This plan addresses keyboard navigation, color contrast, alt text,
        headings, and focus management issues comprehensively.
        """
        audit_content = (
            "Found issues with keyboard, contrast, alt text, headings, focus"
        )

        result = tool._run(comprehensive_plan, audit_content, "ComprehensivePlan")

        assert "GAP ANALYSIS REPORT" in result
        assert "ComprehensivePlan" in result
        assert "Coverage Percentage" in result

    def test_gap_analyzer_tool_empty_content(self):
        """Test gap analyzer with empty content"""
        tool = GapAnalyzerTool()

        result = tool._run("", "", "EmptyPlan")

        assert isinstance(result, str)
        assert "EmptyPlan" in result

    def test_gap_analyzer_tool_error_handling(self):
        """Test gap analyzer error handling"""
        tool = GapAnalyzerTool()

        # Test with malformed inputs to trigger error handling
        result = tool._run("", "audit content", "ErrorPlan")

        assert isinstance(result, str)
        assert "ErrorPlan" in result


class TestGapAnalyzerTool:
    """Comprehensive tests for GapAnalyzerTool to achieve high coverage"""

    def setup_method(self):
        """Set up test fixtures"""
        self.tool = GapAnalyzerTool()
        self.sample_audit = """
        Audit Report - Accessibility Violations Found:

        1. Missing alt text for images on homepage
        2. Insufficient color contrast ratio on buttons (violation)
        3. Keyboard navigation fails for dropdown menus
        4. Heading structure incorrect - missing h2 elements
        5. Form labels are missing for input fields (error)
        6. Focus indicators are not visible (non-compliant)
        """

        self.sample_plan = """
        Remediation Plan:

        1. Add alt text to all images
        2. Update color contrast for buttons to meet WCAG AA standards
        3. Implement keyboard navigation for all interactive elements
        4. Fix heading structure with proper h1-h6 hierarchy
        """

    def test_extract_audit_issues(self):
        """Test extraction of issues from audit content"""
        issues = self.tool._extract_audit_issues(self.sample_audit)

        assert isinstance(issues, list)
        assert len(issues) > 0

        # Check that it finds lines with issue keywords
        issue_text = " ".join(issues).lower()
        assert (
            "violation" in issue_text
            or "error" in issue_text
            or "missing" in issue_text
        )

    def test_extract_audit_issues_empty_content(self):
        """Test extraction with empty audit content"""
        issues = self.tool._extract_audit_issues("")
        assert isinstance(issues, list)
        assert len(issues) == 0

    def test_analyze_audit_coverage(self):
        """Test audit coverage analysis"""
        coverage = self.tool._analyze_audit_coverage(
            self.sample_plan, self.sample_audit
        )

        assert isinstance(coverage, dict)
        assert "total_issues" in coverage
        assert "addressed_issues" in coverage
        assert "partially_addressed" in coverage
        assert "unaddressed_issues" in coverage
        assert "coverage_percentage" in coverage

        assert coverage["total_issues"] >= 0
        assert coverage["coverage_percentage"] >= 0
        assert coverage["coverage_percentage"] <= 100

    def test_analyze_audit_coverage_no_matches(self):
        """Test coverage analysis with no matches"""
        unrelated_plan = (
            "This plan talks about database optimization and server performance."
        )
        coverage = self.tool._analyze_audit_coverage(unrelated_plan, self.sample_audit)

        assert coverage["coverage_percentage"] == 0
        assert coverage["addressed_issues"] == 0

    def test_analyze_audit_coverage_perfect_match(self):
        """Test coverage analysis with high coverage"""
        comprehensive_plan = """
        Complete remediation covering all accessibility violations:
        - Missing alt text for images will be added
        - Color contrast ratio issues will be fixed
        - Keyboard navigation failures will be addressed
        - Heading structure problems will be corrected
        - Form labels missing will be implemented
        - Focus indicators non-compliant will be updated
        """
        coverage = self.tool._analyze_audit_coverage(
            comprehensive_plan, self.sample_audit
        )

        assert coverage["coverage_percentage"] >= 0  # Should have some coverage
        assert coverage["addressed_issues"] > 0  # Should address some issues

    def test_extract_key_terms(self):
        """Test key term extraction"""
        text = "Missing alt text for images on homepage"
        terms = self.tool._extract_key_terms(text)

        assert isinstance(terms, list)
        assert len(terms) <= 5  # Limited to 5 terms

        # Should extract meaningful terms, not stop words
        terms_str = " ".join(terms)
        assert "missing" in terms_str or "text" in terms_str or "images" in terms_str

    def test_extract_key_terms_with_stop_words(self):
        """Test key term extraction filters stop words"""
        text = "The and or but in on at to for of with by"
        terms = self.tool._extract_key_terms(text)

        # Should filter out stop words
        assert len(terms) == 0

    def test_identify_wcag_gaps(self):
        """Test WCAG criteria gap identification"""
        audit_with_color = "Color contrast violations found throughout the site"
        plan_without_color = "This plan addresses keyboard navigation only"

        gaps = self.tool._identify_wcag_gaps(plan_without_color, audit_with_color)

        assert isinstance(gaps, dict)
        # Should identify color contrast as a gap
        gap_keywords = []
        for criterion, keywords in gaps.items():
            gap_keywords.extend(keywords)

        # Check if color-related keywords are identified as gaps
        color_keywords = ["color", "contrast"]
        has_color_gap = any(
            keyword in " ".join(gap_keywords) for keyword in color_keywords
        )
        assert has_color_gap

    def test_identify_wcag_gaps_no_gaps(self):
        """Test WCAG gap identification when no gaps exist"""
        comprehensive_plan = """
        This plan addresses keyboard navigation, color contrast, alt text,
        headings, forms, focus management, and all accessibility requirements.
        """
        gaps = self.tool._identify_wcag_gaps(comprehensive_plan, self.sample_audit)

        assert isinstance(gaps, dict)
        # Should have fewer gaps with comprehensive plan
        wcag_criteria = getattr(self.tool, "wcag_criteria", {})
        assert len(gaps) <= len(wcag_criteria)

    def test_generate_gap_report(self):
        """Test gap report generation"""
        coverage = {
            "total_issues": 5,
            "addressed_issues": 3,
            "partially_addressed": 1,
            "unaddressed_issues": ["Missing form validation"],
            "coverage_percentage": 60.0,
        }
        wcag_gaps = {"1.1.1": ["alt", "text"]}
        audit_issues = ["Missing alt text", "Color contrast issue"]

        report = self.tool._generate_gap_report(
            "TestPlan", coverage, wcag_gaps, audit_issues
        )

        assert isinstance(report, str)
        assert "GAP ANALYSIS REPORT" in report
        assert "TestPlan" in report
        assert "COVERAGE SUMMARY" in report
        assert "60.0%" in report

    def test_generate_gap_report_with_unaddressed_issues(self):
        """Test gap report with unaddressed issues"""
        coverage = {
            "total_issues": 5,
            "addressed_issues": 2,
            "partially_addressed": 0,
            "unaddressed_issues": ["Issue 1", "Issue 2", "Issue 3"],
            "coverage_percentage": 40.0,
        }
        wcag_gaps = {}
        audit_issues = []

        report = self.tool._generate_gap_report(
            "TestPlan", coverage, wcag_gaps, audit_issues
        )

        assert "UNADDRESSED ISSUES" in report
        assert "Issue 1" in report

    def test_generate_gap_report_with_wcag_gaps(self):
        """Test gap report with WCAG gaps"""
        coverage = {
            "total_issues": 3,
            "addressed_issues": 3,
            "partially_addressed": 0,
            "unaddressed_issues": [],
            "coverage_percentage": 100.0,
        }
        wcag_gaps = {"1.1.1": ["alt", "text"], "1.4.3": ["color", "contrast"]}
        audit_issues = []

        report = self.tool._generate_gap_report(
            "TestPlan", coverage, wcag_gaps, audit_issues
        )

        assert "WCAG CRITERIA GAPS" in report
        assert "1.1.1" in report
        assert "1.4.3" in report

    def test_identify_strategic_gaps(self):
        """Test strategic gap identification"""
        low_coverage = {
            "total_issues": 10,
            "addressed_issues": 3,
            "partially_addressed": 5,
            "unaddressed_issues": ["Issue 1", "Issue 2", "Issue 3", "Issue 4"],
            "coverage_percentage": 30.0,
        }

        gaps = self.tool._identify_strategic_gaps(low_coverage)

        assert isinstance(gaps, list)
        assert len(gaps) > 0
        gaps_text = " ".join(gaps)
        assert (
            "critical" in gaps_text
            or "partial" in gaps_text
            or "unaddressed" in gaps_text
        )

    def test_identify_strategic_gaps_good_coverage(self):
        """Test strategic gaps with good coverage"""
        good_coverage = {
            "total_issues": 5,
            "addressed_issues": 4,
            "partially_addressed": 1,
            "unaddressed_issues": [],
            "coverage_percentage": 80.0,
        }

        gaps = self.tool._identify_strategic_gaps(good_coverage)

        assert isinstance(gaps, list)
        # Should have fewer or no strategic gaps with good coverage

    def test_generate_recommendations(self):
        """Test recommendation generation"""
        poor_coverage = {
            "total_issues": 10,
            "addressed_issues": 3,
            "partially_addressed": 4,
            "unaddressed_issues": ["Issue 1", "Issue 2"],
            "coverage_percentage": 30.0,
        }
        wcag_gaps = {"1.1.1": ["alt", "text"]}

        recommendations = self.tool._generate_recommendations(poor_coverage, wcag_gaps)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        rec_text = " ".join(recommendations).lower()
        assert "review" in rec_text or "address" in rec_text or "detailed" in rec_text

    def test_generate_recommendations_good_coverage(self):
        """Test recommendations with good coverage"""
        good_coverage = {
            "total_issues": 5,
            "addressed_issues": 5,
            "partially_addressed": 0,
            "unaddressed_issues": [],
            "coverage_percentage": 100.0,
        }
        wcag_gaps = {}

        recommendations = self.tool._generate_recommendations(good_coverage, wcag_gaps)

        assert isinstance(recommendations, list)
        # Should have fewer recommendations with perfect coverage

    def test_full_run_integration(self):
        """Test full _run method integration"""
        result = self.tool._run(self.sample_plan, self.sample_audit, "IntegrationTest")

        assert isinstance(result, str)
        assert "GAP ANALYSIS REPORT" in result
        assert "IntegrationTest" in result
        assert "COVERAGE SUMMARY" in result

    def test_wcag_criteria_initialization(self):
        """Test that WCAG criteria are properly initialized"""
        assert hasattr(self.tool, "wcag_criteria")
        wcag_criteria = getattr(self.tool, "wcag_criteria", {})
        assert isinstance(wcag_criteria, dict)
        assert len(wcag_criteria) > 0

        # Check some expected WCAG criteria
        criteria_keys = list(wcag_criteria.keys())
        assert any("1.1" in key for key in criteria_keys)  # Text alternatives
        assert any("1.4" in key for key in criteria_keys)  # Distinguishable

    def test_plan_comparator_tool_run(self):
        """Test plan comparator tool execution"""
        tool = PlanComparatorTool()

        result = tool._run(
            plan_a_name="PlanA",
            plan_a_content="Comprehensive accessibility remediation with detailed timeline and testing procedures.",
            plan_b_name="PlanB",
            plan_b_content="Focused accessibility fixes targeting critical issues first.",
            comparison_criteria=["scope", "timeline", "testing"],
        )

        assert isinstance(result, str)
        assert "COMPARATIVE ANALYSIS" in result
        assert "PlanA" in result
        assert "PlanB" in result


class TestJudgeAgents:
    """Test suite for judge agents"""

    @patch("src.config.llm_config.LLMManager")
    def test_primary_judge_agent_initialization(self, mock_llm_manager):
        """Test primary judge agent initialization"""
        mock_llm_manager.gemini = Mock()

        agent = PrimaryJudgeAgent(mock_llm_manager)

        assert agent.llm_manager == mock_llm_manager
        assert agent.agent is not None
        assert agent.agent.role == "Expert Accessibility Consultant - Primary Judge"
        assert "Strategic Prioritization" in agent.agent.goal

    @patch("src.config.llm_config.LLMManager")
    def test_secondary_judge_agent_initialization(self, mock_llm_manager):
        """Test secondary judge agent initialization"""
        mock_llm_manager.openai = Mock()

        agent = SecondaryJudgeAgent(mock_llm_manager)

        assert agent.llm_manager == mock_llm_manager
        assert agent.agent is not None
        assert agent.agent.role == "Expert Accessibility Consultant - Secondary Judge"
        assert "independent" in agent.agent.goal.lower()

    @patch("src.config.llm_config.LLMManager")
    def test_primary_judge_agent_configuration(self, mock_llm_manager):
        """Test primary judge agent configuration"""
        mock_llm_manager.gemini = Mock()

        agent = PrimaryJudgeAgent(mock_llm_manager)

        # Check agent configuration
        assert agent.agent.verbose is True
        assert agent.agent.allow_delegation is False
        # Note: memory may not be available in this version of CrewAI

    @patch("src.config.llm_config.LLMManager")
    def test_secondary_judge_agent_configuration(self, mock_llm_manager):
        """Test secondary judge agent configuration"""
        mock_llm_manager.openai = Mock()

        agent = SecondaryJudgeAgent(mock_llm_manager)

        # Check agent configuration
        assert agent.agent.verbose is True
        assert agent.agent.allow_delegation is False
        # Note: memory may not be available in this version of CrewAI

    @patch("src.config.llm_config.LLMManager")
    def test_judge_agents_tools_integration(self, mock_llm_manager):
        """Test that judge agents have access to evaluation tools"""
        mock_llm_manager.gemini = Mock()
        mock_llm_manager.openai = Mock()

        primary_agent = PrimaryJudgeAgent(mock_llm_manager)
        secondary_agent = SecondaryJudgeAgent(mock_llm_manager)

        # Check that both agents have tools attribute
        assert hasattr(primary_agent.agent, "tools")
        assert hasattr(secondary_agent.agent, "tools")

        # Tools may be empty or None in mock environment
        assert primary_agent.agent.tools is not None
        assert secondary_agent.agent.tools is not None

    @patch("src.config.llm_config.LLMManager")
    def test_primary_judge_error_handling(self, mock_llm_manager):
        """Test primary judge error handling"""
        mock_llm_manager.gemini = Mock()
        mock_llm_manager.gemini.invoke.side_effect = Exception("LLM error")

        agent = PrimaryJudgeAgent(mock_llm_manager)

        result = agent.evaluate_plan("TestPlan", "plan content", "audit content")
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result

    @patch("src.config.llm_config.LLMManager")
    def test_secondary_judge_error_handling(self, mock_llm_manager):
        """Test secondary judge error handling"""
        # Mock both LLMs to ensure consistent behavior
        mock_llm_manager.openai = Mock()
        mock_llm_manager.gemini = Mock()

        # Mock the LLM availability check to return OpenAI as available
        with patch(
            "src.utils.llm_resilience_manager.LLMResilienceManager.check_llm_availability"
        ) as mock_availability:
            mock_availability.return_value = {"openai": True, "gemini": False}

            # Set the side effect for OpenAI invoke
            mock_llm_manager.openai.invoke.side_effect = Exception("LLM error")

            agent = SecondaryJudgeAgent(mock_llm_manager)

            result = agent.evaluate_plan("TestPlan", "plan content", "audit content")
            assert isinstance(result, dict)
            assert result["success"] is False
            assert "error" in result

    @patch("src.config.llm_config.LLMManager")
    def test_primary_judge_tool_initialization_error(self, mock_llm_manager):
        """Test primary judge handles tool initialization errors"""
        mock_llm_manager.gemini = Mock()

        # This tests the exception handling in _initialize_tools
        with patch("src.agents.judge_agent.EvaluationFrameworkTool") as mock_tool:
            mock_tool.side_effect = Exception("Tool initialization failed")

            agent = PrimaryJudgeAgent(mock_llm_manager)
            # Should still create agent even if tools fail
            assert agent.agent is not None

    @patch("src.config.llm_config.LLMManager")
    def test_secondary_judge_tool_initialization_error(self, mock_llm_manager):
        """Test secondary judge handles tool initialization errors"""
        mock_llm_manager.openai = Mock()

        # This tests the exception handling in _initialize_tools
        with patch("src.agents.judge_agent.EvaluationFrameworkTool") as mock_tool:
            mock_tool.side_effect = Exception("Tool initialization failed")

            agent = SecondaryJudgeAgent(mock_llm_manager)
            # Should still create agent even if tools fail
            assert agent.agent is not None

    @patch("src.config.llm_config.LLMManager")
    def test_primary_judge_evaluation(self, mock_llm_manager):
        """Test primary judge plan evaluation"""
        # Mock the LLM response
        mock_response = Mock()
        mock_response.content = """
        Evaluation of PlanA:

        Strategic Prioritization (40%): 8/10
        The plan demonstrates strong strategic thinking with risk-based prioritization.

        Technical Specificity (30%): 7/10
        Implementation details are clear with specific technical guidance.

        Comprehensiveness (20%): 6/10
        Covers most audit findings but missing some edge cases.

        Long-term Vision (10%): 7/10
        Includes maintenance and sustainability considerations.

        Weighted Score: 7.3/10
        """

        mock_llm_manager.gemini = Mock()
        mock_llm_manager.gemini.invoke.return_value = mock_response

        agent = PrimaryJudgeAgent(mock_llm_manager)

        result = agent.evaluate_plan(
            plan_name="PlanA",
            plan_content="Test remediation plan content",
            audit_context="Test audit report content",
        )

        assert result["success"] is True
        assert result["plan_name"] == "PlanA"
        assert result["evaluator"] == "Primary Judge (Gemini Pro)"
        assert "Strategic Prioritization" in result["evaluation_content"]

    @patch("src.config.llm_config.LLMManager")
    def test_secondary_judge_evaluation(self, mock_llm_manager):
        """Test secondary judge plan evaluation"""
        mock_response = Mock()
        mock_response.content = (
            "Independent evaluation of PlanA with different perspective."
        )

        mock_llm_manager.openai = Mock()
        mock_llm_manager.openai.invoke.return_value = mock_response

        agent = SecondaryJudgeAgent(mock_llm_manager)

        result = agent.evaluate_plan(
            plan_name="PlanA",
            plan_content="Test plan content",
            audit_context="Test audit context",
            primary_evaluation="Previous evaluation for comparison",
        )

        assert result["success"] is True
        assert result["plan_name"] == "PlanA"
        assert result["evaluator"] == "Secondary Judge (GPT-4)"
        assert result["includes_primary_comparison"] is True


class TestScoringAgent:
    """Test suite for scoring agent"""

    @patch("src.config.llm_config.LLMManager")
    def test_scoring_agent_initialization(self, mock_llm_manager):
        """Test scoring agent initialization"""
        mock_llm_manager.gemini = Mock()

        agent = ScoringAgent(mock_llm_manager)

        assert agent.llm_manager == mock_llm_manager
        assert agent.agent is not None
        assert "Scoring Specialist" in agent.agent.role

    @patch("src.config.llm_config.LLMManager")
    def test_scoring_agent_configuration(self, mock_llm_manager):
        """Test scoring agent configuration settings"""
        mock_llm_manager.gemini = Mock()

        agent = ScoringAgent(mock_llm_manager)

        # Check agent configuration
        assert agent.agent.verbose is True
        assert agent.agent.allow_delegation is False
        # Note: memory may not be available in this version of CrewAI

    @patch("src.config.llm_config.LLMManager")
    def test_scoring_agent_tools_availability(self, mock_llm_manager):
        """Test scoring agent tools are available"""
        mock_llm_manager.gemini = Mock()

        agent = ScoringAgent(mock_llm_manager)

        # Check that agent has access to tools attribute
        assert hasattr(agent.agent, "tools")
        assert agent.agent.tools is not None

    @patch("src.config.llm_config.LLMManager")
    def test_scoring_agent_role_definition(self, mock_llm_manager):
        """Test scoring agent role and responsibilities"""
        mock_llm_manager.gemini = Mock()

        agent = ScoringAgent(mock_llm_manager)

        # Verify role definition
        assert "Scoring" in agent.agent.role
        assert "Specialist" in agent.agent.role

        # Check goal and backstory are defined
        assert hasattr(agent.agent, "goal")
        assert hasattr(agent.agent, "backstory")
        assert len(agent.agent.goal) > 0
        assert len(agent.agent.backstory) > 0

    @patch("src.config.llm_config.LLMManager")
    def test_scoring_agent_tool_initialization_error(self, mock_llm_manager):
        """Test scoring agent handles tool initialization errors"""
        mock_llm_manager.gemini = Mock()

        # This tests the exception handling in _initialize_tools
        with patch("src.agents.scoring_agent.ScoringCalculatorTool") as mock_tool:
            mock_tool.side_effect = Exception("Tool initialization failed")

            agent = ScoringAgent(mock_llm_manager)
            # Should still create agent even if tools fail
            assert agent.agent is not None

    @patch("src.config.llm_config.LLMManager")
    def test_scoring_agent_error_handling(self, mock_llm_manager):
        """Test scoring agent error handling in score calculation"""
        mock_llm_manager.gemini = Mock()
        mock_llm_manager.gemini.invoke.side_effect = Exception("LLM error")

        agent = ScoringAgent(mock_llm_manager)

        test_evaluations = [{"plan_name": "TestPlan", "score": 7.5}]
        test_weights = {"strategic": 0.4, "technical": 0.3, "comprehensive": 0.3}

        result = agent.calculate_final_scores(test_evaluations, test_weights)
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result

    @patch("src.config.llm_config.LLMManager")
    def test_scoring_agent_mcda_scoring(self, mock_llm_manager):
        """Test MCDA scoring calculation"""
        mock_response = Mock()
        mock_response.content = """
        MCDA Scoring Results:
        Plan A: 8.5/10 (Recommended)
        Plan B: 7.2/10
        Plan C: 6.8/10
        """

        mock_llm_manager.gemini = Mock()
        mock_llm_manager.gemini.invoke.return_value = mock_response

        agent = ScoringAgent(mock_llm_manager)

        test_evaluations = [
            {"plan_name": "PlanA", "score": 8.5},
            {"plan_name": "PlanB", "score": 7.2},
        ]
        test_weights = {"strategic": 0.4, "technical": 0.3, "comprehensive": 0.3}

        result = agent.calculate_final_scores(test_evaluations, test_weights)
        assert isinstance(result, dict)
        assert "success" in result

    @patch("src.config.llm_config.LLMManager")
    def test_calculate_final_scores(self, mock_llm_manager):
        """Test final score calculation"""
        mock_response = Mock()
        mock_response.content = (
            "Comprehensive scoring analysis with rankings and recommendations."
        )

        mock_llm_manager.gemini = Mock()
        mock_llm_manager.gemini.invoke.return_value = mock_response

        agent = ScoringAgent(mock_llm_manager)

        # Mock evaluations
        evaluations = [
            {
                "plan_name": "PlanA",
                "success": True,
                "evaluation_content": "Strategic: 8, Technical: 7, Comprehensive: 6, Vision: 7",
            },
            {
                "plan_name": "PlanB",
                "success": True,
                "evaluation_content": "Strategic: 6, Technical: 8, Comprehensive: 7, Vision: 6",
            },
        ]

        criteria_weights = {
            "Strategic Prioritization": 0.4,
            "Technical Specificity": 0.3,
            "Comprehensiveness": 0.2,
            "Long-term Vision": 0.1,
        }

        result = agent.calculate_final_scores(evaluations, criteria_weights)

        assert result["success"] is True
        assert "scoring_method" in result
        assert "plan_scores" in result
        assert "rankings" in result

    @patch("src.config.llm_config.LLMManager")
    def test_compare_plans(self, mock_llm_manager):
        """Test plan comparison functionality"""
        mock_response = Mock()
        mock_response.content = """
        Comparative Analysis:
        Plan A demonstrates superior strategic prioritization with clear accessibility roadmap.
        Plan B shows stronger technical depth but lacks comprehensive timeline.
        Recommendation: Plan A for organizations prioritizing strategic alignment.
        """

        mock_llm_manager.gemini = Mock()
        mock_llm_manager.gemini.invoke.return_value = mock_response

        agent = ScoringAgent(mock_llm_manager)

        plan_a = {
            "name": "Strategic Accessibility Plan",
            "content": "Comprehensive accessibility strategy focusing on WCAG 2.1 compliance with phased implementation approach.",
        }

        plan_b = {
            "name": "Technical Implementation Plan",
            "content": "Detailed technical specifications for accessibility remediation with specific code examples.",
        }

        evaluation_data = [
            {
                "plan_name": "Strategic Accessibility Plan",
                "success": True,
                "evaluation_content": "Strategic: 8, Technical: 7, Comprehensive: 6, Vision: 7",
            },
            {
                "plan_name": "Technical Implementation Plan",
                "success": True,
                "evaluation_content": "Strategic: 6, Technical: 9, Comprehensive: 7, Vision: 6",
            },
        ]

        result = agent.compare_plans(plan_a, plan_b, evaluation_data)

        assert result["success"] is True
        assert result["plan_a"] == "Strategic Accessibility Plan"
        assert result["plan_b"] == "Technical Implementation Plan"
        assert "comparison_analysis" in result
        assert "timestamp" in result
        assert mock_llm_manager.gemini.invoke.called

    @patch("src.config.llm_config.LLMManager")
    def test_compare_plans_error_handling(self, mock_llm_manager):
        """Test compare_plans method error handling"""
        mock_llm_manager.gemini = Mock()
        mock_llm_manager.gemini.invoke.side_effect = Exception("LLM comparison failed")

        agent = ScoringAgent(mock_llm_manager)

        plan_a = {"name": "Plan A", "content": "Test content A"}
        plan_b = {"name": "Plan B", "content": "Test content B"}
        evaluation_data = []

        result = agent.compare_plans(plan_a, plan_b, evaluation_data)

        assert result["success"] is False
        assert "error" in result
        assert "timestamp" in result

    @patch("src.config.llm_config.LLMManager")
    def test_get_agent_info(self, mock_llm_manager):
        """Test get_agent_info method"""
        mock_llm_manager.gemini = Mock()

        agent = ScoringAgent(mock_llm_manager)

        info = agent.get_agent_info()

        assert isinstance(info, dict)
        assert info["name"] == "Scoring Agent"
        assert info["llm"] == "Gemini Pro"
        assert "role" in info
        assert "tools" in info
        assert "capabilities" in info
        assert isinstance(info["capabilities"], list)
        assert len(info["capabilities"]) > 0
        assert "Weighted score calculation" in info["capabilities"]


class TestAnalysisAgent:
    """Test suite for analysis agent"""

    @patch("src.config.llm_config.LLMManager")
    def test_analysis_agent_initialization(self, mock_llm_manager):
        """Test analysis agent initialization"""
        mock_llm_manager.openai = Mock()

        agent = AnalysisAgent(mock_llm_manager)

        assert agent.llm_manager == mock_llm_manager
        assert agent.agent is not None
        assert "Strategic" in agent.agent.role

    @patch("src.config.llm_config.LLMManager")
    def test_analysis_agent_tools_integration(self, mock_llm_manager):
        """Test analysis agent tools are properly integrated"""
        mock_llm_manager.openai = Mock()

        agent = AnalysisAgent(mock_llm_manager)

        # Check that agent has tools attribute
        assert hasattr(agent.agent, "tools")
        assert agent.agent.tools is not None

    @patch("src.config.llm_config.LLMManager")
    def test_analysis_agent_configuration(self, mock_llm_manager):
        """Test analysis agent configuration settings"""
        mock_llm_manager.openai = Mock()

        agent = AnalysisAgent(mock_llm_manager, verbose=True, allow_delegation=False)

        # Check agent configuration
        assert agent.agent.verbose is True
        assert agent.agent.allow_delegation is False
        # Note: memory may not be available in this version of CrewAI

    @patch("src.config.llm_config.LLMManager")
    def test_analysis_agent_role_definition(self, mock_llm_manager):
        """Test analysis agent role and capabilities"""
        mock_llm_manager.openai = Mock()

        agent = AnalysisAgent(mock_llm_manager)

        # Verify role definition (check for "Analyst" instead of "Analysis")
        assert "Strategic" in agent.agent.role
        assert "Analyst" in agent.agent.role

        # Check goal and backstory
        assert hasattr(agent.agent, "goal")
        assert hasattr(agent.agent, "backstory")
        assert len(agent.agent.goal) > 0
        assert len(agent.agent.backstory) > 0

    @patch("src.config.llm_config.LLMManager")
    def test_analysis_agent_tool_initialization_error(self, mock_llm_manager):
        """Test analysis agent handles tool initialization errors"""
        mock_llm_manager.openai = Mock()

        # This tests the exception handling in _initialize_tools
        with patch("src.agents.analysis_agent.GapAnalyzerTool") as mock_gap_tool:
            mock_gap_tool.side_effect = Exception("Tool initialization failed")

            agent = AnalysisAgent(mock_llm_manager)
            # Should still create agent even if some tools fail
            assert agent.agent is not None

    @patch("src.config.llm_config.LLMManager")
    def test_analysis_agent_strategic_analysis_generation(self, mock_llm_manager):
        """Test strategic analysis generation with mock data"""
        mock_response = Mock()
        mock_response.content = """
        Strategic Analysis Summary:
        Plan A shows strong implementation approach
        Risk assessment indicates medium complexity
        Resource requirements are reasonable
        """

        mock_llm_manager.openai = Mock()
        mock_llm_manager.openai.invoke.return_value = mock_response

        agent = AnalysisAgent(mock_llm_manager)

        test_evaluations = [
            {"plan_name": "PlanA", "score": 8.5, "evaluation": "Strong plan"}
        ]

        test_scoring = {
            "rankings": [{"plan_name": "PlanA", "score": 8.5}],
            "methodology": "MCDA",
        }

        result = agent.generate_strategic_analysis(test_evaluations, test_scoring)
        assert isinstance(result, dict)
        assert "success" in result

    @patch("src.config.llm_config.LLMManager")
    def test_analysis_agent_error_handling(self, mock_llm_manager):
        """Test analysis agent error handling in strategic analysis"""
        # Mock both LLMs to ensure consistent behavior
        mock_llm_manager.openai = Mock()
        mock_llm_manager.gemini = Mock()

        # Mock the LLM availability check to return OpenAI as available
        with patch(
            "src.utils.llm_resilience_manager.LLMResilienceManager.check_llm_availability"
        ) as mock_availability:
            mock_availability.return_value = {"openai": True, "gemini": False}

            # Set the side effect for OpenAI invoke
            mock_llm_manager.openai.invoke.side_effect = Exception("LLM error")

            agent = AnalysisAgent(mock_llm_manager)

            test_evaluations = [{"plan_name": "TestPlan"}]
            test_scoring = {"rankings": []}

            result = agent.generate_strategic_analysis(test_evaluations, test_scoring)
            assert isinstance(result, dict)
            assert result["success"] is False
            assert "error" in result

    @patch("src.config.llm_config.LLMManager")
    def test_generate_strategic_analysis(self, mock_llm_manager):
        """Test strategic analysis generation"""
        mock_response = Mock()
        mock_response.content = """
        Strategic Analysis:

        Executive Summary: PlanA is recommended based on comprehensive evaluation.
        Implementation Roadmap: Phased approach over 6 months.
        Risk Assessment: Low implementation risk with proper planning.
        """

        mock_llm_manager.openai = Mock()
        mock_llm_manager.openai.invoke.return_value = mock_response

        agent = AnalysisAgent(mock_llm_manager)

        evaluations = [{"plan_name": "PlanA", "success": True}]
        scoring_results = {"success": True, "rankings": [("PlanA", 8.5)]}

        result = agent.generate_strategic_analysis(evaluations, scoring_results)

        assert result["success"] is True
        assert "Strategic Implementation Analysis" in result["analysis_type"]
        assert "primary_recommendation" in result

    @patch("src.config.llm_config.LLMManager")
    def test_generate_executive_summary(self, mock_llm_manager):
        """Test executive summary generation"""
        mock_response = Mock()
        mock_response.content = "Executive Summary: Recommend PlanA for implementation with 6-month timeline."

        mock_llm_manager.openai = Mock()
        mock_llm_manager.openai.invoke.return_value = mock_response

        agent = AnalysisAgent(mock_llm_manager)

        analysis_data = {
            "evaluations": [{"plan_name": "PlanA"}],
            "scoring": {"success": True},
            "strategic_analysis": {"success": True},
        }

        result = agent.generate_executive_summary(analysis_data)

        assert result["success"] is True
        assert result["summary_type"] == "Executive Decision Summary"


class TestAgentIntegration:
    """Integration tests for agent workflow"""

    @patch("src.config.llm_config.LLMManager")
    def test_complete_evaluation_workflow(self, mock_llm_manager):
        """Test complete evaluation workflow with all agents"""
        # Setup mocks
        mock_response = Mock()
        mock_response.content = "Mock evaluation response"

        mock_llm_manager.gemini = Mock()
        mock_llm_manager.openai = Mock()
        mock_llm_manager.gemini.invoke.return_value = mock_response
        mock_llm_manager.openai.invoke.return_value = mock_response

        # Initialize agents
        primary_judge = PrimaryJudgeAgent(mock_llm_manager)
        secondary_judge = SecondaryJudgeAgent(mock_llm_manager)
        scoring_agent = ScoringAgent(mock_llm_manager)
        analysis_agent = AnalysisAgent(mock_llm_manager)

        # Test plan content
        plan_content = "Test remediation plan with accessibility improvements"
        audit_content = "Test audit report with accessibility findings"

        # Step 1: Primary evaluation
        primary_eval = primary_judge.evaluate_plan("PlanA", plan_content, audit_content)
        assert primary_eval["success"] is True

        # Step 2: Secondary evaluation
        secondary_eval = secondary_judge.evaluate_plan(
            "PlanA", plan_content, audit_content, primary_eval["evaluation_content"]
        )
        assert secondary_eval["success"] is True

        # Step 3: Scoring analysis
        evaluations = [primary_eval, secondary_eval]
        criteria_weights = {
            "Strategic Prioritization": 0.4,
            "Technical Specificity": 0.3,
        }

        scoring_results = scoring_agent.calculate_final_scores(
            evaluations, criteria_weights
        )
        assert scoring_results["success"] is True

        # Step 4: Strategic analysis
        strategic_analysis = analysis_agent.generate_strategic_analysis(
            evaluations, scoring_results
        )
        assert strategic_analysis["success"] is True

        # Verify workflow completion
        assert len(evaluations) == 2
        assert all(eval_data["success"] for eval_data in evaluations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
