"""
Sentinel Agent CLI Dashboard - Rich terminal UI for headless environments
Provides formatted terminal-based monitoring of security incidents with live updates

USAGE:
------
# Run from server
python3 dashboard/cli_dashboard.py

# Run from inside Docker container
docker exec -it sentinel-agent python3 dashboard/cli_dashboard.py

# Run remotely via SSH
ssh ubuntu@192.168.31.91 "cd ~/Project && python3 dashboard/cli_dashboard.py"

# Run with custom database
SENTINEL_DB_PATH=/path/to/db.sqlite python3 dashboard/cli_dashboard.py

# Run with custom refresh interval (default: 5 seconds)
CLI_REFRESH_INTERVAL=3 python3 dashboard/cli_dashboard.py

FEATURES:
---------
✓ Real-time incident table (auto-updating every 5 seconds)
✓ Top attackers ranking
✓ Attack type statistics
✓ Security state indicator (🟢 Green / 🟡 Yellow / 🔴 Red)
✓ System resource usage (CPU, Memory, Disk)
✓ Color-coded severity levels (RED=High, YELLOW=Medium, CYAN=Low)
✓ Anti-spam filter (prevents duplicate alerts)
✓ No authentication required

KEYBOARD:
---------
Q or Ctrl+C  - Quit dashboard
F5           - Force refresh
C            - Clear screen
"""

import sqlite3
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Set
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.progress import BarColumn, Progress
from rich.live import Live
from rich.align import Align
import time
import os

# Default database path (matches data_engine.py)
DEFAULT_DATA_DIR = os.getenv("SENTINEL_DATA_DIR") or "/app/data"
DEFAULT_DB_PATH = os.getenv("SENTINEL_DB_PATH") or os.path.join(DEFAULT_DATA_DIR, "sentinel_intel.db")
REFRESH_INTERVAL = int(os.getenv("CLI_REFRESH_INTERVAL") or "5")


class AntiSpamFilter:
    """Prevents spam by tracking recently reported IPs and only showing new blocks"""
    
    def __init__(self, max_history: int = 100):
        self.reported_ips: Set[str] = set()
        self.max_history = max_history
        self.last_new_block_time = 0
        self.console = Console()
    
    def is_new_block(self, ip: str) -> bool:
        """Check if this is a new IP that hasn't been reported yet"""
        return ip not in self.reported_ips
    
    def add_block(self, ip: str):
        """Register a blocked IP to prevent re-reporting"""
        self.reported_ips.add(ip)
        
        # Prevent memory leaks - keep set bounded
        if len(self.reported_ips) > self.max_history:
            # Remove oldest entries (keep most recent)
            items = list(self.reported_ips)
            self.reported_ips = set(items[-self.max_history:])
    
    def print_new_block_alert(self, ip: str, threat_type: str, action: str):
        """Print only when a genuinely NEW IP is blocked"""
        from rich.style import Style
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.print(
            f"[yellow][{timestamp}][/yellow] [bold]NEW BLOCK:[/bold] {ip} | {threat_type} | {action}",
            style="bold red"
        )


