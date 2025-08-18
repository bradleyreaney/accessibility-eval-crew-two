# LLM Resilience Troubleshooting Guide
*Phase 4 - LLM Error Handling Enhancement Plan*

## Overview

This guide helps you troubleshoot common issues with the LLM resilience system. The resilience system is designed to handle LLM failures gracefully, but understanding how to diagnose and resolve issues is important for optimal system performance.

## Quick Diagnostic Checklist

Before diving into specific issues, run through this quick checklist:

- [ ] Are your LLM API keys configured correctly?
- [ ] Is your network connection stable?
- [ ] Are you within your LLM service rate limits?
- [ ] Do you have sufficient quota remaining?
- [ ] Are the LLM services operational?

## Common Issues and Solutions

### 1. All Evaluations Return NA (Not Available)

**Symptoms:**
- All evaluation results show status "NA"
- No successful evaluations in reports
- System reports "LLM unavailable" for all plans

**Diagnostic Steps:**

1. **Check LLM Availability:**
   ```python
   from src.utils.llm_resilience_manager import LLMResilienceManager
   
   resilience_manager = LLMResilienceManager(llm_manager)
   availability = resilience_manager.check_llm_availability()
   print(f"Gemini available: {availability['gemini']}")
   print(f"OpenAI available: {availability['openai']}")
   ```

2. **Check API Keys:**
   ```bash
   # Verify environment variables are set
   echo $GEMINI_API_KEY
   echo $OPENAI_API_KEY
   ```

3. **Test Individual LLMs:**
   ```python
   # Test Gemini
   try:
       result = llm_manager.gemini_llm.invoke("Test prompt")
       print("Gemini working")
   except Exception as e:
       print(f"Gemini error: {e}")
   
   # Test OpenAI
   try:
       result = llm_manager.openai_llm.invoke("Test prompt")
       print("OpenAI working")
   except Exception as e:
       print(f"OpenAI error: {e}")
   ```

**Solutions:**

- **API Key Issues**: Verify and update your API keys
- **Network Issues**: Check firewall settings and proxy configuration
- **Service Outages**: Check LLM service status pages
- **Rate Limiting**: Reduce request frequency or upgrade your plan

### 2. High Failure Rates

**Symptoms:**
- Many evaluations fail with retry errors
- Slow system performance
- High failure counts in status reports

**Diagnostic Steps:**

1. **Check Failure Counts:**
   ```python
   status = resilience_manager.get_status_summary()
   print(f"Failure counts: {status['failure_counts']}")
   ```

2. **Monitor Error Types:**
   ```python
   # Enable debug logging
   import logging
   logging.getLogger('src.utils.llm_resilience_manager').setLevel(logging.DEBUG)
   ```

3. **Check Rate Limits:**
   ```python
   # Review your current usage
   # This varies by LLM provider
   ```

**Solutions:**

- **Increase Retry Delays**: Adjust `retry_delay_seconds` in configuration
- **Reduce Concurrency**: Limit simultaneous requests
- **Upgrade Plans**: Consider higher rate limits
- **Implement Circuit Breaker**: Add additional failure handling

### 3. Slow Performance

**Symptoms:**
- Evaluations take much longer than expected
- System appears unresponsive
- High latency in responses

**Diagnostic Steps:**

1. **Check Timeout Settings:**
   ```python
   config = ResilienceConfig(timeout_seconds=30)  # Adjust as needed
   ```

2. **Monitor Response Times:**
   ```python
   import time
   
   start_time = time.time()
   result = resilience_manager.evaluate_plan_with_fallback(...)
   end_time = time.time()
   
   print(f"Evaluation time: {end_time - start_time:.2f} seconds")
   ```

3. **Check Network Latency:**
   ```bash
   # Test network connectivity to LLM services
   ping api.openai.com
   ping generativelanguage.googleapis.com
   ```

**Solutions:**

