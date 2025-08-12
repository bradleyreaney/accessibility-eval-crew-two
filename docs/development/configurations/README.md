# Development Configurations

This directory contains alternative and backup configuration files for development tools.

## Pre-commit Configurations

### Available Configurations
- **[.pre-commit-config-full.yaml](./.pre-commit-config-full.yaml)** - Full pre-commit configuration
  - Comprehensive code quality checks
  - Black formatting, Flake8 linting, security scanning
  - Type checking and documentation validation
  - Use for strict development environments

- **[.pre-commit-config-simple.yaml](./.pre-commit-config-simple.yaml)** - Minimal pre-commit configuration
  - Essential formatting and basic checks only
  - Faster execution for quick iterations
  - Use for rapid prototyping phases

### Active Configuration
The active pre-commit configuration is in the project root: `/.pre-commit-config.yaml`

### Switching Configurations
```bash
# Use full configuration
cp docs/development/configurations/.pre-commit-config-full.yaml .pre-commit-config.yaml

# Use simple configuration  
cp docs/development/configurations/.pre-commit-config-simple.yaml .pre-commit-config.yaml

# Reinstall hooks after switching
pre-commit uninstall
pre-commit install
```

## Usage Notes

- **Full Configuration**: Recommended for main development and CI/CD
- **Simple Configuration**: Useful for rapid prototyping or when dealing with CI/CD performance issues
- **Custom Configuration**: Modify the active `.pre-commit-config.yaml` as needed for specific requirements

## Navigation

- **[← Back to Development Docs](../README.md)**
- **[Pre-commit Setup Guide](../pre-commit-setup.md)**
- **[Quality Assurance →](../quality-assurance/)**
