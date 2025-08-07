# Phase 2: Core Agent Development
*Week 2 Implementation Plan*

**← [Phase 1: Foundation](./phase-1-foundation.md)** | **[Phase 3: Workflow →](./phase-3-workflow.md)**

## Overview

Phase 2 focuses on implementing the core CrewAI agents that will perform the **evaluation, comparison, and scoring** of accessibility remediation plans. This phase builds on the foundation established in Phase 1 and creates the intelligent judge agents that form the heart of the LLM as a Judge system.

## Prerequisites

- [x] **Phase 1 Complete**: Foundation components working (PDF parsing, LLM connections, prompt management)
- [x] **API Access**: Confirmed working connections to Gemini Pro and GPT-4
- [x] **Data Processing**: Ability to load audit reports and remediation plans
- [x] **Evaluation Framework**: `promt/eval-prompt.md` integration validated

## Objectives

- [x] **Judge Agents**: Implement primary and secondary evaluation agents
- [x] **Scoring Agent**: Comparative analysis and weighted scoring
- [x] **Analysis Agent**: Head-to-head comparison and gap analysis  
- [x] **Agent Tools**: Custom tools for evaluation, scoring, and comparative analysis
- [x] **Integration Testing**: Validate agent interactions and scoring consistency
- [x] **Agent Documentation**: API references, examples, and Copilot prompts for agent development

## Deliverables

### 2.1 Judge Agent Implementation

