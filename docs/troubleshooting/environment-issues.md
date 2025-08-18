# Environment Issues Troubleshooting Guide

Complete troubleshooting guide for environment variable configuration and API connectivity issues.

## 🚨 Common Error Messages

### LLM Connection Issues

**Error**: `LLMConnectionError: Unable to connect to Gemini Pro`
**Cause**: Network connectivity issues or API service unavailable.
**Solutions**:
1. **Check internet connection** - Ensure stable network connectivity
2. **Verify API endpoints** - Confirm API services are operational
3. **Check firewall settings** - Ensure outbound connections are allowed
4. **Retry the operation** - The system will automatically retry with exponential backoff

**Error**: `LLMTimeoutError: Request timed out after 30 seconds`
**Cause**: LLM service taking too long to respond.
**Solutions**:
1. **Increase timeout settings** - Modify `LLM_TIMEOUT` environment variable
2. **Check service status** - Verify LLM services are not experiencing high load
3. **Retry the operation** - Transient timeouts are automatically retried

### LLM Rate Limiting

**Error**: `LLMRateLimitError: Rate limit exceeded for OpenAI API`
**Cause**: API rate limits exceeded.
**Solutions**:
1. **Check API quotas** - Verify current usage and limits
2. **Implement rate limiting** - Add delays between requests
3. **Upgrade API plan** - Consider higher rate limits if needed
4. **Use fallback LLM** - System will automatically use alternative LLM

### LLM Authentication Issues

**Error**: `LLMAuthenticationError: Invalid API key for Gemini Pro`
**Cause**: Invalid or expired API key.
**Solutions**:
1. **Verify API keys** - Check environment variables are correctly set
2. **Regenerate API keys** - Create new keys if current ones are invalid
3. **Check key permissions** - Ensure keys have required permissions
4. **Restart application** - Reload environment variables

### LLM Quota Issues

**Error**: `LLMQuotaExceededError: Quota exceeded for OpenAI API`
**Cause**: API quota or billing limit reached.
**Solutions**:
1. **Check billing status** - Verify account has sufficient credits
2. **Monitor usage** - Track API usage to prevent future issues
3. **Upgrade plan** - Consider higher quota limits
4. **Use alternative LLM** - System will fallback to available LLM

## 🛡️ LLM Resilience Troubleshooting

### Partial Evaluation Issues

**Symptom**: Some evaluations marked as "NA" in results
**Cause**: One or more LLMs unavailable during evaluation
**Solutions**:
1. **Check LLM status** - Review availability status in CLI output
2. **Verify API keys** - Ensure all required API keys are valid
3. **Check network connectivity** - Confirm stable internet connection
4. **Review error logs** - Check specific failure reasons in logs

**Example Output**:
```
✅ LLM availability check complete:
   Gemini Pro: Available
   GPT-4: Unavailable (Rate limit exceeded)
⚠️  Operating with 1 available LLM(s)
📊 Partial evaluation completed: 8/10 plans evaluated (80.0%)
```

### High Retry Counts

**Symptom**: Many retry attempts visible in logs
**Cause**: Persistent LLM connectivity or service issues
**Solutions**:
1. **Check network stability** - Ensure consistent internet connection
2. **Review API rate limits** - Verify not hitting rate limits
3. **Increase retry delays** - Modify `LLM_RETRY_DELAY` environment variable
4. **Check service status** - Verify LLM services are operational

### Complete LLM Failure

**Symptom**: All evaluations marked as "NA"
**Cause**: No LLMs available for evaluation
**Solutions**:
1. **Check all API keys** - Verify both Gemini and OpenAI keys are valid
2. **Test connectivity** - Use `--dry-run --verbose` to check LLM status
3. **Review error messages** - Check specific failure reasons
4. **Contact support** - If issues persist, check LLM service status pages

### Monitoring LLM Health

**Command**: Check LLM status before evaluation
```bash
python main.py --dry-run --verbose
```

**Expected Output**:
```
✅ Environment validation complete
✅ LLM availability check complete:
   Gemini Pro: Available
   GPT-4: Available
✅ All systems operational
```

