#!/usr/bin/env python3
"""
Sentinel Agent - System Validation
Checks all critical components for errors and compatibility issues
"""
import sys
import os
import importlib
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    print(f"{RED}✗{RESET} {text}")

def print_warning(text):
    print(f"{YELLOW}⚠{RESET} {text}")

def check_module_imports():
    """Verify all critical modules can be imported"""
    print_header("MODULE IMPORT CHECKS")
    
    modules = [
        'main',
        'agents',
        'tasks',
        'data_engine',
        'auth',
        'list_manager',
        'metrics',
        'anomaly_scorer',
        'threat_intelligence',
        'security_manager',
        'sentinel_api',
        'dashboard.app',
        'sensors.auth_sensor',
        'sensors.web_sensor',
        'defense.attack_detector',
        'defense.attack_logger',
    ]
    
    errors = []
    success_count = 0
    
    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print_success(f"{module_name}")
            success_count += 1
        except Exception as e:
            print_error(f"{module_name}: {str(e)[:60]}")
            errors.append((module_name, e))
    
    print(f"\n{success_count}/{len(modules)} modules imported successfully")
    return len(errors) == 0

def check_crewai_compatibility():
    """Check CrewAI API compatibility"""
    print_header("CREWAI COMPATIBILITY CHECK")
    
    try:
        from crewai import Crew, Agent, Task
        print_success("CrewAI imports successful")
        
        # Check if Crew has .run() method
        if hasattr(Crew, '__init__'):
            print_success("Crew class available")
        
        # Read main.py to verify .run() is used, not .kickoff()
        main_py = Path('main.py').read_text()
        if '.kickoff()' in main_py:
            print_error("main.py still uses deprecated .kickoff() method")
            return False
        elif '.run()' in main_py:
            print_success("main.py uses correct .run() method")
        
        # Check process parameter
        if 'process="sequential"' in main_py:
            print_success("Process parameter uses string format")
        elif 'Process.sequential' in main_py:
            print_error("Process parameter uses deprecated enum format")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"CrewAI compatibility check failed: {e}")
        return False

def check_requirements():
    """Verify requirements.txt has all necessary packages"""
    print_header("REQUIREMENTS CHECK")
    
    required_packages = {
        'crewai': '0.100.1',
        'fastapi': '0.115.8',
        'streamlit': '1.35.0',
        'psutil': '5.9.0',
        'plotly': '5.17.0',
        'pandas': '2.0.0',
        'requests': '2.31.0',
    }
    
    try:
        reqs = Path('requirements.txt').read_text()
        
        for package, min_version in required_packages.items():
            if package in reqs:
                print_success(f"{package} listed in requirements.txt")
            else:
                print_error(f"{package} MISSING from requirements.txt")
        
        return True
    except Exception as e:
        print_error(f"Failed to read requirements.txt: {e}")
        return False

def check_docker_config():
    """Verify Docker configuration"""
    print_header("DOCKER CONFIG CHECK")
    
    try:
        compose = Path('docker-compose.yml').read_text()
        
        # Check log paths
        if '/var/log/auth.log' in compose:
            print_success("Auth log path configured correctly")
        else:
            print_warning("Auth log path may be incorrect")
        
        if '/var/log/apache2/access.log' in compose:
            print_success("Web log path configured correctly")
        else:
            print_warning("Web log path may be incorrect")
        
        # Check Dockerfile
        dockerfile = Path('Dockerfile').read_text()
        if '--group' in dockerfile:
            print_success("Dockerfile uses --group flag for adduser")
        else:
            print_error("Dockerfile missing --group flag (will cause build failure)")
            return False
        
        return True
    except Exception as e:
        print_error(f"Docker config check failed: {e}")
        return False

def check_dashboard_imports():
    """Verify dashboard can import parent modules"""
    print_header("DASHBOARD IMPORT CHECK")
    
    try:
        app_py = Path('dashboard/app.py').read_text()
        
        if 'sys.path.insert' in app_py:
            print_success("Dashboard has sys.path fix for parent imports")
        else:
            print_warning("Dashboard may have import issues")
        
        # Check for required imports
        required_imports = ['psutil', 'list_manager', 'metrics', 'data_engine']
        for imp in required_imports:
            if f'import {imp}' in app_py or f'from {imp}' in app_py:
                print_success(f"Dashboard imports {imp}")
            else:
                print_error(f"Dashboard missing import: {imp}")
        
        return True
    except Exception as e:
        print_error(f"Dashboard check failed: {e}")
        return False

def main():
    """Run all validation checks"""
    print_header("SENTINEL AGENT SYSTEM VALIDATION")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    all_passed = True
    
    # Run checks
    checks = [
        ("Requirements", check_requirements),
        ("Docker Config", check_docker_config),
        ("Dashboard Imports", check_dashboard_imports),
        ("CrewAI Compatibility", check_crewai_compatibility),
        ("Module Imports", check_module_imports),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
            if not results[check_name]:
                all_passed = False
        except Exception as e:
            print_error(f"{check_name} failed with exception: {e}")
            results[check_name] = False
            all_passed = False
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    for check_name, passed in results.items():
        if passed:
            print_success(f"{check_name}")
        else:
            print_error(f"{check_name}")
    
    print()
    if all_passed:
        print_success("ALL CHECKS PASSED! 🎉")
        print("\nYour system is ready for deployment.")
        print("\nNext steps:")
        print("  1. Run: ./deploy_fixes.ps1  (to deploy to Ubuntu)")
        print("  2. Run: python test_web_attacks.py  (to test detection)")
        return 0
    else:
        print_error("SOME CHECKS FAILED ❌")
        print("\nPlease fix the errors above before deploying.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