#### Primary Judge Agent - Gemini Pro (`src/agents/judge_agent.py`)
```python
"""
Primary evaluation agent using Gemini Pro
References: Master Plan - Agent Specifications, Phase 1 - LLM Integration
"""
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, List
from ..tools.evaluation_framework import EvaluationFrameworkTool
from ..tools.scoring_calculator import ScoringCalculatorTool
from ..tools.gap_analyzer import GapAnalyzerTool

class PrimaryJudgeAgent:
    """
    Expert accessibility consultant using Gemini Pro for primary evaluation
    Follows evaluation framework from promt/eval-prompt.md exactly
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the primary judge agent with proper configuration"""
        return Agent(
            role="Expert Accessibility Consultant - Primary Judge",
            goal="""Provide comprehensive evaluation of remediation plans using the 
                   established framework from promt/eval-prompt.md with weighted criteria:
                   - Strategic Prioritization (40%)
                   - Technical Specificity (30%) 
                   - Comprehensiveness (20%)
                   - Long-term Vision (10%)""",
            backstory="""You are a senior accessibility consultant with deep expertise in 
                        WCAG 2.1/2.2 standards, practical remediation experience, and 
                        strategic thinking. You evaluate remediation plans not just for 
                        technical correctness, but for strategic coherence, efficiency, 
                        and real-world impact on users with disabilities. You think like 
                        a senior developer, project manager, and user advocate simultaneously.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[
                EvaluationFrameworkTool(),
                ScoringCalculatorTool(),
                GapAnalyzerTool()
            ]
        )
    
    def evaluate_plan(self, plan_name: str, plan_content: str, audit_context: str) -> Dict:
        """
        Evaluate a single remediation plan using the established framework
        
        Args:
            plan_name: Name of the plan (e.g., "PlanA")
            plan_content: Full text content of the remediation plan
            audit_context: Original accessibility audit report
            
        Returns:
            Structured evaluation following eval-prompt.md format
        """
        evaluation_prompt = f"""
        You are evaluating {plan_name} for accessibility remediation effectiveness.
        
        CONTEXT (Original Audit):
        {audit_context}
        
        PLAN TO EVALUATE ({plan_name}):
        {plan_content}
        
        EVALUATION REQUIREMENTS:
        Follow the exact evaluation framework from promt/eval-prompt.md:
        
        1. **Strategic Prioritization (40%)**:
           - Assess logic and rationale behind task sequencing
           - Evaluate synthesis of prioritization models (user impact, architectural leverage, effort, risk)
           - Check prioritization of critical user paths and high-impact issues
           - Provide specific examples of strengths and weaknesses
        
        2. **Technical Specificity (30%)**:
           - Evaluate clarity, accuracy, and actionability of technical solutions
           - Check if solutions are specific enough for developer implementation
           - Assess technical soundness and modern web development alignment
        
        3. **Comprehensiveness (20%)**:
           - Verify all audit violations are addressed
           - Assess plan structure and multi-disciplinary team usability
           - Check connection of fixes to POUR principles
        
        4. **Long-Term Vision (10%)**:
           - Review post-remediation verification provisions
           - Assess understanding of accessibility as continuous process
        
        OUTPUT FORMAT:
        Provide your evaluation in this exact structure:
        
        ## Evaluation of {plan_name}
        
        ### Strategic Prioritization (Weight: 40%)
        **Score: [X.X/10]**
        [Detailed analysis with specific examples]
        
        ### Technical Specificity (Weight: 30%)
        **Score: [X.X/10]**
        [Detailed analysis with specific examples]
        
        ### Comprehensiveness (Weight: 20%)
        **Score: [X.X/10]**
        [Detailed analysis with specific examples]
        
        ### Long-Term Vision (Weight: 10%)
        **Score: [X.X/10]**
        [Detailed analysis with specific examples]
        
        ### Overall Assessment
        **Overall Score: [X.X/10]**
        **Key Strengths:**
        - [List 2-3 key strengths]
        
        **Key Weaknesses:**
        - [List 2-3 key weaknesses]
        
        **Rationale:** [Brief summary of scoring reasoning]
        """
        
        # Execute evaluation through CrewAI agent
        result = self.agent.execute_task(evaluation_prompt)
        return self._parse_evaluation_result(result)
    
    def _parse_evaluation_result(self, raw_result: str) -> Dict:
        """Parse the agent's evaluation into structured format"""
        # Implementation to extract scores and analysis from response
        # Returns structured dictionary for further processing
        pass

class SecondaryJudgeAgent:
    """
    Secondary evaluation agent using GPT-4 for cross-validation
    Identical evaluation framework for consensus building
    """
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create secondary judge agent with identical evaluation criteria"""
        return Agent(
            role="Expert Accessibility Consultant - Secondary Judge",
            goal="""Provide independent evaluation for cross-validation using the same 
                   framework from promt/eval-prompt.md. Focus on technical implementation 
                   and user experience perspectives to complement primary judge.""",
            backstory="""You are an accessibility expert with complementary expertise 
                        focusing on technical implementation and user experience. You use 
                        identical evaluation criteria as the primary judge but bring a 
                        different perspective to ensure comprehensive assessment. Your role 
                        is crucial for consensus building and validation.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[
                EvaluationFrameworkTool(),
                ScoringCalculatorTool(),
                TechnicalValidatorTool()
            ]
        )
    
    def evaluate_plan(self, plan_name: str, plan_content: str, audit_context: str) -> Dict:
        """
        Provide independent evaluation using identical framework
        Implementation mirrors PrimaryJudgeAgent.evaluate_plan()
        """
        # Similar implementation to primary judge
        # Ensures consistent evaluation approach
        pass
```

### 2.2 Comparison Agent Implementation