**Troubleshooting Commands**:
```bash
# Check specific LLM status
python -c "
from src.utils.llm_resilience_manager import LLMResilienceManager
from src.config.llm_config import LLMManager

manager = LLMResilienceManager(LLMManager())
status = manager.check_llm_availability()
print(f'LLM Status: {status}')
"

# Get detailed health information
python -c "
from src.utils.llm_resilience_manager import LLMResilienceManager
from src.config.llm_config import LLMManager

manager = LLMResilienceManager(LLMManager())
stats = manager.get_evaluation_statistics()
print(f'Evaluation Statistics: {stats}')
"
```

### "Required environment variables are missing"

**Cause**: One or both API keys are not set as environment variables.

**Solution**:
1. **Check current environment**:
   ```bash
   echo "GOOGLE_API_KEY: ${GOOGLE_API_KEY:-NOT SET}"
   echo "OPENAI_API_KEY: ${OPENAI_API_KEY:-NOT SET}"
   ```

2. **For local development**, ensure `.env` file exists:
   ```bash
   ls -la .env
   cat .env  # Verify contents (be careful not to expose keys)
   ```

3. **Set missing variables**:
   ```bash
   # In .env file
   GOOGLE_API_KEY=your_actual_gemini_key
   OPENAI_API_KEY=your_actual_openai_key
   
   # Or export directly
   export GOOGLE_API_KEY=your_actual_gemini_key
   export OPENAI_API_KEY=your_actual_openai_key
   ```

4. **Restart the application** after setting variables.

### "API connection tests failed"

**Cause**: Environment variables are set but API keys are invalid or have insufficient permissions.

**Diagnosis**:
1. **Test Gemini API connection**:
   ```bash
   curl -s -H "Content-Type: application/json" \
        -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GOOGLE_API_KEY"
   ```

2. **Test OpenAI API connection**:
   ```bash
   curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"model":"gpt-4","messages":[{"role":"user","content":"test"}],"max_tokens":5}' \
        "https://api.openai.com/v1/chat/completions"
   ```

**Solutions**:
- Verify API keys are active and valid
- Check API quotas and billing status
- Ensure keys have required permissions
- Try regenerating API keys if necessary

### "System configuration failed"

**Cause**: Unexpected error during system initialization.

**Diagnosis**:
1. **Check application logs** for detailed error messages
2. **Verify Python dependencies**:
   ```bash

   ```

3. **Test basic imports**:
   ```python
   python -c "
   try:
       from src.config.llm_config import LLMManager
       print('✅ LLMManager import successful')
   except Exception as e:
       print(f'❌ Import failed: {e}')
   "
   ```

**Solutions**:
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version compatibility (3.11+ required)
- Review full error traceback for specific issues

## 🔧 Platform-Specific Issues

### Local Development

#### Issue: .env file not loading
```bash
# Verify file exists and has correct name
ls -la .env

# Check file permissions
chmod 644 .env

# Verify python-dotenv is installed
pip list | grep python-dotenv

# Test manual loading
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('GOOGLE_API_KEY:', os.getenv('GOOGLE_API_KEY', 'NOT SET'))
"
```

#### Issue: Environment variables not persisting
```bash
# For bash/zsh, add to profile
echo 'export GOOGLE_API_KEY=your_key' >> ~/.zshrc
echo 'export OPENAI_API_KEY=your_key' >> ~/.zshrc
source ~/.zshrc

# Verify persistence
echo $GOOGLE_API_KEY
```




```bash
# Check if variables are set in host


# Test with explicit values

  -e GOOGLE_API_KEY=test_key \
  -e OPENAI_API_KEY=test_key \
  alpine env | grep -E "(GOOGLE|OPENAI)"



version: '3.8'
services:
  app:
    build: .

```


```bash





```

### Cloud Platforms

#### AWS ECS/Fargate
```bash
# Check task definition environment variables


# Check if using secrets manager



aws logs tail /aws/ecs/your-cluster --follow
```

#### Google Cloud Run
```bash
# Check service environment variables


# View logs
gcloud logs tail "resource.type=cloud_run_revision"
```


