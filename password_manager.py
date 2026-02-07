#!/usr/bin/env python3
"""
Password Management Utility
Manage passwords and credentials securely for Sentinel Agent.
"""

import sys
import getpass
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from auth import get_authenticator
from security_manager import get_security_manager


def change_password():
    """Change user password."""
    print("\n=== Change Password ===\n")
    
    username = input("Username: ")
    old_password = getpass.getpass("Current Password: ")
    new_password = getpass.getpass("New Password: ")
    confirm_password = getpass.getpass("Confirm New Password: ")
    
    if new_password != confirm_password:
        print("❌ Error: Passwords don't match")
        return
    
    auth = get_authenticator()
    success, message = auth.change_password(username, old_password, new_password)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")


def create_user():
    """Create new user."""
    print("\n=== Create New User ===\n")
    
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")
    
    if password != confirm_password:
        print("❌ Error: Passwords don't match")
        return
    
    print("\nRoles:")
    print("  1. admin    - Full access")
    print("  2. analyst  - Normal access")
    print("  3. viewer   - Read-only access")
    
    role_choice = input("\nSelect role (1-3): ").strip()
    role_map = {"1": "admin", "2": "analyst", "3": "viewer"}
    role = role_map.get(role_choice, "analyst")
    
    auth = get_authenticator()
    success, message = auth.create_user(username, password, role)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")


def create_api_key():
    """Create API key."""
    print("\n=== Create API Key ===\n")
    
    username = input("Username: ")
    key_name = input("API Key Name: ")
    
    auth = get_authenticator()
    api_key = auth.create_api_key(username, key_name)
    
    if api_key:
        print(f"\n✅ API Key created successfully!")
        print(f"\nAPI Key: {api_key}")
        print("\n⚠️  SAVE THIS KEY NOW - It won't be shown again!")
    else:
        print(f"❌ Failed to create API key")


def encrypt_credential():
    """Encrypt and store credential."""
    print("\n=== Encrypt Credential ===\n")
    
    name = input("Credential name (e.g., 'db_password'): ")
    value = getpass.getpass("Credential value: ")
    
    security = get_security_manager()
    security.store_credential(name, value)
    
    print(f"✅ Credential '{name}' encrypted and stored")


def decrypt_credential():
    """Decrypt and display credential."""
    print("\n=== Decrypt Credential ===\n")
    
    name = input("Credential name: ")
    
    security = get_security_manager()
    value = security.load_credential(name)
    
    if value:
        print(f"\nCredential value: {value}")
    else:
        print(f"❌ Credential '{name}' not found")


def test_password_strength():
    """Test password strength."""
    print("\n=== Test Password Strength ===\n")
    
    password = getpass.getpass("Enter password to test: ")
    
    security = get_security_manager()
    is_valid, message = security.validate_password_strength(password)
    
    if is_valid:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")


def main():
    """Main menu."""
    while True:
        print("\n" + "=" * 50)
        print("Sentinel Agent - Password Management")
        print("=" * 50)
        print("\n1. Change Password")
        print("2. Create New User")
        print("3. Create API Key")
        print("4. Encrypt Credential")
        print("5. Decrypt Credential")
        print("6. Test Password Strength")
        print("0. Exit")
        
        choice = input("\nSelect option (0-6): ").strip()
        
        if choice == "1":
            change_password()
        elif choice == "2":
            create_user()
        elif choice == "3":
            create_api_key()
        elif choice == "4":
            encrypt_credential()
        elif choice == "5":
            decrypt_credential()
        elif choice == "6":
            test_password_strength()
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
