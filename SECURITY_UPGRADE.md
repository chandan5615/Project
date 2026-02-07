# 🔐 Security Upgrade - Password Encryption

## ✅ What Changed

Your Sentinel Agent now uses **enterprise-grade encryption** for passwords:

- **Old:** SHA-256 hashing (vulnerable to rainbow tables)
- **New:** bcrypt with automatic salting (industry standard)

## 🚀 Quick Start

### 1. Install New Dependencies

**Option A: Docker (Recommended)**
```bash
docker-compose build --no-cache
docker-compose up -d
```

**Option B: Traditional Install**
```bash
pip install bcrypt cryptography
```

### 2. Get Your New Admin Password

**First-time users:**
The system generates a **secure random password** on first startup.

**Find it in:**
```bash
# In logs:
docker-compose logs sentinel-agent | grep "DEFAULT ADMIN"

# Or in file:
cat data/INITIAL_CREDENTIALS.txt
```

You'll see:
```
Username: admin
Password: Xj7kP9mN4vQ2wR5tY8zL6hB3nV1cF0gS
```

### 3. Change Your Password

**Using the password manager:**
```bash
python password_manager.py
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

### 4. Delete Temporary Credentials

```bash
rm data/INITIAL_CREDENTIALS.txt
```

## 🛠️ Password Manager Tool

Interactive CLI for managing passwords:

```bash
python password_manager.py
```

**Features:**
- Change password
- Create new user
- Create API key
- Encrypt credentials
- Test password strength

## 📋 Password Requirements

**Minimum (Weak):**
- 8+ characters

**Recommended (Strong):**
- 12+ characters
- Mixed case (A-z)
- Numbers (0-9)
- Special characters (@#$%)

**Examples:**
- ❌ `sentinel123` (weak)
- ⚠️  `Sentinel2024` (moderate)
- ✅ `S3nt!n3l@2024#Sec` (strong)

## 🔑 API Key Management

**Create:**
```bash
python password_manager.py
# Select: 3. Create API Key
```

**Use in requests:**
```bash
curl -H "X-API-Key: sk_abc123..." http://localhost:8000/api/attack-records
```

## 🛡️ Security Features

### What's Protected Now:

1. **Passwords** - bcrypt hashing (12 rounds, ~300ms)
2. **API Keys** - Secure generation with `sk_` prefix
3. **Credentials** - Fernet encryption (AES-128)
4. **Master Key** - Stored in `data/secrets/.master.key` (600 permissions)

### Best Practices:

✅ Change default password immediately  
✅ Use API keys for automation  
✅ Rotate keys every 90 days  
✅ Backup master encryption key  
✅ Never commit passwords/keys to git  

## 🔧 Migration from Old System

**If you have existing users:**

Users with old SHA-256 passwords will **auto-migrate** on first login:
1. Login with old password
2. System detects SHA-256 hash
3. Automatically re-hashes with bcrypt
4. Next login uses new secure hash

**Or force reset:**
```bash
# Backup database
cp data/auth.db data/auth.db.backup

# Delete and restart
rm data/auth.db
docker-compose restart

# Use new random password from logs
```

## 📚 Full Documentation

See [SECURITY_IMPLEMENTATION.md](docs_markdown/SECURITY_IMPLEMENTATION.md) for:
- Complete security architecture
- API endpoint details  
- Troubleshooting guide
- Advanced configuration

## ⚠️ Important Security Notes

1. **Save your admin password** when you first see it
2. **Backup your master key** at `data/secrets/.master.key`
3. **Without the master key**, encrypted data cannot be recovered
4. **Change default password** immediately after installation

## 🐛 Troubleshooting

**"bcrypt not available":**
```bash
pip install bcrypt
# Or rebuild Docker:
docker-compose build --no-cache
```

**"Can't login":**
- Check `data/INITIAL_CREDENTIALS.txt`
- Or check Docker logs: `docker-compose logs | grep PASSWORD`
- Or reset database (see Migration section)

**"Password too weak":**
- Use at least 12 characters
- Include uppercase, lowercase, numbers, symbols
- Test with: `python password_manager.py` → option 6

## 📞 Support

**Quick Commands:**

```bash
# Password management tool
python password_manager.py

# View logs
docker-compose logs -f sentinel-agent

# Check initial credentials
cat data/INITIAL_CREDENTIALS.txt

# Test password strength
python -c "from security_manager import get_security_manager; print(get_security_manager().validate_password_strength('your_password'))"
```

---

**Version:** Sentinel Agent v2.2  
**Security Update:** February 2026  
**Dependencies:** bcrypt 4.0.0+, cryptography 41.0.0+
