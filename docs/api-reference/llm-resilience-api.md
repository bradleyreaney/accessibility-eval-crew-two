# LLM Resilience API Reference
*Phase 4 - LLM Error Handling Enhancement Plan*

## Overview

The LLM Resilience API provides comprehensive error handling and fallback capabilities for LLM-based evaluation systems. This API ensures that evaluation processes continue even when one or more LLMs become unavailable, providing graceful degradation and clear reporting of unavailable evaluations.

## Core Components

### LLMResilienceManager

The central component for managing LLM failures and fallback strategies.

#### Constructor

```python
LLMResilienceManager(
    llm_manager: LLMManager,
    config: Optional[ResilienceConfig] = None
)
```

**Parameters:**
- `llm_manager`: The LLM manager instance containing Gemini and OpenAI LLMs
- `config`: Optional resilience configuration (uses defaults if not provided)

#### Methods

##### `check_llm_availability() -> Dict[str, bool]`

Tests the availability of all configured LLMs and returns their status.

**Returns:**
```python
{
    "gemini": True,   # Gemini Pro availability
    "openai": False   # GPT-4 availability
}
```

**Example:**
```python
resilience_manager = LLMResilienceManager(llm_manager)
availability = resilience_manager.check_llm_availability()
print(f"Gemini available: {availability['gemini']}")
print(f"OpenAI available: {availability['openai']}")
```

##### `safe_llm_invoke(llm, prompt: str, max_retries: int = 3) -> Dict[str, Any]`

Safely invokes an LLM with retry logic and error handling.

**Parameters:**
- `llm`: The LLM instance to invoke
- `prompt`: The prompt to send to the LLM
- `max_retries`: Maximum number of retry attempts (default: 3)

**Returns:**
```python
{
    "success": True,
    "content": "LLM response content",
    "attempts": 1,
    "retryable": True
}
```

**Error Response:**
```python
{
    "success": False,
    "error": "Error description",
    "attempts": 3,
    "retryable": False
}
```

**Example:**
```python
result = resilience_manager.safe_llm_invoke(
    llm_manager.gemini_llm,
    "Evaluate this accessibility plan",
    max_retries=3
)

if result["success"]:
    print(f"Evaluation: {result['content']}")
else:
    print(f"Failed: {result['error']}")
```

##### `evaluate_plan_with_fallback(plan_name: str, plan_content: str, audit_context: str) -> Dict[str, Any]`

Evaluates a plan using available LLMs with automatic fallback.

**Parameters:**
- `plan_name`: Name of the plan being evaluated
- `plan_content`: Content of the plan to evaluate
- `audit_context`: Audit context for the evaluation

**Returns:**
```python
{
    "status": "completed",  # "completed" or "NA"
    "evaluation_content": "Evaluation result",
    "llm_used": "gemini",
    "timestamp": "2025-01-15T10:30:00Z",
    "reason": None
}
```

**NA Response:**
```python
{
    "status": "NA",
    "evaluation_content": None,
    "llm_used": None,
    "timestamp": "2025-01-15T10:30:00Z",
    "reason": "LLM unavailable"
}
```

**Example:**
```python
result = resilience_manager.evaluate_plan_with_fallback(
    "MyAccessibilityPlan",
    "Plan content here...",
    "Audit context here..."
)

if result["status"] == "completed":
    print(f"Evaluation completed using {result['llm_used']}")
    print(f"Result: {result['evaluation_content']}")
else:
    print(f"Evaluation not available: {result['reason']}")
```

##### `mark_evaluation_as_na(plan_name: str, llm_type: str, reason: str) -> Dict[str, Any]`

Creates a standardized NA (Not Available) evaluation result.

**Parameters:**
- `plan_name`: Name of the plan
- `llm_type`: Type of LLM that failed ("gemini" or "openai")
- `reason`: Reason for the NA status

**Returns:**
```python
{
    "status": "NA",
    "plan_name": "MyPlan",
    "evaluation_content": None,
    "llm_used": None,
    "timestamp": "2025-01-15T10:30:00Z",
    "reason": "LLM unavailable"
}
```

##### `get_status_summary() -> Dict[str, Any]`

Returns a comprehensive status summary of all LLMs.

**Returns:**
```python
{
    "total_llms": 2,
    "available_llms": 1,
    "unavailable_llms": 1,
    "failure_counts": {
        "gemini": 0,
        "openai": 2
    },
    "availability_status": {
        "gemini": True,
        "openai": False
    }
}
```

