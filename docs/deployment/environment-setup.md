# Environment Setup Guide

Comprehensive guide for configuring environment variables across different platforms and deployment scenarios.

## 🔒 Security Overview

This application uses **environment-only configuration** for enhanced security:
- API keys are never stored in the application code

- Server-side environment variable configuration only
- Reduced risk of accidental key exposure

## 📋 Required Environment Variables

```bash
GOOGLE_API_KEY=your_gemini_pro_api_key
OPENAI_API_KEY=your_openai_api_key
```

Both variables are **required** for the application to start.

## 🏠 Local Development Setup

### Option 1: .env File (Recommended)

1. **Copy the template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file**:
   ```bash
   # .env file content
   GOOGLE_API_KEY=your_actual_gemini_key_here
   OPENAI_API_KEY=your_actual_openai_key_here
   ```

3. **Verify the setup**:
   ```bash
   # Check if python-dotenv loads the variables
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅' if os.getenv('GOOGLE_API_KEY') else '❌', 'GOOGLE_API_KEY')"
   ```

### Option 2: Shell Environment

```bash
# Set for current session
export GOOGLE_API_KEY=your_gemini_key
export OPENAI_API_KEY=your_openai_key

# Add to shell profile for persistence
echo 'export GOOGLE_API_KEY=your_gemini_key' >> ~/.zshrc
echo 'export OPENAI_API_KEY=your_openai_key' >> ~/.zshrc
source ~/.zshrc
```

### Option 3: IDE Configuration

#### VS Code
1. Open `.vscode/settings.json`
2. Add environment variables:
   ```json
   {
     "python.terminal.activateEnvironment": true,
     "python.envFile": "${workspaceFolder}/.env"
   }
   ```

#### PyCharm
1. Go to Run/Debug Configurations
2. Add Environment Variables:
   - `GOOGLE_API_KEY`: your_key
   - `OPENAI_API_KEY`: your_key




```bash

  -e GOOGLE_API_KEY=your_gemini_key \
  -e OPENAI_API_KEY=your_openai_key \

  accessibility-evaluator:latest
```


```yaml

version: '3.8'
services:
  accessibility-evaluator:
    build: .
    ports:

    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    env_file:
      - .env
```

### Method 3: Environment File
```bash

GOOGLE_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key



```

## ☁️ Cloud Platform Setup

### AWS

#### ECS Task Definition
```json
{
  "family": "accessibility-evaluator",

    {
      "name": "app",
      "image": "your-registry/accessibility-evaluator:latest",
      "environment": [
        {"name": "GOOGLE_API_KEY", "value": "your_key"},
        {"name": "OPENAI_API_KEY", "value": "your_key"}
      ]
    }
  ]
}
```

#### ECS with AWS Secrets Manager
```json
{
  "secrets": [
    {
      "name": "GOOGLE_API_KEY",
      "valueFrom": "arn:aws:secretsmanager:region:account:secret:gemini-api-key"
    },
    {
      "name": "OPENAI_API_KEY", 
      "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-api-key"
    }
  ]
}
```

#### Lambda Environment Variables
```bash
aws lambda update-function-configuration \
  --function-name accessibility-evaluator \
  --environment Variables='{
    "GOOGLE_API_KEY":"your_key",
    "OPENAI_API_KEY":"your_key"
  }'
```

#### Elastic Beanstalk
```bash
# .ebextensions/environment.config
option_settings:
  aws:elasticbeanstalk:application:environment:
    GOOGLE_API_KEY: your_gemini_key
    OPENAI_API_KEY: your_openai_key
```

### Google Cloud Platform

#### Cloud Run
```bash
# Deploy with environment variables
gcloud run deploy accessibility-evaluator \
  --image gcr.io/your-project/accessibility-evaluator \
  --set-env-vars GOOGLE_API_KEY=your_key,OPENAI_API_KEY=your_key

# Using Secret Manager
gcloud run deploy accessibility-evaluator \
  --image gcr.io/your-project/accessibility-evaluator \
  --set-secrets GOOGLE_API_KEY=gemini-key:latest,OPENAI_API_KEY=openai-key:latest
```

