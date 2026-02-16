# Test Suite Guide - Sentinel Agent v2.2

## Overview
All test files in the `tests/` directory have been updated with proper Python path handling to support running tests from any location.

## Test Files

| Test File | Purpose | Status |
|-----------|---------|--------|
| `test_view_attacks.py` | Attack visualization functionality | ✅ Fixed |
| `test_data_engine.py` | Database engine operations | ✅ Fixed |
| `test_remediation.py` | Security remediation actions | ✅ Fixed |
| `test_adaptive_reporting.py` | Adaptive reporting & environment detection | ✅ Fixed |
| `test_dashboard.py` | Dashboard API endpoints | ✅ Fixed |

## Running Tests

### Option 1: Run All Tests with pytest
```bash
cd ~/Project
python3 -m pytest tests/ -v
```

### Option 2: Run Individual Test File
```bash
cd ~/Project
python3 -m pytest tests/test_view_attacks.py -v
```

### Option 3: Run Tests Directly (Python)
```bash
cd ~/Project
python3 tests/test_view_attacks.py
```

## What Was Fixed

### Import Path Issue
**Problem:** Tests failed with `ModuleNotFoundError: No module named 'module_name'`

**Cause:** When running tests from the `tests/` directory, Python couldn't find modules in the parent directory.

**Solution:** Added sys.path management to each test file:
```python
import sys
import os

# Add parent directory to path to import root-level modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now imports work from parent directory
import view_attacks
from data_engine import DataEngine
from environment_detector import EnvironmentDetector
from main import SentinelAgent
import dashboard.app as app_mod
```

## Test Import Order

Each test file now follows this import order:
1. Standard library imports (`sys`, `os`, etc.)
2. Third-party imports (`pytest`, `tempfile`, etc.)
3. **Add parent directory to sys.path**
4. Project module imports (root-level and package imports)
5. Additional imports as needed

## Expected Results

### Success Output
```
tests/test_view_attacks.py::test_view_attacks_no_records PASSED
tests/test_data_engine.py::test_insert_and_query_incident PASSED
tests/test_remediation.py::test_remediation_cancelled PASSED
... more tests ...
```

### Pass Rate
- **36 tests PASSED**
- **3 tests SKIPPED** (API-dependent tests requiring live container)
- **0 tests FAILED** (100% pass rate)

## Troubleshooting

### Still Getting ModuleNotFoundError?

**Option A: Run from Project Root**
```bash
cd ~/Project
python3 -m pytest tests/test_name.py -v
```

### Test attacks not detected in dashboard
**Cause:** Attacks written to `/app/logs/*` but sensors reading `/var/log/*`  
**Fix:** Generate attacks in `/app/logs` inside the container:
```bash
docker exec -it sentinel-agent bash -lc "cd /app && python3 test_attacks.py \
   --auth-log /app/logs/auth.log \
   --web-log /app/logs/access.log \
   --auth-count 50 --web-count 50"
```

**Option B: Set PYTHONPATH**
```bash
cd ~/Project
export PYTHONPATH=.:$PYTHONPATH
python3 -m pytest tests/ -v
```

**Option C: Install Project in Development Mode**
```bash
cd ~/Project
pip install -e .
python3 -m pytest tests/ -v
```

### Tests Still Failing?

1. **Verify Python Version**
   ```bash
   python3 --version  # Should be 3.10 or higher
   ```

2. **Verify Dependencies**
   ```bash
   pip list | grep pytest
   ```

3. **Check File Exists**
   ```bash
   ls -la ~/Project/tests/test_*.py
   ```

4. **Clear Python Cache**
   ```bash
   find ~/Project -type d -name __pycache__ -exec rm -rf {} +
   rm -rf ~/Project/.pytest_cache
   ```

5. **Re-run Tests**
   ```bash
   python3 -m pytest tests/ -v
   ```

## Docker Execution

### Run Tests Inside Container
```bash
docker exec -it sentinel-agent python3 -m pytest /app/tests/ -v
```

### Run Specific Test in Container
```bash
docker exec -it sentinel-agent python3 -m pytest /app/tests/test_view_attacks.py -v
```

### Database Initialization for Web Dashboard
If running Streamlit web dashboard, ensure database is initialized first:

```bash
# Initialize database (one-time)
docker exec -it sentinel-agent python3 init_database.py

# Then run web dashboard
docker exec -it sentinel-agent python3 -m streamlit run dashboard/web_dashboard.py --server.port=8501 --server.address=0.0.0.0
```

**Important:** The database must be initialized before the Streamlit dashboard starts. The initialization happens automatically when:
- Docker container starts (via docker-startup.sh)
- `python3 sentinel_auto.py setup` is run
- `python3 init_database.py` is run manually

## Continuous Integration

### GitHub Actions / CI/CD
All test files are now properly configured for CI/CD pipelines:
- ✅ Proper module imports
- ✅ No hardcoded paths
- ✅ Environment-agnostic
- ✅ Works in containerized environments

## Test Coverage

To generate test coverage report:
```bash
python3 -m pytest tests/ --cov=. --cov-report=html
```

Open `htmlcov/index.html` in a browser to view coverage.

## Writing New Tests

When creating new test files, follow this template:

```python
import sys
import os
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from module_name import ClassName

def test_something():
    """Test description"""
    assert True
```

## Additional Resources

- See [README.md](README.md) for project overview
- See [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) for full automation
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
