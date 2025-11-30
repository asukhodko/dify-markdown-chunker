# GitHub Configuration

This directory contains GitHub-specific configuration files.

## Recommended Workflows

### CI/CD Pipeline

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        source venv/bin/activate
        make test
    
    - name: Run linter
      run: |
        source venv/bin/activate
        make lint
    
    - name: Validate structure
      run: |
        source venv/bin/activate
        make validate

  package:
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dify-plugin CLI
      run: |
        curl -L https://github.com/langgenius/dify-plugin-daemon/releases/latest/download/dify-plugin-linux-amd64 -o /tmp/dify-plugin
        chmod +x /tmp/dify-plugin
        sudo mv /tmp/dify-plugin /usr/local/bin/dify-plugin
    
    - name: Build package
      run: make package
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: plugin-package
        path: '*.difypkg'
```

### Release Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    
    - name: Install dify-plugin CLI
      run: |
        curl -L https://github.com/langgenius/dify-plugin-daemon/releases/latest/download/dify-plugin-linux-amd64 -o /tmp/dify-plugin
        chmod +x /tmp/dify-plugin
        sudo mv /tmp/dify-plugin /usr/local/bin/dify-plugin
    
    - name: Run tests
      run: |
        source venv/bin/activate
        make test
    
    - name: Build package
      run: make package
    
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: '*.difypkg'
        generate_release_notes: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Configure plugin with '...'
2. Process document '...'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment:**
 - Dify version: [e.g. 1.9.0]
 - Plugin version: [e.g. 2.0.0]
 - Python version: [e.g. 3.12]

**Additional context**
Add any other context about the problem here.
```

Create `.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

## Pull Request Template

Create `.github/pull_request_template.md`:

```markdown
## Description

Please include a summary of the changes and which issue is fixed.

Fixes # (issue)

## Type of change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Checklist:

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Testing

Please describe the tests that you ran to verify your changes:

- [ ] Test A
- [ ] Test B

**Test Configuration**:
* Python version:
* Dify version:
```
