#!/usr/bin/env python3
"""
Security Verification Script
Tests all security features to ensure proper installation
"""

import sys
from pathlib import Path


def _print_section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def _run_with_traceback(label: str, func) -> bool:
    try:
        return func()
    except Exception as e:
        print(f"❌ {label} error: {e}")
        import traceback
        traceback.print_exc()
        return False


def _run_test(test_name: str, test_func, results: list) -> None:
    try:
        result = test_func()
    except Exception as e:
        print(f"\n❌ {test_name} CRASHED: {e}")
        result = False
    results.append((test_name, result))


def _check_dependencies() -> bool:
    """Check that required dependencies are installed."""
    required_modules = [
        ("fastapi", "fastapi"),
        ("requests", "requests"),
        ("watchdog", "watchdog"),
        ("dotenv", "python-dotenv"),
        ("multipart", "python-multipart"),
        ("uvicorn", "uvicorn"),
        ("langchain_community", "langchain-community"),
        ("crewai", "crewai"),
        ("rich", "rich"),
        ("streamlit", "streamlit"),
        ("pandas", "pandas"),
    ]

    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
            print(f"✅ {package_name} installed")
        except ImportError as e:
            print(f"❌ {package_name} NOT installed: {e}")
            return False
    return True

def test_dependencies():
    """Test that security dependencies are installed."""
    _print_section("1. Testing Security Dependencies")

    assert _check_dependencies() is True


def _check_security_manager() -> bool:
    """Test security manager initialization."""
    _print_section("2. Testing Security Manager")

    def _run() -> bool:
        from security_manager import get_security_manager
        sm = get_security_manager()
        print("✅ SecurityManager initialized")
        
        # Test password hashing
        test_password = "TestPassword123!"
        hashed = sm.hash_password(test_password)
        print(f"✅ Password hashing works (hash length: {len(hashed)})")
        
        # Test password verification
        if sm.verify_password(test_password, hashed):
            print("✅ Password verification works")
        else:
            print("❌ Password verification FAILED")
            return False
        
        # Test wrong password
        if not sm.verify_password("WrongPassword", hashed):
            print("✅ Wrong password correctly rejected")
        else:
            print("❌ Wrong password was accepted!")
            return False
        
        return True

    return _run_with_traceback("SecurityManager", _run)


def test_security_manager():
    """Test security manager initialization."""
    assert _check_security_manager() is True


def _check_encryption() -> bool:
    """Test encryption/decryption."""
    _print_section("3. Testing Encryption")

    def _run() -> bool:
        from security_manager import get_security_manager
        sm = get_security_manager()
        
        test_data = "Secret API Key: sk_test_12345"
        
        # Test encryption
        encrypted = sm.encrypt(test_data)
        print(f"✅ Encryption works (encrypted length: {len(encrypted)})")
        
        # Test decryption
        decrypted = sm.decrypt(encrypted)
        if decrypted == test_data:
            print("✅ Decryption works (data matches)")
        else:
            print(f"❌ Decryption FAILED: got '{decrypted}' expected '{test_data}'")
            return False
        
        return True

    return _run_with_traceback("Encryption", _run)


def test_encryption():
    """Test encryption/decryption."""
    assert _check_encryption() is True


def _check_credential_storage() -> bool:
    """Test credential storage."""
    _print_section("4. Testing Credential Storage")

    def _run() -> bool:
        from security_manager import get_security_manager
        sm = get_security_manager()
        
        test_cred_name = "test_credential"
        test_cred_value = "test_secret_value_12345"
        
        # Store credential
        sm.store_credential(test_cred_name, test_cred_value)
        print(f"✅ Credential stored: {test_cred_name}")
        
        # Load credential
        loaded_value = sm.load_credential(test_cred_name)
        if loaded_value == test_cred_value:
            print("✅ Credential loaded correctly")
        else:
            print(f"❌ Credential mismatch: got '{loaded_value}' expected '{test_cred_value}'")
            return False
        
        # Clean up test credential
        import os
        test_file = Path("data/secrets") / f"{test_cred_name}.enc"
        if test_file.exists():
            os.remove(test_file)
            print("✅ Test credential cleaned up")
        
        return True

    return _run_with_traceback("Credential storage", _run)


