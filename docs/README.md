# Documentation Hub
*LLM as a Judge - Accessibility Evaluation System*

Welcome to the comprehensive documentation for our local AI-powered accessibility evaluation system. This documentation covers everything from initial setup to advanced agent configuration.

## 🎯 Quick Navigation

### � Getting Started
- **[Setup Guide](development/setup-guide.md)** - Complete installation and configuration
- **[Architecture Overview](architecture/system-overview.md)** - System design and components
- **[Development Workflow](development/README.md)** - Development standards and practices

### 🤖 Technical Documentation
- **[API Reference](api-reference/)** - Complete component documentation
- **[Agent System](../src/agents/)** - CrewAI agent implementations
- **[Configuration](../src/config/)** - LLM and system configuration
- **[Data Models](../src/models/)** - Pydantic validation models

### � Implementation Guides
- **[Phase 1: Foundation](../plans/phase-1-foundation.md)** - Core infrastructure ✅
- **[Phase 2: Core Agents](../plans/phase-2-agents.md)** - Agent development ✅  
- **[Phase 3: Workflows](../plans/phase-3-workflow.md)** - CrewAI orchestration ✅
- **[Phase 4: Interface](../plans/phase-4-interface.md)** - User interface (In Progress)

### � Development Resources
- **[Development Standards](development/README.md)** - Code quality and testing
- **[Project Structure](development/setup-guide.md#project-structure)** - Codebase organization
- **[Configuration Guide](development/configurations/)** - Environment setup

## 📊 Current Status

### ✅ Completed Phases
- **Phase 1**: Foundation with 90.28% test coverage
- **Phase 2**: Four specialized CrewAI agents operational
- **Phase 3**: Complete multi-agent workflow orchestration

### 🔄 Active Development
- **Phase 4**: Streamlit web interface development

## 🏗️ Architecture Overview

Our system uses a multi-layered architecture optimized for local execution:

```
┌─────────────────┐
│ Streamlit UI    │ (Phase 4 - In Progress)
├─────────────────┤
│ CrewAI Workflow │ (Phase 3 - Complete)
├─────────────────┤
│ Agent Layer     │ (Phase 2 - Complete)  
├─────────────────┤
│ Foundation      │ (Phase 1 - Complete)
└─────────────────┘
```

### Core Components
- **Multi-Agent System**: 4 specialized agents with Gemini Pro & GPT-4
- **PDF Processing**: Automated document parsing and content extraction
- **Evaluation Framework**: Weighted scoring with WCAG alignment
- **Local Interface**: Streamlit-based web application

## 🧪 Testing & Validation

### Quality Metrics
- **143 tests passing** with 90.28% coverage
- **Comprehensive validation** across all components
- **Real data testing** with sample PDF documents
- **Agent integration testing** with live LLM connections

### Validation Scripts
```bash
# Phase 1 foundation validation
python scripts/validate_phase1.py

# Phase 2 agent demonstration  
python scripts/phase2_demo.py

# Quality gates validation
python scripts/validate_quality_gates.py
```

## 📚 Key Documentation Files

### Essential Reading
1. **[System Overview](architecture/system-overview.md)** - Complete system design
2. **[Development Guide](development/README.md)** - Development workflow
3. **[Setup Guide](development/setup-guide.md)** - Installation instructions
4. **[Master Plan](../plans/master-plan.md)** - Complete project roadmap

### Component Documentation
- **[PDF Parser](api-reference/pdf-parser.md)** - Document processing
- **[LLM Config](api-reference/llm-config.md)** - LLM integration
- **[Evaluation Models](api-reference/evaluation-models.md)** - Data structures
- **[Agent Tools](api-reference/agent-tools.md)** - Specialized agent tools

## 🔧 Development Workflow

### Quick Start
```bash
# Clone and setup
git clone <repository-url>
cd accessibility-eval-crew-two
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Validate installation
python scripts/validate_phase1.py
```

### Development Standards
- **Test-Driven Development**: Write tests before implementation
- **90%+ Test Coverage**: Maintain high quality standards
- **Type Safety**: Comprehensive Pydantic models and type hints
- **Documentation**: Every component thoroughly documented

## 🚀 Future Development

### Phase 4: User Interface (In Progress)
- Streamlit web application
- File upload and processing
- Real-time evaluation display
- Report generation and export

### Local Application Focus
This system is designed for local execution with:
- No external dependencies for core functionality
- Local data processing for privacy
- Streamlit interface for ease of use
- PDF-based input/output workflow

## 📞 Support & Contributing

- **Issues**: Use GitHub Issues for bug reports
- **Development**: Follow [Copilot Instructions](../.github/copilot-instructions.md)
- **Documentation**: Update docs with any changes
- **Testing**: Maintain 90%+ test coverage

---

*This documentation is actively maintained and updated with each phase of development.*

**Last Updated**: February 2025  
**Version**: 3.0.0 (Phase 3 Complete)  
**Status**: Local Application Focus