#### Cross-Plan Comparison Agent (`src/agents/comparison_agent.py`)
```python
"""
Agent for performing head-to-head comparisons between remediation plans
References: Master Plan - Agent Architecture, Phase 1 - Data Models
"""
from crewai import Agent
from typing import Dict, List, Tuple
from ..models.evaluation_models import PlanEvaluation, ComparisonResult

class ComparisonAgent:
    """
    Performs detailed head-to-head comparisons between remediation plans
    Identifies relative strengths, weaknesses, and trade-offs
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create comparison agent specialized in cross-plan analysis"""
        return Agent(
            role="Accessibility Strategy Comparison Analyst",
            goal="""Perform detailed head-to-head comparisons between remediation plans,
                   identifying relative strengths, weaknesses, and strategic trade-offs.
                   Create comprehensive pros/cons analysis and comparative scoring.""",
            backstory="""You are an expert in strategic analysis and comparison of 
                        accessibility approaches. You excel at identifying the relative 
                        merits of different strategies, understanding trade-offs, and 
                        providing clear comparative insights that help decision-makers 
                        understand the differences between approaches.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[
                ComparisonAnalysisTool(),
                ProConsAnalyzerTool(),
                TradeoffIdentifierTool()
            ]
        )
    
    def compare_plans(self, 
                     evaluations: List[PlanEvaluation], 
                     audit_context: str) -> ComparisonResult:
        """
        Perform comprehensive comparison of all evaluated plans
        
        Args:
            evaluations: List of individual plan evaluations from judges
            audit_context: Original audit report for context
            
        Returns:
            Structured comparison with pros/cons and recommendations
        """
        comparison_prompt = f"""
        You are comparing {len(evaluations)} accessibility remediation plans based on 
        their detailed evaluations. Your task is to provide a comprehensive comparative 
        analysis that will inform the creation of an optimal synthesis plan.
        
        CONTEXT (Original Audit):
        {audit_context}
        
        PLAN EVALUATIONS:
        {self._format_evaluations_for_comparison(evaluations)}
        
        COMPARISON REQUIREMENTS:
        
        1. **Head-to-Head Analysis**: Create detailed comparison table showing:
           - Strategic Prioritization scores and approaches
           - Technical Specificity levels and examples
           - Comprehensiveness coverage
           - Long-term Vision provisions
        
        2. **Pros and Cons Summary**: For each plan, identify:
           - Top 3 unique strengths
           - Top 3 significant weaknesses
           - Best use cases or scenarios
        
        3. **Trade-off Analysis**: Identify key trade-offs between plans:
           - Speed vs. thoroughness
           - Technical complexity vs. implementation ease
           - Short-term fixes vs. long-term strategy
           - Resource requirements vs. impact
        
        4. **Gap Analysis**: Identify what's missing from ALL plans:
           - Overlooked accessibility issues
           - Missing implementation details
           - Absent process considerations
           - Lack of stakeholder considerations
        
        OUTPUT FORMAT:
        ## Comprehensive Plan Comparison
        
        ### Comparison Matrix
        | Criterion | Plan A | Plan B | Plan C | ... |
        |-----------|--------|--------|--------|-----|
        | Strategic Prioritization | [Score & Key Approach] | ... |
        | Technical Specificity | [Score & Examples] | ... |
        | Comprehensiveness | [Score & Coverage] | ... |
        | Long-term Vision | [Score & Provisions] | ... |
        | **Overall Score** | **[X.X]** | **[X.X]** | **[X.X]** | ... |
        
        ### Individual Plan Analysis
        
        #### Plan A
        **Pros:**
        - [Specific strength with evidence]
        - [Specific strength with evidence]
        - [Specific strength with evidence]
        
        **Cons:**
        - [Specific weakness with evidence]
        - [Specific weakness with evidence]
        - [Specific weakness with evidence]
        
        **Best For:** [Scenarios where this plan excels]
        
        [Repeat for all plans]
        
        ### Key Trade-offs Identified
        [Analysis of major strategic trade-offs between approaches]
        
        ### Critical Gaps (Missing from ALL Plans)
        [What an ideal plan would include that no current plan addresses]
        """
        
        result = self.agent.execute_task(comparison_prompt)
        return self._parse_comparison_result(result)
    
    def _format_evaluations_for_comparison(self, evaluations: List[PlanEvaluation]) -> str:
        """Format individual evaluations for comparison analysis"""
        formatted = ""
        for eval in evaluations:
            formatted += f"\n### {eval.plan_name} (Judge: {eval.judge_id})\n"
            formatted += f"Overall Score: {eval.overall_score}\n"
            formatted += f"Analysis: {eval.detailed_analysis}\n"
            formatted += f"Pros: {', '.join(eval.pros)}\n"
            formatted += f"Cons: {', '.join(eval.cons)}\n\n"
        return formatted
    
    def _parse_comparison_result(self, raw_result: str) -> ComparisonResult:
        """Parse comparison analysis into structured format"""
        # Implementation to extract structured comparison data
        pass
```

