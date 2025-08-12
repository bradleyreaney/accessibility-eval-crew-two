# Development Environment Setup Guide

## Prerequisites
- Python 3.9+
- Virtual environment tools (venv/conda)
- API keys for Gemini Pro and GPT-4

## Quick Start
```bash
# Clone repository
git clone https://github.com/bradleyreaney/accessibility-eval-crew-two.git
cd accessibility-eval-crew-two

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Environment Variables
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key
```

## Verification
```bash
# Test PDF parsing
python -m pytest tests/unit/test_pdf_parser.py -v

# Test LLM connections (requires API keys)
python -m pytest tests/unit/test_llm_config.py::TestLLMIntegration -v

# Run all unit tests
python -m pytest tests/unit/ -v --cov=src

# Run integration tests (requires data files and API keys)
python -m pytest tests/integration/ -v
```

## Development Tools

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Run linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Testing (Updated for Phase 2)
```bash
# Run all tests with coverage
python -m pytest tests/ -v --cov=src --cov-report=html

# Run only unit tests (includes agent tests)
python -m pytest tests/unit/ -v

# Run agent-specific tests
python -m pytest tests/unit/test_agents.py -v

# Run only integration tests
python -m pytest tests/integration/ -v

# Run tests with specific markers
python -m pytest -m "not llm" -v  # Skip LLM tests
python -m pytest -m "integration" -v  # Only integration tests

# Test agent system
python scripts/phase2_demo.py  # Complete agent workflow demo
```

### Security Scanning
```bash
# Check dependencies for vulnerabilities
safety check

# Scan code for security issues
bandit -r src/
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the virtual environment and have installed all dependencies
2. **API Connection Failures**: Check API keys in `.env` file and verify quota limits
3. **PDF Parsing Errors**: Ensure PDF files exist in `data/` directories and are not corrupted
4. **Test Failures**: Check that all required test dependencies are installed

### Debug Commands
```bash
# Test PDF parsing
python -c "from src.tools.pdf_parser import PDFParser; parser = PDFParser(); print('Parser ready')"

# Test LLM connections (with API keys)
python -c "from src.config.llm_config import LLMManager; manager = LLMManager.from_environment(); print(manager.test_connections())"

# Test agent initialization (Phase 2)
python -c "from src.agents.judge_agent import PrimaryJudgeAgent; from src.config.llm_config import LLMManager; manager = LLMManager.from_environment(); agent = PrimaryJudgeAgent(manager); print('Agent ready')"

# Test prompt loading
python -c "from src.tools.prompt_manager import PromptManager; from pathlib import Path; manager = PromptManager(Path('promt/eval-prompt.md')); print(f'Prompt loaded: {len(manager.base_prompt)} chars')"
```

### Performance Testing
```bash
# Basic performance benchmarks
python -c "
import time
from pathlib import Path
from src.tools.pdf_parser import PDFParser

parser = PDFParser()
start = time.time()
# Test with actual files if available
print(f'Parser initialization: {time.time() - start:.3f}s')
"
```

## Phase 2 Completion Checklist ✅

- [x] Virtual environment setup and activated
- [x] All dependencies installed (`requirements.txt` and `requirements-test.txt`)
- [x] Environment variables configured (`.env` file)
- [x] All unit tests passing (`pytest tests/unit/ -v`)
- [x] Code coverage above 90% (`pytest --cov=src --cov-report=html`)
- [x] LLM connections working (if API keys available)
- [x] PDF parsing functional (if data files available)
- [x] Prompt loading working
- [x] Security scans passing (`safety check` and `bandit -r src/`)
- [x] **Agent system operational** (4 specialized agents)
- [x] **Agent tools functional** (4 evaluation tools)
- [x] **Multi-LLM integration** (Gemini Pro + GPT-4)
- [x] **Complete workflow demo** (`python scripts/phase2_demo.py`)

## Next Steps

**Phase 2 Complete ✅** - Multi-Agent System Operational:
1. **Phase 3 Ready**: Begin CrewAI crew orchestration and workflow automation
2. **Production Ready**: Complete evaluation pipeline with 4 specialized agents
3. **Advanced Features**: User interface and optimization (Phases 4-5)