##### `reset_failure_counts()`

Resets all failure counters for recovery scenarios.

### ResilienceConfig

Configuration class for resilience behavior.

#### Constructor

```python
ResilienceConfig(
    max_retries: int = 3,
    retry_delay_seconds: int = 2,
    exponential_backoff: bool = True,
    timeout_seconds: int = 30,
    enable_partial_evaluation: bool = True,
    minimum_llm_requirement: int = 1,
    na_reporting_enabled: bool = True
)
```

**Parameters:**
- `max_retries`: Maximum number of retry attempts for failed requests
- `retry_delay_seconds`: Base delay between retries in seconds
- `exponential_backoff`: Whether to use exponential backoff for retries
- `timeout_seconds`: Request timeout in seconds
- `enable_partial_evaluation`: Whether to allow partial evaluation with reduced LLMs
- `minimum_llm_requirement`: Minimum number of LLMs required to start evaluation
- `na_reporting_enabled`: Whether to generate NA reports for failed evaluations

**Example:**
```python
config = ResilienceConfig(
    max_retries=5,
    retry_delay_seconds=3,
    exponential_backoff=True,
    timeout_seconds=60,
    enable_partial_evaluation=True,
    minimum_llm_requirement=1,
    na_reporting_enabled=True
)

resilience_manager = LLMResilienceManager(llm_manager, config)
```

## Error Handling

### Custom Exceptions

The resilience system uses custom exceptions for different error types:

#### `LLMConnectionError`
Raised when LLM API connection fails.

```python
LLMConnectionError(llm_type: str, error_details: str)
```

#### `LLMTimeoutError`
Raised when LLM request times out.

```python
LLMTimeoutError(llm_type: str, error_details: str)
```

#### `LLMRateLimitError`
Raised when LLM rate limit is exceeded.

```python
LLMRateLimitError(llm_type: str, error_details: str)
```

#### `LLMAuthenticationError`
Raised when LLM authentication fails.

```python
LLMAuthenticationError(llm_type: str, error_details: str)
```

#### `LLMQuotaExceededError`
Raised when LLM quota is exceeded.

```python
LLMQuotaExceededError(llm_type: str, error_details: str)
```

#### `NoLLMAvailableError`
Raised when no LLMs are available for evaluation.

```python
NoLLMAvailableError(message: str)
```

### Error Classification

The system automatically classifies errors to determine retry behavior:

```python
from src.utils.llm_exceptions import classify_llm_error

classification = classify_llm_error(error)
print(f"Error type: {classification['error_type']}")
print(f"Retryable: {classification['retryable']}")
```

**Error Types:**
- `connection`: Network connectivity issues (retryable)
- `timeout`: Request timeout issues (retryable)
- `rate_limit`: Rate limiting issues (not retryable)
- `authentication`: Authentication issues (not retryable)
- `quota`: Quota exceeded issues (not retryable)
- `unknown`: Unknown errors (retryable by default)

## Integration Examples

### Basic Usage

```python
from src.utils.llm_resilience_manager import LLMResilienceManager, ResilienceConfig
from src.config.llm_config import LLMManager

# Initialize LLM manager
llm_manager = LLMManager()

# Create resilience manager
resilience_manager = LLMResilienceManager(llm_manager)

# Check availability
availability = resilience_manager.check_llm_availability()
print(f"Available LLMs: {sum(availability.values())}")

# Evaluate with fallback
result = resilience_manager.evaluate_plan_with_fallback(
    "MyPlan",
    "Plan content...",
    "Audit context..."
)

if result["status"] == "completed":
    print("Evaluation successful!")
else:
    print(f"Evaluation not available: {result['reason']}")
```

### Advanced Configuration

```python
# Custom resilience configuration
config = ResilienceConfig(
    max_retries=5,
    retry_delay_seconds=3,
    exponential_backoff=True,
    timeout_seconds=60,
    enable_partial_evaluation=True,
    minimum_llm_requirement=1,
    na_reporting_enabled=True
)

resilience_manager = LLMResilienceManager(llm_manager, config)

# Monitor status
status = resilience_manager.get_status_summary()
print(f"System health: {status['available_llms']}/{status['total_llms']} LLMs available")

# Reset after recovery
if status['failure_counts']['gemini'] > 5:
    resilience_manager.reset_failure_counts()
    print("Failure counts reset")
```