### 2.3 Comparative Analysis Agent Implementation

#### Head-to-Head Comparison Agent (`src/agents/analysis_agent.py`)
```python
"""
Agent for detailed comparative analysis and gap identification
References: Master Plan - Analysis Agent specification  
"""
from crewai import Agent
from typing import Dict, List
from ..models.evaluation_models import ComparisonResult, GapAnalysis

class ComparativeAnalysisAgent:
    """
    Performs head-to-head comparison of plans and identifies what's missing
    Specializes in pros/cons analysis and expert gap identification
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create comparative analysis agent specialized in plan comparison"""
        return Agent(
            role="Accessibility Remediation Plan Analyst",
            goal="""Perform detailed head-to-head comparison of remediation plans,
                   identify relative strengths and weaknesses, and highlight gaps
                   that an expert would address but are missing from all plans.""",
            backstory="""You are an expert accessibility analyst with a keen eye
                        for comparative evaluation. You excel at identifying what
                        makes one approach superior to another and can spot missing
                        elements that would make plans more comprehensive and effective.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[
                PlanSynthesizerTool(),
                BestPracticeExtractorTool(),
                RecommendationGeneratorTool(),
                CoherenceValidatorTool()
            ]
        )
    
    def synthesize_optimal_plan(self, 
                               comparison_result: ComparisonResult, 
                               all_evaluations: List[PlanEvaluation],
                               audit_context: str) -> SynthesizedPlan:
        """
        Create optimal plan by synthesizing best elements from all plans
        
        Args:
            comparison_result: Comprehensive comparison analysis
            all_evaluations: Individual plan evaluations from both judges
            audit_context: Original audit report
            
        Returns:
            Synthesized optimal remediation plan
        """
        synthesis_prompt = f"""
        You are tasked with creating the ultimate accessibility remediation plan by 
        synthesizing the best elements from all evaluated plans while addressing their 
        collective weaknesses.
        
        CONTEXT (Original Audit):
        {audit_context}
        
        COMPARISON ANALYSIS:
        {comparison_result.summary}
        
        INDIVIDUAL PLAN STRENGTHS TO INCORPORATE:
        {self._extract_plan_strengths(all_evaluations)}
        
        IDENTIFIED GAPS TO ADDRESS:
        {comparison_result.critical_gaps}
        
        SYNTHESIS REQUIREMENTS:
        
        1. **Strategic Foundation**: Design a prioritization strategy that combines:
           - Best prioritization logic from strongest plans
           - Multi-factor considerations (user impact, architectural leverage, effort, risk)
           - Clear sequencing rationale with dependencies
        
        2. **Technical Excellence**: Integrate the most effective technical solutions:
           - Specific, actionable implementation guidance
           - Code examples and technical specifications
           - Modern web development best practices
           - Clear acceptance criteria
        
        3. **Comprehensive Coverage**: Ensure complete audit coverage:
           - Address ALL issues identified in the original audit
           - Fill gaps missed by individual plans
           - Connect all fixes to POUR principles
           - Provide clear implementation roadmap
        
        4. **Long-term Sustainability**: Include robust ongoing provisions:
           - Post-remediation verification processes
           - Continuous monitoring strategies
           - Team training and capability building
           - Cultural integration recommendations
        
        5. **Expert Enhancements**: Add elements that no original plan included:
           - Advanced accessibility considerations
           - Innovative implementation approaches
           - Process improvements and automation
           - Stakeholder engagement strategies
        
        OUTPUT FORMAT:
        # Synthesized Optimal Accessibility Remediation Plan
        
        ## Executive Summary
        [High-level overview of the synthesized approach and key innovations]
        
        ## Strategic Prioritization Framework
        ### Prioritization Logic
        [Explanation of how tasks are prioritized - synthesized from best approaches]
        
        ### Implementation Phases
        [Clear phases with dependencies and rationale]
        
        ## Technical Implementation Guide
        ### High-Impact Issues (Phase 1)
        [Specific technical solutions with code examples]
        
        ### Structural Improvements (Phase 2)
        [Architectural changes and systematic fixes]
        
        ### Enhancement and Optimization (Phase 3)
        [Advanced features and optimizations]
        
        ## Comprehensive Issue Coverage
        ### POUR Principle Alignment
        [How each fix aligns with Perceivable, Operable, Understandable, Robust]
        
        ### Audit Issue Mapping
        [Direct mapping of each audit finding to specific remediation action]
        
        ## Long-term Sustainability Plan
        ### Verification and Testing
        [Post-implementation validation processes]
        
        ### Continuous Monitoring
        [Ongoing accessibility monitoring and maintenance]
        
        ### Team Development
        [Training and capability building recommendations]
        
        ## Innovation and Best Practices
        ### Expert Recommendations
        [Advanced considerations not present in original plans]
        
        ### Process Improvements
        [Workflow and automation enhancements]
        
        ### Success Metrics
        [How to measure remediation success and ongoing compliance]
        
        ## Implementation Timeline and Resources
        [Realistic timeline with resource requirements and dependencies]
        """
        
        result = self.agent.execute_task(synthesis_prompt)
        return self._parse_synthesis_result(result)
    
    def _extract_plan_strengths(self, evaluations: List[PlanEvaluation]) -> str:
        """Extract and format the key strengths from all plans"""
        strengths = ""
        for eval in evaluations:
            strengths += f"\n### {eval.plan_name} Key Strengths:\n"
            for pro in eval.pros:
                strengths += f"- {pro}\n"
        return strengths
    
    def _parse_synthesis_result(self, raw_result: str) -> SynthesizedPlan:
        """Parse synthesis result into structured plan format"""
        # Implementation to extract structured synthesis data
        pass
```

