"""
Tests for evaluation models
"""

import pytest

from src.models.evaluation_models import (
    DocumentContent,
    EvaluationCriteria,
    EvaluationInput,
    JudgmentScore,
    PlanEvaluation,
    PlanType,
)


class TestDocumentContent:
    """Test DocumentContent model"""

    def test_document_content_creation(self):
        """Test creating DocumentContent with valid data"""
        doc = DocumentContent(
            title="Test Document",
            content="Sample content",
            page_count=5,
            metadata={"author": "Test Author"},
        )

        assert doc.title == "Test Document"
        assert doc.content == "Sample content"
        assert doc.page_count == 5
        assert doc.metadata["author"] == "Test Author"


class TestEvaluationCriteria:
    """Test EvaluationCriteria model"""

    def test_evaluation_criteria_defaults(self):
        """Test default evaluation criteria weights"""
        criteria = EvaluationCriteria()

        assert criteria.strategic_prioritization_weight == 0.40
        assert criteria.technical_specificity_weight == 0.30
        assert criteria.comprehensiveness_weight == 0.20
        assert criteria.long_term_vision_weight == 0.10

    def test_evaluation_criteria_validation(self):
        """Test weight validation"""
        # Valid weights
        criteria = EvaluationCriteria(
            strategic_prioritization_weight=0.5,
            technical_specificity_weight=0.3,
            comprehensiveness_weight=0.15,
            long_term_vision_weight=0.05,
        )

        # Should not raise validation error during creation
        assert criteria.strategic_prioritization_weight == 0.5

    def test_evaluation_criteria_invalid_weights(self):
        """Test invalid weight values"""
        with pytest.raises(ValueError):
            EvaluationCriteria(strategic_prioritization_weight=1.5)

        with pytest.raises(ValueError):
            EvaluationCriteria(technical_specificity_weight=-0.1)

    def test_weights_sum_validation(self):
        """Test weights sum validation method"""
        # Valid sum
        criteria = EvaluationCriteria()
        criteria.validate_weights_sum()  # Should not raise

        # Invalid sum
        criteria_invalid = EvaluationCriteria(
            strategic_prioritization_weight=0.5,
            technical_specificity_weight=0.5,
            comprehensiveness_weight=0.2,
            long_term_vision_weight=0.2,
        )

        with pytest.raises(ValueError, match="must sum to 1.0"):
            criteria_invalid.validate_weights_sum()


class TestPlanType:
    """Test PlanType enum"""

    def test_plan_type_values(self):
        """Test all plan type values"""
        assert PlanType.PLAN_A == "PlanA"
        assert PlanType.PLAN_B == "PlanB"
        assert PlanType.PLAN_G == "PlanG"

        # Test all values exist
        expected_plans = [f"Plan{letter}" for letter in "ABCDEFG"]
        actual_plans = [plan.value for plan in PlanType]
        assert all(plan in actual_plans for plan in expected_plans)


class TestEvaluationInput:
    """Test EvaluationInput model"""

    def test_evaluation_input_creation(self, sample_audit_content, sample_plan_content):
        """Test creating evaluation input with valid data"""
        eval_input = EvaluationInput(
            audit_report=sample_audit_content,
            remediation_plans={"PlanA": sample_plan_content},
        )

        assert eval_input.audit_report == sample_audit_content
        assert "PlanA" in eval_input.remediation_plans
        assert isinstance(eval_input.evaluation_criteria, EvaluationCriteria)

    def test_evaluation_input_invalid_plan_names(
        self, sample_audit_content, sample_plan_content
    ):
        """Test validation of plan names"""
        with pytest.raises(ValueError, match="Invalid plan name"):
            EvaluationInput(
                audit_report=sample_audit_content,
                remediation_plans={"InvalidPlan": sample_plan_content},
            )


class TestJudgmentScore:
    """Test JudgmentScore model"""

    def test_judgment_score_creation(self):
        """Test creating judgment score with valid data"""
        score = JudgmentScore(
            criterion="Strategic Prioritization",
            score=8.5,
            rationale="Well-structured approach",
            confidence=0.9,
        )

        assert score.criterion == "Strategic Prioritization"
        assert score.score == 8.5
        assert score.rationale == "Well-structured approach"
        assert score.confidence == 0.9

    def test_judgment_score_validation(self):
        """Test score validation constraints"""
        # Valid score
        JudgmentScore(criterion="Test", score=5.0, rationale="Test", confidence=0.5)

        # Invalid score (too high)
        with pytest.raises(ValueError):
            JudgmentScore(
                criterion="Test", score=11.0, rationale="Test", confidence=0.5
            )

        # Invalid confidence (too low)
        with pytest.raises(ValueError):
            JudgmentScore(
                criterion="Test", score=5.0, rationale="Test", confidence=-0.1
            )


class TestPlanEvaluation:
    """Test PlanEvaluation model"""

    def test_plan_evaluation_creation(self):
        """Test creating plan evaluation with valid data"""
        scores = [
            JudgmentScore(
                criterion="Strategic Prioritization",
                score=8.0,
                rationale="Good prioritization",
                confidence=0.8,
            )
        ]

        evaluation = PlanEvaluation(
            plan_name="PlanA",
            judge_id="gemini",
            scores=scores,
            overall_score=8.0,
            detailed_analysis="Comprehensive analysis...",
            pros=["Well structured"],
            cons=["Could be more detailed"],
        )

        assert evaluation.plan_name == "PlanA"
        assert evaluation.judge_id == "gemini"
        assert len(evaluation.scores) == 1
        assert evaluation.overall_score == 8.0
        assert len(evaluation.pros) == 1
        assert len(evaluation.cons) == 1
        assert evaluation.timestamp  # Should be auto-generated