def test_credential_storage():
    """Test credential storage."""
    assert _check_credential_storage() is True


def _check_password_strength() -> bool:
    """Test password strength validation."""
    _print_section("5. Testing Password Strength Validation")

    def _run() -> bool:
        from security_manager import get_security_manager
        sm = get_security_manager()
        
        test_cases = [
            ("weak", False, "Should reject weak password"),
            ("Weak123", False, "Should reject 7-char password"),
            ("StrongPassword123!", True, "Should accept strong password"),
            ("VeryStr0ng!Pass", True, "Should accept strong password"),
        ]
        
        for password, should_pass, description in test_cases:
            is_valid, message = sm.validate_password_strength(password)
            
            status = "✅" if is_valid == should_pass else "❌"
                
            print(f"{status} {description}: {message}")
            
            if is_valid != should_pass:
                return False
        
        return True

    return _run_with_traceback("Password strength", _run)


def test_password_strength():
    """Test password strength validation."""
    assert _check_password_strength() is True


def _check_auth_module() -> bool:
    """Test auth module with new security."""
    _print_section("6. Testing Auth Module Integration")

    def _run() -> bool:
        from auth import get_authenticator
        get_authenticator()
        print("✅ Authenticator initialized with security manager")
        
        # Note: We don't test actual authentication here because
        # it requires a database connection. Just verify it loads.
        return True

    return _run_with_traceback("Auth module", _run)


def test_auth_module():
    """Test auth module with new security."""
    assert _check_auth_module() is True


def _check_token_generation() -> bool:
    """Test token and API key generation."""
    _print_section("7. Testing Token Generation")

    def _run() -> bool:
        from security_manager import get_security_manager
        sm = get_security_manager()
        
        # Test token generation
        token = sm.generate_token(32)
        if len(token) >= 32:
            print(f"✅ Token generation works (length: {len(token)})")
        else:
            print(f"❌ Token too short: {len(token)}")
            return False
        
        # Test API key generation
        api_key = sm.generate_api_key()
        if api_key.startswith("sk_") and len(api_key) > 35:
            print(f"✅ API key generation works (length: {len(api_key)})")
        else:
            print(f"❌ API key format invalid: {api_key}")
            return False
        
        return True

    return _run_with_traceback("Token generation", _run)


def test_token_generation():
    """Test token and API key generation."""
    assert _check_token_generation() is True


def _check_master_key() -> bool:
    """Test master key creation and permissions."""
    _print_section("8. Testing Master Key")

    def _run() -> bool:
        from security_manager import get_security_manager
        import os
        get_security_manager()
        
        master_key_path = Path("data/secrets/.master.key")
        
        if master_key_path.exists():
            print(f"✅ Master key exists: {master_key_path}")
            
            # Check permissions on Unix systems
            if os.name != 'nt':  # Not Windows
                stat_info = os.stat(master_key_path)
                permissions = oct(stat_info.st_mode)[-3:]
                if permissions == '600':
                    print(f"✅ Master key permissions correct: {permissions}")
                else:
                    print(f"⚠️  Master key permissions: {permissions} (should be 600)")
            else:
                print("ℹ️  Skipping permission check on Windows")
        else:
            print("⚠️  Master key not yet created (will be created on first use)")
        
        return True

    return _run_with_traceback("Master key", _run)


def test_master_key():
    """Test master key creation and permissions."""
    assert _check_master_key() is True


def main():
    """Run all tests."""
    _print_section("Sentinel Agent v2.2 - Security Verification")
    
    tests = [
        ("Dependencies", _check_dependencies),
        ("Security Manager", _check_security_manager),
        ("Encryption", _check_encryption),
        ("Credential Storage", _check_credential_storage),
        ("Password Strength", _check_password_strength),
        ("Auth Integration", _check_auth_module),
        ("Token Generation", _check_token_generation),
        ("Master Key", _check_master_key),
    ]
    
    results = []
    for test_name, test_func in tests:
        _run_test(test_name, test_func, results)
    
    # Print summary
    _print_section("SUMMARY")
    
    passed = sum(result for _, result in results)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:12} {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All security tests PASSED! System is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