### 2.4 Agent Tools Development

#### Evaluation Framework Tool (`src/tools/evaluation_framework.py`)
```python
"""
Custom tool for applying the evaluation framework from promt/eval-prompt.md
References: Phase 1 - Prompt Manager, Master Plan - Tool Integration
"""
from crewai_tools import BaseTool
from typing import Dict, Any
from ..tools.prompt_manager import PromptManager
from pathlib import Path

class EvaluationFrameworkTool(BaseTool):
    name: str = "evaluation_framework"
    description: str = """Apply the comprehensive evaluation framework from promt/eval-prompt.md 
                         to assess remediation plans. Returns structured evaluation with weighted 
                         criteria scores."""
    
    def __init__(self):
        super().__init__()
        self.prompt_manager = PromptManager(Path("promt/eval-prompt.md"))
        self.criteria_weights = self.prompt_manager.extract_evaluation_criteria()
    
    def _run(self, plan_content: str, plan_name: str, **kwargs) -> Dict[str, Any]:
        """
        Apply evaluation framework to a remediation plan
        
        Args:
            plan_content: Full text of the remediation plan
            plan_name: Name identifier for the plan
            
        Returns:
            Structured evaluation data
        """
        return {
            "framework_applied": True,
            "criteria_weights": self.criteria_weights,
            "evaluation_sections": [
                "Strategic Prioritization (40%)",
                "Technical Specificity (30%)",
                "Comprehensiveness (20%)",
                "Long-term Vision (10%)"
            ],
            "output_format": "detailed_analysis_with_scores"
        }

class ScoringCalculatorTool(BaseTool):
    name: str = "scoring_calculator"
    description: str = """Calculate weighted scores based on evaluation criteria. 
                         Ensures consistent scoring methodology across all evaluations."""
    
    def _run(self, criterion_scores: Dict[str, float], **kwargs) -> Dict[str, Any]:
        """
        Calculate overall score from weighted criteria scores
        
        Args:
            criterion_scores: Dict of criterion_name -> score (0-10)
            
        Returns:
            Calculated overall score and breakdown
        """
        weights = {
            "Strategic Prioritization": 0.40,
            "Technical Specificity": 0.30,
            "Comprehensiveness": 0.20,
            "Long-term Vision": 0.10
        }
        
        overall_score = 0.0
        for criterion, score in criterion_scores.items():
            if criterion in weights:
                overall_score += score * weights[criterion]
        
        return {
            "overall_score": round(overall_score, 2),
            "weighted_breakdown": {
                criterion: {
                    "score": score,
                    "weight": weights.get(criterion, 0),
                    "weighted_contribution": score * weights.get(criterion, 0)
                }
                for criterion, score in criterion_scores.items()
            }
        }

class GapAnalyzerTool(BaseTool):
    name: str = "gap_analyzer"
    description: str = """Identify gaps in remediation plans compared to audit requirements 
                         and accessibility best practices."""
    
    def _run(self, plan_content: str, audit_content: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze gaps between plan and requirements
        
        Args:
            plan_content: Remediation plan text
            audit_content: Original audit report
            
        Returns:
            Identified gaps and missing elements
        """
        # Implementation would analyze content for missing elements
        return {
            "coverage_analysis": "detailed_gap_identification",
            "missing_elements": [],
            "recommendations": []
        }
```

