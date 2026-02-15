"""
Tests for Sentinel Agent Adaptive Reporting System
Tests environment detection, logging, and dashboard controllers
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import logging
import os
import sys

# Test environment_detector
from environment_detector import EnvironmentDetector


class TestEnvironmentDetector:
    """Test environment detection functionality"""
    
    def test_detector_singleton(self):
        """Test that EnvironmentDetector is a singleton"""
        detector1 = EnvironmentDetector()
        detector2 = EnvironmentDetector()
        
        # Should be same instance
        assert detector1.get_mode() == detector2.get_mode()
    
    def test_has_display(self):
        """Test display detection"""
        detector = EnvironmentDetector()
        result = detector.has_display()
        assert isinstance(result, bool)
    
    def test_is_docker(self):
        """Test Docker detection"""
        detector = EnvironmentDetector()
        result = detector.is_docker()
        assert isinstance(result, bool)
    
    def test_is_systemd(self):
        """Test systemd detection"""
        detector = EnvironmentDetector()
        result = detector.is_systemd()
        assert isinstance(result, bool)
    
    def test_get_mode(self):
        """Test that get_mode returns valid mode"""
        detector = EnvironmentDetector()
        mode = detector.get_mode()
        
        assert mode in ["gui", "cli", "docker", "systemd"]
    
    def test_get_config(self):
        """Test configuration dictionary"""
        detector = EnvironmentDetector()
        config = detector.get_environment_config()
        
        # Check required keys
        assert "mode" in config
        assert "dashboard_url" in config
        assert "print_heartbeat" in config
        assert "use_rich_output" in config
        assert "db_path" in config
        
        # Check types
        assert isinstance(config["mode"], str)
        assert isinstance(config["print_heartbeat"], bool)
        assert isinstance(config["use_rich_output"], bool)


# Test logging_adapter
from logging_adapter import AdaptiveLogger, AdaptivePrinter, create_adaptive_logger


class TestAdaptiveLogger:
    """Test adaptive logging functionality"""
    
    @pytest.fixture
    def temp_log_file(self):
        """Create temporary log file"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as f:
            path = f.name
        yield path
        # Cleanup
        if Path(path).exists():
            Path(path).unlink()
    
    def test_logger_creation(self, temp_log_file):
        """Test logger creation with different modes"""
        for mode in ["gui", "cli", "docker", "systemd"]:
            logger = AdaptiveLogger(
                mode=mode,
                log_file=temp_log_file,
                console_level=logging.WARNING,
                file_level=logging.DEBUG
            )
            assert logger.mode == mode
            assert logger.logger is not None
    
    def test_heartbeat_logging(self, temp_log_file):
        """Test heartbeat logging"""
        logger = AdaptiveLogger(mode="cli", log_file=temp_log_file)
        
        # Should not raise exception
        logger.heartbeat(threat_count=3, blocked_ips=2)
        logger.heartbeat(threat_count=0, blocked_ips=0)
    
    def test_threat_logging(self, temp_log_file):
        """Test threat detection logging"""
        logger = AdaptiveLogger(mode="cli", log_file=temp_log_file)
        
        logger.log_threat_detected("Brute Force", "192.168.1.100", "BLOCK")
        logger.log_system_status("Test Status", "Test details")
        logger.log_error("Test error", None)
    
    def test_adaptive_printer(self):
        """Test adaptive printer"""
        for mode in ["gui", "cli", "docker", "systemd"]:
            printer = AdaptivePrinter(mode=mode)
            
            # Should not raise exceptions
            printer.print_dashboard_header()
            printer.print_threat_alert("Brute Force", "192.168.1.100", "BLOCK")
            printer.print_status_message("Test message")
            printer.print_network_summary(10, 5, 75)


# Test dashboard_controller
pytest.importorskip("streamlit")  # Skip tests if streamlit not installed

from dashboard_controller import DashboardController, DashboardConfig


