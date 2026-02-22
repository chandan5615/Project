"""
Environment Detection Module

Determines if the system is running in a GUI-capable environment or CLI-only headless mode.
Used to switch between web dashboard and terminal UI modes.
"""

import os
import sys
import logging
from contextlib import suppress
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
        return bool(
            os.environ.get("DISPLAY")
            or os.environ.get("WAYLAND_DISPLAY")
            or (
                sys.platform == "win32"
                and (os.environ.get("WT_SESSION") or os.environ.get("TERM_PROGRAM"))
            )
            or (sys.platform == "darwin" and os.environ.get("DISPLAY"))
        )

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
        with suppress(FileNotFoundError, IOError):
            with open("/proc/self/cgroup", "r") as f:
                return "docker" in f.read()
        
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
        with suppress(FileNotFoundError, IOError):
            with open("/proc/1/comm", "r") as f:
                return "systemd" in f.read()
        
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
        
        return "gui" if EnvironmentDetector.has_display() else "cli"

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
        
        dashboard_enabled = mode == "gui"
        config["dashboard_url"] = "http://127.0.0.1:8501" if dashboard_enabled else None
        config["dashboard_enabled"] = dashboard_enabled
        
        return config

    def get_environment_config(self) -> dict:
        """Compatibility wrapper for tests expecting this name."""
        return self.get_config()


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