```bash
# Check environment variables
echo "GOOGLE_API_KEY: ${GOOGLE_API_KEY:+set}"
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+set}"

# View logs
# View CLI logs
python main.py --verbose
```

## 🧪 Diagnostic Tools

### Environment Validation Script
Create and run this diagnostic script:

```python
# diagnostic.py
import os
import sys
from pathlib import Path

def check_environment():
    """Comprehensive environment check"""
    print("🔍 Environment Diagnostic Report")
    print("=" * 50)
    
    # Check Python version
    print(f"Python Version: {sys.version}")
    
    # Check working directory
    print(f"Working Directory: {os.getcwd()}")
    
    # Check for .env file
    env_file = Path('.env')
    print(f".env file exists: {'✅' if env_file.exists() else '❌'}")
    
    # Check environment variables
    google_key = os.getenv('GOOGLE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"GOOGLE_API_KEY: {'✅ Set' if google_key else '❌ Missing'}")
    if google_key:
        print(f"  Length: {len(google_key)} characters")
        print(f"  Preview: {google_key[:8]}...")
    
    print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Missing'}")
    if openai_key:
        print(f"  Length: {len(openai_key)} characters")
        print(f"  Preview: {openai_key[:8]}...")
    
    # Test imports
    try:
        from dotenv import load_dotenv
        print("python-dotenv: ✅ Available")
        load_dotenv()
        print("load_dotenv(): ✅ Executed")
    except ImportError:
        print("python-dotenv: ❌ Not installed")
    
    try:
        from src.config.llm_config import LLMManager
        print("LLMManager import: ✅ Success")
    except Exception as e:
        print(f"LLMManager import: ❌ Failed - {e}")
    
    print("=" * 50)
    print("Diagnostic complete")

if __name__ == "__main__":
    check_environment()
```

Run with:
```bash
python diagnostic.py
```

### API Connectivity Test
```python
# test_apis.py
import os
import requests

def test_apis():
    """Test API connectivity"""
    google_key = os.getenv('GOOGLE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not google_key or not openai_key:
        print("❌ API keys not set")
        return
    
    # Test Gemini
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={google_key}",
            json={"contents": [{"parts": [{"text": "Hello"}]}]},
            timeout=10
        )
        print(f"Gemini API: {'✅' if response.status_code == 200 else '❌'} (Status: {response.status_code})")
    except Exception as e:
        print(f"Gemini API: ❌ Error - {e}")
    
    # Test OpenAI
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {openai_key}"},
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            },
            timeout=10
        )
        print(f"OpenAI API: {'✅' if response.status_code == 200 else '❌'} (Status: {response.status_code})")
    except Exception as e:
        print(f"OpenAI API: ❌ Error - {e}")

if __name__ == "__main__":
    test_apis()
```

## 🆘 Emergency Solutions

### Quick Reset
1. **Clear all environment variables**:
   ```bash
   unset GOOGLE_API_KEY
   unset OPENAI_API_KEY
   ```

2. **Start fresh with .env file**:
   ```bash
   cp .env.example .env
   # Edit .env with correct keys
   ```

3. **Restart application**:
   ```bash
   python main.py
   ```

### Environment Reset
```bash
# Clear environment variables
unset GOOGLE_API_KEY
unset OPENAI_API_KEY

# Reload environment
source .env
```

### Complete Reinstall
```bash
# Remove virtual environment
rm -rf venv/

# Create new environment
python -m venv venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your keys

# Test application
python main.py
```

## 📞 Getting Help

### Before Seeking Help
1. Run the diagnostic script above
2. Check all error messages carefully
3. Verify API keys are active and valid
4. Test with minimal configuration

### Support Resources
- **Documentation**: [Environment Setup Guide](../deployment/environment-setup.md)
- **API Documentation**: 
  - [Google AI Studio](https://makersuite.google.com/app/apikey)
  - [OpenAI API](https://platform.openai.com/docs)
- **Issue Tracking**: Project repository issues

### Information to Include
When reporting issues, include:
- Operating system and version
- Python version
- Error messages (with sensitive data removed)
- Output from diagnostic script
- Deployment environment (local/CLI)
- Steps to reproduce the issue

Remember: Never share actual API keys when seeking help!
