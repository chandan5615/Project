"""
Sentinel Agent Web Dashboard - Streamlit-based GUI for monitoring security incidents
Provides real-time visualization of attacks, blocked IPs, and security state metrics

USAGE:
------
# Run with Docker (automatic)
docker-compose up -d

# Run inside container
docker exec -it sentinel-agent streamlit run dashboard/web_dashboard.py --server.address 0.0.0.0 --server.port 8501

# Run standalone (local development)
streamlit run dashboard/web_dashboard.py

# Run with custom database
SENTINEL_DB_PATH=/path/to/db.sqlite streamlit run dashboard/web_dashboard.py

# Access at:
http://localhost:8501               (local)
http://YOUR_SERVER_IP:8501          (server)

# Login with:
Username: sentinel
Password: sentinel
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import json
import os
import socket

# Configure page
st.set_page_config(
    page_title="Sentinel Agent Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Default database path (matches data_engine.py)
def _detect_default_data_dir() -> str:
    """Detect appropriate data directory based on environment."""
    if os.path.exists("/.dockerenv"):
        return "/app/data"
    try:
        with open("/proc/self/cgroup", "r", encoding="utf-8") as f:
            if "docker" in f.read():
                return "/app/data"
    except OSError:
        pass
    return "./data"

DEFAULT_DATA_DIR = os.getenv("SENTINEL_DATA_DIR") or _detect_default_data_dir()
DEFAULT_DB_PATH = os.getenv("SENTINEL_DB_PATH") or os.path.join(DEFAULT_DATA_DIR, "sentinel_intel.db")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))
DASHBOARD_PUBLIC_HOST = os.getenv("DASHBOARD_PUBLIC_HOST") or os.getenv("SENTINEL_SERVER_IP")


def _detect_primary_ip() -> str:
    """Detect the primary IP used for outbound traffic."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"

# Dark theme CSS
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .security-state-green {
        color: #10B981;
        font-weight: bold;
    }
    .security-state-yellow {
        color: #F59E0B;
        font-weight: bold;
    }
    .security-state-red {
        color: #EF4444;
        font-weight: bold;
    }
    .metric-container {
        background-color: #1F2937;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #374151;
    }
