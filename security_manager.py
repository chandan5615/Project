"""
Sentinel Agent - Security Manager
Enterprise-grade encryption and credential management.
"""

import os
import secrets
import base64
from typing import Optional, Tuple
from pathlib import Path
import logging

# Cryptography imports
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Manages encryption, password hashing, and secure credential storage.
    
    Features:
    - bcrypt password hashing (industry standard)
    - Fernet symmetric encryption for sensitive data
    - Secure secret key management
    - Environment variable encryption
    """
    
    def __init__(self, secrets_dir: str = "/app/data/secrets"):
        """
        Initialize security manager.
        
        Args:
            secrets_dir: Directory to store encrypted secrets
        """
        self.secrets_dir = Path(secrets_dir)
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        
        # Security settings
        self.bcrypt_rounds = 12  # Cost factor for bcrypt (higher = more secure but slower)
        
        # Initialize encryption key
        self._encryption_key = self._load_or_create_master_key()
        self._cipher = None
        if CRYPTOGRAPHY_AVAILABLE:
            self._cipher = Fernet(self._encryption_key)
        
        logger.info("Security Manager initialized")
    
    def _load_or_create_master_key(self) -> bytes:
        """
        Load or create master encryption key.
        
        Returns:
            Master encryption key
        """
        key_file = self.secrets_dir / ".master.key"
        
        if key_file.exists():
            # Load existing key
            with open(key_file, 'rb') as f:
                key = f.read()
            logger.info("Loaded existing master encryption key")
        else:
            # Generate new key
            if CRYPTOGRAPHY_AVAILABLE:
                key = Fernet.generate_key()
            else:
                # Fallback to base64-encoded random bytes
                key = base64.urlsafe_b64encode(secrets.token_bytes(32))
            
            # Save securely (restrict permissions)
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Set file permissions (Unix-like systems)
            try:
                os.chmod(key_file, 0o600)  # Owner read/write only
                logger.info("Created new master encryption key with restricted permissions")
            except Exception as e:
                logger.warning(f"Could not set file permissions: {e}")
        
        return key
    
    # ========================================================================
    # PASSWORD HASHING (bcrypt - Industry Standard)
    # ========================================================================
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt (with automatic salt).
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password (includes salt)
        """
        if not BCRYPT_AVAILABLE:
            logger.error("bcrypt not available - falling back to insecure method")
            return self._fallback_hash(password)
        
        # bcrypt automatically handles salt generation
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against bcrypt hash.
        
        Args:
            password: Plain text password to verify
            hashed_password: Stored bcrypt hash
            
        Returns:
            True if password matches
        """
        if not BCRYPT_AVAILABLE:
            return self._fallback_verify(password, hashed_password)
        
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def _fallback_hash(self, password: str) -> str:
        """Fallback hash method if bcrypt unavailable (NOT RECOMMENDED)."""
        import hashlib
        salt = secrets.token_hex(16)
        return f"sha256${salt}${hashlib.sha256((password + salt).encode()).hexdigest()}"
    
    def _fallback_verify(self, password: str, hashed: str) -> bool:
        """Fallback verification for SHA-256 hashes."""
        import hashlib
        try:
            if hashed.startswith("sha256$"):
                _, salt, hash_value = hashed.split("$")
                computed = hashlib.sha256((password + salt).encode()).hexdigest()
                return computed == hash_value
            else:
                # Old unsalted SHA-256 (migrate these!)
                return hashlib.sha256(password.encode()).hexdigest() == hashed
        except:
            return False
    
    # ========================================================================
    # DATA ENCRYPTION (Fernet - Symmetric)
    # ========================================================================
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Plain text data
            
        Returns:
            Encrypted data (base64-encoded)
        """
        if not CRYPTOGRAPHY_AVAILABLE or not self._cipher:
            logger.warning("Encryption not available - data stored in plain text!")
            return f"PLAIN:{data}"
        
        try:
            encrypted = self._cipher.encrypt(data.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return f"PLAIN:{data}"
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Plain text data
        """
        # Handle plain text (fallback)
        if encrypted_data.startswith("PLAIN:"):
            return encrypted_data[6:]
        
        if not CRYPTOGRAPHY_AVAILABLE or not self._cipher:
            logger.error("Decryption not available!")
            return ""
        
        try:
            decrypted = self._cipher.decrypt(encrypted_data.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return ""
    
    # ========================================================================
    # SECURE CREDENTIAL STORAGE
    # ========================================================================
    
    def store_credential(self, name: str, value: str):
        """
        Store credential encrypted on disk.
        
        Args:
            name: Credential name (e.g., 'api_key', 'db_password')
            value: Credential value (will be encrypted)
        """
        encrypted = self.encrypt(value)
        cred_file = self.secrets_dir / f"{name}.enc"
        
        with open(cred_file, 'w') as f:
            f.write(encrypted)
        
        # Restrict permissions
        try:
            os.chmod(cred_file, 0o600)
        except:
            pass
        
        logger.info(f"Stored encrypted credential: {name}")
    
    def load_credential(self, name: str) -> Optional[str]:
        """
        Load and decrypt credential.
        
        Args:
            name: Credential name
            
        Returns:
            Decrypted credential value or None
        """
        cred_file = self.secrets_dir / f"{name}.enc"
        
        if not cred_file.exists():
            logger.warning(f"Credential not found: {name}")
            return None
        
        with open(cred_file, 'r') as f:
            encrypted = f.read()
        
        return self.decrypt(encrypted)
    
    def delete_credential(self, name: str):
        """Delete stored credential."""
        cred_file = self.secrets_dir / f"{name}.enc"
        if cred_file.exists():
            cred_file.unlink()
            logger.info(f"Deleted credential: {name}")
    
    # ========================================================================
    # TOKEN GENERATION
    # ========================================================================
    
    def generate_token(self, length: int = 32) -> str:
        """
        Generate secure random token.
        
        Args:
            length: Token length in bytes
            
        Returns:
            URL-safe token
        """
        return secrets.token_urlsafe(length)
    
    def generate_api_key(self) -> str:
        """Generate secure API key."""
        return f"sk_{secrets.token_urlsafe(32)}"
    
    # ========================================================================
    # PASSWORD STRENGTH VALIDATION
    # ========================================================================
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(password) < 12:
            return True, "Password is weak but acceptable (12+ chars recommended)"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        score = sum([has_upper, has_lower, has_digit, has_special])
        
        if score < 3:
            return True, "Password is moderate (add mixed case, numbers, symbols for strong)"
        
        return True, "Password is strong"


# Singleton instance
_security_manager = None

def get_security_manager() -> SecurityManager:
    """Get security manager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager
