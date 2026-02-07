# Security Implementation Guide - Sentinel Agent v2.2

##  Enterprise-Grade Security Features

Your Sentinel Agent now includes enterprise-grade encryption and security:

### ✅ Security Features Implemented

1. **bcrypt Password Hashing**
   - Industry-standard password encryption
   - Automatic salt generation
   - Configurable cost factor (12 rounds = ~300ms per hash)
   - Resistant to rainbow table attacks

2. **Fernet Symmetric Encryption**
   - AES 128-bit encryption for sensitive data
   - Secure credential storage
   - Environment variable encryption
   - Master key management

3. **Secure Token Generation**
   - Cryptographically secure random tokens
   - URL-safe API keys with prefixes
   - 32-byte default length

4. **Password Strength Validation**
   - Minimum 8 characters (12+ recommended)
   - Checks for mixed case, numbers, symbols
   - Provides strength feedback

5. **Secure Default Credentials**
   - Random password generation on first install
   - One-time display in logs
   - Saved to `INITIAL_CREDENTIALS.txt` file

---

##  New Dependencies

Added to `requirements.txt`:

```
bcrypt>=4.0.0         # Password hashing
cryptography>=41.0.0  # Data encryption
```

**Install:**
```bash
pip install bcrypt cryptography
```

Or rebuild Docker:
```bash
docker-compose build --no-cache
```

---

##  Usage

### 1. Password Management

**Using the Password Manager Tool:**
```bash
python password_manager.py
```

**Menu Options:**
- Change password
- Create new user
- Create API key
- Encrypt credential
- Decrypt credential
- Test password strength

### 2. Programmatic Usage

**Hash Password:**
```python
from security_manager import get_security_manager

security = get_security_manager()
hashed = security.hash_password("my_password")
```

**Verify Password:**
```python
is_valid = security.verify_password("my_password", hashed)
```

**Encrypt Data:**
```python
encrypted = security.encrypt("sensitive_data")
decrypted = security.decrypt(encrypted)
```

**Store Credentials:**
```python
security.store_credential("api_key", "sk_abc123")
api_key = security.load_credential("api_key")
```

### 3. Authentication

**Login (automatically uses bcrypt):**
```python
from auth import get_authenticator

auth = get_authenticator()
success, token = auth.authenticate("admin", "password")
```

**Change Password:**
```python
success, message = auth.change_password("admin", "old_pass", "new_pass")
```

**Create User:**
```python
success, message = auth.create_user("analyst1", "secure_pass", "analyst")
```

---

##  First-Time Setup

### Step 1: First Login

When you first start the system, check for default credentials:

**Option A: Check Logs**
```bash
docker-compose logs sentinel-agent | grep "DEFAULT ADMIN"
```

**Option B: Check Credentials File**
```bash
cat data/INITIAL_CREDENTIALS.txt
```

You'll see something like:
```
Username: admin
Password: Xj7kP9mN4vQ2wR5tY8zL6hB3nV1cF0gS
```

### Step 2: Change Password Immediately

**Using the tool:**
```bash
docker-compose exec sentinel-agent python password_manager.py
# Select: 1. Change Password
```

**Or via API:**
```bash
curl -X POST http://localhost:8000/api/auth/change-password \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "old_password": "Xj7kP9mN4vQ2wR5tY8zL6hB3nV1cF0gS",
    "new_password": "MyNewSecurePassword123!"
  }'
```

### Step 3: Delete Credentials File

```bash
rm data/INITIAL_CREDENTIALS.txt
```

---

## ️ Security Best Practices

### Password Requirements

**Minimum:**
- At least 8 characters
- Will be accepted but marked as weak

