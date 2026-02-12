#!/usr/bin/env python3
"""
CLI Dashboard Launcher with Database Initialization
Ensures all databases are properly initialized before starting the dashboard
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Initialize databases and launch CLI dashboard"""
    print("=" * 60)
    print("Sentinel Agent - CLI Dashboard Launcher")
    print("=" * 60)
    print()
    
    # Step 1: Initialize all databases
    print("[1/2] Initializing databases...")
    try:
        from init_database import initialize_all_databases
        initialize_all_databases()
        print("✓ All databases initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        print("Attempting to continue anyway...")
    
    print()
    
    # Step 2: Launch CLI dashboard
    print("[2/2] Starting CLI dashboard...")
    print()
    
    try:
        # Import and run the dashboard
        from dashboard.cli_dashboard import main as dashboard_main
        dashboard_main()
    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user")
    except Exception as e:
        print(f"\n✗ Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