## Quality Gates

### Phase 2 Completion Criteria
- [ ] **Primary Judge Agent**: Gemini-based agent fully functional
- [ ] **Secondary Judge Agent**: GPT-4-based agent providing independent evaluation
- [ ] **Comparison Agent**: Cross-plan analysis working correctly
- [ ] **Synthesis Agent**: Optimal plan generation operational
- [ ] **Agent Tools**: All custom tools integrated and tested
- [ ] **Output Validation**: Structured outputs matching expected format

### Enhanced Quality Gates

#### 🔒 Agent Security & Reliability
- [ ] **Prompt Injection Protection**: Agents resistant to malicious input attempts
- [ ] **Output Validation**: All agent responses conform to expected schemas
- [ ] **Context Management**: Proper handling of large context windows without memory leaks
- [ ] **Sensitive Data**: Agents don't retain sensitive information between calls
- [ ] **Deterministic Behavior**: Same inputs produce consistent outputs (±5% variance)

#### 📊 Performance & Efficiency
- [ ] **Response Time**: Individual agent evaluations complete within 45 seconds
- [ ] **Token Management**: Requests stay within model token limits
- [ ] **Cost Monitoring**: API usage tracking and budget alerting implemented
- [ ] **Concurrent Execution**: Multiple agents run efficiently in parallel
- [ ] **Resource Usage**: Agent execution stays within memory limits

#### 🔧 Multi-Agent Coordination
- [ ] **Agent Communication**: Secure and validated inter-agent communication
- [ ] **Deadlock Prevention**: No infinite loops in agent workflows
- [ ] **State Management**: Agent state properly managed and recoverable
- [ ] **Isolation**: Agent failures don't cascade to other agents
- [ ] **Conflict Resolution**: Disagreement handling works reliably

#### 🎯 Tool Integration Quality
- [ ] **Tool Validation**: All custom tools thoroughly tested and validated
- [ ] **Error Propagation**: Tool errors properly handled and logged
- [ ] **Permission Model**: Tools operate with minimal required permissions
- [ ] **Audit Logging**: All tool usage logged for security auditing
- [ ] **Performance Impact**: Tools don't significantly impact agent performance

