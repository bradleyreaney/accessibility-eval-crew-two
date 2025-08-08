"""
Test suite for Phase 2 agent implementation.
References: Master Plan - Testing Standards, Phase 2 - Agent Validation
"""

import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, patch

from src.agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent
from src.agents.scoring_agent import ScoringAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.tools.evaluation_framework import EvaluationFrameworkTool
from src.agents.tools.scoring_calculator import ScoringCalculatorTool
from src.agents.tools.gap_analyzer import GapAnalyzerTool
from src.agents.tools.plan_comparator import PlanComparatorTool
from src.config.llm_config import LLMManager


class TestAgentTools:
    """Test suite for agent tools"""
    
    def test_evaluation_framework_tool_initialization(self):
        """Test that evaluation framework tool initializes correctly"""
        tool = EvaluationFrameworkTool()
        assert tool.name == "evaluation_framework"
        assert "evaluation framework" in tool.description.lower()
        assert hasattr(tool, 'criteria_weights')
    
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
        assert hasattr(tool, 'wcag_criteria')
    
    def test_plan_comparator_tool_initialization(self):
        """Test that plan comparator tool initializes correctly"""
        tool = PlanComparatorTool()
        assert tool.name == "plan_comparator"
        assert "comparison" in tool.description.lower()
        assert hasattr(tool, 'comparison_dimensions')
    
    def test_evaluation_framework_tool_run(self):
        """Test evaluation framework tool execution"""
        tool = EvaluationFrameworkTool()
        
        result = tool._run(
            plan_name="TestPlan",
            plan_content="This is a test remediation plan with accessibility improvements.",
            audit_context="Test audit report with identified accessibility issues."
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
            "Long-term Vision": 7.0
        }
        
        criteria_weights = {
            "Strategic Prioritization": 0.4,
            "Technical Specificity": 0.3,
            "Comprehensiveness": 0.2,
            "Long-term Vision": 0.1
        }
        
        result = tool._run(criterion_scores, criteria_weights, "TestPlan")
        
        assert isinstance(result, str)
        assert "SCORING ANALYSIS" in result
        assert "TestPlan" in result
        assert "7.3" in result or "7.25" in result  # Expected weighted score
    
    def test_gap_analyzer_tool_run(self):
        """Test gap analyzer tool execution"""
        tool = GapAnalyzerTool()
        
        plan_content = "This plan addresses keyboard navigation and color contrast issues."
        audit_content = "Audit found violations in: keyboard navigation, color contrast, alt text, and heading structure."
        
        result = tool._run(plan_content, audit_content, "TestPlan")
        
        assert isinstance(result, str)
        assert "GAP ANALYSIS REPORT" in result
        assert "TestPlan" in result
    
    def test_plan_comparator_tool_run(self):
        """Test plan comparator tool execution"""
        tool = PlanComparatorTool()
        
        result = tool._run(
            plan_a_name="PlanA",
            plan_a_content="Comprehensive accessibility remediation with detailed timeline and testing procedures.",
            plan_b_name="PlanB", 
            plan_b_content="Focused accessibility fixes targeting critical issues first.",
            comparison_criteria=["scope", "timeline", "testing"]
        )
        
        assert isinstance(result, str)
        assert "COMPARATIVE ANALYSIS" in result
        assert "PlanA" in result
        assert "PlanB" in result


class TestJudgeAgents:
    """Test suite for judge agents"""
    
    @patch('src.config.llm_config.LLMManager')
    def test_primary_judge_agent_initialization(self, mock_llm_manager):
        """Test primary judge agent initialization"""
        mock_llm_manager.gemini = Mock()
        
        agent = PrimaryJudgeAgent(mock_llm_manager)
        
        assert agent.llm_manager == mock_llm_manager
        assert agent.agent is not None
        assert agent.agent.role == "Expert Accessibility Consultant - Primary Judge"
        assert "Strategic Prioritization" in agent.agent.goal
    
    @patch('src.config.llm_config.LLMManager')
    def test_secondary_judge_agent_initialization(self, mock_llm_manager):
        """Test secondary judge agent initialization"""
        mock_llm_manager.openai = Mock()
        
        agent = SecondaryJudgeAgent(mock_llm_manager)
        
        assert agent.llm_manager == mock_llm_manager
        assert agent.agent is not None
        assert agent.agent.role == "Expert Accessibility Consultant - Secondary Judge"
        assert "independent" in agent.agent.goal.lower()
    
    @patch('src.config.llm_config.LLMManager')
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
            audit_context="Test audit report content"
        )
        
        assert result['success'] is True
        assert result['plan_name'] == "PlanA"
        assert result['evaluator'] == "Primary Judge (Gemini Pro)"
        assert "Strategic Prioritization" in result['evaluation_content']
    
    @patch('src.config.llm_config.LLMManager')
    def test_secondary_judge_evaluation(self, mock_llm_manager):
        """Test secondary judge plan evaluation"""
        mock_response = Mock()
        mock_response.content = "Independent evaluation of PlanA with different perspective."
        
        mock_llm_manager.openai = Mock()
        mock_llm_manager.openai.invoke.return_value = mock_response
        
        agent = SecondaryJudgeAgent(mock_llm_manager)
        
        result = agent.evaluate_plan(
            plan_name="PlanA",
            plan_content="Test plan content",
            audit_context="Test audit context",
            primary_evaluation="Previous evaluation for comparison"
        )
        
        assert result['success'] is True
        assert result['plan_name'] == "PlanA"
        assert result['evaluator'] == "Secondary Judge (GPT-4)"
        assert result['includes_primary_comparison'] is True