**Recommended:**
- At least 12 characters
- Mix of uppercase and lowercase
- Include numbers
- Include special characters (@, #, $, etc.)

**Examples:**
- ❌ Weak: `sentinel123` (8 chars, no mixed case/symbols)
- ⚠️  Moderate: `Sentinel2024` (12 chars, mixed case, number)
- ✅ Strong: `S3nt!n3l@2024#Sec` (17 chars, all types)

### API Key Security

**Best Practices:**
1. Use API keys instead of passwords for automation
2. Rotate keys regularly (every 90 days)
3. Use descriptive names: `prod-server-1`, `backup-system`
4. Never commit API keys to git
5. Store in encrypted credential storage

**Create API Key:**
```bash
python password_manager.py
# Select: 3. Create API Key
```

### Credential Storage

**Encrypt sensitive data:**
```bash
python password_manager.py
# Select: 4. Encrypt Credential

# Examples:
# - Database passwords
# - Third-party API keys
# - Service tokens
```

**Stored encrypted in:** `data/secrets/<name>.enc`

---

##  Configuration

### bcrypt Cost Factor

Higher = more secure but slower. Default is 12 (recommended).

**Change in `security_manager.py`:**
```python
self.bcrypt_rounds = 12  # 10-14 recommended
```

**Performance:**
- Cost 10: ~100ms per hash
- Cost 12: ~300ms per hash (default)
- Cost 14: ~1200ms per hash

### Master Encryption Key

Automatically generated on first run and stored in:
```
data/secrets/.master.key
```

**⚠️  Important:**
- This key encrypts all credentials
- Backup this file securely
- If lost, encrypted data cannot be recovered
- Permissions: 0600 (owner read/write only)

**Backup:**
```bash
cp data/secrets/.master.key /secure/backup/location/
```

---

##  Migration from Old System

If you have existing users with SHA-256 hashes:

**Option 1: Auto-Migration on Login**

The system detects old hashes and can migrate:

```python
# In security_manager.py, _fallback_verify handles old hashes
# Users must login once to migrate to bcrypt
```

**Option 2: Force Reset**

```bash
# Backup old database
cp data/auth.db data/auth.db.backup

# Delete and recreate
rm data/auth.db

# Restart - new database with bcrypt created
docker-compose restart

# Users must use new random password from logs
```

---

##  Security Checklist

After implementing encryption:

- [ ] Install bcrypt and cryptography: `pip install bcrypt cryptography`
- [ ] Rebuild Docker image: `docker-compose build --no-cache`
- [ ] Start system and save initial admin password
- [ ] Login and change admin password immediately
- [ ] Delete `INITIAL_CREDENTIALS.txt` file
- [ ] Create API keys for automation
- [ ] Encrypt sensitive credentials
- [ ] Backup master encryption key
- [ ] Test password strength requirements
- [ ] Update documentation with new passwords

---

##  Troubleshooting

### "bcrypt not available"

**Solution:**
```bash
pip install bcrypt

# Or in Docker:
docker-compose build --no-cache
docker-compose restart
```

### "Encryption not available"

**Solution:**
```bash
pip install cryptography

# Or in Docker:
docker-compose build --no-cache
docker-compose restart
```

### "Password verification failed"

If migrating from old system:
1. Old SHA-256 hashes are auto-detected
2. Fallback verification tries old method
3. User must login once to migrate to bcrypt

### Lost master encryption key

**⚠️  Critical:** Without the key, encrypted data is unrecoverable.

**Prevention:**
1. Backup `data/secrets/.master.key`
2. Store backup securely offline
3. Test restore procedure

**If lost:**
- Re-encrypt all credentials with new key
- Users must reset passwords
- Recreate API keys

---

##  Support

**Password Management:** Use `password_manager.py` tool

**API Endpoints:**
- `POST /api/auth/login` - Authenticate
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/create-user` - Create user
- `POST /api/auth/create-api-key` - Create API key

**Documentation:**
- `security_manager.py` - Security implementation
- `auth.py` - Authentication with bcrypt
- `password_manager.py` - CLI management tool

---

**Last Updated:** February 2026  
**Version:** Sentinel Agent v2.2 with Enterprise Security