### Integration Testing
- [ ] **Single Plan Evaluation**: Both judges can evaluate one plan independently
- [ ] **Multi-Plan Comparison**: Comparison agent can analyze multiple evaluations
- [ ] **Plan Synthesis**: Synthesis agent can generate optimal plan from comparisons
- [ ] **Consensus Building**: Disagreement detection and resolution working
- [ ] **Output Parsing**: All agent outputs properly structured and parseable
- [ ] **Error Recovery**: Agents handle API failures gracefully
- [ ] **Load Testing**: Agents perform consistently under concurrent load

## Testing Strategy

### Unit Tests (`tests/test_agents.py`)
```python
"""
Comprehensive testing for all agent implementations
"""
import pytest
from src.agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent
from src.agents.comparison_agent import ComparisonAgent
from src.agents.synthesis_agent import SynthesisAgent

class TestJudgeAgents:
    """Test both primary and secondary judge agents"""
    
    @pytest.mark.integration
    def test_judge_agent_evaluation(self):
        """Test agent evaluation with sample plan"""
        # Mock plan content and audit report
        sample_plan = "Sample remediation plan content..."
        sample_audit = "Sample audit report content..."
        
        # Test primary judge
        primary_judge = PrimaryJudgeAgent(mock_gemini_llm)
        result = primary_judge.evaluate_plan("PlanA", sample_plan, sample_audit)
        
        assert result is not None
        assert "overall_score" in result
        assert "detailed_analysis" in result
    
    def test_cross_judge_consistency(self):
        """Test that both judges use same evaluation framework"""
        # Verify both agents have same evaluation structure
        pass

class TestComparisonAgent:
    """Test comparison agent functionality"""
    
    def test_plan_comparison(self):
        """Test cross-plan comparison functionality"""
        # Mock evaluation results from multiple plans
        mock_evaluations = [
            # Sample evaluation data
        ]
        
        comparison_agent = ComparisonAgent(mock_llm)
        result = comparison_agent.compare_plans(mock_evaluations, "audit_context")
        
        assert result is not None
        assert "comparison_matrix" in result
        assert "pros_cons_analysis" in result

class TestSynthesisAgent:
    """Test synthesis agent functionality"""
    
    def test_plan_synthesis(self):
        """Test optimal plan generation"""
        # Mock comparison results and evaluations
        mock_comparison = "comparison_result"
        mock_evaluations = []
        
        synthesis_agent = SynthesisAgent(mock_llm)
        result = synthesis_agent.synthesize_optimal_plan(
            mock_comparison, mock_evaluations, "audit_context"
        )
        
        assert result is not None
        assert "synthesized_plan" in result
        assert "implementation_timeline" in result
```

## Troubleshooting

### Common Issues
1. **Agent Response Format**: Ensure agents follow exact output format requirements
2. **Tool Integration**: Verify all custom tools are properly registered with agents
3. **LLM Consistency**: Monitor for response variations between identical prompts
4. **Memory Management**: Watch for context window limits with large plans

### Debug Commands
```bash
# Test individual agent creation
python -c "from src.agents.judge_agent import PrimaryJudgeAgent; print('Judge agent ready')"

# Test tool integration
python -c "from src.tools.evaluation_framework import EvaluationFrameworkTool; tool = EvaluationFrameworkTool(); print('Tools ready')"

# Test agent evaluation (requires API keys)
python tests/test_agents.py -v
```

## Next Steps

Upon successful completion of Phase 2:
1. **Proceed to [Phase 3: CrewAI Workflow Integration](./phase-3-workflow.md)**
2. **Begin orchestrating agents into coordinated workflows**
3. **Implement task definitions and crew configuration**

---

**← [Phase 1: Foundation](./phase-1-foundation.md)** | **[Phase 3: Workflow →](./phase-3-workflow.md)**
