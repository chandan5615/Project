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
import sys
from pathlib import Path

# Add parent directory to path to import auth module
sys.path.insert(0, str(Path(__file__).parent.parent))
import sqlite3
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import json
import os
import socket
import subprocess
import re
from collections import Counter, defaultdict

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

# Log file paths
DEFAULT_AUTH_LOG = os.getenv("AUTH_LOG_PATH", "/var/log/auth.log")
DEFAULT_WEB_LOG = os.getenv("WEB_LOG_PATH", "/var/log/apache2/access.log")


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


class LogFileManager:
    """Manages log file reading and tailing"""
    
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.logger = logging.getLogger(__name__)
    
    def tail_log(self, lines: int = 100) -> List[str]:
        """Read last N lines from log file"""
        try:
            if not os.path.exists(self.log_path):
                return [f"Log file not found: {self.log_path}"]
            
            with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                return list(f.readlines()[-lines:])
        except Exception as e:
            self.logger.error(f"Error reading log file {self.log_path}: {e}")
            return [f"Error reading log: {str(e)}"]
    
    def search_log(self, pattern: str, lines: int = 100) -> List[str]:
        """Search for pattern in log file"""
        try:
            if not os.path.exists(self.log_path):
                return []
            
            with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                if pattern:
                    return [line for line in all_lines if pattern.lower() in line.lower()][-lines:]
                return all_lines[-lines:]
        except Exception as e:
            self.logger.error(f"Error searching log: {e}")
            return []


class ApacheLogParser:
    """Parse and analyze Apache access logs"""
    
    # Apache Combined Log Format regex
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d.]+) - - \[(?P<timestamp>[^\]]+)\] "(?P<method>\w+) (?P<url>[^\s]+) HTTP/[\d.]+" '
        r'(?P<status>\d+) (?P<size>\d+|-) "(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.logger = logging.getLogger(__name__)
    
    def parse_line(self, line: str) -> Optional[Dict]:
        """Parse a single Apache log line"""
        match = self.LOG_PATTERN.match(line)
        if match:
            return match.groupdict()
        return None
    
    def get_traffic_stats(self, lines: int = 1000) -> Dict:
        """Get traffic statistics from recent log entries"""
        try:
            if not os.path.exists(self.log_path):
                return {}
            
            with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_lines = list(f.readlines()[-lines:])
            
            parsed_entries = []
            for line in log_lines:
                entry = self.parse_line(line)
                if entry:
                    parsed_entries.append(entry)
            
            if not parsed_entries:
                return {}
            
            # Aggregate statistics
            stats = {
                'total_requests': len(parsed_entries),
                'unique_ips': len(set(e['ip'] for e in parsed_entries)),
                'status_codes': Counter(e['status'] for e in parsed_entries),
                'methods': Counter(e['method'] for e in parsed_entries),
                'top_ips': Counter(e['ip'] for e in parsed_entries).most_common(10),
                'top_urls': Counter(e['url'] for e in parsed_entries).most_common(10),
                'user_agents': Counter(e['user_agent'] for e in parsed_entries).most_common(5),
                'error_requests': [e for e in parsed_entries if int(e['status']) >= 400],
            }
            
            return stats
        except Exception as e:
            self.logger.error(f"Error parsing Apache logs: {e}")
            return {}


