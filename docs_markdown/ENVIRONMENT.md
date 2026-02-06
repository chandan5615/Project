# Sentinel Agent - Environment Management

This guide ensures all dependencies are kept in one isolated virtual environment.

## Quick Start

### Linux/macOS
```bash
# 1. Setup (one-time)
./setup.sh

# 2. Activate environment (each session)
source venv/bin/activate
# OR use the quick script:
./activate_env.sh

# 3. Run Sentinel Agent
sudo python main.py
```

### Windows
```powershell
# PowerShell
.\setup.ps1
.\venv\Scripts\Activate.ps1
sudo python main.py

# OR CMD
setup.bat
venv\Scripts\activate.bat
sudo python main.py
```

## Why Use a Virtual Environment?

- **Isolation**: Keeps Sentinel Agent dependencies separate from system Python
- **Reproducibility**: Ensures consistent versions across different machines
- **Clean Management**: Easy to remove and recreate if needed
- **No Conflicts**: Prevents conflicts with other Python projects

## Environment Structure

```
Sentinel Agent/
├── venv/              # Virtual environment (created by setup script)
│   ├── bin/           # Executables (Linux/macOS)
│   ├── Scripts/        # Executables (Windows)
│   ├── lib/            # Installed packages
│   └── ...
├── requirements.txt    # Dependency list
└── ...
```

## Verifying Your Environment

The `main.py` script automatically checks:
- ✅ If you're in a virtual environment
- ✅ If all required dependencies are installed

You can skip the check with:
```bash
python main.py --skip-env-check
```

## Managing Dependencies

### Adding a New Package
1. Activate environment: `source venv/bin/activate`
2. Install: `pip install package-name`
3. Update requirements: `pip freeze > requirements.txt`

### Recreating Environment
```bash
# Remove old environment
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# Recreate
./setup.sh  # or setup.ps1 / setup.bat
```

## Troubleshooting

### "Module not found" errors
- Ensure virtual environment is activated
- Check: `which python` should point to `venv/bin/python`
- Reinstall: `pip install -r requirements.txt`

### Environment not activating
- Verify Python 3.10+ is installed: `python --version`
- Try recreating: Delete `venv/` and run setup script again

### Permission errors
- Use `sudo` only for running Sentinel Agent (for log access)
- Don't use `sudo` for `pip install` (installs to system Python)

## Best Practices

1. **Always activate** the environment before running Sentinel Agent
2. **Never commit** `venv/` to git (already in .gitignore)
3. **Update requirements.txt** when adding new dependencies
4. **Use the same Python version** across development and production
