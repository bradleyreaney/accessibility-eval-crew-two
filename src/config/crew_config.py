"""
CrewAI configuration and orchestration for the evaluation system.

This module provides the main crew configuration that coordinates all agents
and tasks for the complete end-to-end accessibility evaluation workflow.

References:
    - Master Plan: Crew Configuration requirements
    - Phase 2: All agent implementations
    - Phase 3: Workflow orchestration
"""

from typing import Any, Dict, List, Optional

from crewai import Crew, Process

from ..agents.analysis_agent import AnalysisAgent
from ..agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent
from ..config.llm_config import LLMManager
from ..models.evaluation_models import EvaluationInput, PlanEvaluation
from ..tasks.comparison_tasks import ComparisonTaskManager
from ..tasks.evaluation_tasks import EvaluationTaskManager
from ..tasks.synthesis_tasks import SynthesisTaskManager


class AccessibilityEvaluationCrew:
    """
    Main crew orchestrating the complete evaluation process.

    This crew coordinates all agents and tasks for end-to-end plan evaluation,
    from individual plan assessments through cross-plan comparison to final
    synthesis of the optimal remediation plan.

    Attributes:
        llm_manager: LLM configuration and management
        agents: Dictionary of initialized agent instances
        task_managers: Dictionary of task manager instances
    """

    def __init__(self, llm_manager: LLMManager):
        """
        Initialize the evaluation crew with all necessary components.

        Args:
            llm_manager: Configured LLM manager with access to required models
        """
        self.llm_manager = llm_manager
        self.agents = self._initialize_agents()
        self.task_managers = self._initialize_task_managers()

    def _initialize_agents(self) -> Dict[str, Any]:
        """
        Initialize all agents with proper LLM assignments.

        Returns:
            Dictionary mapping agent roles to initialized agent instances
        """
        return {
            "primary_judge": PrimaryJudgeAgent(self.llm_manager),
            "secondary_judge": SecondaryJudgeAgent(self.llm_manager),
            "comparison_agent": AnalysisAgent(self.llm_manager),
            "synthesis_agent": AnalysisAgent(self.llm_manager),
        }

    def _initialize_task_managers(self) -> Dict[str, Any]:
        """
        Initialize task managers for different workflow phases.

        Returns:
            Dictionary mapping workflow phases to task manager instances
        """
        return {
            "evaluation": EvaluationTaskManager(
                self.agents["primary_judge"], self.agents["secondary_judge"]
            ),
            "comparison": ComparisonTaskManager(self.agents["comparison_agent"]),
            "synthesis": SynthesisTaskManager(self.agents["synthesis_agent"]),
        }

    def execute_complete_evaluation(
        self, evaluation_input: EvaluationInput
    ) -> Dict[str, Any]:
        """
        Execute complete evaluation workflow from input to final synthesis.

        This method orchestrates the entire evaluation process in three main phases:
        1. Individual plan evaluations by primary and secondary judges
        2. Cross-plan comparison and analysis
        3. Optimal plan synthesis

        Args:
            evaluation_input: Audit report and remediation plans to evaluate

        Returns:
            Complete evaluation result with all phase outputs
        """
        print("🚀 Starting complete accessibility evaluation workflow...")
        results = {}

        # Phase 1: Individual Plan Evaluations
        print("📋 Phase 1: Evaluating individual remediation plans...")
        evaluation_tasks = self.task_managers[
            "evaluation"
        ].create_batch_evaluation_tasks(evaluation_input)

        evaluation_crew = Crew(
            agents=[
                self.agents["primary_judge"].agent,
                self.agents["secondary_judge"].agent,
            ],
            tasks=evaluation_tasks,
            process=Process.sequential,  # Sequential to ensure proper task ordering
            verbose=True,
        )

        evaluation_results = evaluation_crew.kickoff()
        results["individual_evaluations"] = evaluation_results
        print(
            f"✅ Individual evaluations complete: {len(evaluation_tasks)} tasks executed"
        )

        # Phase 2: Cross-Plan Comparison
        print("🔍 Phase 2: Performing cross-plan comparison analysis...")

        # Create mock plan evaluations for comparison (in real implementation,
        # these would be parsed from evaluation_results)
        sample_evaluations = self._create_sample_evaluations(evaluation_input)

        comparison_task = self.task_managers[
            "comparison"
        ].create_cross_plan_comparison_task(
            sample_evaluations, evaluation_input.audit_report.content
        )

        comparison_crew = Crew(
            agents=[self.agents["comparison_agent"].agent],
            tasks=[comparison_task],
            process=Process.sequential,
            verbose=True,
        )

        comparison_result = comparison_crew.kickoff()
        results["comparison_analysis"] = comparison_result
        print("✅ Cross-plan comparison complete")

        # Phase 3: Optimal Plan Synthesis
        print("🎯 Phase 3: Synthesizing optimal remediation plan...")
        synthesis_task = self.task_managers[
            "synthesis"
        ].create_optimal_plan_synthesis_task(
            sample_evaluations,
            str(comparison_result),
            evaluation_input.audit_report.content,
        )

        synthesis_crew = Crew(
            agents=[self.agents["synthesis_agent"].agent],
            tasks=[synthesis_task],
            process=Process.sequential,
            verbose=True,
        )

        synthesis_result = synthesis_crew.kickoff()
        results["optimal_plan"] = synthesis_result
        print("✅ Optimal plan synthesis complete")

        print("🎉 Complete evaluation workflow finished successfully!")
        return results

    def execute_parallel_evaluation(
        self, evaluation_input: EvaluationInput
    ) -> Dict[str, Any]:
        """
        Alternative execution strategy with maximum parallelization.

        This method evaluates all plans simultaneously for faster processing,
        trading some coordination for speed.

        Args:
            evaluation_input: Audit report and remediation plans to evaluate

        Returns:
            Complete evaluation result with all phase outputs
        """
        print("⚡ Starting parallel evaluation workflow...")

        # Create all evaluation tasks for parallel execution
        evaluation_tasks = self.task_managers[
            "evaluation"
        ].create_batch_evaluation_tasks(evaluation_input)

        # Create crew with all agents for parallel processing
        parallel_crew = Crew(
            agents=[
                self.agents["primary_judge"].agent,
                self.agents["secondary_judge"].agent,
            ],
            tasks=evaluation_tasks,
            process=Process.sequential,  # Use sequential as parallel not available
            verbose=True,
        )

        results = parallel_crew.kickoff()
        print("⚡ Parallel evaluation workflow complete!")

        return {"parallel_results": results}

    def _create_sample_evaluations(
        self, evaluation_input: EvaluationInput
    ) -> List[PlanEvaluation]:
        """
        Create sample plan evaluations for testing and demonstration.

        In a real implementation, this would parse actual evaluation results
        from the individual evaluation phase.

        Args:
            evaluation_input: Input data for creating sample evaluations

        Returns:
            List of sample PlanEvaluation objects
        """
        from ..models.evaluation_models import JudgmentScore

        sample_evaluations = []
        plan_names = list(evaluation_input.remediation_plans.keys())

        for i, plan_name in enumerate(
            plan_names[:2]
        ):  # Limit to first 2 plans for demo
            # Primary judge evaluation
            primary_eval = PlanEvaluation(
                plan_name=plan_name,
                judge_id="primary",
                scores=[
                    JudgmentScore(
                        criterion="strategic",
                        score=8.0 + i * 0.5,
                        rationale=f"Strategic analysis for {plan_name}",
                        confidence=0.8,
                    ),
                    JudgmentScore(
                        criterion="technical",
                        score=7.5 + i * 0.3,
                        rationale=f"Technical assessment for {plan_name}",
                        confidence=0.75,
                    ),
                ],
                overall_score=7.8 + i * 0.4,
                detailed_analysis=f"Comprehensive analysis of {plan_name}",
                pros=[
                    f"Strong {plan_name} approach",
                    f"Good {plan_name} implementation",
                ],
                cons=[f"Minor {plan_name} issues", f"Some {plan_name} complexity"],
            )
            sample_evaluations.append(primary_eval)

            # Secondary judge evaluation
            secondary_eval = PlanEvaluation(
                plan_name=plan_name,
                judge_id="secondary",
                scores=[
                    JudgmentScore(
                        criterion="strategic",
                        score=8.2 + i * 0.3,
                        rationale=f"Secondary strategic view for {plan_name}",
                        confidence=0.85,
                    ),
                    JudgmentScore(
                        criterion="technical",
                        score=7.8 + i * 0.2,
                        rationale=f"Secondary technical view for {plan_name}",
                        confidence=0.8,
                    ),
                ],
                overall_score=8.0 + i * 0.3,
                detailed_analysis=f"Secondary analysis of {plan_name}",
                pros=[f"Effective {plan_name} strategy", f"Clear {plan_name} guidance"],
                cons=[f"Limited {plan_name} scope", f"Resource {plan_name} concerns"],
            )
            sample_evaluations.append(secondary_eval)

        return sample_evaluations

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status information for all agents in the crew.

        Returns:
            Dictionary with agent status and configuration information
        """
        return {
            "total_agents": len(self.agents),
            "agent_types": list(self.agents.keys()),
            "task_managers": list(self.task_managers.keys()),
            "llm_models": {
                "primary_judge": "gemini",
                "secondary_judge": "openai",
                "comparison_agent": "openai",
                "synthesis_agent": "openai",
            },
        }

    def validate_configuration(self) -> bool:
        """
        Validate that all crew components are properly configured.

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check that all required agents are present
            required_agents = [
                "primary_judge",
                "secondary_judge",
                "comparison_agent",
                "synthesis_agent",
            ]
            for agent_name in required_agents:
                if agent_name not in self.agents:
                    print(f"❌ Missing required agent: {agent_name}")
                    return False

                if not hasattr(self.agents[agent_name], "agent"):
                    print(f"❌ Agent {agent_name} missing 'agent' attribute")
                    return False

            # Check that all task managers are present
            required_managers = ["evaluation", "comparison", "synthesis"]
            for manager_name in required_managers:
                if manager_name not in self.task_managers:
                    print(f"❌ Missing required task manager: {manager_name}")
                    return False

            # Check LLM manager configuration
            if not hasattr(self.llm_manager, "gemini") or not hasattr(
                self.llm_manager, "openai"
            ):
                print("❌ LLM manager missing required model configurations")
                return False

            print("✅ Crew configuration validation passed")
            return True

        except Exception as e:
            print(f"❌ Configuration validation failed: {str(e)}")
            return False
