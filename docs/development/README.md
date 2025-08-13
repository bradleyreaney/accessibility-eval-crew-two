# Development Documentation

This directory contains comprehensive development documentation for the LLM-as-a-Judge accessibility evaluation system.

## 📚 Documentation Structure

### 🚀 Getting Started
- **[setup-guide.md](./setup-guide.md)** - Complete development environment setup
- **[pre-commit-setup.md](./pre-commit-setup.md)** - Pre-commit hooks configuration for code quality

### 🏗️ CI/CD Pipeline  
- **[ci-cd-pipeline.md](./ci-cd-pipeline.md)** - CI/CD pipeline overview and configuration
- **[ci-cd-github-actions.md](./ci-cd-github-actions.md)** - Detailed GitHub Actions implementation

### 📊 Project Progress
- **[phase-reports/](./phase-reports/)** - Development phase completion reports
  - Phase 1: Foundation & PDF Processing ✅
  - Phase 2: CrewAI Multi-Agent System ✅
  - Future phases roadmap

### 🔍 Quality Assurance
- **[quality-assurance/](./quality-assurance/)** - Code quality, testing, and validation
  - Quality gates and standards
  - Test coverage reports (91% maintained with 212 tests)
  - Test organization mirrors source structure
  - TDD implementation results
  - Pre-commit validation processes

## 🎯 Development Standards

### Code Quality Requirements
- **Test Coverage**: 91%+ maintained across all modules (212 tests)
- **Test Organization**: Tests mirror source code directory structure
- **Code Formatting**: Black formatting enforced
- **Linting**: Flake8 standards with zero errors
- **Type Safety**: mypy static analysis passing
- **Security**: Bandit scanning with no vulnerabilities
- **Documentation**: Comprehensive docstrings required

### Development Workflow
1. **Feature Development**: Create feature branch from main
2. **Pre-commit Hooks**: Automatic code formatting and validation
3. **Testing**: Write tests before implementation (TDD approach)
4. **Quality Gates**: All quality checks must pass
5. **Code Review**: Peer review required before merge
6. **CI/CD Pipeline**: Automated testing and validation

## 🛠️ Development Tools

### Core Tools
- **Python 3.11+**: Primary development language
- **CrewAI**: Multi-agent framework for LLM coordination
- **pytest**: Testing framework with comprehensive coverage
- **Black**: Code formatting
- **Flake8**: Code linting and style checking
- **mypy**: Static type checking
- **Bandit**: Security vulnerability scanning

### CI/CD Tools
- **GitHub Actions**: Automated testing and quality gates
- **Pre-commit**: Local code quality checks
- **Coverage.py**: Test coverage measurement
- **codecov**: Coverage reporting and tracking

## 📈 Current Status

### Phase 2 Complete ✅
- **CrewAI Multi-Agent System**: Fully implemented with 4 core agents
- **Quality Standards**: All quality gates passing consistently
- **Test Coverage**: 90.02% maintained with comprehensive test suite
- **CI/CD Pipeline**: Optimized from 20+ minute timeouts to 3-4 minute runs
- **Documentation**: Enterprise-grade documentation standards

### Ready for Phase 3
- Multi-agent workflows and coordination
- Advanced evaluation consensus mechanisms
- Performance optimization and scaling

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