class TestScoringAgent:
    """Test suite for scoring agent"""
    
    @patch('src.config.llm_config.LLMManager')
    def test_scoring_agent_initialization(self, mock_llm_manager):
        """Test scoring agent initialization"""
        mock_llm_manager.gemini = Mock()
        
        agent = ScoringAgent(mock_llm_manager)
        
        assert agent.llm_manager == mock_llm_manager
        assert agent.agent is not None
        assert "Scoring Specialist" in agent.agent.role
    
    @patch('src.config.llm_config.LLMManager')
    def test_calculate_final_scores(self, mock_llm_manager):
        """Test final score calculation"""
        mock_response = Mock()
        mock_response.content = "Comprehensive scoring analysis with rankings and recommendations."
        
        mock_llm_manager.gemini = Mock()
        mock_llm_manager.gemini.invoke.return_value = mock_response
        
        agent = ScoringAgent(mock_llm_manager)
        
        # Mock evaluations
        evaluations = [
            {
                'plan_name': 'PlanA',
                'success': True,
                'evaluation_content': 'Strategic: 8, Technical: 7, Comprehensive: 6, Vision: 7'
            },
            {
                'plan_name': 'PlanB', 
                'success': True,
                'evaluation_content': 'Strategic: 6, Technical: 8, Comprehensive: 7, Vision: 6'
            }
        ]
        
        criteria_weights = {
            'Strategic Prioritization': 0.4,
            'Technical Specificity': 0.3,
            'Comprehensiveness': 0.2,
            'Long-term Vision': 0.1
        }
        
        result = agent.calculate_final_scores(evaluations, criteria_weights)
        
        assert result['success'] is True
        assert 'scoring_method' in result
        assert 'plan_scores' in result
        assert 'rankings' in result


class TestAnalysisAgent:
    """Test suite for analysis agent"""
    
    @patch('src.config.llm_config.LLMManager')
    def test_analysis_agent_initialization(self, mock_llm_manager):
        """Test analysis agent initialization"""
        mock_llm_manager.openai = Mock()
        
        agent = AnalysisAgent(mock_llm_manager)
        
        assert agent.llm_manager == mock_llm_manager
        assert agent.agent is not None
        assert "Strategic" in agent.agent.role
    
    @patch('src.config.llm_config.LLMManager')
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
        
        evaluations = [{'plan_name': 'PlanA', 'success': True}]
        scoring_results = {'success': True, 'rankings': [('PlanA', 8.5)]}
        
        result = agent.generate_strategic_analysis(evaluations, scoring_results)
        
        assert result['success'] is True
        assert 'Strategic Implementation Analysis' in result['analysis_type']
        assert 'primary_recommendation' in result
    
    @patch('src.config.llm_config.LLMManager')
    def test_generate_executive_summary(self, mock_llm_manager):
        """Test executive summary generation"""
        mock_response = Mock()
        mock_response.content = "Executive Summary: Recommend PlanA for implementation with 6-month timeline."
        
        mock_llm_manager.openai = Mock()
        mock_llm_manager.openai.invoke.return_value = mock_response
        
        agent = AnalysisAgent(mock_llm_manager)
        
        analysis_data = {
            'evaluations': [{'plan_name': 'PlanA'}],
            'scoring': {'success': True},
            'strategic_analysis': {'success': True}
        }
        
        result = agent.generate_executive_summary(analysis_data)
        
        assert result['success'] is True
        assert result['summary_type'] == "Executive Decision Summary"


class TestAgentIntegration:
    """Integration tests for agent workflow"""
    
    @patch('src.config.llm_config.LLMManager')
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
        assert primary_eval['success'] is True
        
        # Step 2: Secondary evaluation 
        secondary_eval = secondary_judge.evaluate_plan(
            "PlanA", plan_content, audit_content, primary_eval['evaluation_content']
        )
        assert secondary_eval['success'] is True
        
        # Step 3: Scoring analysis
        evaluations = [primary_eval, secondary_eval]
        criteria_weights = {'Strategic Prioritization': 0.4, 'Technical Specificity': 0.3}
        
        scoring_results = scoring_agent.calculate_final_scores(evaluations, criteria_weights)
        assert scoring_results['success'] is True
        
        # Step 4: Strategic analysis
        strategic_analysis = analysis_agent.generate_strategic_analysis(evaluations, scoring_results)
        assert strategic_analysis['success'] is True
        
        # Verify workflow completion
        assert len(evaluations) == 2
        assert all(eval_data['success'] for eval_data in evaluations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
