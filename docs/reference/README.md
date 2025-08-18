# Quick Reference

Essential quick reference materials for the accessibility evaluation system.

## 📋 Reference Guides

### 🎯 Evaluation Framework
- **[evaluation-criteria.md](./evaluation-criteria.md)** - WCAG-aligned evaluation criteria
- **[scoring-weights.md](./scoring-weights.md)** - Weighted scoring methodology
- **[accessibility-standards.md](./accessibility-standards.md)** - Accessibility compliance reference

### 🤖 System Components
- **[agent-roles.md](./agent-roles.md)** - Agent responsibilities and specializations
- **[api-endpoints.md](./api-endpoints.md)** - Key API methods and parameters
- **[error-codes.md](./error-codes.md)** - System error codes and meanings

### 🔧 Configuration
- **[environment-variables.md](./environment-variables.md)** - Required environment setup
- **[llm-models.md](./llm-models.md)** - Supported LLM models and configuration
- **[file-formats.md](./file-formats.md)** - Supported input and output formats

### 📊 Data Structures
- **[data-models.md](./data-models.md)** - Pydantic model schemas
- **[response-formats.md](./response-formats.md)** - API response structures
- **[report-templates.md](./report-templates.md)** - PDF report formats

## ⚡ Quick Commands

### Essential Commands
```bash
# Launch application


# Run tests
python -m pytest tests/unit/ -v

# Validate setup
python scripts/validate_phase4_quality_gates.py

# Generate demo
python scripts/phase4_demo.py
```

### Quality Checks
```bash
# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Test coverage
pytest --cov=src --cov-report=html
```

## 📊 Score Interpretation

### Weighted Criteria (Total: 100%)
- **Strategic Prioritization**: 40% - Focus on high-impact issues
- **Technical Specificity**: 30% - Implementation detail quality
- **Comprehensiveness**: 20% - Coverage of identified issues
- **Long-term Vision**: 10% - Sustainability and scalability

### Score Ranges
- **9.0-10.0**: Excellent - Ready for immediate implementation
- **8.0-8.9**: Very Good - Minor refinements needed
- **7.0-7.9**: Good - Some improvements required
- **6.0-6.9**: Adequate - Moderate revisions needed
- **5.0-5.9**: Below Standard - Significant improvements required
- **< 5.0**: Poor - Major revision or replacement needed

## 🔧 Common Configurations

### Environment Variables (.env)
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional
LOG_LEVEL=INFO
CACHE_ENABLED=true
MAX_WORKERS=4
TIMEOUT_SECONDS=300
```

### LLM Model Options
```python
# Gemini Models
"gemini-pro"          # Default, balanced performance
"gemini-pro-vision"   # With image processing (if needed)

# OpenAI Models  
"gpt-4"               # Default, highest quality
"gpt-4-turbo"         # Faster responses
"gpt-3.5-turbo"       # Cost-effective option
```

## 📁 File Structure Quick Reference

```
src/
├── agents/           # CrewAI agents
├── config/           # LLM configuration
├── models/           # Pydantic data models
├── tools/            # PDF parsing, prompts
├── reports/          # PDF generation
├── consensus/        # Conflict resolution
├── batch/            # Batch processing
└── monitoring/       # Performance tracking

data/
├── audit-reports/    # Input audit PDFs
└── remediation-plans/ # Input plan PDFs

docs/
├── api-reference/    # API documentation
├── examples/         # Usage examples
├── architecture/     # System design
└── development/      # Dev guides
```

## 🚨 Troubleshooting Quick Fixes

### Common Issues
```bash
# LLM connection issues
export GOOGLE_API_KEY="your_key"
export OPENAI_API_KEY="your_key"

# PDF parsing errors
pip install --upgrade pdfplumber PyPDF2

# Missing dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt



```

### Performance Issues
```python
# Optimize for speed
agent = PrimaryJudgeAgent(
    llm_manager,
    temperature=0.1,  # More deterministic
    max_tokens=1000   # Shorter responses
)

# Enable caching
os.environ["CACHE_ENABLED"] = "true"
```

## 🔗 Navigation

- **[← Back to Documentation Hub](../README.md)**
- **[Examples →](../examples/)**
- **[API Reference →](../api-reference/)**

## 📞 Support Links

- **[GitHub Issues](https://github.com/bradleyreaney/accessibility-eval-crew-two/issues)**
- **[Development Guide](../development/README.md)**
- **[Troubleshooting](../troubleshooting/)**
