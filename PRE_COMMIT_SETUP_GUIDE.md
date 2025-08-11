# Pre-commit Hooks Setup Guide

## Overview
Pre-commit hooks have been configured to automatically format code and perform quality checks before each commit, preventing GitHub Actions failures from Black formatting and linting issues.

## Installation

### 1. Install Pre-commit (if not already installed)
```bash
pip install pre-commit
```

### 2. Install the Hooks
```bash
cd /path/to/accessibility-eval-crew-two
pre-commit install
```

### 3. Test the Setup
```bash
# Run hooks on all files to test
pre-commit run --all-files
```

## Configured Hooks

### **Essential Hooks** (Default Configuration)
The current `.pre-commit-config.yaml` includes essential formatting tools:

1. **Black** - Python code formatter
   - Enforces consistent code formatting
   - Line length: 88 characters
   - Automatically fixes formatting issues

2. **isort** - Import sorting
   - Sorts and organizes imports
   - Compatible with Black formatting
   - Maintains consistent import structure

3. **Basic File Checks**
   - Removes trailing whitespace
   - Ensures files end with newlines
   - Validates YAML files
   - Checks for merge conflicts
   - Prevents large file commits (>1MB)

### **Advanced Hooks** (Optional)
The `.pre-commit-config-full.yaml` includes additional tools:

4. **Flake8** - Python linting
   - Code style enforcement
   - Error detection
   - Complexity analysis

5. **Bandit** - Security scanning
   - Identifies common security issues
   - Scans for vulnerable patterns

6. **Pytest** - Test runner
   - Runs unit tests before commit
   - Prevents broken code commits

## Usage

### **Automatic Execution**
Once installed, hooks run automatically on `git commit`:

```bash
git add .
git commit -m "Your commit message"
# Hooks run automatically and may modify files
# If files are modified, you'll need to add and commit again
```

### **Manual Execution**
Run hooks manually when needed:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run black
pre-commit run isort
```

### **Skip Hooks** (Emergency Use Only)
```bash
# Skip all hooks (not recommended)
git commit --no-verify -m "Emergency commit"

# Skip specific hook
SKIP=flake8 git commit -m "Skip linting"
```

## Configuration Files

### `.pre-commit-config.yaml` (Active)
- **Purpose**: Essential formatting and basic checks
- **Speed**: Fast execution
- **Focus**: Code formatting consistency

### `.pre-commit-config-full.yaml` (Available)
- **Purpose**: Comprehensive quality checks
- **Speed**: Slower execution
- **Focus**: Full quality assurance

### `.flake8` 
- **Purpose**: Flake8 linting configuration
- **Settings**: Line length, ignored errors, excluded files
- **Compatibility**: Configured for Black formatting

## Switching Configurations

### Use Full Configuration
```bash
mv .pre-commit-config.yaml .pre-commit-config-simple.yaml
mv .pre-commit-config-full.yaml .pre-commit-config.yaml
pre-commit install
```

### Revert to Simple Configuration
```bash
mv .pre-commit-config.yaml .pre-commit-config-full.yaml
mv .pre-commit-config-simple.yaml .pre-commit-config.yaml
pre-commit install
```

## Troubleshooting

### **Common Issues**

1. **"pre-commit command not found"**
   ```bash
   pip install pre-commit
   ```

2. **Hooks not running**
   ```bash
   pre-commit install
   ```

3. **Hook execution errors**
   ```bash
   pre-commit clean
   pre-commit install
   ```

4. **Black/isort conflicts**
   - Already configured to work together
   - Both use 88-character line length
   - isort uses `--profile=black`

### **Update Hooks**
```bash
pre-commit autoupdate
```

### **Uninstall Hooks**
```bash
pre-commit uninstall
```

## GitHub Actions Integration

The pre-commit hooks prevent the issues that cause GitHub Actions to fail:

### **Before Pre-commit**
- GitHub Actions fail due to formatting issues
- Manual formatting required after failures
- Inconsistent code style in repository

### **After Pre-commit** ✅
- Code automatically formatted before commit
- GitHub Actions pass consistently
- Consistent code style across all commits
- Faster development workflow

## Benefits

### **Developer Experience**
- ✅ **Automatic Formatting**: No manual Black/isort commands
- ✅ **Immediate Feedback**: Catches issues before push
- ✅ **Consistent Style**: Enforced across all commits
- ✅ **Faster CI/CD**: No formatting failures in Actions

### **Code Quality**
- ✅ **Consistent Imports**: Sorted and organized
- ✅ **Clean Files**: No trailing whitespace
- ✅ **Valid Syntax**: Basic validation before commit
- ✅ **Merge Safety**: Conflict detection

### **Team Workflow**
- ✅ **Zero Configuration**: Works automatically after setup
- ✅ **Fast Execution**: Essential hooks run in <10 seconds
- ✅ **Customizable**: Easy to enable/disable specific tools
- ✅ **CI/CD Ready**: Prevents GitHub Actions failures

## Next Steps

1. **Install hooks**: `pre-commit install`
2. **Test setup**: `pre-commit run --all-files`
3. **Start committing**: Hooks run automatically
4. **Optional**: Switch to full configuration if desired

The pre-commit setup ensures that code formatting issues that previously caused GitHub Actions failures are caught and fixed locally before commits reach the repository.

---
*Generated: August 2025*
*Pre-commit Version: 3.4.0+*
*Compatibility: Black 24.8.0, isort 5.13.2*