class TestDashboardController:
    """Test dashboard controller functionality"""
    
    def test_config_get_config(self):
        """Test getting configuration for modes"""
        for mode in ["gui", "cli", "docker", "systemd"]:
            config = DashboardConfig.get_config(mode)
            assert isinstance(config, dict)
            assert "type" in config
    
    def test_config_merge(self):
        """Test configuration merging"""
        default = DashboardConfig.get_config("cli")
        custom = {"refresh_interval": 60}
        merged = DashboardConfig.merge_config("cli", custom)
        
        # Custom values should override
        assert merged["refresh_interval"] == 60
        # Default values should be preserved
        assert "type" in merged
    
    def test_controller_creation(self):
        """Test controller creation"""
        config = {
            "mode": "cli",
            "db_path": "test.db",
            "dashboard_url": "http://127.0.0.1:8501"
        }
        
        controller = DashboardController(config)
        assert controller.mode == "cli"
        assert controller.db_path == "test.db"
    
    def test_controller_status(self):
        """Test controller status reporting"""
        config = {
            "mode": "cli",
            "db_path": "test.db",
            "dashboard_url": "http://127.0.0.1:8501"
        }
        
        controller = DashboardController(config)
        status = controller.get_dashboard_status()
        
        assert status["mode"] == "cli"
        assert status["db_path"] == "test.db"
        assert isinstance(status["active"], bool)


# Test CLI Dashboard (if available)
pytest.importorskip("rich")

from dashboard.cli_dashboard import CLIDashboardDataManager, CLIDashboard


class TestCLIDashboard:
    """Test CLI dashboard functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database with test data"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name
        
        # Create schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE incidents (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                source_ip TEXT,
                threat_type TEXT,
                details TEXT,
                action TEXT
            )
        """)
        
        # Insert test data
        now = datetime.now()
        for i in range(5):
            timestamp = (now - timedelta(minutes=i)).isoformat()
            cursor.execute("""
                INSERT INTO incidents 
                (timestamp, source_ip, threat_type, details, action)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, f"192.168.1.{100+i}", "Brute Force", f"Test threat {i}", "BLOCK"))
        
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        if Path(db_path).exists():
            Path(db_path).unlink()
    
    def test_data_manager_creation(self, temp_db):
        """Test data manager creation"""
        manager = CLIDashboardDataManager(temp_db)
        assert manager.db_path == temp_db
    
    def test_recent_blocks(self, temp_db):
        """Test fetching recent blocks"""
        manager = CLIDashboardDataManager(temp_db)
        blocks = manager.get_recent_blocks(limit=3)
        
        assert isinstance(blocks, list)
        assert len(blocks) > 0
        assert "ip" in blocks[0]
        assert "threat_type" in blocks[0]
    
    def test_security_score(self, temp_db):
        """Test security score calculation"""
        manager = CLIDashboardDataManager(temp_db)
        score, status, color = manager.calculate_security_score()
        
        assert 0 <= score <= 100
        assert status in ["SECURE", "CAUTION", "CRITICAL"]
        assert color in ["green", "yellow", "red"]
    
    def test_cli_dashboard_creation(self, temp_db):
        """Test CLI dashboard creation"""
        dashboard = CLIDashboard(temp_db)
        assert dashboard.data_manager is not None
        assert dashboard.console is not None


# Integration tests
class TestAdaptiveReportingIntegration:
    """Integration tests for adaptive reporting system"""
    
    def test_full_workflow(self):
        """Test complete workflow"""
        # Detect environment
        detector = EnvironmentDetector()
        config = detector.get_environment_config()
        
        # Create logger with temp file (Windows-safe)
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            temp_log_path = f.name
        
        try:
            config_with_log = config.copy()
            config_with_log["log_path"] = temp_log_path
            
            logger = create_adaptive_logger(config_with_log)
            
            # Test various logging operations
            logger.heartbeat(threat_count=5, blocked_ips=3)
            logger.log_threat_detected("Brute Force", "192.168.1.100", "BLOCK")
            logger.log_system_status("Monitoring", "All systems operational")
            logger.log_error("Test error", None)
            
            logger.close()
        finally:
            if Path(temp_log_path).exists():
                Path(temp_log_path).unlink()
    
    def test_printer_with_config(self):
        """Test printer created from config"""
        from logging_adapter import create_adaptive_printer
        
        config = {
            "mode": "cli",
            "db_path": "test.db"
        }
        
        printer = create_adaptive_printer(config)
        assert printer.mode == "cli"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
