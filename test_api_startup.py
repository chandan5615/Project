#!/usr/bin/env python3
"""
Test if sentinel_api.py can start properly
"""
import sys
import traceback

print("=" * 60)
print("Testing Sentinel API Startup")
print("=" * 60)
print()

# Test 1: Check if we can import required modules
print("[1/5] Testing imports...")
try:
    from fastapi import FastAPI
    print("  ✓ FastAPI")
    
    import uvicorn
    print("  ✓ uvicorn")
    
    from auth import get_authenticator
    print("  ✓ auth module")
    
    from metrics import get_metrics
    print("  ✓ metrics module")
    
    from list_manager import get_list_manager
    print("  ✓ list_manager module")
    
    from threat_intelligence import get_threat_intelligence
    print("  ✓ threat_intelligence module")
    
    from anomaly_scorer import get_anomaly_scorer
    print("  ✓ anomaly_scorer module")
    
    from data_engine import get_engine
    print("  ✓ data_engine module")
    
    print("  ✓ All imports successful!")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# Test 2: Check if database is accessible
print("[2/5] Testing database connection...")
try:
    engine = get_engine()
    print("  ✓ Database engine initialized")
except Exception as e:
    print(f"  ⚠ Database warning: {e}")
    print("  (This might be OK if database doesn't exist yet)")

print()

# Test 3: Create minimal API
print("[3/5] Creating FastAPI app...")
try:
    app = FastAPI(title="Test API")
    
    @app.get("/health")
    def health():
        return {"status": "ok"}
    
    print("  ✓ FastAPI app created")
except Exception as e:
    print(f"  ✗ Failed to create app: {e}")
    sys.exit(1)

print()

# Test 4: Check if port 8000 is available
print("[4/5] Checking if port 8000 is available...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result == 0:
        print("  ✗ Port 8000 is ALREADY IN USE!")
        print("    Kill the process using it: sudo fuser -k 8000/tcp")
        sys.exit(1)
    else:
        print("  ✓ Port 8000 is available")
except Exception as e:
    print(f"  ⚠ Could not check port: {e}")

print()

# Test 5: Try to import the actual API
print("[5/5] Loading actual sentinel_api.py...")
try:
    import sentinel_api
    print("  ✓ sentinel_api.py loaded successfully")
    print()
    print("=" * 60)
    print("✓ ALL TESTS PASSED - API should work!")
    print("=" * 60)
    print()
    print("Run: python sentinel_api.py")
except Exception as e:
    print(f"  ✗ Failed to load sentinel_api.py: {e}")
    print()
    traceback.print_exc()
    print()
    print("=" * 60)
    print("✗ TESTS FAILED - Fix errors above")
    print("=" * 60)
    sys.exit(1)
