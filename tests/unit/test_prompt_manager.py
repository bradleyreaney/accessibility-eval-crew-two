"""
Tests for prompt manager functionality
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from src.tools.prompt_manager import PromptManager


class TestPromptManager:
    """Test evaluation framework integration"""

    def test_prompt_loading_from_file(self, sample_eval_prompt):
        """Test prompt loading functionality"""
        with patch("builtins.open", mock_open(read_data=sample_eval_prompt)):
            manager = PromptManager(Path("test_prompt.md"))
            assert hasattr(manager, "base_prompt")
            assert len(manager.base_prompt) > 0
            assert "### PERSONA" in manager.base_prompt

    def test_prompt_loading_file_not_found(self):
        """Test error handling for missing prompt file"""
        with pytest.raises(FileNotFoundError):
            PromptManager(Path("nonexistent.md"))

    def test_validate_prompt_structure(self, sample_eval_prompt):
        """Test prompt structure validation"""
        with patch("builtins.open", mock_open(read_data=sample_eval_prompt)):
            manager = PromptManager(Path("test_prompt.md"))
            missing = manager.validate_prompt_structure()
            assert len(missing) == 0  # All required sections present

    def test_validate_prompt_structure_missing_sections(self):
        """Test detection of missing sections"""
        incomplete_prompt = "### PERSONA\nOnly persona section"

        with patch("builtins.open", mock_open(read_data=incomplete_prompt)):
            manager = PromptManager(Path("test_prompt.md"))
            missing = manager.validate_prompt_structure()
            assert len(missing) > 0
            assert "### CORE TASK" in missing

    def test_extract_evaluation_criteria(self, sample_eval_prompt):
        """Test extraction of weighted criteria"""
        with patch("builtins.open", mock_open(read_data=sample_eval_prompt)):
            manager = PromptManager(Path("test_prompt.md"))
            criteria = manager.extract_evaluation_criteria()

            assert "Strategic Prioritization" in criteria
            assert "Technical Specificity & Correctness" in criteria
            assert "Comprehensiveness & Structure" in criteria
            assert "Long-Term Vision" in criteria

            # Check weights are correct
            assert criteria["Strategic Prioritization"] == 0.4
            assert criteria["Technical Specificity & Correctness"] == 0.3

    def test_prepare_judge_prompt(self, sample_eval_prompt):
        """Test prompt preparation with content injection"""
        with patch("builtins.open", mock_open(read_data=sample_eval_prompt)):
            manager = PromptManager(Path("test_prompt.md"))

            audit_content = "Detailed audit findings..."
            plans = {"PlanA": "Plan A content"}

            result = manager.prepare_judge_prompt(audit_content, plans)

            assert audit_content in result
            assert "Plan A content" in result

    def test_extract_evaluation_criteria_error_handling(self):
        """Test criteria extraction with malformed content"""
        malformed_prompt = "### PERSONA\nNo criteria here\n### TASK\nStill no criteria"

        with patch("builtins.open", mock_open(read_data=malformed_prompt)):
            manager = PromptManager(Path("test_prompt.md"))
            criteria = manager.extract_evaluation_criteria()
            # Should return empty dict if no criteria found
            assert isinstance(criteria, dict)

    def test_load_evaluation_framework_file_error(self):
        """Test error handling when loading framework file"""
        with patch("builtins.open", side_effect=IOError("Read error")):
            with pytest.raises(ValueError, match="Failed to load evaluation prompt"):
                PromptManager(Path("test_prompt.md"))

    def test_extract_evaluation_criteria_alternative_patterns(self):
        """Test criteria extraction with alternative patterns"""
        alt_prompt = """
        ### PERSONA
        You are an expert

        ### EVALUATION
        40% Strategic Prioritization: Important factor
        30% Technical Details: Another factor
        """

        with patch("builtins.open", mock_open(read_data=alt_prompt)):
            manager = PromptManager(Path("test_prompt.md"))
            criteria = manager.extract_evaluation_criteria()
            assert isinstance(criteria, dict)

    def test_get_plan_sections_edge_cases(self):
        """Test plan section extraction edge cases"""
        prompt_with_plans = """
        #### Plan A: First plan
        #### PlanB: Second plan
        #### Plan C: Third plan
        """

        with patch("builtins.open", mock_open(read_data=prompt_with_plans)):
            manager = PromptManager(Path("test_prompt.md"))
            sections = manager.get_plan_sections()
            assert isinstance(sections, list)

    def test_get_prompt_length_and_preview(self, sample_eval_prompt):
        """Test prompt length and preview functionality"""
        with patch("builtins.open", mock_open(read_data=sample_eval_prompt)):
            manager = PromptManager(Path("test_prompt.md"))

            # Test length
            length = manager.get_prompt_length()
            assert length > 0
            assert isinstance(length, int)

            # Test preview
            preview = manager.get_prompt_preview(100)
            assert len(preview) <= 103  # 100 + "..."
            assert isinstance(preview, str)

    def test_get_plan_sections(self, sample_eval_prompt):
        """Test extraction of plan sections"""
        with patch("builtins.open", mock_open(read_data=sample_eval_prompt)):
            manager = PromptManager(Path("test_prompt.md"))
            plans = manager.get_plan_sections()
            # Should match either "Plan A" or "PlanA" format
            assert "PlanA" in plans or "Plan A" in plans

    def test_get_prompt_preview(self, sample_eval_prompt):
        """Test prompt preview functionality"""
        with patch("builtins.open", mock_open(read_data=sample_eval_prompt)):
            manager = PromptManager(Path("test_prompt.md"))
            preview = manager.get_prompt_preview(100)
            assert len(preview) <= 103  # 100 + "..."
            assert preview.endswith("...") or len(sample_eval_prompt) <= 100


class TestPromptManagerIntegration:
    """Integration tests with real prompt file"""

    @pytest.mark.integration
    def test_load_real_evaluation_prompt(self):
        """Test loading the actual evaluation prompt"""
        prompt_path = Path("promt/eval-prompt.md")

        if prompt_path.exists():
            manager = PromptManager(prompt_path)
            assert len(manager.base_prompt) > 1000

            # Test structure validation
            missing = manager.validate_prompt_structure()
            assert len(missing) == 0, f"Missing sections: {missing}"

            # Test criteria extraction
            criteria = manager.extract_evaluation_criteria()
            assert len(criteria) > 0, "No evaluation criteria found"
        else:
            pytest.skip("Real evaluation prompt not available")
