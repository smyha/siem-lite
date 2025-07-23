# Contributing to SIEM Lite

Thank you for your interest in contributing to SIEM Lite! This document provides guidelines for contributing to the project.

## 🤝 Ways to Contribute

### 🐛 Bug Reports
- Use the [GitHub Issues](https://github.com/siem-lite/siem-lite/issues) to report bugs
- Include detailed reproduction steps
- Provide system information (OS, Python version, etc.)

### 💡 Feature Requests
- Use GitHub Issues with the "enhancement" label
- Clearly describe the feature and its use case
- Discuss the implementation approach

### 🔧 Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Submit a pull request

## 🛠️ Development Setup

### Prerequisites
- Python 3.9+
- Git

### Setup Instructions

```bash
# Clone your fork
git clone https://github.com/your-username/siem-lite.git
cd siem-lite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run code quality checks
black .
isort .
flake8
mypy .
```

## 📋 Code Standards

### Python Code Style
- Follow PEP 8
- Use Black for formatting: `black .`
- Use isort for imports: `isort .`
- Maximum line length: 88 characters

### Type Hints
- Use type hints for all function parameters and return values
- Run mypy for type checking: `mypy .`

### Documentation
- Document all public functions and classes
- Use Google-style docstrings
- Update README.md for user-facing changes

### Testing
- Write tests for all new functionality
- Maintain minimum 80% code coverage
- Use pytest for testing framework

## 🔍 Code Review Process

1. All contributions require code review
2. Maintainers will review pull requests
3. Address feedback and update the PR
4. Squash commits before merging

## 🏷️ Commit Message Format

Use conventional commits format:

```
type(scope): description

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(cli): add interactive dashboard command
fix(api): resolve authentication token validation
docs(readme): update installation instructions
```

## 🌟 Recognition

Contributors will be acknowledged in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributors page

## 📞 Getting Help

- Join our [Discussions](https://github.com/siem-lite/siem-lite/discussions)
- Ask questions in GitHub Issues
- Contact maintainers via GitHub

## 📜 Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct. Please be respectful and inclusive in all interactions.

## 🔒 Security

For security vulnerabilities, please email security@siem-lite.dev instead of creating a public issue.

Thank you for contributing to SIEM Lite! 🚀