### Error Handling Patterns

```python
try:
    result = resilience_manager.evaluate_plan_with_fallback(
        "MyPlan",
        "Plan content...",
        "Audit context..."
    )
    
    if result["status"] == "completed":
        process_evaluation(result["evaluation_content"])
    else:
        handle_na_evaluation(result["reason"])
        
except NoLLMAvailableError:
    print("No LLMs available for evaluation")
    # Handle complete system unavailability
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle unexpected errors
```

## Report Generation

### NA Section Generation

The report generator automatically creates NA sections for unavailable evaluations:

```python
from src.reports.generators.evaluation_report_generator import EvaluationReportGenerator

report_generator = EvaluationReportGenerator()

# Generate report with NA sections
evaluation_results = {
    "evaluations": [
        {
            "plan_name": "PlanA",
            "status": "completed",
            "evaluation_content": "Evaluation result"
        },
        {
            "plan_name": "PlanB",
            "status": "NA",
            "reason": "LLM unavailable"
        }
    ],
    "resilience_info": {
        "available_llms": ["gemini"],
        "unavailable_llms": ["openai"],
        "completion_percentage": 50.0,
        "na_evaluations_count": 1
    }
}

report_content = report_generator._create_evaluation_summary(evaluation_results)
```

### Availability Status Reporting

Reports include LLM availability status:

```python
# Add availability status to report
availability_status = resilience_manager.get_status_summary()
report_generator._add_availability_notice(report_content, availability_status["availability_status"])
```

## Performance Considerations

### Retry Logic

- **Exponential Backoff**: Retry delays increase exponentially (1s, 2s, 4s, etc.)
- **Maximum Retries**: Configurable limit to prevent infinite retry loops
- **Error Classification**: Non-retryable errors (auth, quota) fail immediately

### Monitoring

- **Failure Tracking**: Automatic tracking of failure counts per LLM
- **Status Monitoring**: Real-time availability status
- **Performance Metrics**: Execution time and success rate tracking

### Best Practices

1. **Configure Appropriate Timeouts**: Set realistic timeouts based on your use case
2. **Monitor Failure Patterns**: Use status summaries to identify problematic LLMs
3. **Handle NA Results Gracefully**: Always check for NA status in evaluation results
4. **Reset Counters After Recovery**: Reset failure counts when LLMs become available again
5. **Use Partial Evaluation**: Enable partial evaluation to maximize system availability

## Troubleshooting

### Common Issues

#### All Evaluations Return NA
- Check LLM API keys and authentication
- Verify network connectivity
- Review rate limits and quotas
- Check LLM service status

#### High Failure Rates
- Increase retry delays
- Reduce concurrent requests
- Check for rate limiting
- Monitor API quotas

#### Slow Performance
- Reduce timeout values
- Optimize prompt sizes
- Use appropriate retry limits
- Monitor network latency

### Debug Information

Enable debug logging to get detailed error information:

```python
import logging
logging.getLogger('src.utils.llm_resilience_manager').setLevel(logging.DEBUG)
```

### Status Monitoring

Regular status checks help identify issues early:

```python
# Monitor system health
status = resilience_manager.get_status_summary()
if status['available_llms'] == 0:
    print("WARNING: No LLMs available!")
elif status['available_llms'] < status['total_llms']:
    print(f"WARNING: {status['unavailable_llms']} LLMs unavailable")
```

## Migration Guide

### From Non-Resilient to Resilient System

1. **Add Resilience Manager**:
   ```python
   # Before
   result = llm.invoke(prompt)
   
   # After
   result = resilience_manager.safe_llm_invoke(llm, prompt)
   ```

2. **Handle NA Results**:
   ```python
   # Before
   evaluation = process_evaluation(result)
   
   # After
   if result["status"] == "completed":
       evaluation = process_evaluation(result["evaluation_content"])
   else:
       evaluation = handle_na_evaluation(result["reason"])
   ```

3. **Add Availability Checks**:
   ```python
   # Before
   start_evaluation()
   
   # After
   availability = resilience_manager.check_llm_availability()
   if sum(availability.values()) > 0:
       start_evaluation()
   else:
       handle_no_availability()
   ```

## API Versioning

This API is part of Phase 4 of the LLM Error Handling Enhancement Plan. All methods are backward compatible with existing code.

**Version**: 1.0  
**Phase**: 4  
**Status**: Complete  
**Compatibility**: Backward compatible
