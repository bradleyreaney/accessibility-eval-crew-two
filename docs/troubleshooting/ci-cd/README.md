# CI/CD Troubleshooting

This directory contains troubleshooting guides and fix documentation for CI/CD pipeline issues.

## GitHub Actions Issues & Fixes

### Major CI/CD Improvements
- **[github-actions-complete-fix.md](./github-actions-complete-fix.md)** - Complete GitHub Actions fixes
  - Pipeline optimization solutions
  - Dependency resolution improvements
  - Timeout and performance fixes

- **[github-actions-fix.md](./github-actions-fix.md)** - Core GitHub Actions troubleshooting
  - Common CI/CD issues and solutions
  - Workflow configuration fixes
  - Build and test failures resolution

### Phase-Specific CI/CD Fixes
- **[phase2-github-actions-fixes.md](./phase2-github-actions-fixes.md)** - Phase 2 specific CI/CD issues
  - CrewAI dependency challenges
  - Multi-LLM integration testing
  - Agent-specific testing pipeline adjustments

## Common Issues & Solutions

### Pipeline Performance
- **Timeout Issues**: Resolved 20+ minute timeouts → 3-4 minute runs
- **Dependency Installation**: Ultra-minimal `requirements-ci.txt` approach
- **Caching Strategy**: Optimized pip caching for faster builds
- **Parallel Testing**: Multi-Python version testing (3.11 & 3.12)

### Quality Gates
- **Test Coverage**: Maintaining 90%+ coverage in CI
- **Code Quality**: Black, Flake8, mypy integration
- **Security Scanning**: Bandit security validation
- **Documentation**: Automated docstring validation

### Integration Testing
- **API Key Management**: Secure secrets handling
- **LLM Integration**: Mocked vs. real API testing
- **Environment Variables**: CI/CD environment configuration

## Navigation

- **[← Back to Troubleshooting](../README.md)**
- **[Testing Issues →](../testing/)**
- **[Development Docs →](../../development/)**
- **[Quality Assurance →](../../development/quality-assurance/)**

## Quick Reference

### Pipeline Status Check
```bash
gh run list --branch phase-two --limit 5
gh run view <run-id>
```

### Local Quality Validation
```bash
python scripts/validate_quality_gates.py
```

### CI/CD Best Practices
- Use `requirements-ci.txt` for minimal CI dependencies
- Pin exact versions for reproducible builds
- Configure appropriate timeouts for each step
- Use caching for dependency installation
- Run quality gates in parallel where possible
