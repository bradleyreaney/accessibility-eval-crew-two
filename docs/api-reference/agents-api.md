# Agent API Documentation

Complete API reference for all CrewAI agents in the system.

## 🤖 Agent Classes

### Primary Judge Agent

**Class**: `PrimaryJudgeAgent`  
**LLM**: Gemini Pro  
**Role**: Expert Accessibility Consultant - Primary Judge

#### Initialization
```python
from src.agents.judge_agent import PrimaryJudgeAgent
from src.config.llm_config import LLMManager

llm_manager = LLMManager.from_env()
agent = PrimaryJudgeAgent(llm_manager)
```

#### Methods

##### `evaluate_plan(plan_id: str, plan_content: str, audit_context: str) -> Dict[str, Any]`
Evaluates a single remediation plan using weighted criteria.

**Parameters:**
- `plan_id`: Unique identifier for the plan (e.g., "Plan A")  
- `plan_content`: Full text content of the remediation plan
- `audit_context`: Audit report context for evaluation

**Returns:**
```python
{
    "plan_id": "Plan A",
    "scores": {
        "strategic_prioritization": 8.5,
        "technical_specificity": 7.2,
        "comprehensiveness": 6.8,
        "long_term_vision": 8.0
    },
    "weighted_score": 7.8,
    "reasoning": "Detailed evaluation reasoning...",
    "success": True
}
```

### Secondary Judge Agent

**Class**: `SecondaryJudgeAgent`  
**LLM**: GPT-4  
**Role**: Expert Accessibility Consultant - Secondary Judge

#### Initialization
```python
from src.agents.judge_agent import SecondaryJudgeAgent

agent = SecondaryJudgeAgent(llm_manager)
```

#### Methods

##### `evaluate_plan(plan_id: str, plan_content: str, audit_context: str) -> Dict[str, Any]`
Provides independent evaluation using the same framework.

### Scoring Agent

**Class**: `ScoringAgent`  
**LLM**: Gemini Pro  
**Role**: Accessibility Evaluation Scoring Specialist

#### Methods

##### `calculate_weighted_scores(evaluations: List[Dict]) -> Dict[str, Any]`
Calculates final weighted scores from multiple evaluations.

##### `rank_plans(plan_evaluations: List[Dict]) -> List[Dict]`
Ranks multiple plans by their weighted scores.

### Analysis Agent

**Class**: `AnalysisAgent`  
**LLM**: GPT-4  
**Role**: Strategic Analysis and Insights Specialist

#### Methods

##### `analyze_evaluation_results(results: Dict) -> Dict[str, Any]`
Provides strategic analysis and implementation insights.

##### `generate_recommendations(top_plan: Dict) -> Dict[str, Any]`
Generates actionable recommendations for the highest-scoring plan.

## 🛠️ Agent Tools

Each agent has access to specialized tools:

### EvaluationFrameworkTool
- **Purpose**: Apply weighted evaluation criteria
- **Usage**: Integrated automatically in judge agents

### ScoringCalculatorTool  
- **Purpose**: Calculate weighted scores and rankings
- **Usage**: Used by scoring agent for final calculations

### GapAnalyzerTool
- **Purpose**: Identify gaps between audit findings and plans
- **Usage**: Available to all agents for comprehensive analysis

### PlanComparatorTool
- **Purpose**: Compare multiple plans side-by-side
- **Usage**: Used for comparative analysis and ranking

## 🔄 Agent Workflow

```python
# Complete multi-agent evaluation
async def evaluate_with_agents(audit_content, plans):
    # Primary evaluation
    primary_results = []
    for plan in plans:
        result = primary_judge.evaluate_plan(
            plan['id'], plan['content'], audit_content
        )
        primary_results.append(result)
    
    # Secondary validation
    secondary_results = []
    for plan in plans:
        result = secondary_judge.evaluate_plan(
            plan['id'], plan['content'], audit_content
        )
        secondary_results.append(result)
    
    # Scoring and ranking
    final_scores = scoring_agent.calculate_weighted_scores(
        primary_results + secondary_results
    )
    ranked_plans = scoring_agent.rank_plans(final_scores)
    
    # Strategic analysis
    analysis = analysis_agent.analyze_evaluation_results(ranked_plans)
    
    return {
        "ranked_plans": ranked_plans,
        "analysis": analysis,
        "primary_evaluations": primary_results,
        "secondary_evaluations": secondary_results
    }
```

## 📊 Error Handling

### Common Exceptions

- **`LLMConnectionError`**: LLM service unavailable
- **`EvaluationTimeoutError`**: Evaluation exceeded time limit  
- **`InvalidPlanContentError`**: Plan content cannot be processed
- **`AgentInitializationError`**: Agent failed to initialize

### Error Response Format
```python
{
    "success": False,
    "error": "LLMConnectionError",
    "message": "Unable to connect to Gemini Pro",
    "plan_id": "Plan A",
    "timestamp": "2025-08-14T10:30:00Z"
}
```

## 🔗 Related Documentation

- **[Agent Tools API](./agent-tools.md)** - Detailed tool documentation
- **[LLM Configuration](./llm-config.md)** - LLM setup and management
- **[Workflow Controller](./workflow-controller.md)** - Agent orchestration
- **[Examples](../examples/agent-examples.md)** - Usage examples