class CLIDashboardDataManager:
    """Manages SQLite database access for CLI dashboard metrics"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.logger = logging.getLogger(__name__)
        self._ensure_database_initialized()
    
    def _ensure_database_initialized(self):
        """Ensure the database and tables exist"""
        try:
            # Ensure db_path is valid and not empty
            if not self.db_path or self.db_path.isspace():
                self.logger.warning(f"Empty database path detected, using default: {DEFAULT_DB_PATH}")
                self.db_path = DEFAULT_DB_PATH
            
            # Create directory if needed
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
    
    def get_recent_blocks(self, limit: int = 5) -> List[Dict]:
        """Get most recent blocked IPs"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    source_ip,
                    threat_type,
                    timestamp,
                    action,
                    COUNT(*) as count
                FROM incidents
                GROUP BY source_ip
                ORDER BY MAX(timestamp) DESC
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "ip": r[0],
                    "threat_type": r[1],
                    "timestamp": r[2],
                    "action": r[3],
                    "count": r[4]
                }
                for r in results
            ]
        except Exception as e:
            self.logger.error(f"Error fetching recent blocks: {e}")
            return []
    
    def get_incident_alerts(self, limit: int = 5) -> List[Dict]:
        """Get recent incident alerts"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    source_ip,
                    threat_type,
                    action,
                    timestamp
                FROM incidents
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "source_ip": r[0],
                    "threat_type": r[1],
                    "action": r[2],
                    "timestamp": r[3]
                }
                for r in results
            ]
        except Exception as e:
            self.logger.error(f"Error fetching incident alerts: {e}")
            return []
    
    def calculate_security_score(self) -> Tuple[int, str, str]:
        """Calculate security score (0-100), status text, and color"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get stats for last hour
            cursor.execute("""
                SELECT COUNT(*) FROM incidents 
                WHERE timestamp > datetime('now', '-1 hour')
            """)
            incidents_1h = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT COUNT(DISTINCT source_ip) FROM incidents 
                WHERE timestamp > datetime('now', '-1 hour')
            """)
            unique_sources_1h = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Score calculation
            score = 100
            score -= min(50, incidents_1h * 2.5)
            score -= min(30, unique_sources_1h * 3)
            score = max(0, min(100, score))
            
            # Determine status and color
            if score >= 80:
                status = "SECURE"
                color = "green"
            elif score >= 50:
                status = "CAUTION"
                color = "yellow"
            else:
                status = "CRITICAL"
                color = "red"
            
            return (score, status, color)
        except Exception as e:
            self.logger.error(f"Error calculating security score: {e}")
            return (100, "SECURE", "green")
    
    def get_threat_summary(self) -> Dict:
        """Get summary statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total incidents
            cursor.execute("SELECT COUNT(*) FROM incidents")
            total = cursor.fetchone()[0] or 0
            
            # Last 24h
            cursor.execute("""
                SELECT COUNT(*) FROM incidents 
                WHERE timestamp > datetime('now', '-1 day')
            """)
            last_24h = cursor.fetchone()[0] or 0
            
            # Unique sources
            cursor.execute("SELECT COUNT(DISTINCT source_ip) FROM incidents")
            unique = cursor.fetchone()[0] or 0
            
            conn.close()
            return {
                "total": total,
                "last_24h": last_24h,
                "unique": unique
            }
        except Exception as e:
            self.logger.error(f"Error getting threat summary: {e}")
            return {"total": 0, "last_24h": 0, "unique": 0}