- **Optimize Prompts**: Reduce prompt size and complexity
- **Adjust Timeouts**: Set appropriate timeout values
- **Use Caching**: Implement result caching for repeated evaluations
- **Network Optimization**: Use closer data centers if available

### 4. Partial Evaluation Issues

**Symptoms:**
- Some evaluations complete, others fail
- Inconsistent results across different plans
- Mixed success/failure patterns

**Diagnostic Steps:**

1. **Check Partial Results:**
   ```python
   # Review evaluation results
   for evaluation in results["evaluations"]:
       print(f"Plan: {evaluation['plan_name']}")
       print(f"Status: {evaluation['status']}")
       if evaluation['status'] == 'NA':
           print(f"Reason: {evaluation['reason']}")
   ```

2. **Analyze Pattern:**
   ```python
   # Check if failures correlate with specific factors
   na_plans = [e for e in results["evaluations"] if e['status'] == 'NA']
   completed_plans = [e for e in results["evaluations"] if e['status'] == 'completed']
   
   print(f"NA plans: {len(na_plans)}")
   print(f"Completed plans: {len(completed_plans)}")
   ```

**Solutions:**

- **Review Plan Content**: Check if specific plans cause issues
- **Adjust Retry Logic**: Increase retries for problematic evaluations
- **Implement Fallback**: Add additional fallback strategies
- **Monitor Patterns**: Track which types of plans fail more often

### 5. Configuration Issues

**Symptoms:**
- System behaves unexpectedly
- Errors related to configuration parameters
- Performance doesn't match expectations

**Diagnostic Steps:**

1. **Validate Configuration:**
   ```python
   try:
       config = ResilienceConfig(
           max_retries=5,
           retry_delay_seconds=3,
           timeout_seconds=60
       )
       print("Configuration valid")
   except ValueError as e:
       print(f"Configuration error: {e}")
   ```

2. **Check Default Values:**
   ```python
   # Review current configuration
   print(f"Max retries: {resilience_manager.config.max_retries}")
   print(f"Timeout: {resilience_manager.config.timeout_seconds}")
   print(f"Partial evaluation: {resilience_manager.config.enable_partial_evaluation}")
   ```

**Solutions:**

- **Use Valid Values**: Ensure all configuration parameters are within valid ranges
- **Test Incrementally**: Change one parameter at a time
- **Document Settings**: Keep track of working configurations
- **Environment-Specific**: Use different settings for different environments

## Advanced Troubleshooting

### Debug Mode

Enable comprehensive debugging:

```python
import logging

# Enable debug logging for all resilience components
logging.getLogger('src.utils.llm_resilience_manager').setLevel(logging.DEBUG)
logging.getLogger('src.utils.llm_exceptions').setLevel(logging.DEBUG)
logging.getLogger('src.utils.workflow_controller').setLevel(logging.DEBUG)

# Run evaluation with debug output
result = resilience_manager.evaluate_plan_with_fallback(...)
```

### Performance Profiling

Profile system performance:

```python
import cProfile
import pstats

def profile_evaluation():
    resilience_manager.evaluate_plan_with_fallback(...)

# Run profiler
profiler = cProfile.Profile()
profiler.enable()
profile_evaluation()
profiler.disable()

# Analyze results
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Network Diagnostics

Check network connectivity:

```python
import requests
import time

def test_llm_connectivity():
    # Test Gemini
    try:
        start_time = time.time()
        response = requests.get('https://generativelanguage.googleapis.com', timeout=10)
        gemini_latency = time.time() - start_time
        print(f"Gemini latency: {gemini_latency:.2f}s")
    except Exception as e:
        print(f"Gemini connectivity issue: {e}")
    
    # Test OpenAI
    try:
        start_time = time.time()
        response = requests.get('https://api.openai.com', timeout=10)
        openai_latency = time.time() - start_time
        print(f"OpenAI latency: {openai_latency:.2f}s")
    except Exception as e:
        print(f"OpenAI connectivity issue: {e}")
