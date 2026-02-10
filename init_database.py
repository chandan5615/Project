"""
Database Initialization Script
Ensures all required tables and databases are created before the application starts
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_all_databases():
    """Initialize all databases used by Sentinel Agent"""
    
    # Create data directory
    data_dir = os.getenv("SENTINEL_DATA_DIR", "/app/data")
    os.makedirs(data_dir, exist_ok=True)
    logger.info(f"✓ Data directory ready: {data_dir}")
    
    try:
        # Initialize main data engine (creates sentinel_intel.db with incidents, actions, threat_intel tables)
        from data_engine import get_engine
        engine = get_engine()
        logger.info("✓ Data Engine initialized (sentinel_intel.db created)")
        
        # Initialize auth (creates auth.db with users, sessions, api_keys tables)
        from auth import get_authenticator
        authenticator = get_authenticator()
        logger.info("✓ Authentication module initialized (auth.db created)")
        
        # Initialize threat intelligence (creates threat_intel.db)
        from threat_intelligence import get_threat_intelligence
        threat_intel = get_threat_intelligence()
        logger.info("✓ Threat Intelligence module initialized (threat_intel.db created)")
        
        # Initialize list manager (creates lists.db)
        from list_manager import get_list_manager
        list_manager = get_list_manager()
        logger.info("✓ List Manager module initialized (lists.db created)")
        
        # Initialize metrics (creates metrics.db)
        from metrics import get_metrics
        metrics = get_metrics()
        logger.info("✓ Performance Metrics module initialized (metrics.db created)")
        
        # Initialize anomaly scorer (creates anomalies.db)
        from anomaly_scorer import get_anomaly_scorer
        anomaly_scorer = get_anomaly_scorer()
        logger.info("✓ Anomaly Scorer module initialized (anomalies.db created)")
        
        logger.info("")
        logger.info("=" * 50)
        logger.info("✓ ALL DATABASES INITIALIZED SUCCESSFULLY")
        logger.info("=" * 50)
        logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = initialize_all_databases()
    sys.exit(0 if success else 1)