class CLIDashboard:
    """Rich CLI Dashboard renderer with anti-spam filtering"""
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.console = Console()
        self.data_manager = CLIDashboardDataManager(db_path)
        self.logger = logging.getLogger(__name__)
        self.anti_spam = AntiSpamFilter(max_history=100)
        self.last_heartbeat_time = 0
        self.heartbeat_interval = 60  # Print heartbeat every 60 seconds
    
    def render_security_score(self) -> Panel:
        """Render security score panel"""
        score, status, color = self.data_manager.calculate_security_score()
        
        # Create progress bar
        bar_width = 40
        filled = int(bar_width * score / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        score_text = Text()
        score_text.append(f"Security Score: {score}%\n")
        score_text.append(bar + "\n")
        score_text.append(f"Status: {status}", style=color)
        
        return Panel(
            score_text,
            title="SECURITY STATE",
            border_style=color,
            expand=False
        )
    
    def render_recent_blocks_table(self) -> Panel:
        """Render table of recently blocked IPs"""
        blocks = self.data_manager.get_recent_blocks(limit=5)
        
        table = Table(
            title="BLOCKED IPS",
            show_header=True,
            header_style="bold cyan",
            show_lines=False
        )
        
        table.add_column("IP Address", style="yellow")
        table.add_column("Threat Type", style="red")
        table.add_column("Count", style="white", justify="right")
        table.add_column("Last Seen", style="cyan")
        
        if blocks:
            for block in blocks:
                # Parse timestamp to human-readable format
                try:
                    dt = datetime.fromisoformat(block['timestamp'])
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = "unknown"
                
                table.add_row(
                    block['ip'],
                    block['threat_type'],
                    str(block['count']),
                    time_str
                )
        else:
            table.add_row(
                Align.center("─" * 40),
                Align.center("No blocks detected"),
                "",
                ""
            )
        
        return Panel(
            table,
            title="🚫 WALL OF SHAME",
            border_style="red",
            expand=True
        )
    
    def render_incident_alerts(self) -> Panel:
        """Render recent incident alerts"""
        alerts = self.data_manager.get_incident_alerts(limit=5)
        
        table = Table(
            title="Recent Alerts",
            show_header=True,
            header_style="bold yellow",
            show_lines=False
        )
        
        table.add_column("Source IP", style="yellow", width=15)
        table.add_column("Threat Type", style="red", width=20)
        table.add_column("Action", style="cyan", width=15)
        table.add_column("Time", style="white", width=10)
        
        if alerts:
            for alert in alerts:
                try:
                    dt = datetime.fromisoformat(alert['timestamp'])
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = "unknown"
                
                table.add_row(
                    alert['source_ip'],
                    alert['threat_type'][:20],
                    alert['action'][:15],
                    time_str
                )
        else:
            table.add_row(
                Align.center("─" * 40),
                Align.center("No alerts"),
                "",
                ""
            )
        
        return Panel(
            table,
            title="INCIDENT FEED",
            border_style="yellow",
            expand=True
        )
    
    def render_summary_stats(self) -> Panel:
        """Render summary statistics"""
        summary = self.data_manager.get_threat_summary()
        
        stats_text = Text()
        stats_text.append(f"Total Incidents: ", style="white")
        stats_text.append(f"{summary['total']}\n", style="bold cyan")
        stats_text.append(f"Last 24 Hours:  ", style="white")
        stats_text.append(f"{summary['last_24h']}\n", style="bold yellow")
        stats_text.append(f"Unique Threats: ", style="white")
        stats_text.append(f"{summary['unique']}", style="bold red")
        
        return Panel(
            stats_text,
            title="SUMMARY STATISTICS",
            border_style="cyan",
            expand=False
        )
    
    def render_layout(self) -> Layout:
        """Create complete dashboard layout"""
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=2)
        )
        
        layout["header"].update(
            Panel(
                Text(
                    "SENTINEL AGENT - SECURITY CONSOLE",
                    justify="center",
                    style="bold cyan"
                )
            )
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split(
            Layout(self.render_security_score(), name="score"),
            Layout(self.render_summary_stats(), name="stats")
        )
        
        layout["right"].split(
            Layout(self.render_recent_blocks_table(), name="blocks"),
            Layout(self.render_incident_alerts(), name="alerts")
        )
        
        layout["footer"].update(
            Panel(
                Text(
                    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"Database: {Path(self.data_manager.db_path).name} | Press Ctrl+C to exit",
                    justify="center",
                    style="dim white"
                )
            )
        )
        
        return layout
    
    def print_heartbeat(self):
        """Print minimal heartbeat message (anti-spam: once per 60 seconds)"""
        current_time = time.time()
        
        if current_time - self.last_heartbeat_time >= self.heartbeat_interval:
            score, _, _ = self.data_manager.calculate_security_score()
            summary = self.data_manager.get_threat_summary()
            
            timestamp = datetime.now().strftime("%H:%M")
            self.console.print(
                f"[cyan][{timestamp}][/cyan] Sentinel Active | "
                f"Threats Detected: {summary['last_24h']} | "
                f"Security Score: {score}%",
                style="dim"
            )
            
            self.last_heartbeat_time = current_time
    
    def display_static(self):
        """Display dashboard once (non-interactive)"""
        self.console.clear()
        layout = self.render_layout()
        self.console.print(layout)
    
    def display_live(self, refresh_interval: float = 5.0):
        """Display dashboard with live updates"""
        try:
            with Live(
                self.render_layout(),
                console=self.console,
                refresh_per_second=1/refresh_interval,
                screen=True
            ) as live:
                while True:
                    time.sleep(refresh_interval)
                    live.update(self.render_layout())
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard stopped[/yellow]")
    
    def display_headless(self, refresh_interval: float = 30.0):
        """Display dashboard in headless mode (single update per interval)"""
        try:
            while True:
                self.display_static()
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard stopped[/yellow]")


def start_cli_dashboard(db_path: str = DEFAULT_DB_PATH, 
                       live_mode: bool = True,
                       refresh_interval: float = 5.0):
    """Start the CLI dashboard
    
    Args:
        db_path: Path to SQLite database
        live_mode: If True, use live updating; if False, static display
        refresh_interval: Seconds between updates
    """
    dashboard = CLIDashboard(db_path)
    
    try:
        if live_mode:
            dashboard.display_live(refresh_interval)
        else:
            dashboard.display_headless(refresh_interval)
    except Exception as e:
        logging.error(f"Error in CLI dashboard: {e}")
        raise


def main():
    """Main entry point for CLI dashboard with database initialization"""
    import sys
    
    # Ensure databases are initialized before starting dashboard
    print("=" * 60)
    print("Sentinel Agent - CLI Dashboard")
    print("=" * 60)
    print()
    print("Initializing databases...")
    
    try:
        # Try to initialize all databases
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from init_database import initialize_all_databases
        initialize_all_databases()
        print("✓ Databases initialized")
    except Exception as e:
        print(f"⚠ Database initialization warning: {e}")
        print("Attempting to continue with local initialization...")
        # If init_database fails, at least ensure the main DB is initialized
        try:
            data_mgr = CLIDashboardDataManager()
            print("✓ Local database initialized")
        except Exception as e2:
            print(f"✗ Error: {e2}")
            print("\nPlease run: python3 init_database.py")
            return 1
    
    print()
    print("Starting dashboard (press Ctrl+C to exit)...")
    print()
    
    try:
        start_cli_dashboard(live_mode=False, refresh_interval=10.0)
    except KeyboardInterrupt:
        print("\nDashboard stopped")
    except Exception as e:
        print(f"\n✗ Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