```

## Error Code Reference

### Common Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `LLM unavailable` | LLM service is down or unreachable | Check service status, verify network |
| `Rate limit exceeded` | Too many requests in time period | Reduce request frequency, upgrade plan |
| `Quota exceeded` | Monthly usage limit reached | Upgrade plan or wait for reset |
| `Authentication failed` | Invalid or expired API key | Verify and update API keys |
| `Request timeout` | LLM took too long to respond | Increase timeout, check network |
| `Connection failed` | Network connectivity issue | Check firewall, proxy settings |

### Error Classification

The system automatically classifies errors:

```python
from src.utils.llm_exceptions import classify_llm_error

# Test error classification
error = LLMConnectionError("gemini", "Network timeout")
classification = classify_llm_error(error)

print(f"Error type: {classification['error_type']}")
print(f"Retryable: {classification['retryable']}")
print(f"Description: {classification['description']}")
```

## Recovery Procedures

### System Recovery

When the system has been experiencing issues:

1. **Reset Failure Counts:**
   ```python
   resilience_manager.reset_failure_counts()
   ```

2. **Check System Health:**
   ```python
   status = resilience_manager.get_status_summary()
   if status['available_llms'] > 0:
       print("System recovered")
   else:
       print("System still unavailable")
   ```

3. **Test with Simple Evaluation:**
   ```python
   # Test with minimal content
   result = resilience_manager.evaluate_plan_with_fallback(
       "TestPlan",
       "Simple test content",
       "Test context"
   )
   print(f"Test result: {result['status']}")
   ```

### Data Recovery

If evaluations were lost:

1. **Check for Partial Results:**
   ```python
   # Look for any completed evaluations
   completed = [e for e in results if e['status'] == 'completed']
   print(f"Recovered {len(completed)} evaluations")
   ```

2. **Re-run Failed Evaluations:**
   ```python
   # Re-run only NA evaluations
   na_plans = [e for e in results if e['status'] == 'NA']
   for plan in na_plans:
       # Re-run evaluation
       pass
   ```

## Best Practices

### Prevention

1. **Monitor Proactively:**
   - Set up alerts for high failure rates
   - Monitor LLM service status
   - Track usage and quotas

2. **Configure Appropriately:**
   - Use realistic timeout values
   - Set appropriate retry limits
   - Enable partial evaluation

3. **Test Regularly:**
   - Run health checks periodically
   - Test with various plan types
   - Validate configuration changes

### Response

1. **Document Issues:**
   - Record error patterns
   - Note successful resolutions
   - Track configuration changes

2. **Escalate Appropriately:**
   - Contact LLM providers for service issues
   - Review logs for system problems
   - Consider alternative configurations

3. **Learn from Failures:**
   - Analyze failure patterns
   - Adjust configurations based on findings
   - Update procedures based on lessons learned

## Getting Help

### Internal Resources

- **Logs**: Check application logs for detailed error information
- **Documentation**: Review API documentation and user guides
- **Configuration**: Verify all settings are correct

### External Resources

- **LLM Service Status**: Check official status pages
- **API Documentation**: Review LLM provider documentation
- **Community Forums**: Search for similar issues and solutions

### Contact Information

For persistent issues that cannot be resolved with this guide:

1. **Collect Information:**
   - Error logs and messages
   - Configuration settings
   - Steps to reproduce
   - System environment details

2. **Document Attempts:**
   - Troubleshooting steps taken
   - Results of each attempt
   - Any temporary workarounds

3. **Escalate:**
   - Contact system administrators
   - Reach out to development team
   - Consider external support if needed

## Conclusion

The LLM resilience system is designed to handle failures gracefully, but understanding how to troubleshoot issues is essential for maintaining optimal performance. Use this guide as a starting point, and don't hesitate to seek additional help when needed.

Remember: The goal is not to eliminate all failures, but to handle them gracefully and provide useful feedback to users when issues occur.