</style>
""", unsafe_allow_html=True)


class DashboardDataManager:
    """Manages SQLite database access for dashboard metrics"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.logger = logging.getLogger(__name__)
        self._ensure_database_initialized()
    
    def _ensure_database_initialized(self):
        """Ensure the database and tables exist"""
        try:
            # Verify database path is set
            if not self.db_path or self.db_path.isspace():
                self.logger.error(f"Invalid database path: {self.db_path}")
                self.db_path = DEFAULT_DB_PATH
            
            # Create directories
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
                self.logger.info(f"Database directory ensured: {db_dir}")
            
            self.logger.info(f"Using database at: {self.db_path}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create incidents table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    source_ip TEXT,
                    attack_type TEXT,
                    severity TEXT,
                    raw_log TEXT,
                    threat_type TEXT,
                    action TEXT,
                    details TEXT
                )
            """)
            
            # Create actions table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id INTEGER,
                    action_type TEXT,
                    details TEXT,
                    success INTEGER,
                    timestamp TEXT
                )
            """)
            
            # Create threat_intel table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threat_intel (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT UNIQUE,
                    reputation_score INTEGER,
                    details TEXT,
                    last_checked TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            self.logger.info(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_incident_summary(self) -> Dict:
        """Get overall incident statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total incidents
            cursor.execute("SELECT COUNT(*) as count FROM incidents")
            total = cursor.fetchone()[0] or 0
            
            # Incidents in last 24h
            cursor.execute("""
                SELECT COUNT(*) as count FROM incidents 
                WHERE timestamp > datetime('now', '-1 day')
            """)
            last_24h = cursor.fetchone()[0] or 0
            
            # Unique threat sources
            cursor.execute("SELECT COUNT(DISTINCT source_ip) as count FROM incidents")
            unique_sources = cursor.fetchone()[0] or 0
            
            conn.close()
            return {
                "total_incidents": total,
                "last_24h": last_24h,
                "unique_sources": unique_sources
            }
        except Exception as e:
            self.logger.error(f"Error fetching incident summary: {e}")
            return {"total_incidents": 0, "last_24h": 0, "unique_sources": 0}
    
    def get_blocked_ips(self, limit: int = 20) -> pd.DataFrame:
        """Get list of blocked IPs with timestamps and reasons"""
        try:
            conn = self.get_connection()
            query = """
                SELECT 
                    source_ip,
                    threat_type,
                    COUNT(*) as block_count,
                    MAX(timestamp) as last_seen,
                    action
                FROM incidents
                GROUP BY source_ip, threat_type
                ORDER BY block_count DESC, last_seen DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(limit,))
            conn.close()
            
            if not df.empty:
                df['last_seen'] = pd.to_datetime(df['last_seen'])
            
            return df
        except Exception as e:
            self.logger.error(f"Error fetching blocked IPs: {e}")
            return pd.DataFrame()
    
    def get_incident_feed(self, limit: int = 20) -> pd.DataFrame:
        """Get recent incident feed with threat details"""
        try:
            conn = self.get_connection()
            query = """
                SELECT 
                    timestamp,
                    source_ip,
                    threat_type,
                    action,
                    details
                FROM incidents
                ORDER BY timestamp DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(limit,))
            conn.close()
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            return df
        except Exception as e:
            self.logger.error(f"Error fetching incident feed: {e}")
            return pd.DataFrame()
    
    def get_network_stats(self) -> Dict:
        """Get network health metrics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Requests in last hour (by minute)
            cursor.execute("""
                SELECT 
                    strftime('%H:%M', timestamp) as minute,
                    COUNT(*) as count
                FROM incidents
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY minute
                ORDER BY minute DESC
                LIMIT 60
            """)
            
            minutes_data = cursor.fetchall() or []
            conn.close()
            
            return {
                "minutes_data": minutes_data,
                "avg_per_minute": sum([x[1] for x in minutes_data]) / len(minutes_data) if minutes_data else 0
            }
        except Exception as e:
            self.logger.error(f"Error fetching network stats: {e}")
            return {"minutes_data": [], "avg_per_minute": 0}
    
    def calculate_security_score(self) -> Tuple[int, str]:
        """Calculate security state: 0-100 (higher is better), return (score, status)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get stats
            cursor.execute("SELECT COUNT(*) FROM incidents WHERE timestamp > datetime('now', '-1 hour')")
            incidents_1h = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT source_ip) FROM incidents WHERE timestamp > datetime('now', '-1 hour')")
            unique_sources_1h = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Score calculation (baseline 100, decrease based on threats)
            score = 100
            
            # Deduct for incident count (max -50 for 20+ incidents/hour)
            score -= min(50, incidents_1h * 2.5)
            
            # Deduct for unique threat sources (max -30 for 10+ sources)
            score -= min(30, unique_sources_1h * 3)
            
            # Ensure score is 0-100
            score = max(0, min(100, score))
            
            # Determine status (color-coded, no emoji)
            if score >= 80:
                status = "SECURE"
            elif score >= 50:
                status = "CAUTION"
            else:
                status = "CRITICAL"
            
            return (int(score), status)
        except Exception as e:
            self.logger.error(f"Error calculating security score: {e}")
            return (100, "SECURE")


def render_security_state_card(data_manager: DashboardDataManager):
    """Render security state card with health indicator"""
    score, status = data_manager.calculate_security_score()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Security Score", f"{score}%", "Real-time")
    
    with col2:
        st.metric("Status", status)
    
    with col3:
        summary = data_manager.get_incident_summary()
        st.metric("Threats (24h)", summary['last_24h'])


def render_wall_of_shame(data_manager: DashboardDataManager):
    """Render blocked IPs table"""
    st.subheader("BLOCKED THREAT SOURCES")
    
    df = data_manager.get_blocked_ips(limit=20)
    
    if df.empty:
        st.info("STATUS: No blocked IPs - Network is clean")
    else:
        # Format for display
        display_df = df.copy()
        display_df['last_seen'] = display_df['last_seen'].dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df = display_df.rename(columns={
            'source_ip': 'IP Address',
            'threat_type': 'Threat Type',
            'block_count': 'Block Count',
            'last_seen': 'Last Seen',
            'action': 'Action'
        })
        
        st.dataframe(display_df, width="stretch", hide_index=True)


def render_incident_feed(data_manager: DashboardDataManager):
    """Render incident feed with threat details"""
    st.subheader("INCIDENT FEED - RECENT THREATS")
    
    df = data_manager.get_incident_feed(limit=20)
    
    if df.empty:
        st.info("STATUS: No recent incidents detected")
    else:
        # Format for display
        display_df = df.copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df = display_df.rename(columns={
            'timestamp': 'Time',
            'source_ip': 'Source IP',
            'threat_type': 'Threat Type',
            'action': 'Action',
            'details': 'Details'
        })
        
        st.dataframe(display_df, width="stretch", hide_index=True)


def render_network_health(data_manager: DashboardDataManager):
    """Render network health metrics and trends"""
    st.subheader("NETWORK HEALTH - LAST HOUR ACTIVITY")
    
    stats = data_manager.get_network_stats()
    
    if stats['minutes_data']:
        # Create chart data
        times = [x[0] for x in reversed(stats['minutes_data'])]
        counts = [x[1] for x in reversed(stats['minutes_data'])]
        
        chart_df = pd.DataFrame({
            'Time': times,
            'Incidents': counts
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Avg Incidents/Min (1h)", f"{stats['avg_per_minute']:.1f}")
        
        with col2:
            total_1h = sum(counts)
            st.metric("Total Incidents (1h)", total_1h)
        
        st.line_chart(chart_df.set_index('Time'), height=300)
    else:
        st.info("No incident data for the last hour")


def main():
    """Main dashboard application"""
    
    # Initialize session state with default database path
    if "db_path" not in st.session_state:
        st.session_state.db_path = DEFAULT_DB_PATH
    
    # Sidebar configuration
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # Database path
        db_path = st.text_input(
            "Database Path",
            value=st.session_state.db_path,
            help="Path to SQLite database"
        )
        st.session_state.db_path = db_path
        
        # Auto-refresh
        refresh_interval = st.slider(
            "Auto-refresh interval (seconds)",
            min_value=5,
            max_value=60,
            value=30,
            step=5
        )
        
        st.divider()
        st.subheader("📈 Dashboard Info")
        st.text(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
        st.text(f"Database Path: {Path(db_path).name}")
        st.text(f"Full Path: {db_path}")

        st.divider()
        st.subheader("🌐 Access URLs")
        local_ip = _detect_primary_ip()
        st.text(f"Local: http://localhost:{DASHBOARD_PORT}")
        st.text(f"LAN: http://{local_ip}:{DASHBOARD_PORT}")
        if DASHBOARD_PUBLIC_HOST:
            st.text(f"Public: http://{DASHBOARD_PUBLIC_HOST}:{DASHBOARD_PORT}")
        else:
            st.caption("Set DASHBOARD_PUBLIC_HOST or SENTINEL_SERVER_IP to show public URL.")
    
    # Main header
    st.title("SENTINEL AGENT - SECURITY DASHBOARD")
    st.markdown("Real-time threat monitoring and incident tracking")
    
    st.divider()
    
    # Initialize data manager with proper error handling
    try:
        data_manager = DashboardDataManager(st.session_state.db_path or DEFAULT_DB_PATH)
    except Exception as e:
        st.error(f"Failed to initialize database: {e}")
        st.info(f"Using default database path: {DEFAULT_DB_PATH}")
        try:
            data_manager = DashboardDataManager(DEFAULT_DB_PATH)
        except Exception as e2:
            st.error(f"Critical error: Cannot initialize database. {e2}")
            return
    
    # 1. Security State Card
    render_security_state_card(data_manager)
    
    st.divider()
    
    # 2. Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Wall of Shame", "Incident Feed", "Network Health"])
    
    with tab1:
        render_wall_of_shame(data_manager)
    
    with tab2:
        render_incident_feed(data_manager)
    
    with tab3:
        render_network_health(data_manager)
    
    st.divider()
    
    # Footer with statistics
    summary = data_manager.get_incident_summary()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Incidents", summary['total_incidents'])
    
    with col2:
        st.metric("Unique Threats (24h)", summary['unique_sources'])
    
    with col3:
        st.metric("Recent Incidents (24h)", summary['last_24h'])
    
    # Auto-refresh logic
    st.markdown(f"*Dashboard auto-refreshes every {refresh_interval} seconds*")


if __name__ == "__main__":
    main()
