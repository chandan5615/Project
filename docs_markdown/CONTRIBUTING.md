# Contributing to Sentinel Agent

Thank you for your interest in contributing to Sentinel Agent! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on security and reliability
- No harassment, discrimination, or abusive language

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Linux development environment
- Ollama installed and running (for testing)
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourorg/sentinel-agent.git
cd sentinel-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# Run tests
python -m pytest -q
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-xxx` — New feature
- `fix/issue-xxx` — Bug fix
- `docs/update-xxx` — Documentation update
- `refactor/improve-xxx` — Code refactoring
- `test/add-xxx` — Test additions

### Commit Messages

Follow these guidelines:

```
[type] Brief description (50 chars max)

Longer explanation if needed (wrap at 72 chars)
- Point 1
- Point 2

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Code Style

- Follow PEP 8 with `black` for formatting
- Use type hints for all functions
- Docstrings for modules, classes, and public functions
- Maximum line length: 100 characters

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

### Testing

- Write tests for all new features
- Ensure all tests pass: `python -m pytest -q`
- Aim for >80% code coverage
- Test both happy path and edge cases

```python
# Example test
def test_ip_validation_rejects_invalid():
    result = validate_ip("192.168.abc.1")
    assert result is False

def test_ip_validation_accepts_valid():
    result = validate_ip("192.168.1.1")
    assert result is True
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code and tests
   - Update documentation
   - Format with `black`
   - Run `pytest` and `mypy`

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "[feat] Add your feature description"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Use a clear title describing the change
   - Reference any related issues (#123)
   - Describe what changed and why
   - Include test results

### PR Requirements

- [ ] Tests pass (`pytest -q`)
- [ ] Code formatted (`black .`)
- [ ] Type hints complete (`mypy .`)
- [ ] Documentation updated
- [ ] Commit messages follow guidelines
- [ ] No breaking changes (unless major version)

## Reporting Issues

### Bug Reports

Include:
- System information (OS, Python version)
- Reproduction steps
- Expected behavior
- Actual behavior
- Error messages and logs
- Relevant code snippets

```
**System**: Ubuntu 22.04, Python 3.11
**Steps to reproduce**:
1. Start sentinel agent
2. Monitor /var/log/auth.log
3. Generate failed login

**Expected**: Alert is triggered
**Actual**: No alert received

**Error logs**: [paste relevant log excerpt]
```

### Feature Requests

Describe:
- Use case and motivation
- Expected behavior
- How it benefits users
- Any alternative approaches considered

## Documentation

### README

- Keep concise and up-to-date
- Include quick-start instructions
- Link to detailed documentation

### Code Documentation

```python
def validate_ip(ip_string: str) -> bool:
    """
    Validate an IPv4 address format.
    
    Args:
        ip_string: IP address string to validate
        
    Returns:
        True if valid IPv4, False otherwise
        
    Raises:
        ValueError: If input is not a string
    """
```

### CHANGELOG

Update with each PR:
- Add entry under [Unreleased]
- Reference related issues/PRs
- Keep format consistent

## Security

### Reporting Security Issues

**Do not open public issues for security vulnerabilities.**

Email security concerns to: [security@example.com]

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

- Always validate user input
- Use type hints for clarity
- Keep dependencies updated
- Review for SQL injection risks
- Avoid hardcoding credentials
- Use environment variables for secrets

## Architecture Guidelines

### Adding New Sensors

```python
# sensors/new_sensor.py
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class NewSensor(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
    
    def on_modified(self, event):
        # Implement detection logic
        if self.detect_threat(event):
            self.callback(threat_info)
```

### Adding New Tools

```python
# tools/tools.py
@tool
def new_security_tool(input_param: str) -> str:
    """
    Brief description.
    
    Args:
        input_param: Description
        
    Returns:
        Description of return value
    """
    return result
```

### Adding New Agents

```python
# agents.py
agent = Agent(
    role="Role Name",
    goal="Goal of this agent",
    backstory="Background and expertise",
    tools=[tool1, tool2],
    verbose=True,
)
```

## Performance Considerations

- Log rotation: Monitor inode changes
- File I/O: Use efficient read patterns
- Database: Index frequently queried columns
- Memory: Clean up old data periodically
- API: Cache threat intel results

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes (2.0 → 3.0)
- MINOR: New features, backward compatible (2.1 → 2.2)
- PATCH: Bug fixes (2.1.0 → 2.1.1)

## License

By contributing, you agree your code is licensed under the same license as the project.

---

**Thank you for contributing to Sentinel Agent! **

Questions? Open an issue or email maintainers@example.com
