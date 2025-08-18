# LLM Error Resilience Feature
*Graceful Degradation and Partial Results*

**Feature Status**: ✅ **Phase 1 Complete** - ✅ **Phase 2 Complete** - ✅ **Phase 3 Complete**  
**Implementation Date**: January 2025  
**Test Coverage**: 90%+  

---

## 🎯 Overview

The LLM Error Resilience feature provides robust error handling that allows the evaluation process to continue even when one or more LLMs become unavailable. Instead of failing completely, the system gracefully degrades and provides partial results with clear indication of what couldn't be evaluated.

### Key Benefits
- **🛡️ Reliability**: System continues processing when one LLM fails
- **📊 Partial Results**: Users get available evaluations instead of complete failure
- **🔍 Transparency**: Clear indication of what couldn't be evaluated (marked as "NA")
- **📈 Monitoring**: Detailed logging and status tracking for troubleshooting
- **⚡ Performance**: Automatic retry with exponential backoff for transient failures
- **📋 Professional Reporting**: Enhanced reports with NA sections and availability status
- **📊 Completion Statistics**: Detailed completion rate and status tracking in reports

---

## 🏗️ Architecture

### Core Components

#### 1. LLM Resilience Manager (`src/utils/llm_resilience_manager.py`)
The central component that manages LLM failures and fallback strategies:

```python
class LLMResilienceManager:
    """Centralized LLM failure management and fallback coordination"""
    
    def check_llm_availability(self) -> Dict[str, bool]:
        """Test both LLMs and return availability status"""
        
    def execute_with_fallback(self, evaluation_input: EvaluationInput) -> Dict[str, Any]:
        """Execute evaluation with automatic fallback handling"""
        
    def safe_llm_invoke(self, llm, prompt: str, llm_type: str) -> Dict[str, Any]:
        """Safely invoke LLM with retry logic and error handling"""
```

#### 2. Custom LLM Exceptions (`src/utils/llm_exceptions.py`)
Specialized exception types for different LLM failure scenarios:

- **LLMConnectionError**: API connectivity issues
- **LLMTimeoutError**: Request timeout issues
- **LLMRateLimitError**: Rate limiting issues
- **LLMAuthenticationError**: Authentication failures
- **LLMQuotaExceededError**: Quota exceeded issues
- **PartialEvaluationError**: Partial completion scenarios
- **NoLLMAvailableError**: When no LLMs are available

#### 3. Enhanced Agent Error Handling
All agents now include improved error handling with automatic error classification:

```python
# Enhanced error handling in judge agents
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

#### 4. Enhanced Report Generator (`src/reports/generators/evaluation_report_generator.py`)
Professional report generation with NA handling and availability status:

```python
class EvaluationReportGenerator:
    """Enhanced report generator with NA handling and availability status"""
    
    def _create_na_evaluation_section(self, plan_name: str, llm_type: str, reason: str) -> List:
        """Generate standardized NA section for reports"""
        
    def _create_availability_status_section(self, availability: Dict[str, bool]) -> List:
        """Create LLM availability status section"""
        
    def create_completion_statistics(self, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate completion statistics and LLM availability"""
```

#### 5. Enhanced Data Models (`src/models/evaluation_models.py`)
New models for tracking evaluation status and completion:

```python
class EvaluationStatus(str, Enum):
    """Status of an evaluation result"""
    COMPLETED = "completed"
    NA = "NA"  # Not Available
    FAILED = "failed"

class EvaluationResult(BaseModel):
    """Enhanced evaluation result with availability tracking"""
    plan_name: str
    evaluator: str
    evaluation_content: Optional[str] = None
    status: EvaluationStatus = EvaluationStatus.COMPLETED
    na_reason: Optional[str] = None
    llm_used: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True
    overall_score: Optional[float] = None
    criteria_scores: Optional[Dict[str, float]] = None
    analysis: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None

class PartialEvaluationSummary(BaseModel):
    """Summary of partial evaluation results"""
    total_plans: int
    completed_evaluations: int
    na_evaluations: int
    failed_evaluations: int
    available_llms: List[str]
    unavailable_llms: List[str]
    completion_percentage: float
    evaluation_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )

class LLMAvailabilityStatus(BaseModel):
    """LLM availability status information"""
    llm_type: str
    available: bool
    last_check: str
    failure_count: int = 0
    last_failure_reason: Optional[str] = None

class ResilienceInfo(BaseModel):
    """Information about resilience handling during evaluation"""
    partial_evaluation: bool
    available_llms: List[str]
    unavailable_llms: List[str]
    na_evaluations_count: int
    completion_percentage: float
    resilience_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
```

---

## 🔄 How It Works

### 1. Availability Checking
Before starting evaluation, the system tests both LLMs:

```python
availability = resilience_manager.check_llm_availability()
# Returns: {"gemini": True, "openai": False}
```

### 2. Fallback Strategy
If one LLM fails, the system automatically tries the other:

```python
# Try primary LLM (Gemini Pro) first
if gemini_available:
    result = primary_judge.evaluate_plan(plan_name, plan_content, audit_context)
    if result["success"]:
        return result

# Fallback to secondary LLM (GPT-4)
if openai_available:
    result = secondary_judge.evaluate_plan(plan_name, plan_content, audit_context)
    if result["success"]:
        return result

# Both failed - mark as NA
return mark_evaluation_as_na(plan_name, "both", "Both LLMs unavailable")
```

### 3. Retry Logic
For transient failures, the system automatically retries with exponential backoff:

```python
# Configuration
max_retries = 3
retry_delay_seconds = 2
exponential_backoff = True

# Retry attempts: 2s, 4s, 8s delays
```

### 4. NA Result Generation
When evaluations can't be completed, standardized NA results are generated:

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

### 5. Enhanced Report Generation
Reports now include comprehensive NA handling and availability status:

```python
# NA Section in PDF Reports
def _create_na_evaluation_section(self, plan_name: str, llm_type: str, reason: str) -> List:
    """Create standardized NA section for PDF reports"""
    return [
        Paragraph(f"<b>Plan: {plan_name}</b>", self.styles["Heading3"]),
        Paragraph(f"<b>Status: Not Available (NA)</b>", self.styles["Normal"]),
        Paragraph(f"<b>LLM: {llm_type}</b>", self.styles["Normal"]),
        Paragraph(f"<b>Reason: {reason}</b>", self.styles["Normal"]),
        Paragraph(
            "This evaluation could not be completed due to LLM availability issues. "
            "Please refer to the system status section for troubleshooting guidance.",
            self.styles["Normal"]
        ),
        Spacer(1, 12)
    ]

# Availability Status Section
def _create_availability_status_section(self, availability: Dict[str, bool]) -> List:
    """Create LLM availability status section"""
    available_llms = [llm for llm, status in availability.items() if status]
    unavailable_llms = [llm for llm, status in availability.items() if not status]
    
    return [
        Paragraph("<b>LLM Availability Status</b>", self.styles["Heading2"]),
        Paragraph(f"Available: {', '.join(available_llms) if available_llms else 'None'}", self.styles["Normal"]),
        Paragraph(f"Unavailable: {', '.join(unavailable_llms) if unavailable_llms else 'None'}", self.styles["Normal"]),
        Spacer(1, 12)
    ]
```

---

## 📊 Error Classification

The system automatically classifies errors into specific types for better handling:

### Error Types and Handling

| Error Type | Retryable | Description | Handling |
|------------|-----------|-------------|----------|
| **LLMConnectionError** | ✅ Yes | Network connectivity issues | Retry with exponential backoff |
| **LLMTimeoutError** | ✅ Yes | Request timeout | Retry with exponential backoff |
| **LLMRateLimitError** | ✅ Yes | Rate limit exceeded | Retry after delay |
| **LLMAuthenticationError** | ❌ No | Invalid API key | Fail immediately |
| **LLMQuotaExceededError** | ❌ No | Quota exceeded | Fail immediately |

### Automatic Classification
```python
def classify_llm_error(error: Exception, llm_type: str) -> LLMError:
    """Classify generic exceptions into specific LLM error types"""
    error_str = str(error).lower()
    
    if "timeout" in error_str:
        return LLMTimeoutError(llm_type, 30)
    elif "rate limit" in error_str:
        return LLMRateLimitError(llm_type)
    elif "authentication" in error_str:
        return LLMAuthenticationError(llm_type, str(error))
    # ... more classification logic
```

---

## 🎛️ Configuration

### Resilience Configuration
```python
class ResilienceConfig(BaseModel):
    max_retries: int = 3
    retry_delay_seconds: int = 2
    exponential_backoff: bool = True
    timeout_seconds: int = 30
    enable_partial_evaluation: bool = True
    minimum_llm_requirement: int = 1
    na_reporting_enabled: bool = True
```

### Environment Variables
```bash
# Optional resilience configuration
LLM_MAX_RETRIES=3
LLM_RETRY_DELAY=2
LLM_TIMEOUT=30
LLM_MINIMUM_REQUIREMENT=1
```

---

## 📈 Monitoring and Status

### Status Tracking
The system tracks LLM health and availability:

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
    },
    "evaluation_stats": {
        "total_evaluations": 10,
        "successful_evaluations": 8,
        "na_evaluations": 2,
        "partial_evaluations": 1
    }
}
```

### Logging
Comprehensive logging for troubleshooting:

```
INFO: Checking LLM availability...
INFO: LLM availability check complete: 1/2 available
WARNING: Only 1 LLM(s) available, minimum required: 1
INFO: Starting evaluation with fallback handling...
WARNING: Primary LLM failed for Plan A: Rate limit exceeded
INFO: Secondary LLM evaluation successful for Plan A
INFO: Partial evaluation completed: 8/10 (80.0%)
```

---

## 🧪 Testing

### Test Coverage
- **55 Unit Tests**: Comprehensive test coverage for Phase 1
- **25 Unit Tests**: Workflow integration testing for Phase 2
- **15 Unit Tests**: Report generation testing for Phase 3
- **90%+ Coverage**: Meeting enterprise standards
- **Error Scenarios**: All failure modes tested
- **Integration Tests**: End-to-end workflow testing

### Test Scenarios
```python
# Test single LLM failure
def test_execute_with_fallback_partial_success():
    """Test partial execution when one LLM fails"""
    
# Test both LLMs failing
def test_execute_with_fallback_no_llms_available():
    """Test behavior when no LLMs are available"""
    
# Test retry logic
def test_safe_llm_invoke_retry_success():
    """Test successful retry after initial failure"""
    
# Test NA section generation
def test_create_na_evaluation_section():
    """Test NA section generation in reports"""
    
# Test availability status reporting
def test_create_availability_status_section():
    """Test availability status section generation"""
    
# Test completion statistics
def test_create_completion_statistics():
    """Test completion statistics calculation"""
```

---

## 🚀 Usage Examples

### Basic Usage
The feature works automatically - no additional configuration required:

```bash
# Normal evaluation - resilience is automatic
python main.py

# If one LLM fails, you'll get partial results
# Failed evaluations will be marked as "NA" in the report
```

### Monitoring Status
```python
from src.utils.llm_resilience_manager import LLMResilienceManager

# Get current status
status = resilience_manager.get_status_summary()
print(f"Available LLMs: {sum(status['llm_status'].values())}/2")

# Check specific LLM
if status['llm_status']['gemini']['available']:
    print("Gemini Pro is available")
```

### Custom Configuration
```python
from src.utils.llm_resilience_manager import ResilienceConfig

config = ResilienceConfig(
    max_retries=5,
    retry_delay_seconds=3,
    minimum_llm_requirement=2  # Require both LLMs
)

resilience_manager = LLMResilienceManager(llm_manager, config)
```

### Enhanced Report Generation
```python
from src.reports.generators.evaluation_report_generator import EvaluationReportGenerator

# Generate reports with NA handling
generator = EvaluationReportGenerator()

# PDF report with NA sections
pdf_path = generator.generate_pdf_report(evaluation_results)

# CSV export with NA status
csv_path = generator.generate_csv_export(evaluation_results)

# JSON export with resilience information
json_path = generator.generate_json_export(evaluation_results)

# Completion summary report
summary_path = generator.generate_completion_summary_report(evaluation_results)
```

---

## 📋 Troubleshooting

### Common Issues

#### 1. Both LLMs Unavailable
**Symptoms**: All evaluations marked as "NA"
**Solutions**:
- Check API keys in environment variables
- Verify network connectivity
- Check API quotas and billing status

#### 2. Partial Results
**Symptoms**: Some evaluations successful, others marked "NA"
**Solutions**:
- Check specific LLM status in logs
- Review error messages for specific failure reasons
- Consider retrying failed evaluations

#### 3. High Retry Counts
**Symptoms**: Many retry attempts in logs
**Solutions**:
- Check network stability
- Review API rate limits
- Consider increasing timeout values

### Debug Information
```bash
# Enable verbose logging
python main.py --verbose

# Check LLM status
python -c "
from src.utils.llm_resilience_manager import LLMResilienceManager
from src.config.llm_config import LLMManager

manager = LLMResilienceManager(LLMManager())
status = manager.check_llm_availability()
print(f'LLM Status: {status}')
"
```

---

## 🔮 Future Enhancements

### Phase 4: Testing and Validation (Planned)
- Comprehensive testing of all resilience features
- Performance testing with degraded LLM availability
- Error scenario testing and validation
- Documentation updates and user guides

### Advanced Features
- **Automatic Failover**: Seamless switching between LLMs
- **Predictive Failure Detection**: Proactive LLM health monitoring
- **Load Balancing**: Intelligent distribution across available LLMs
- **Interactive Dashboards**: Real-time status monitoring

---

## 📚 Related Documentation

- [LLM Error Handling Enhancement Plan](../plans/llm-error-handling-enhancement-plan.md)
- [API Reference - Agents](../api-reference/agents-api.md)
- [API Reference - Report Generator](../api-reference/report-generator.md)
- [Architecture Overview](../architecture/system-overview.md)
- [Troubleshooting Guide](../troubleshooting/environment-issues.md)

---

**Feature Status**: ✅ **Phase 1 Complete** - ✅ **Phase 2 Complete** - ✅ **Phase 3 Complete**  
**Next Steps**: Phase 4 testing and validation  
**Support**: See troubleshooting guide for common issues
