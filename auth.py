"""
Dashboard Authentication Module
Enterprise-grade authentication with encrypted password storage.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
import sqlite3
from pathlib import Path
import logging

# Import security manager for password encryption
from security_manager import get_security_manager

logger = logging.getLogger(__name__)


class DashboardAuthenticator:
    """Handles dashboard authentication and session management with encryption."""
    
    def __init__(self, db_path: str = "/app/data/auth.db"):
        """Initialize authenticator."""
        # Ensure db_path is valid
        if not db_path or db_path.isspace():
            db_path = "/app/data/auth.db"
        self.db_path = db_path
        self.security = get_security_manager()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._init_default_user()
    
    def _init_db(self):
        """Initialize authentication database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                role TEXT,  -- admin, analyst, viewer
                created_date TEXT,
                last_login TEXT
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                token TEXT UNIQUE,
                created_at TEXT,
                expires_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        
        # API keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                key_hash TEXT UNIQUE,
                name TEXT,
                created_date TEXT,
                last_used TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _init_default_user(self):
        """Initialize default admin user with secure random password."""
        default_username = "admin"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (default_username,))
        if cursor.fetchone()[0] == 0:
            # Generate secure random password (will be shown ONCE in logs)
            default_password = self.security.generate_token(16)
            password_hash = self._hash_password(default_password)
            
            try:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, created_date)
                    VALUES (?, ?, ?, ?)
                """, (default_username, password_hash, "admin", datetime.now().isoformat()))
                conn.commit()
                
                # Log password ONCE (user must save it or change it immediately)
                logger.warning("=" * 70)
                logger.warning("DEFAULT ADMIN CREDENTIALS (SAVE THESE NOW!):")
                logger.warning(f"  Username: {default_username}")
                logger.warning(f"  Password: {default_password}")
                logger.warning("CHANGE PASSWORD IMMEDIATELY AFTER FIRST LOGIN!")
                logger.warning("=" * 70)
                
                # Also save to secure file
                creds_file = Path(self.db_path).parent / "INITIAL_CREDENTIALS.txt"
                with open(creds_file, 'w') as f:
                    f.write(f"Initial Admin Credentials\n")
                    f.write(f"Generated: {datetime.now().isoformat()}\n")
                    f.write(f"Username: {default_username}\n")
                    f.write(f"Password: {default_password}\n")
                    f.write(f"\nWARNING: Change password immediately!\n")
                    f.write(f"Delete this file after saving credentials.\n")
                
                logger.info(f"Credentials saved to: {creds_file}")
                
            except Exception as e:
                logger.error(f"Error creating default user: {e}")
        
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt with automatic salting."""
        return self.security.hash_password(password)
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Authenticate user and return session token.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, token)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Fetch user's password hash
        cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, None
        
        user_id, stored_hash = user
        
        # Verify password using bcrypt
        if not self.security.verify_password(password, stored_hash):
            conn.close()
            return False, None
        
        # Create session token
        token = secrets.token_urlsafe(32)
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        
        try:
            cursor.execute("""
                INSERT INTO sessions (user_id, token, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, token, datetime.now().isoformat(), expires_at))
            
            # Update last login
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", 
                         (datetime.now().isoformat(), user_id))
            
            conn.commit()
            logger.info(f"User {username} authenticated successfully")
            return True, token
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return False, None
        finally:
            conn.close()
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        Verify session token.
        
        Args:
            token: Session token
            
        Returns:
            Tuple of (valid, username)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.username FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > ?
        """, (token, datetime.now().isoformat()))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return True, result[0]
        return False, None
    
    def create_api_key(self, username: str, key_name: str = "") -> Optional[str]:
        """
        Create and return encrypted API key for user.
        
        Args:
            username: Username
            key_name: Name for the API key
            
        Returns:
            API key or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return None
        
        user_id = user[0]
        # Generate secure API key with prefix
        api_key = self.security.generate_api_key()
        key_hash = self._hash_password(api_key)
        
        try:
            cursor.execute("""
                INSERT INTO api_keys (user_id, key_hash, name, created_date)
                VALUES (?, ?, ?, ?)
            """, (user_id, key_hash, key_name, datetime.now().isoformat()))
            conn.commit()
            logger.info(f"Created API key for {username}")
            return api_key
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            return None
        finally:
            conn.close()
    
    def verify_api_key(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Verify encrypted API key or session token.
        
        Args:
            api_key: API key or session token to verify
            
        Returns:
            Tuple of (valid, username)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First, check if it's a valid session token (plain text comparison)
        cursor.execute("""
            SELECT s.token, u.username, s.expires_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ?
        """, (api_key,))
        
        session = cursor.fetchone()
        if session:
            token, username, expires_at = session
            # Check if session is still valid
            if datetime.fromisoformat(expires_at) > datetime.now():
                conn.close()
                return True, username
        
        # If not a session token, check if it's an API key (bcrypt hashed)
        cursor.execute("""
            SELECT ak.key_hash, u.username 
            FROM api_keys ak
            JOIN users u ON ak.user_id = u.id
        """)
        
        all_keys = cursor.fetchall()
        
        # Check each key (bcrypt requires full verification, no simple hash lookup)
        for stored_hash, username in all_keys:
            if self.security.verify_password(api_key, stored_hash):
                # Update last_used
                cursor.execute("UPDATE api_keys SET last_used = ? WHERE key_hash = ?",
                             (datetime.now().isoformat(), stored_hash))
                conn.commit()
                conn.close()
                return True, username
        
        conn.close()
        return False, None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Change user password securely.
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        # Validate new password strength
        is_valid, message = self.security.validate_password_strength(new_password)
        if not is_valid:
            return False, message
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verify old password
        cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, "User not found"
        
        user_id, stored_hash = user
        
        if not self.security.verify_password(old_password, stored_hash):
            conn.close()
            return False, "Current password incorrect"
        
        # Hash new password
        new_hash = self._hash_password(new_password)
        
        try:
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
            conn.commit()
            logger.info(f"Password changed for user: {username}")
            return True, "Password changed successfully"
        except Exception as e:
            logger.error(f"Password change error: {e}")
            return False, "Error changing password"
        finally:
            conn.close()
    
    def create_user(self, username: str, password: str, role: str = "analyst") -> Tuple[bool, str]:
        """
        Create new user with encrypted password.
        
        Args:
            username: Username
            password: Password
            role: User role (admin, analyst, viewer)
            
        Returns:
            Tuple of (success, message)
        """
        # Validate password strength
        is_valid, message = self.security.validate_password_strength(password)
        if not is_valid:
            return False, message
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self._hash_password(password)
        
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, created_date)
                VALUES (?, ?, ?, ?)
            """, (username, password_hash, role, datetime.now().isoformat()))
            conn.commit()
            logger.info(f"Created user: {username} with role: {role}")
            return True, f"User {username} created successfully"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False, "Error creating user"
        finally:
            conn.close()
    
    def logout(self, token: str):
        """Logout user by removing session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()
            logger.info("User logged out")
        except Exception as e:
            logger.error(f"Error during logout: {e}")
        finally:
            conn.close()


# Convenience singleton
_auth_instance = None

def get_authenticator() -> DashboardAuthenticator:
    """Get authenticator instance."""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = DashboardAuthenticator()
    return _auth_instance
