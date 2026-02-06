"""
Dashboard Authentication Module
Simple but secure authentication for web and CLI dashboards.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DashboardAuthenticator:
    """Handles dashboard authentication and session management."""
    
    def __init__(self, db_path: str = "/app/data/auth.db"):
        """Initialize authenticator."""
        self.db_path = db_path
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
        """Initialize default admin user."""
        # Default credentials (should be changed on first login)
        default_username = "admin"
        default_password = "sentinel123"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (default_username,))
        if cursor.fetchone()[0] == 0:
            password_hash = self._hash_password(default_password)
            try:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, created_date)
                    VALUES (?, ?, ?, ?)
                """, (default_username, password_hash, "admin", datetime.now().isoformat()))
                conn.commit()
                logger.info(f"Created default user: {default_username}")
            except Exception as e:
                logger.error(f"Error creating default user: {e}")
        
        conn.close()
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
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
        
        password_hash = self._hash_password(password)
        cursor.execute("""
            SELECT id FROM users WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        user = cursor.fetchone()
        if not user:
            conn.close()
            return False, None
        
        # Create session token
        user_id = user[0]
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
    
    def create_api_key(self, username: str, key_name: str) -> Optional[str]:
        """
        Create API key for user.
        
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
        api_key = secrets.token_urlsafe(32)
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
        Verify API key.
        
        Args:
            api_key: API key to verify
            
        Returns:
            Tuple of (valid, username)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        key_hash = self._hash_password(api_key)
        cursor.execute("""
            SELECT u.username FROM api_keys ak
            JOIN users u ON ak.user_id = u.id
            WHERE ak.key_hash = ?
        """, (key_hash,))
        
        result = cursor.fetchone()
        
        if result:
            # Update last_used
            cursor.execute("UPDATE api_keys SET last_used = ? WHERE key_hash = ?",
                         (datetime.now().isoformat(), key_hash))
            conn.commit()
            conn.close()
            return True, result[0]
        
        conn.close()
        return False, None
    
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
