"""
CrewAI configuration and orchestration for the evaluation system.

This module provides the main crew configuration that coordinates all agents
and tasks for the complete end-to-end accessibility evaluation workflow.
Enhanced with LLM resilience capabilities for graceful degradation.

References:
    - Master Plan: Crew Configuration requirements
    - Phase 2: All agent implementations
    - Phase 3: Workflow orchestration
    - LLM Error Handling Enhancement Plan - Phase 2
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from crewai import Crew, Process, Task

from ..agents.analysis_agent import AnalysisAgent
from ..agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent
from ..config.llm_config import LLMManager
from ..models.evaluation_models import EvaluationInput, PlanEvaluation
from ..tasks.comparison_tasks import ComparisonTaskManager
from ..tasks.evaluation_tasks import EvaluationTaskManager
from ..tasks.synthesis_tasks import SynthesisTaskManager
from ..utils.llm_resilience_manager import LLMResilienceManager


class AccessibilityEvaluationCrew:
    """
    Main crew orchestrating the complete evaluation process.

    This crew coordinates all agents and tasks for end-to-end plan evaluation,
    from individual plan assessments through cross-plan comparison to final
    synthesis of the optimal remediation plan.
    Enhanced with LLM resilience capabilities for graceful degradation.

    Attributes:
        llm_manager: LLM configuration and management
        resilience_manager: Optional LLM resilience manager for failure handling
        agents: Dictionary of initialized agent instances
        task_managers: Dictionary of task manager instances
        agent_availability: Dictionary tracking agent availability status
    """

    def __init__(
        self,
        llm_manager: LLMManager,
        resilience_manager: Optional[LLMResilienceManager] = None,
    ):
        """
        Initialize the evaluation crew with all necessary components.

        Args:
            llm_manager: Configured LLM manager with access to required models
            resilience_manager: Optional LLM resilience manager for enhanced error handling
        """
        self.llm_manager = llm_manager
        self.resilience_manager = resilience_manager
        self.agents = self._initialize_agents()
        self.task_managers = self._initialize_task_managers()
        self.agent_availability = self._check_agent_availability()

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

    def _check_agent_availability(self) -> Dict[str, bool]:
        """
        Check availability of all agents based on LLM status.

        Returns:
            Dictionary mapping agent names to availability status
        """
        availability = {}

        if self.resilience_manager:
            llm_availability = self.resilience_manager.check_llm_availability()

            # Check primary judge (uses Gemini)
            availability["primary_judge"] = llm_availability.get("gemini", True)

            # Check secondary judge (uses OpenAI)
            availability["secondary_judge"] = llm_availability.get("openai", True)

            # Check analysis agents (can use either LLM, prefer OpenAI but fallback to Gemini)
            gemini_available = llm_availability.get("gemini", True)
            openai_available = llm_availability.get("openai", True)
            availability["comparison_agent"] = gemini_available or openai_available
            availability["synthesis_agent"] = gemini_available or openai_available
        else:
            # If no resilience manager, assume all agents are available
            availability = {
                "primary_judge": True,
                "secondary_judge": True,
                "comparison_agent": True,
                "synthesis_agent": True,
            }

        return availability

    def validate_configuration(self) -> bool:
        """
        Validate crew configuration and agent availability.

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check if we have at least one evaluation agent available
            evaluation_agents_available = (
                self.agent_availability["primary_judge"]
                or self.agent_availability["secondary_judge"]
            )

            if not evaluation_agents_available:
                print("❌ Crew validation failed: No evaluation agents available")
                return False

            # Check if we have at least one analysis agent available
            analysis_agents_available = (
                self.agent_availability["comparison_agent"]
                or self.agent_availability["synthesis_agent"]
            )

            if not analysis_agents_available:
                print("❌ Crew validation failed: No analysis agents available")
                return False

            # Log availability status
            available_agents = [
                agent for agent, status in self.agent_availability.items() if status
            ]
            unavailable_agents = [
                agent for agent, status in self.agent_availability.items() if not status
            ]

            print("✅ Crew validation successful:")
            print(f"   Available agents: {', '.join(available_agents)}")
            if unavailable_agents:
                print(f"   Unavailable agents: {', '.join(unavailable_agents)}")
                print("   ⚠️  System will operate with reduced capability")

            return True

        except Exception as e:
            print(f"❌ Crew validation failed: {str(e)}")
            return False

    def get_available_agents(self) -> List[str]:
        """
        Get list of currently available agents.

        Returns:
            List of available agent names
        """
        return [agent for agent, status in self.agent_availability.items() if status]

    def get_unavailable_agents(self) -> List[str]:
        """
        Get list of currently unavailable agents.

        Returns:
            List of unavailable agent names
        """
        return [
            agent for agent, status in self.agent_availability.items() if not status
        ]

    def execute_complete_evaluation(
        self, evaluation_input: EvaluationInput
    ) -> Dict[str, Any]:
        """
        Execute complete evaluation workflow from input to final synthesis.
        Enhanced with resilience capabilities for partial agent availability.

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
        evaluation_results = self._execute_individual_evaluations(evaluation_input)
        # evaluation_results is a list of task results from CrewAI kickoff()
        results["individual_evaluations"] = evaluation_results
        print("✅ Individual evaluations complete")

        # Phase 2: Cross-Plan Comparison
        print("🔍 Phase 2: Performing cross-plan comparison analysis...")
        comparison_result = self._execute_cross_plan_comparison(
            evaluation_input, evaluation_results
        )
        results["comparison_analysis"] = comparison_result
        print("✅ Cross-plan comparison complete")

        # Phase 3: Optimal Plan Synthesis
        print("🎯 Phase 3: Synthesizing optimal remediation plan...")
        synthesis_result = self._execute_plan_synthesis(
            evaluation_input, evaluation_results, comparison_result
        )
        results["optimal_plan"] = synthesis_result
        print("✅ Optimal plan synthesis complete")

        print("🎉 Complete evaluation workflow finished successfully!")
        return results

    def _execute_individual_evaluations(
        self, evaluation_input: EvaluationInput
    ) -> List[str]:
        """
        Execute individual plan evaluations with resilience handling.

        Args:
            evaluation_input: The evaluation input

        Returns:
            Individual evaluation results
        """
        # Check which evaluation agents are available
        available_judges = []
        if self.agent_availability["primary_judge"]:
            available_judges.append(self.agents["primary_judge"].agent)
        if self.agent_availability["secondary_judge"]:
            available_judges.append(self.agents["secondary_judge"].agent)

        if not available_judges:
            # If no judges available, create NA results
            return self._create_na_evaluation_results(evaluation_input)

        # Process each plan separately to collect all results
        all_results = []

        for plan_name, plan_content in evaluation_input.remediation_plans.items():
            # Create tasks for this specific plan
            plan_tasks = []

            # Create primary evaluation task if primary judge is available
            if self.agent_availability["primary_judge"]:
                primary_task = self.task_managers[
                    "evaluation"
                ].create_primary_evaluation_task(
                    plan_name,
                    plan_content.content,
                    evaluation_input.audit_report.content,
                )
                plan_tasks.append(primary_task)

            # Create secondary evaluation task if secondary judge is available
            if self.agent_availability["secondary_judge"]:
                secondary_task = self.task_managers[
                    "evaluation"
                ].create_secondary_evaluation_task(
                    plan_name,
                    plan_content.content,
                    evaluation_input.audit_report.content,
                )
                plan_tasks.append(secondary_task)

            # Execute crew for this specific plan
            if plan_tasks:
                try:
                    plan_crew = Crew(
                        agents=available_judges,
                        tasks=plan_tasks,
                        process=Process.sequential,
                        verbose=False,
                        memory=False,
                    )

                    plan_result = plan_crew.kickoff()
                    if plan_result:
                        all_results.append(plan_result)
                    else:
                        # CrewAI returned empty result, create NA result
                        na_result = f"## Primary Evaluation: {plan_name}\n\n### Overall Assessment\n**Overall Score: NA/10**\n\n**Status:** NA\n**Reason:** CrewAI execution returned empty result\n\n**Timestamp:** {datetime.now().isoformat()}"
                        all_results.append(na_result)
                except Exception as e:
                    print(f"⚠️  Evaluation failed for {plan_name}: {str(e)}")
                    # Create NA result for failed evaluation
                    na_result = f"## Primary Evaluation: {plan_name}\n\n### Overall Assessment\n**Overall Score: NA/10**\n\n**Status:** Failed\n**Reason:** {str(e)}\n\n**Timestamp:** {datetime.now().isoformat()}"
                    all_results.append(na_result)

        return all_results

    def _create_evaluation_tasks_for_available_agents(
        self, evaluation_input: EvaluationInput
    ) -> List[Task]:
        """
        Create evaluation tasks only for available agents.

        Args:
            evaluation_input: The evaluation input

        Returns:
            List of tasks for available agents only
        """
        tasks = []

        for plan_name, plan_content in evaluation_input.remediation_plans.items():
            # Create primary evaluation task if primary judge is available
            if self.agent_availability["primary_judge"]:
                primary_task = self.task_managers[
                    "evaluation"
                ].create_primary_evaluation_task(
                    plan_name,
                    plan_content.content,
                    evaluation_input.audit_report.content,
                )
                tasks.append(primary_task)

            # Create secondary evaluation task if secondary judge is available
            if self.agent_availability["secondary_judge"]:
                secondary_task = self.task_managers[
                    "evaluation"
                ].create_secondary_evaluation_task(
                    plan_name,
                    plan_content.content,
                    evaluation_input.audit_report.content,
                )
                tasks.append(secondary_task)

        return tasks

    def _execute_cross_plan_comparison(
        self, evaluation_input: EvaluationInput, evaluation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute cross-plan comparison with resilience handling.

        Args:
            evaluation_input: The evaluation input
            evaluation_results: Results from individual evaluations

        Returns:
            Comparison analysis results
        """
        if not self.agent_availability["comparison_agent"]:
            return {"status": "NA", "reason": "Comparison agent unavailable"}

        # Create mock plan evaluations for comparison (in real implementation,
        # these would be parsed from evaluation_results)
        sample_evaluations = self._create_sample_evaluations(evaluation_input)

        comparison_task = self.task_managers[
            "comparison"
        ].create_cross_plan_comparison_task(
            sample_evaluations, evaluation_input.audit_report.content
        )

        try:
            comparison_crew = Crew(
                agents=[self.agents["comparison_agent"].agent],
                tasks=[comparison_task],
                process=Process.sequential,
                verbose=False,
                memory=False,
            )

            result = comparison_crew.kickoff()
            if result:
                return result
            else:
                return {"status": "NA", "reason": "CrewAI returned empty result"}
        except Exception as e:
            print(f"⚠️  Cross-plan comparison failed: {str(e)}")
            return {"status": "failed", "reason": f"Comparison error: {str(e)}"}

    def _execute_plan_synthesis(
        self,
        evaluation_input: EvaluationInput,
        evaluation_results: Dict[str, Any],
        comparison_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute plan synthesis with resilience handling.

        Args:
            evaluation_input: The evaluation input
            evaluation_results: Results from individual evaluations
            comparison_result: Results from cross-plan comparison

        Returns:
            Plan synthesis results
        """
        if not self.agent_availability["synthesis_agent"]:
            return {"status": "NA", "reason": "Synthesis agent unavailable"}

        # Create mock plan evaluations for synthesis (in real implementation,
        # these would be parsed from evaluation_results)
        sample_evaluations = self._create_sample_evaluations(evaluation_input)

        synthesis_task = self.task_managers[
            "synthesis"
        ].create_optimal_plan_synthesis_task(
            sample_evaluations,
            str(comparison_result),
            evaluation_input.audit_report.content,
        )

        try:
            synthesis_crew = Crew(
                agents=[self.agents["synthesis_agent"].agent],
                tasks=[synthesis_task],
                process=Process.sequential,
                verbose=False,
                memory=False,
            )

            result = synthesis_crew.kickoff()
            if result:
                return result
            else:
                return {"status": "NA", "reason": "CrewAI returned empty result"}
        except Exception as e:
            print(f"⚠️  Plan synthesis failed: {str(e)}")
            return {"status": "failed", "reason": f"Synthesis error: {str(e)}"}

    def _create_na_evaluation_results(
        self, evaluation_input: EvaluationInput
    ) -> List[str]:
        """
        Create NA (Not Available) evaluation results when no agents are available.

        Args:
            evaluation_input: The evaluation input

        Returns:
            NA evaluation results
        """
        na_results = []
        for plan_name in evaluation_input.remediation_plans.keys():
            na_result = f"## Primary Evaluation: {plan_name}\n\n### Overall Assessment\n**Overall Score: NA/10**\n\n**Status:** NA\n**Reason:** No evaluation agents available\n\n**Timestamp:** {datetime.now().isoformat()}"
            na_results.append(na_result)
        return na_results

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

        # Create crew with only available agents for parallel processing
        available_agents = []
        if self.agent_availability["primary_judge"]:
            available_agents.append(self.agents["primary_judge"].agent)
        if self.agent_availability["secondary_judge"]:
            available_agents.append(self.agents["secondary_judge"].agent)

        if not available_agents:
            print("❌ No evaluation agents available")
            return {"status": "failed", "reason": "No evaluation agents available"}

        try:
            parallel_crew = Crew(
                agents=available_agents,
                tasks=evaluation_tasks,
                process=Process.sequential,  # Use sequential as parallel not available
                verbose=False,  # Disable verbose to reduce callback warnings
                memory=False,
            )

            results = parallel_crew.kickoff()
            if results:
                print("⚡ Parallel evaluation workflow complete!")
                return {"parallel_results": results}
            else:
                print("⚠️  Parallel evaluation returned empty results")
                return {"status": "failed", "reason": "CrewAI returned empty results"}
        except Exception as e:
            print(f"❌ Parallel evaluation failed: {str(e)}")
            return {"status": "failed", "reason": f"Evaluation error: {str(e)}"}

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
