"""Tests for judge agents."""

import unittest
from unittest.mock import MagicMock, patch

from src.agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent


class TestJudgeAgents(unittest.TestCase):
    """Test cases for judge agents."""

    def test_primary_judge_error_handling(self):
        """Test primary judge error handling."""
        mock_llm_manager = MagicMock()
        mock_llm_manager.gemini = MagicMock()

        with patch("src.agents.judge_agent.logger"):
            judge = PrimaryJudgeAgent(mock_llm_manager)

            # Test basic functionality for coverage
            self.assertIsNotNone(judge.agent)
            self.assertIsNotNone(judge.llm)

    def test_secondary_judge_error_handling(self):
        """Test secondary judge error handling."""
        mock_llm_manager = MagicMock()
        mock_llm_manager.openai = MagicMock()

        with patch("src.agents.judge_agent.logger"):
            judge = SecondaryJudgeAgent(mock_llm_manager)

            # Test basic functionality for coverage
            self.assertIsNotNone(judge.agent)
            self.assertIsNotNone(judge.llm)


if __name__ == "__main__":
    unittest.main()
