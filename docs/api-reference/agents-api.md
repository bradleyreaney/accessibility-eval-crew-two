# Agent API Documentation

Complete API reference for all CrewAI agents in the system.

## 🤖 Agent Classes

### Primary Judge Agent

**Class**: `PrimaryJudgeAgent`  
**LLM**: Gemini Pro  










































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