#### App Engine
```yaml
# app.yaml
runtime: python311
env_variables:
  GOOGLE_API_KEY: your_gemini_key
  OPENAI_API_KEY: your_openai_key

# Using Secret Manager
env_variables:
  GOOGLE_API_KEY: ${GEMINI_KEY}
  OPENAI_API_KEY: ${OPENAI_KEY}
```

#### Kubernetes (GKE)
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
type: Opaque
stringData:
  GOOGLE_API_KEY: your_gemini_key
  OPENAI_API_KEY: your_openai_key

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: accessibility-evaluator
spec:
  template:
    spec:

      - name: app
        image: gcr.io/your-project/accessibility-evaluator
        envFrom:
        - secretRef:
            name: api-keys
```

### Microsoft Azure


```bash

  --resource-group myResourceGroup \
  --name accessibility-evaluator \
  --image your-registry/accessibility-evaluator:latest \
  --environment-variables \
    GOOGLE_API_KEY=your_key \
    OPENAI_API_KEY=your_key
```

#### App Service
```bash
# Set application settings
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name accessibility-evaluator \
  --settings \
    GOOGLE_API_KEY=your_gemini_key \
    OPENAI_API_KEY=your_openai_key
```

#### Azure Functions
```bash
az functionapp config appsettings set \
  --resource-group myResourceGroup \
  --name accessibility-evaluator \
  --settings \
    GOOGLE_API_KEY=your_key \
    OPENAI_API_KEY=your_key
```


```yaml

properties:
  configuration:
    secrets:
    - name: gemini-key
      value: your_gemini_key
    - name: openai-key
      value: your_openai_key
  template:

    - name: accessibility-evaluator
      image: your-registry/accessibility-evaluator:latest
      env:
      - name: GOOGLE_API_KEY
        secretRef: gemini-key
      - name: OPENAI_API_KEY
        secretRef: openai-key
```

## 🔍 Verification & Troubleshooting

### Verify Environment Setup
```bash
# Test environment variable detection
python -c "
import os
print('GOOGLE_API_KEY:', '✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Missing')
print('OPENAI_API_KEY:', '✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing')
"
```

### Test Application Startup
```bash
# Quick startup test
python -c "
import sys
sys.path.append('.')
from app.main import AccessibilityEvaluatorApp
app = AccessibilityEvaluatorApp()
print('✅ Application initialized successfully')
"
```

### Common Issues

#### Issue: "Required environment variables are missing"
**Solution**: Verify both `GOOGLE_API_KEY` and `OPENAI_API_KEY` are set
```bash
echo $GOOGLE_API_KEY
echo $OPENAI_API_KEY
```

#### Issue: "API connection tests failed"
**Solution**: Verify API keys are valid and have correct permissions
```bash
# Test Gemini API
curl -H "Content-Type: application/json" \
     -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
     "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GOOGLE_API_KEY"

# Test OpenAI API
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-4","messages":[{"role":"user","content":"Hello"}],"max_tokens":5}' \
     "https://api.openai.com/v1/chat/completions"
```

#### Issue: ".env file not loading"
**Solution**: Ensure python-dotenv is installed and .env is in project root
```bash
pip install python-dotenv
ls -la .env  # Should exist in project root
```

## 🔐 Security Best Practices

### Development
- ✅ Use `.env` files for local development
- ✅ Add `.env` to `.gitignore`
- ✅ Use environment-specific API keys
- ❌ Never commit API keys to version control

### Production
- ✅ Use secret management services (AWS Secrets Manager, Azure Key Vault, etc.)
- ✅ Rotate API keys regularly
- ✅ Use least-privilege access principles
- ✅ Monitor API key usage
- ❌ Never expose keys in logs or error messages


- ✅ Use multi-stage builds to minimize attack surface

- ✅ Use secrets management for sensitive data
- ✅ Scan images for vulnerabilities

## 📞 Support

If you encounter issues with environment setup:

1. **Check the setup guidance page** in the application
2. **Review the troubleshooting section** above
3. **Verify API keys** are valid and have required permissions
4. **Check platform documentation** for your specific deployment environment

For additional support, see [docs/troubleshooting/environment-issues.md](../troubleshooting/environment-issues.md).
