# Development Documentation

This directory contains comprehensive development documentation for the LLM-as-a-Judge accessibility evaluation system - a local AI application for accessibility professionals.

## 📚 Documentation Structure

### 🚀 Getting Started
- **[setup-guide.md](./setup-guide.md)** - Complete development environment setup

### 📊 Project Progress
- **[phase-reports/](./phase-reports/)** - Development phase completion reports
  - Phase 1: Foundation & PDF Processing ✅
  - Phase 2: CrewAI Multi-Agent System ✅
  - Phase 3: Workflow Orchestration ✅
  - Phase 4: User Interface ✅ COMPLETE
  - Phase 5: Advanced Features & Optimization ✅ COMPLETE

### 🔍 Quality Assurance
- **[quality-assurance/](./quality-assurance/)** - Code quality, testing, and validation
  - Quality gates and standards
  - Test coverage reports (91% maintained with 305 tests)
  - Test organization mirrors source structure
  - TDD implementation results
  - Local development validation

## 🎯 Development Standards

### Code Quality Requirements
- **Test Coverage**: 91%+ maintained across all modules (305 tests)
- **Test Organization**: Tests mirror source code directory structure
- **Code Formatting**: Black formatting enforced
- **Linting**: Flake8 standards with zero errors
- **Type Safety**: mypy static analysis passing
- **Documentation**: Comprehensive docstrings required

### Development Workflow
1. **Feature Development**: Create feature branch from main
2. **Local Validation**: Run quality checks locally
3. **Testing**: Write tests before implementation (TDD approach)
4. **Quality Gates**: All quality checks must pass
5. **Code Review**: Peer review for significant changes
6. **Local Testing**: Comprehensive local validation

## 🛠️ Development Tools

### Core Tools
- **Python 3.11+**: Primary development language
- **CrewAI**: Multi-agent framework for LLM coordination
- **pytest**: Testing framework with comprehensive coverage
- **Black**: Code formatting
- **Flake8**: Code linting and style checking
- **mypy**: Static type checking
- **Streamlit**: Local web interface (Phase 4)

### Local Development Tools
- **Virtual Environment**: Python venv for dependency isolation
- **Coverage.py**: Test coverage measurement
- **Local Scripts**: Quality validation and demo scripts
- **codecov**: Coverage reporting and tracking

## 📈 Current Project Status

### Phase 1 Complete ✅
- **Foundation Infrastructure**: PDF processing, LLM integration, evaluation models
- **Quality Standards**: 82% test coverage maintained
- **Core Components**: All foundation components operational and tested

### Phase 2 Complete ✅
- **CrewAI Multi-Agent System**: Fully implemented with 4 core agents
- **Agent Tools**: 4 specialized tools for evaluation framework
- **Quality Standards**: All quality gates passing consistently
- **Test Coverage**: 82% maintained with comprehensive test suite
- **Documentation**: Complete agent development documentation

### Phase 3 Complete ✅
- **Workflow Orchestration**: CrewAI task management and crew coordination
- **Task Management**: Evaluation, comparison, and synthesis tasks implemented
- **Multi-Agent Coordination**: Complete end-to-end workflow execution
- **Integration Testing**: Comprehensive workflow validation

### Phase 5 Complete ✅ **ENTERPRISE-READY**
- **Advanced Consensus Mechanisms**: Multi-level conflict resolution, evidence quality assessment
- **Batch Processing System**: Parallel evaluation, concurrent processing, scalable operations  
- **Performance Monitoring**: Real-time metrics, intelligent caching (85%+ hit rate), optimization recommendations
- **Production Ready**: Enterprise-grade implementation with 305 tests, 91% coverage, full automation

## 🔧 Local Development Focus

### Local Application Benefits
- **Data Privacy**: All processing done locally, no external data transmission
- **Network Independence**: Works offline after initial API key setup
- **Easy Customization**: Modify evaluation criteria and workflows easily
- **Full Control**: Complete control over evaluation process and data

### Development Environment
- **Python 3.11+**: Robust local development environment
- **Virtual Environment**: Complete dependency isolation
- **Local Testing**: Comprehensive local validation and testing
- **Quality Scripts**: Local quality gate validation

## 🔗 Navigation

### Quick Links
- **[Architecture Overview](../architecture/system-overview.md)**
- **[Setup Guide](./setup-guide.md)**
- **[Project Plans](../../plans/)**
- **[API Reference](../api-reference/)**

### External Resources
- **[CrewAI Documentation](https://docs.crewai.com/)**
- **[WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)**
- **[Streamlit Documentation](https://docs.streamlit.io/)**

## 🤝 Contributing

### Before You Start
1. Review the [setup guide](./setup-guide.md)
2. Understand the local development workflow
3. Check current [project plans](../../plans/) for context
4. Familiarize yourself with the simplified local-only approach

### Development Process
1. **Create Issue**: Document the feature or bug
2. **Feature Branch**: Create from latest main
3. **Implement**: Follow TDD approach with comprehensive testing
4. **Quality Gates**: Ensure all checks pass locally
5. **Pull Request**: Submit with detailed description
6. **Review**: Address feedback and iterate
7. **Merge**: Local validation and testing

### Local Development Standards
- **90%+ Test Coverage**: Maintain high testing standards
- **Local Validation**: Use `scripts/validate_quality_gates.py`
- **Documentation**: Update docs with any changes
- **Local Focus**: Ensure all features work in local environment

For detailed contribution guidelines, see the main project README.

## 🔗 Navigation

### Quick Links
- **[Architecture Overview](../architecture/system-overview.md)**
- **[API Reference](../api-reference/)**
- **[Troubleshooting](../troubleshooting/)**
- **[Examples](../examples/)**

### External Resources
- **[CrewAI Documentation](https://docs.crewai.com/)**
- **[WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)**
- **[LangChain Documentation](https://python.langchain.com/)**

## 🤝 Contributing

### Before You Start
1. Review the [setup guide](./setup-guide.md)
2. Configure [pre-commit hooks](./pre-commit-setup.md)
3. Understand the [quality standards](./quality-assurance/)
4. Check current [phase reports](./phase-reports/) for context

### Development Process
1. **Create Issue**: Document the feature or bug
2. **Feature Branch**: Create from latest main
3. **Implement**: Follow TDD approach with comprehensive testing
4. **Quality Gates**: Ensure all checks pass locally
5. **Pull Request**: Submit with detailed description
6. **Review**: Address feedback and iterate
7. **Merge**: Automated deployment after approval

For detailed contribution guidelines, see the main project README.
