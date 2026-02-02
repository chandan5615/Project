"""
Sentinel Agent Dashboard Control Module
Manages dashboard initialization, configuration, and mode selection
"""

import logging
import threading
import time
from typing import Optional, Dict
from pathlib import Path
import subprocess
import sys


class DashboardController:
    """Controls dashboard lifecycle and configuration"""
    
    def __init__(self, environment_config: Dict):
        """
        Initialize dashboard controller
        
        Args:
            environment_config: Configuration dict from environment_detector
        """
        self.config = environment_config
        self.mode = environment_config.get("mode", "cli")
        self.db_path = environment_config.get("db_path", "sentinel_intel.db")
        self.dashboard_url = environment_config.get("dashboard_url", "http://127.0.0.1:8501")
        self.logger = logging.getLogger(__name__)
        self.dashboard_process = None
        self.dashboard_thread = None
    
    def start_web_dashboard(self, port: int = 8501):
        """
        Start Streamlit web dashboard in subprocess
        
        Args:
            port: Port to run Streamlit on
        """
        if self.mode == "docker" or self.mode == "systemd":
            self.logger.warning("Web dashboard not available in Docker/systemd mode")
            return False
        
        try:
            # Check if Streamlit is installed
            import streamlit
            
            dashboard_script = Path(__file__).parent / "dashboard" / "web_dashboard.py"
            
            if not dashboard_script.exists():
                self.logger.error(f"Dashboard script not found: {dashboard_script}")
                return False
            
            # Build command
            cmd = [
                sys.executable, "-m", "streamlit", "run",
                str(dashboard_script),
                "--server.port", str(port),
                "--server.address", "127.0.0.1",
                "--logger.level", "error",
                "--client.showErrorDetails", "false"
            ]
            
            # Start process
            self.dashboard_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(Path(__file__).parent)
            )
            
            self.logger.info(f"Web dashboard started on {self.dashboard_url}")
            return True
        
        except ImportError:
            self.logger.error("Streamlit not installed. Install with: pip install streamlit")
            return False
        except Exception as e:
            self.logger.error(f"Failed to start web dashboard: {e}")
            return False
    
    def start_cli_dashboard(self, live_mode: bool = True, refresh_interval: float = 5.0):
        """
        Start CLI dashboard in separate thread
        
        Args:
            live_mode: Whether to use live updating mode
            refresh_interval: Seconds between updates
        """
        if self.mode not in ["cli"]:
            self.logger.warning("CLI dashboard only available in CLI mode")
            return False
        
        try:
            from dashboard.cli_dashboard import start_cli_dashboard
            
            def run_dashboard():
                try:
                    start_cli_dashboard(
                        db_path=self.db_path,
                        live_mode=live_mode,
                        refresh_interval=refresh_interval
                    )
                except KeyboardInterrupt:
                    self.logger.info("CLI dashboard stopped")
                except Exception as e:
                    self.logger.error(f"CLI dashboard error: {e}")
            
            # Start in daemon thread
            self.dashboard_thread = threading.Thread(
                target=run_dashboard,
                daemon=True
            )
            self.dashboard_thread.start()
            
            self.logger.info("CLI dashboard started")
            return True
        
        except ImportError as e:
            self.logger.error(f"Failed to import CLI dashboard: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to start CLI dashboard: {e}")
            return False
    
    def start_dashboard(self):
        """Start appropriate dashboard based on environment mode"""
        if self.mode == "gui":
            self.logger.info("Starting web dashboard (GUI mode)")
            return self.start_web_dashboard()
        
        elif self.mode == "cli":
            self.logger.info("Starting CLI dashboard (CLI mode)")
            return self.start_cli_dashboard(live_mode=False, refresh_interval=30.0)
        
        elif self.mode in ["docker", "systemd"]:
            self.logger.info(f"Dashboard disabled for {self.mode} mode - logging only")
            return True
        
        else:
            self.logger.warning(f"Unknown mode: {self.mode}")
            return False
    
    def stop_dashboard(self):
        """Stop running dashboard"""
        try:
            if self.dashboard_process:
                self.dashboard_process.terminate()
                self.dashboard_process.wait(timeout=5)
                self.logger.info("Web dashboard stopped")
            
            # Thread will stop naturally
            if self.dashboard_thread:
                self.logger.info("CLI dashboard stopping")
        
        except Exception as e:
            self.logger.error(f"Error stopping dashboard: {e}")
    
    def get_dashboard_status(self) -> Dict:
        """Get current dashboard status"""
        return {
            "mode": self.mode,
            "active": self.dashboard_process is not None or self.dashboard_thread is not None,
            "url": self.dashboard_url if self.mode == "gui" else None,
            "db_path": self.db_path
        }


class DashboardConfig:
    """Manages dashboard configuration"""
    
    # Default configuration
    DEFAULTS = {
        "gui": {
            "type": "streamlit",
            "port": 8501,
            "address": "127.0.0.1",
            "refresh_interval": 30,
            "auto_start": True,
            "theme": "dark"
        },
        "cli": {
            "type": "rich",
            "live_mode": False,
            "refresh_interval": 30,
            "auto_start": False,
            "width": 120,
            "height": 40
        },
        "docker": {
            "type": "none",
            "auto_start": False
        },
        "systemd": {
            "type": "none",
            "auto_start": False
        }
    }
    
    @staticmethod
    def get_config(mode: str) -> Dict:
        """Get configuration for a specific mode
        
        Args:
            mode: Environment mode (gui, cli, docker, systemd)
            
        Returns:
            Configuration dictionary for the mode
        """
        return DashboardConfig.DEFAULTS.get(mode, {})
    
    @staticmethod
    def merge_config(mode: str, custom_config: Dict) -> Dict:
        """Merge custom config with defaults
        
        Args:
            mode: Environment mode
            custom_config: Custom configuration to merge
            
        Returns:
            Merged configuration dictionary
        """
        default = DashboardConfig.get_config(mode)
        return {**default, **custom_config}


def create_dashboard_controller(environment_config: Dict) -> DashboardController:
    """Factory function to create dashboard controller
    
    Args:
        environment_config: Config dict from environment_detector
        
    Returns:
        DashboardController instance
    """
    return DashboardController(environment_config)


if __name__ == "__main__":
    # Example usage
    config = {
        "mode": "cli",
        "db_path": "sentinel_intel.db",
        "dashboard_url": "http://127.0.0.1:8501"
    }
    
    controller = DashboardController(config)
    
    # Start dashboard
    controller.start_dashboard()
    
    # Keep running for 60 seconds
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop_dashboard()
