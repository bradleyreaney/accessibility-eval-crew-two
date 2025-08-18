# Agent API Documentation

Complete API reference for all CrewAI agents in the system.

## 🤖 Agent Classes

### Primary Judge Agent

**Class**: `PrimaryJudgeAgent`  
**LLM**: Gemini Pro  
**Status**: ✅ **Enhanced with LLM Resilience**

**Key Features**:
- Comprehensive accessibility expertise evaluation
- Structured scoring with detailed reasoning
- **🛡️ Enhanced Error Handling**: Automatic error classification and fallback
- **🔄 Retry Logic**: Exponential backoff for transient failures
- **📊 Status Reporting**: Detailed success/failure metrics

**Error Handling**:
```python
try:
    result = self.llm.invoke(evaluation_prompt)
    return {"success": True, "evaluation_content": result.content}
except Exception as e:
    llm_error = classify_llm_error(e, "Gemini Pro")
    return {
        "success": False,
        "error": str(e),
        "error_type": llm_error.__class__.__name__,
        "retryable": llm_error.retryable,
        "llm_type": "gemini",
        "status": "failed"
    }
```

### Secondary Judge Agent

**Class**: `SecondaryJudgeAgent`  
**LLM**: GPT-4  
**Status**: ✅ **Enhanced with LLM Resilience**

**Key Features**:
- Independent evaluation for cross-validation
- Alternative perspective on plan quality
- Bias reduction through dual-LLM approach
- **🛡️ Enhanced Error Handling**: Automatic error classification and fallback
- **🔄 Retry Logic**: Exponential backoff for transient failures
- **📊 Status Reporting**: Detailed success/failure metrics

### Scoring Agent

**Class**: `ScoringAgent`  
**LLM**: Gemini Pro  
**Status**: ✅ **Enhanced with LLM Resilience**

**Key Features**:
- MCDA-based weighted scoring calculations
- Comparative ranking across multiple plans
- Statistical analysis and score normalization
- **🛡️ Enhanced Error Handling**: Graceful degradation when LLMs unavailable
- **📊 Partial Scoring**: Continue with available evaluation data

### Analysis Agent

**Class**: `AnalysisAgent`  
**LLM**: GPT-4  
**Status**: ✅ **Enhanced with LLM Resilience**

**Key Features**:
- Strategic analysis of evaluation outcomes
- Implementation readiness assessment
- Executive summary generation
- **🛡️ Enhanced Error Handling**: Graceful degradation when LLMs unavailable
- **📊 Partial Analysis**: Continue with available evaluation data

## 🛡️ LLM Resilience Features

### Error Classification System

The system automatically classifies errors into specific types for better handling:

| Error Type | Retryable | Description | Handling |
|------------|-----------|-------------|----------|
| **LLMConnectionError** | ✅ Yes | Network connectivity issues | Retry with exponential backoff |
| **LLMTimeoutError** | ✅ Yes | Request timeout | Retry with exponential backoff |
| **LLMRateLimitError** | ✅ Yes | Rate limit exceeded | Retry after delay |
| **LLMAuthenticationError** | ❌ No | Invalid API key | Fail immediately |
| **LLMQuotaExceededError** | ❌ No | Quota exceeded | Fail immediately |

### Availability Monitoring

**LLM Status Tracking**:
```python
{
    "llm_status": {
        "gemini": {
            "available": True,
            "last_check": "2025-01-15T10:30:00Z",
            "failure_count": 0,
            "consecutive_failures": 0
        },
        "openai": {
            "available": False,
            "last_check": "2025-01-15T10:30:00Z",
            "failure_count": 3,
            "consecutive_failures": 2,
            "last_failure_reason": "Rate limit exceeded"
        }
    }
}
```

### Partial Evaluation Support

When LLMs are unavailable, the system provides partial results:

```python
{
    "plan_name": "Plan A",
    "evaluator": "Primary Judge (Gemini Pro)",
    "evaluation_content": None,
    "status": "NA",
    "na_reason": "LLM unavailable",
    "llm_used": "gemini",
    "timestamp": "2025-01-15 10:30:00",
    "success": False,
    "error": "LLM unavailable"
}
```

## 📊 Error Handling

### Common Exceptions

- **`LLMConnectionError`**: LLM service unavailable
- **`LLMTimeoutError`**: Evaluation exceeded time limit  
- **`LLMRateLimitError`**: Rate limit exceeded
- **`LLMAuthenticationError`**: Invalid API key
- **`LLMQuotaExceededError`**: Quota exceeded
- **`PartialEvaluationError`**: Partial completion scenarios
- **`NoLLMAvailableError`**: When no LLMs are available
- **`InvalidPlanContentError`**: Plan content cannot be processed
- **`AgentInitializationError`**: Agent failed to initialize

### Error Response Format
```python
{
    "success": False,
    "error": "LLMConnectionError",
    "message": "Unable to connect to Gemini Pro",
    "plan_id": "Plan A",
    "timestamp": "2025-08-14T10:30:00Z",
    "retryable": True,
    "llm_type": "gemini",
    "status": "failed"
}
```

## 🔗 Related Documentation

- **[LLM Error Resilience](../features/llm-error-resilience.md)** - Complete resilience feature documentation
- **[Agent Tools API](./agent-tools.md)** - Detailed tool documentation
- **[LLM Configuration](./llm-config.md)** - LLM setup and management
- **[Workflow Controller](./workflow-controller.md)** - Agent orchestration
- **[Examples](../examples/agent-examples.md)** - Usage examples