class IPBlockManager:
    """Manage IP blocking/unblocking using UFW and iptables"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._needs_sudo = self._check_needs_sudo()
    
    def _check_needs_sudo(self) -> bool:
        """Check if sudo is needed (not in Docker, not running as root)"""
        # Check if running in Docker
        if os.path.exists("/.dockerenv"):
            self.logger.info("Running in Docker - sudo not needed")
            return False
        
        # Check if running as root (Unix only)
        try:
            if hasattr(os, 'getuid') and os.getuid() == 0:
                self.logger.info("Running as root - sudo not needed")
                return False
        except Exception:
            pass
        
        # Check if sudo exists and is executable
        try:
            result = subprocess.run(['which', 'sudo'], capture_output=True, timeout=1)
            if result.returncode == 0:
                self.logger.info("Not in Docker, not root - using sudo")
                return True  # sudo exists and we're not root
            else:
                self.logger.info("sudo command not found - running without sudo")
                return False
        except Exception as e:
            self.logger.info(f"Cannot check for sudo ({e}) - running without sudo")
            return False  # sudo doesn't exist or can't be checked
    
    def _build_cmd(self, base_cmd: List[str]) -> List[str]:
        """Build command with or without sudo prefix"""
        if self._needs_sudo:
            return ['sudo'] + base_cmd
        return base_cmd
    
    def get_blocked_ips_ufw(self) -> List[Dict]:
        """Get list of blocked IPs from UFW"""
        try:
            cmd = self._build_cmd(['ufw', 'status', 'numbered'])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return []
            
            blocked_ips = []
            for line in result.stdout.split('\n'):
                # Look for DENY rules with IP addresses
                if 'DENY' in line:
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        blocked_ips.append({
                            'ip': ip_match.group(1),
                            'rule': line.strip(),
                            'firewall': 'ufw'
                        })
            
            return blocked_ips
        except Exception as e:
            self.logger.error(f"Error getting UFW rules: {e}")
            return []
    
    def get_blocked_ips_iptables(self) -> List[Dict]:
        """Get list of blocked IPs from iptables"""
        try:
            cmd = self._build_cmd(['iptables', '-L', 'INPUT', '-n', '-v'])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return []
            
            blocked_ips = []
            for line in result.stdout.split('\n'):
                if 'DROP' in line or 'REJECT' in line:
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        blocked_ips.append({
                            'ip': ip_match.group(1),
                            'rule': line.strip(),
                            'firewall': 'iptables'
                        })
            
            return blocked_ips
        except Exception as e:
            self.logger.error(f"Error getting iptables rules: {e}")
            return []
    
    def block_ip_ufw(self, ip: str) -> Tuple[bool, str]:
        """Block an IP using UFW"""
        try:
            cmd = self._build_cmd(['ufw', 'deny', 'from', ip])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return True, f"Successfully blocked {ip} with UFW"
            else:
                return False, f"Failed to block {ip}: {result.stderr}"
        except Exception as e:
            return False, f"Error blocking IP: {str(e)}"
    
    def unblock_ip_ufw(self, ip: str) -> Tuple[bool, str]:
        """Unblock an IP using UFW"""
        try:
            cmd = self._build_cmd(['ufw', 'delete', 'deny', 'from', ip])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return True, f"Successfully unblocked {ip} with UFW"
            else:
                return False, f"Failed to unblock {ip}: {result.stderr}"
        except Exception as e:
            return False, f"Error unblocking IP: {str(e)}"
    
    def block_ip_iptables(self, ip: str) -> Tuple[bool, str]:
        """Block an IP using iptables"""
        try:
            cmd = self._build_cmd(
                ['iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP',
                 '-m', 'comment', '--comment', 'Sentinel-Agent-Block']
            )
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return True, f"Successfully blocked {ip} with iptables"
            else:
                return False, f"Failed to block {ip}: {result.stderr}"
        except Exception as e:
            return False, f"Error blocking IP: {str(e)}"
    
    def unblock_ip_iptables(self, ip: str) -> Tuple[bool, str]:
        """Unblock an IP using iptables"""
        try:
            cmd = self._build_cmd(['iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return True, f"Successfully unblocked {ip} with iptables"
            else:
                return False, f"Failed to unblock {ip}: {result.stderr}"
        except Exception as e:
            return False, f"Error unblocking IP: {str(e)}"
    
    def unblock_ip_globally(self, ip: str, firewall_type: str = "iptables") -> Tuple[bool, str]:
        """
        GLOBAL IP CLEARANCE: Completely unblock and remove an IP from the system.
        
        This performs:
        - Firewall removal (UFW or iptables)
        - Database deletion of ALL incidents for this IP
        - Removal from blocked_ips table
        
        Args:
            ip: IP address to globally unblock
            firewall_type: "UFW" or "iptables"
            
        Returns:
            (success: bool, message: str)
        """
        try:
            # Step 1: Remove from firewall
            if firewall_type == "UFW":
                fw_success, fw_message = self.unblock_ip_ufw(ip)
            else:
                fw_success, fw_message = self.unblock_ip_iptables(ip)
            
            # Step 2: Global database wipe
            from data_engine import get_engine
            data_eng = get_engine()
            db_result = data_eng.unblock_ip_globally(ip)
            
            # Step 3: Build response message
            if db_result.get("success"):
                total_deleted = db_result.get("total_deleted", 0)
                incidents_deleted = db_result.get("incidents_deleted", 0)
                blocks_deleted = db_result.get("blocks_deleted", 0)
                
                message = (
                    f"✅ GLOBALLY UNBLOCKED {ip}:\n"
                    f"• Firewall: {fw_message}\n"
                    f"• Deleted {incidents_deleted} incident(s)\n"
                    f"• Deleted {blocks_deleted} block record(s)\n"
                    f"• Total records removed: {total_deleted}"
                )
                return True, message
            else:
                error = db_result.get("error", "Unknown error")
                return False, f"❌ Firewall cleared but database cleanup failed: {error}"
                
        except Exception as e:
            return False, f"❌ Error during global unblock: {str(e)}"


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
            
            # Determine status with emoji indicators
            if score >= 80:
                status = "🟢 SECURE"
            elif score >= 50:
                status = "🟡 CAUTION"
            else:
                status = "🔴 CRITICAL"
            
            return (int(score), status)
        except Exception as e:
            self.logger.error(f"Error calculating security score: {e}")
            return (100, "🟢 SECURE")


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
        st.info("ℹ️ STATUS: No blocked IPs - Network is clean")
    else:
        # Format for display
        display_df = df.copy()
        # Safely format last_seen - handle None values
        if 'last_seen' in display_df.columns and not display_df['last_seen'].isna().all():
            display_df['last_seen'] = display_df['last_seen'].apply(
                lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else 'N/A'
            )
        display_df = display_df.rename(columns={
            'source_ip': 'IP Address',
            'threat_type': 'Threat Type',
            'block_count': 'Block Count',
            'last_seen': 'Last Seen',
            'action': 'Action'
        })
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_incident_feed(data_manager: DashboardDataManager):
    """Render incident feed with threat details"""
    st.subheader("INCIDENT FEED - RECENT THREATS")
    
    df = data_manager.get_incident_feed(limit=20)
    
    if df.empty:
        st.info("ℹ️ STATUS: No recent incidents detected - system is running normally")
    else:
        # Format for display
        display_df = df.copy()
        # Safely format timestamp - handle None values
        if 'timestamp' in display_df.columns and not display_df['timestamp'].isna().all():
            display_df['timestamp'] = display_df['timestamp'].apply(
                lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else 'N/A'
            )
        display_df = display_df.rename(columns={
            'timestamp': 'Time',
            'source_ip': 'Source IP',
            'threat_type': 'Threat Type',
            'action': 'Action',
            'details': 'Details'
        })
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)


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
            avg_incidents = stats.get('avg_per_minute', 0) or 0
            st.metric("Avg Incidents/Min (1h)", f"{float(avg_incidents):.1f}")
        
        with col2:
            total_1h = sum(counts) if counts else 0
            st.metric("Total Incidents (1h)", total_1h)
        
        if not chart_df.empty:
            st.line_chart(chart_df.set_index('Time'), height=300)
    else:
        st.info("ℹ️ No incident data available for the last hour - check back later")


def render_log_viewer():
    """Render log file viewer with tail and search functionality"""
    st.subheader("LOG FILE VIEWER")
    
    col1, col2 = st.columns(2)
    
    with col1:
        log_type = st.selectbox(
            "Select Log File",
            ["Auth Log", "Apache Access Log", "Custom Path"]
        )
    
    with col2:
        lines_to_show = st.slider("Lines to Display", 10, 500, 100, 10)
    
    # Determine log path
    if log_type == "Auth Log":
        log_path = DEFAULT_AUTH_LOG
    elif log_type == "Apache Access Log":
        log_path = DEFAULT_WEB_LOG
    else:
        log_path = st.text_input("Enter Custom Log Path", "/var/log/auth.log")
    
    # Search filter
    search_pattern = st.text_input("🔍 Search Pattern (leave empty for all)", "")
    
    # Display log path
    st.text(f"Reading: {log_path}")
    
    # Read and display logs
    log_manager = LogFileManager(log_path)
    
    if search_pattern:
        log_lines = log_manager.search_log(search_pattern, lines_to_show)
        if log_lines:
            st.success(f"Found {len(log_lines)} matching lines")
        else:
            st.warning("No matches found")
    else:
        log_lines = log_manager.tail_log(lines_to_show)
    
    # Display in a scrollable text area
    log_content = ''.join(log_lines)
    st.text_area(
        "Log Content",
        value=log_content,
        height=400,
        label_visibility="collapsed"
    )
    
    # Download button
    if log_lines:
        st.download_button(
            label="📥 Download Log Content",
            data=log_content,
            file_name=f"sentinel_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )


def render_apache_traffic():
    """Render Apache traffic statistics and analysis"""
    st.subheader("APACHE SERVER TRAFFIC ANALYSIS")
    
    # Log file selection
    apache_log_path = st.text_input(
        "Apache Access Log Path",
        value=DEFAULT_WEB_LOG,
        help="Path to Apache access.log file"
    )
    
    lines_to_analyze = st.slider("Log Lines to Analyze", 100, 10000, 1000, 100)
    
    if st.button("🔄 Analyze Traffic", type="primary"):
        with st.spinner("Analyzing Apache logs..."):
            parser = ApacheLogParser(apache_log_path)
            stats = parser.get_traffic_stats(lines_to_analyze)
            
            if not stats:
                st.error(f"Could not parse Apache logs from {apache_log_path}")
                st.info("Make sure the log file exists and is readable")
                return
            
            # Store in session state
            st.session_state.apache_stats = stats
    
    # Display stats if available
    stats = st.session_state.get('apache_stats')
    if stats:
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Requests", stats.get('total_requests', 0))
        
        with col2:
            st.metric("Unique IPs", stats.get('unique_ips', 0))
        
        with col3:
            error_count = len(stats.get('error_requests', []))
            st.metric("Errors (4xx/5xx)", error_count)
        
        with col4:
            total_requests = stats.get('total_requests', 0) or 0
            if total_requests > 0:
                error_rate = (error_count / total_requests) * 100
                st.metric("Error Rate", f"{error_rate:.1f}%")
            else:
                st.metric("Error Rate", "N/A")
        
        st.divider()
        
        # Two column layout
        col1, col2 = st.columns(2)
        
        with col1:
            # HTTP Status Codes
            st.subheader("HTTP Status Codes")
            if stats.get('status_codes'):
                status_df = pd.DataFrame(
                    stats['status_codes'].items(),
                    columns=['Status Code', 'Count']
                )
                st.dataframe(status_df, hide_index=True, use_container_width=True)
            
            # HTTP Methods
            st.subheader("HTTP Methods")
            if stats.get('methods'):
                methods_df = pd.DataFrame(
                    stats['methods'].items(),
                    columns=['Method', 'Count']
                )
                st.dataframe(methods_df, hide_index=True, use_container_width=True)
        
        with col2:
            # Top IPs
            st.subheader("Top Client IPs")
            if stats.get('top_ips'):
                top_ips_df = pd.DataFrame(
                    stats['top_ips'],
                    columns=['IP Address', 'Requests']
                )
                st.dataframe(top_ips_df, hide_index=True, use_container_width=True)
        
        st.divider()
        
        # Top URLs
        st.subheader("Most Requested URLs")
        if stats.get('top_urls'):
            top_urls_df = pd.DataFrame(
                stats['top_urls'],
                columns=['URL', 'Requests']
            )
            st.dataframe(top_urls_df, hide_index=True, use_container_width=True)
        
        # Error Requests
error_requests = stats.get('error_requests', [])
            if error_requests:
                st.subheader("Recent Error Requests")
                error_df = pd.DataFrame(error_requests[:20])
                if not error_df.empty:
                    if 'ip' in error_df.columns:
                        error_df = error_df[['ip', 'timestamp', 'method', 'url', 'status']]
                        error_df.columns = ['IP', 'Timestamp', 'Method', 'URL', 'Status']
                        st.dataframe(error_df, hide_index=True, use_container_width=True)


def render_ip_blocking():
    """Render IP blocking/unblocking interface"""
    st.subheader("IP BLOCKING CONTROLS")
    
    # Firewall selection
    firewall_type = st.radio(
        "Select Firewall Type",
        ["UFW", "iptables"],
        horizontal=True
    )
    
    st.divider()
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Block New IP")
        
        ip_to_block = st.text_input(
            "IP Address to Block",
            placeholder="e.g., 192.168.1.100",
            key="block_ip_input"
        )
        
        if st.button("[BLOCK] Block IP", type="primary", key="block_btn"):
            if ip_to_block:
                # Validate IP format
                ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
                if not ip_pattern.match(ip_to_block):
                    st.error("Invalid IP address format")
                else:
                    try:
                        blocker = IPBlockManager()
                        
                        if firewall_type == "UFW":
                            success, message = blocker.block_ip_ufw(ip_to_block)
                        else:
                            success, message = blocker.block_ip_iptables(ip_to_block)
                        
                        if success:
                            st.toast(f"✅ {message}", icon="✅")
                            st.success(message)
                        else:
                            st.toast(f"❌ {message}", icon="❌")
                            st.error(message)
                    except Exception as e:
                        st.error(f"❌ Error blocking IP: {e}")
            else:
                st.warning("⚠️ Please enter an IP address")
    
    with col2:
        st.subheader("Unblock IP (Global Wipe)")
        
        st.info("⚠️ This will completely remove the IP from firewall AND delete all its incidents from the database.")
        
        ip_to_unblock = st.text_input(
            "IP Address to Unblock",
            placeholder="e.g., 192.168.1.100",
            key="unblock_ip_input"
        )
        
        if st.button("[UNBLOCK] Globally Unblock IP", type="secondary", key="unblock_btn"):
            if ip_to_unblock:
                # Validate IP format
                ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
                if not ip_pattern.match(ip_to_unblock):
                    st.error("Invalid IP address format")
                else:
                    try:
                        blocker = IPBlockManager()
                        
                        # GLOBAL UNBLOCK: Remove from firewall + delete all database records
                        success, message = blocker.unblock_ip_globally(ip_to_unblock, firewall_type)
                        
                        if success:
                            st.toast(f"✅ {message}", icon="✅")
                            st.success(message)
                            # Auto-refresh the blocked IPs list
                            st.rerun()
                        else:
                            st.toast(f"❌ {message}", icon="❌")
                            st.error(message)
                    except Exception as e:
                        st.error(f"❌ Error unblocking IP: {e}")
            else:
                st.warning("⚠️ Please enter an IP address")
    
    st.divider()
    
    # Display currently blocked IPs
    st.subheader("Currently Blocked IPs")
    
    if st.button("🔄 Refresh Blocked IPs List"):
        try:
            blocker = IPBlockManager()
            
            if firewall_type == "UFW":
                blocked = blocker.get_blocked_ips_ufw()
            else:
                blocked = blocker.get_blocked_ips_iptables()
            
            st.session_state.blocked_ips = blocked
            if blocked:
                st.success(f"✅ Loaded {len(blocked)} blocked IP(s)")
            else:
                st.info("ℹ️ No currently blocked IPs")
        except Exception as e:
            st.error(f"❌ Error refreshing blocked IPs: {e}")
    
    # Display blocked IPs
    blocked_ips = st.session_state.get('blocked_ips', [])
    if blocked_ips:
        blocked_df = pd.DataFrame(blocked_ips)
        st.dataframe(blocked_df, hide_index=True, use_container_width=True)
    else:
        st.info("ℹ️ No blocked IPs found - Click 'Refresh' to load current firewall rules")


def render_attack_patterns(data_manager: DashboardDataManager):
    """Render attack patterns visualization"""
    st.subheader("ATTACK PATTERNS ANALYSIS")
    
    try:
        conn = data_manager.get_connection()
        
        # Get attack types distribution
        query = """
            SELECT threat_type, COUNT(*) as count
            FROM incidents
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY threat_type
            ORDER BY count DESC
        """
        attack_types_df = pd.read_sql_query(query, conn)
        
        # Get hourly attack distribution
        hourly_query = """
            SELECT 
                strftime('%Y-%m-%d %H:00', timestamp) as hour,
                COUNT(*) as count
            FROM incidents
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY hour
            ORDER BY hour
        """
        hourly_df = pd.read_sql_query(hourly_query, conn)
        
        conn.close()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Attack Types (7 days)")
            if not attack_types_df.empty:
                st.bar_chart(attack_types_df.set_index('threat_type'))
            else:
                st.info("No attack data available")
        
        with col2:
            st.subheader("Attacks by Hour (24h)")
            if not hourly_df.empty:
                st.line_chart(hourly_df.set_index('hour'))
            else:
                st.info("No hourly data available")
        
    except Exception as e:
        st.error(f"Error analyzing attack patterns: {e}")


def render_export_reports(data_manager: DashboardDataManager):
    """Render export and reporting functionality"""
    st.subheader("EXPORT REPORTS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Incident Report")
        
        time_range = st.selectbox(
            "Time Range",
            ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
            key="export_time_range"
        )
        
        # Map selection to SQL
        time_filter_map = {
            "Last Hour": "-1 hour",
            "Last 24 Hours": "-1 day",
            "Last 7 Days": "-7 days",
            "Last 30 Days": "-30 days",
            "All Time": None
        }
        
        if st.button("📥 Export Incidents to CSV", type="primary"):
            try:
                conn = data_manager.get_connection()
                
                if time_filter_map[time_range]:
                    query = f"""
                        SELECT * FROM incidents
                        WHERE timestamp > datetime('now', '{time_filter_map[time_range]}')
                        ORDER BY timestamp DESC
                    """
                else:
                    query = "SELECT * FROM incidents ORDER BY timestamp DESC"
                
                df = pd.read_sql_query(query, conn)
                conn.close()
                
                if not df.empty:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"sentinel_incidents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    st.success(f"Exported {len(df)} incidents")
                else:
                    st.warning("No incidents to export")
                
            except Exception as e:
                st.error(f"Error exporting data: {e}")
    
    with col2:
        st.subheader("Threat Intelligence Report")
        
        if st.button("📥 Export Threat Intel to JSON", type="primary"):
            try:
                conn = data_manager.get_connection()
                
                # Get threat intel
                threat_query = "SELECT * FROM threat_intel ORDER BY last_checked DESC"
                threat_df = pd.read_sql_query(threat_query, conn)
                
                conn.close()
                
                if not threat_df.empty:
                    json_data = threat_df.to_json(orient='records', indent=2)
                    st.download_button(
                        label="💾 Download JSON",
                        data=json_data,
                        file_name=f"sentinel_threat_intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                    st.success(f"Exported {len(threat_df)} threat intelligence records")
                else:
                    st.warning("No threat intelligence data to export")
                
            except Exception as e:
                st.error(f"Error exporting data: {e}")
    
    st.divider()
    
    # Database statistics
    st.subheader("Database Statistics")
    
    try:
        conn = data_manager.get_connection()
        cursor = conn.cursor()
        
        # Get table sizes
        cursor.execute("SELECT COUNT(*) FROM incidents")
        incidents_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM actions")
        actions_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM threat_intel")
        threat_intel_count = cursor.fetchone()[0]
        
        # Get database file size
        db_size = os.path.getsize(data_manager.db_path) / (1024 * 1024)  # MB
        
        conn.close()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Incidents", incidents_count)
        
        with col2:
            st.metric("Actions", actions_count)
        
        with col3:
            st.metric("Threat Intel", threat_intel_count)
        
        with col4:
            st.metric("DB Size", f"{db_size:.2f} MB")
        
    except Exception as e:
        st.error(f"Error getting database statistics: {e}")


def render_system_info():
    """Render system information and health"""
    st.subheader("SYSTEM INFORMATION")
    
    try:
        # Get system uptime
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_str = str(timedelta(seconds=int(uptime_seconds)))
        
        # Get load average
        with open('/proc/loadavg', 'r') as f:
            load_avg = f.readline().split()[:3]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("System Uptime", uptime_str)
        
        with col2:
            st.metric("Load Average (1m)", load_avg[0])
        
        with col3:
            st.metric("Load Average (5m)", load_avg[1])
        
    except Exception as e:
        st.info(f"System information not available: {e}")
    
    st.divider()
    
    # Disk usage
    st.subheader("Disk Usage")
    
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                headers = lines[0].split()
                values = lines[1].split()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Size", values[1] if len(values) > 1 else "N/A")
                
                with col2:
                    st.metric("Used", values[2] if len(values) > 2 else "N/A")
                
                with col3:
                    st.metric("Available", values[3] if len(values) > 3 else "N/A")
                
                if len(values) > 4:
                    try:
                        usage_percent = int(values[4].rstrip('%'))
                        st.progress(usage_percent / 100, text=f"Usage: {values[4]}")
                    except (ValueError, IndexError) as e:
                        st.warning(f"Could not parse disk usage: {e}")
    except Exception as e:
        st.info(f"Disk usage not available: {e}")


def _show_login_page():
    """Display login page for dashboard authentication."""
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔐 Sentinel Agent Login")
        st.markdown("---")
        
        # Login form
        with st.form("login_form"):
            st.subheader("Enter Credentials")
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit = st.form_submit_button("[LOGIN] Login", use_container_width=True)
            with col_btn2:
                help_btn = st.form_submit_button("❓ Help", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    # Attempt authentication
                    try:
                        success, token = st.session_state.authenticator.authenticate(username, password)
                        
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.auth_token = token
                            st.success(f"✅ Welcome, {username}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                            st.warning("⚠️ Failed login attempt logged")
                    except Exception as e:
                        st.error(f"❌ Authentication error: {e}")
                        st.info("💡 Tip: Check if auth.db exists and default user is created")
            
            if help_btn:
                st.info("""
                **Default Credentials:**
                - Username: `admin`
                - Password: `sentinel2026`
                
                **For password reset:**
                - Contact your system administrator
                - Or access the server console to reset via CLI
                """)
        
        st.markdown("---")
        st.caption("🛡️ Sentinel Agent v2.3 | Secure Dashboard Access")
        st.caption("⚠️ Unauthorized access is monitored and logged")


def main():
    """Main dashboard application"""
    
    # ============================================================
    # 🔐 AUTHENTICATION CHECK
    # ============================================================
    # Initialize authentication if not exists
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "auth_initialized" not in st.session_state:
        try:
            from auth import DashboardAuthenticator
            st.session_state.authenticator = DashboardAuthenticator()
            st.session_state.auth_initialized = True
        except Exception as e:
            st.error(f"⚠️ Authentication module not available: {e}")
            st.warning("[NOTICE] Running in UNAUTHENTICATED mode (development only)")
            st.session_state.auth_initialized = False
            st.session_state.authenticated = True  # Fallback to allow access
    
    # Show login page if not authenticated
    if not st.session_state.authenticated and st.session_state.auth_initialized:
        _show_login_page()
        return  # Stop here until authenticated
    
    # ============================================================
    # 📊 MAIN DASHBOARD (Only shown if authenticated)
    # ============================================================
    
    # Initialize session state with default database path
    if "db_path" not in st.session_state:
        st.session_state.db_path = DEFAULT_DB_PATH
    
    # Sidebar configuration
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # Show logged in user
        if st.session_state.get("username"):
            st.success(f"👤 Logged in as: **{st.session_state.username}**")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.rerun()
        
        st.divider()
        
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
        st.subheader("Dashboard Info")
        st.text(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
        st.text(f"Database Path: {Path(db_path).name}")
        st.text(f"Full Path: {db_path}")

        st.divider()
        st.subheader("Access URLs")
        local_ip = _detect_primary_ip()
        st.text(f"Local: http://localhost:{DASHBOARD_PORT}")
        st.text(f"LAN: http://{local_ip}:{DASHBOARD_PORT}")
        
        st.divider()
        st.subheader("Features")
        st.markdown("""
        - Blocked IPs monitoring
        - Real-time incident feed
        - Network health metrics
        - Live log file viewer
        - Apache traffic analysis
        - IP blocking/unblocking
        - Attack pattern analysis
        - Export reports (CSV/JSON)
        - System information
        """)
        
        st.divider()
        st.info("💡 **Tip:** Use IP Blocking tab to manually block/unblock malicious IPs")
    
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "[BLOCKED] Wall of Shame", 
        "[INCIDENTS] Incident Feed", 
        "[NETWORK] Network Health",
        "[LOGS] Log Viewer",
        "[APACHE] Apache Traffic",
        "[BLOCKING] IP Blocking",
        "[ATTACKS] Attack Patterns",
        "[EXPORT] Export Reports",
        "[SYSTEM] System Info"
    ])
    
    with tab1:
        render_wall_of_shame(data_manager)
    
    with tab2:
        render_incident_feed(data_manager)
    
    with tab3:
        render_network_health(data_manager)
    
    with tab4:
        render_log_viewer()
    
    with tab5:
        render_apache_traffic()
    
    with tab6:
        render_ip_blocking()
    
    with tab7:
        render_attack_patterns(data_manager)
    
    with tab8:
        render_export_reports(data_manager)
    
    with tab9:
        render_system_info()
    
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
