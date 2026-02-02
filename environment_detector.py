"""
Environment Detection Module

Determines if the system is running in a GUI-capable environment or CLI-only headless mode.
Used to switch between web dashboard and terminal UI modes.
"""

import os
import sys
import logging
from typing import Literal

logger = logging.getLogger(__name__)


class EnvironmentDetector:
    """Detects the current environment (GUI vs CLI)."""

    @staticmethod
    def has_display() -> bool:
        """
        Check if a GUI display is available.
        
        Returns:
            True if GUI environment detected, False for headless/CLI-only
        """
        # Check for DISPLAY variable (Unix/Linux GUI)
        if os.environ.get("DISPLAY"):
            return True
        
        # Check for WAYLAND_DISPLAY (Wayland GUI)
        if os.environ.get("WAYLAND_DISPLAY"):
            return True
        
        # Windows: Check if running in terminal with GUI capability
        if sys.platform == "win32":
            # If running in Windows Terminal, VS Code, or similar: assume GUI capable
            if os.environ.get("WT_SESSION") or os.environ.get("TERM_PROGRAM"):
                return True
        
        # macOS: Check for GUI environment
        if sys.platform == "darwin":
            if os.environ.get("DISPLAY"):
                return True
        
        # Default to headless/CLI
        return False

    @staticmethod
    def is_docker() -> bool:
        """
        Check if running inside a Docker container.
        
        Returns:
            True if Docker detected, False otherwise
        """
        # Check for /.dockerenv file
        if os.path.exists("/.dockerenv"):
            return True
        
        # Check for docker in cgroup
        try:
            with open("/proc/self/cgroup", "r") as f:
                return "docker" in f.read()
        except (FileNotFoundError, IOError):
            pass
        
        return False

    @staticmethod
    def is_systemd() -> bool:
        """
        Check if running as a systemd service.
        
        Returns:
            True if systemd detected, False otherwise
        """
        # Check for SYSTEMD_UNIT or similar env vars set by systemd
        if os.environ.get("SYSTEMD_UNIT"):
            return True
        
        # Check if parent process is systemd
        try:
            with open("/proc/1/comm", "r") as f:
                return "systemd" in f.read()
        except (FileNotFoundError, IOError):
            pass
        
        return False

    @staticmethod
    def get_mode() -> Literal["gui", "cli", "docker", "systemd"]:
        """
        Determine the appropriate operational mode.
        
        Returns:
            "gui"      - GUI-capable environment (use web dashboard)
            "cli"      - CLI-only environment (use Rich terminal UI)
            "docker"   - Docker container (use Rich terminal UI)
            "systemd"  - systemd service (use logging only, no interactive UI)
        """
        if EnvironmentDetector.is_systemd():
            return "systemd"
        
        if EnvironmentDetector.is_docker():
            return "docker"
        
        if EnvironmentDetector.has_display():
            return "gui"
        
        return "cli"

    @staticmethod
    def get_config() -> dict:
        """
        Get environment-specific configuration.
        
        Returns:
            Dictionary with environment config:
            - mode: "gui", "cli", "docker", or "systemd"
            - dashboard_url: URL if GUI mode (127.0.0.1:8501)
            - print_heartbeat: Whether to print heartbeat messages
            - use_rich_output: Whether to use Rich terminal formatting
            - db_path: Path to SQLite database
        """
        mode = EnvironmentDetector.get_mode()
        
        config = {
            "mode": mode,
            "print_heartbeat": mode in ["gui", "docker"],
            "use_rich_output": mode in ["cli", "docker"],
            "db_path": os.environ.get("DATA_DIR", "/app/data") + "/sentinel_intel.db",
        }
        
        if mode == "gui":
            config["dashboard_url"] = "http://127.0.0.1:8501"
            config["dashboard_enabled"] = True
        else:
            config["dashboard_url"] = None
            config["dashboard_enabled"] = False
        
        return config


# Singleton instance
_detector = None


def get_detector() -> EnvironmentDetector:
    """Get the global EnvironmentDetector instance."""
    global _detector
    if _detector is None:
        _detector = EnvironmentDetector()
    return _detector


def get_environment_config() -> dict:
    """Get the environment configuration (convenience function)."""
    return get_detector().get_config()
