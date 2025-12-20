"""
System Health Monitoring Module

Provides health checks, diagnostics, and system status monitoring
for professional operation.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class HealthStatus(Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthCheck:
    """Health check result."""
    name: str
    status: HealthStatus
    message: str
    timestamp: float
    details: Optional[Dict] = None


class SystemHealthMonitor:
    """
    System health monitoring and diagnostics.
    """
    
    def __init__(self):
        """Initialize health monitor."""
        self.logger = logging.getLogger(__name__)
        self.checks: List[HealthCheck] = []
        self.last_check_time: Optional[float] = None
        self.check_interval: float = 5.0  # seconds
        
    def check_dependencies(self) -> HealthCheck:
        """Check if all required dependencies are available."""
        missing = []
        
        try:
            import fastapi
        except ImportError:
            missing.append("fastapi")
        
        try:
            import uvicorn
        except ImportError:
            missing.append("uvicorn")
        
        try:
            import numpy
        except ImportError:
            missing.append("numpy")
        
        try:
            import yaml
        except ImportError:
            missing.append("pyyaml")
        
        if missing:
            return HealthCheck(
                name="dependencies",
                status=HealthStatus.ERROR,
                message=f"Missing dependencies: {', '.join(missing)}",
                timestamp=time.time(),
                details={"missing": missing}
            )
        else:
            return HealthCheck(
                name="dependencies",
                status=HealthStatus.HEALTHY,
                message="All dependencies available",
                timestamp=time.time()
            )
    
    def check_hardware_availability(self, photodiode_reader, laser_controller) -> HealthCheck:
        """Check hardware connection status."""
        photodiode_ok = photodiode_reader is not None and photodiode_reader.is_connected()
        laser_ok = laser_controller is not None and laser_controller.is_connected()
        
        if not photodiode_ok and not laser_ok:
            return HealthCheck(
                name="hardware",
                status=HealthStatus.ERROR,
                message="No hardware connected",
                timestamp=time.time(),
                details={"photodiode": photodiode_ok, "laser": laser_ok}
            )
        elif not photodiode_ok or not laser_ok:
            return HealthCheck(
                name="hardware",
                status=HealthStatus.WARNING,
                message="Partial hardware connection",
                timestamp=time.time(),
                details={"photodiode": photodiode_ok, "laser": laser_ok}
            )
        else:
            return HealthCheck(
                name="hardware",
                status=HealthStatus.HEALTHY,
                message="All hardware connected",
                timestamp=time.time(),
                details={"photodiode": photodiode_ok, "laser": laser_ok}
            )
    
    def check_interlock(self, laser_controller) -> HealthCheck:
        """Check safety interlock status."""
        if laser_controller is None:
            return HealthCheck(
                name="interlock",
                status=HealthStatus.ERROR,
                message="Laser controller not initialized",
                timestamp=time.time()
            )
        
        is_safe = laser_controller.is_interlock_safe()
        
        if not is_safe:
            return HealthCheck(
                name="interlock",
                status=HealthStatus.CRITICAL,
                message="Safety interlock is UNSAFE - laser disabled",
                timestamp=time.time(),
                details={"interlock_safe": False}
            )
        else:
            return HealthCheck(
                name="interlock",
                status=HealthStatus.HEALTHY,
                message="Safety interlock engaged",
                timestamp=time.time(),
                details={"interlock_safe": True}
            )
    
    def check_calibration(self, photodiode_reader) -> HealthCheck:
        """Check photodiode calibration status."""
        if photodiode_reader is None:
            return HealthCheck(
                name="calibration",
                status=HealthStatus.WARNING,
                message="Photodiode reader not initialized",
                timestamp=time.time()
            )
        
        if not photodiode_reader.calibration_table:
            return HealthCheck(
                name="calibration",
                status=HealthStatus.WARNING,
                message="No calibration data loaded",
                timestamp=time.time()
            )
        
        cal_points = len(photodiode_reader.calibration_table)
        if cal_points < 3:
            return HealthCheck(
                name="calibration",
                status=HealthStatus.WARNING,
                message=f"Limited calibration data ({cal_points} points)",
                timestamp=time.time(),
                details={"calibration_points": cal_points}
            )
        
        return HealthCheck(
            name="calibration",
            status=HealthStatus.HEALTHY,
            message=f"Calibration loaded ({cal_points} points)",
            timestamp=time.time(),
            details={"calibration_points": cal_points}
        )
    
    def check_file_system(self, log_dir: str = "logs") -> HealthCheck:
        """Check file system accessibility."""
        try:
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True)
            
            # Test write
            test_file = log_path / ".health_check"
            test_file.write_text("test")
            test_file.unlink()
            
            return HealthCheck(
                name="filesystem",
                status=HealthStatus.HEALTHY,
                message="File system accessible",
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheck(
                name="filesystem",
                status=HealthStatus.ERROR,
                message=f"File system error: {str(e)}",
                timestamp=time.time(),
                details={"error": str(e)}
            )
    
    def run_all_checks(self, photodiode_reader=None, laser_controller=None, 
                      log_dir: str = "logs") -> List[HealthCheck]:
        """Run all health checks."""
        checks = []
        
        # Dependency check
        checks.append(self.check_dependencies())
        
        # Hardware check
        checks.append(self.check_hardware_availability(photodiode_reader, laser_controller))
        
        # Interlock check
        checks.append(self.check_interlock(laser_controller))
        
        # Calibration check
        checks.append(self.check_calibration(photodiode_reader))
        
        # File system check
        checks.append(self.check_file_system(log_dir))
        
        self.checks = checks
        self.last_check_time = time.time()
        
        return checks
    
    def get_overall_status(self) -> Tuple[HealthStatus, str]:
        """Get overall system health status."""
        if not self.checks:
            return HealthStatus.WARNING, "No health checks performed"
        
        # Find worst status
        status_priority = {
            HealthStatus.CRITICAL: 4,
            HealthStatus.ERROR: 3,
            HealthStatus.WARNING: 2,
            HealthStatus.HEALTHY: 1
        }
        
        worst_status = max(self.checks, key=lambda c: status_priority.get(c.status, 0))
        
        # Count issues
        critical_count = sum(1 for c in self.checks if c.status == HealthStatus.CRITICAL)
        error_count = sum(1 for c in self.checks if c.status == HealthStatus.ERROR)
        warning_count = sum(1 for c in self.checks if c.status == HealthStatus.WARNING)
        
        if critical_count > 0:
            message = f"{critical_count} critical issue(s)"
        elif error_count > 0:
            message = f"{error_count} error(s)"
        elif warning_count > 0:
            message = f"{warning_count} warning(s)"
        else:
            message = "All systems healthy"
        
        return worst_status.status, message
    
    def get_status_summary(self) -> Dict:
        """Get summary of all health checks."""
        overall_status, overall_message = self.get_overall_status()
        
        return {
            "overall_status": overall_status.value,
            "overall_message": overall_message,
            "last_check": self.last_check_time,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "message": check.message,
                    "details": check.details
                }
                for check in self.checks
            ]
        }
    
    def get_interlock_status(self, laser_controller) -> bool:
        """
        Get interlock status for predicate evaluation.
        
        Args:
            laser_controller: LaserController instance
            
        Returns:
            True if interlock is safe, False otherwise
        """
        if laser_controller is None:
            return False
        try:
            return laser_controller.is_interlock_safe()
        except Exception:
            return False
    
    def get_hardware_health(self, photodiode_reader, laser_controller, log_dir: str = "logs") -> Dict:
        """
        Get hardware health status for predicate evaluation.
        
        Args:
            photodiode_reader: PhotodiodeReader instance
            laser_controller: LaserController instance
            log_dir: Log directory path
            
        Returns:
            Dictionary with health status information
        """
        try:
            checks = self.run_all_checks(photodiode_reader, laser_controller, log_dir)
            overall_status, overall_message = self.get_overall_status()
            
            return {
                "overall_status": overall_status.value,
                "overall_message": overall_message,
                "checks": [
                    {
                        "name": check.name,
                        "status": check.status.value,
                        "message": check.message,
                        "details": check.details
                    }
                    for check in checks
                ],
                "is_healthy": overall_status.value in ["healthy", "warning"]
            }
        except Exception as e:
            return {
                "overall_status": "error",
                "overall_message": str(e),
                "checks": [],
                "is_healthy": False
            }
    
    def get_dependency_status(self) -> Dict:
        """
        Get dependency status for predicate evaluation.
        
        Returns:
            Dictionary with dependency status information
        """
        check = self.check_dependencies()
        return {
            "status": check.status.value,
            "message": check.message,
            "details": check.details or {},
            "is_ok": check.status.value == "healthy"
        }


def validate_config(config_path: str) -> Tuple[bool, List[str]]:
    """
    Validate configuration file.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        required_sections = ['hardware', 'signal_processing', 'logging']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate hardware section
        if 'hardware' in config:
            hw = config['hardware']
            if 'photodiode' not in hw:
                errors.append("Missing hardware.photodiode section")
            if 'laser' not in hw:
                errors.append("Missing hardware.laser section")
        
        # Validate laser power
        if 'hardware' in config and 'laser' in config['hardware']:
            # Check if power limits are reasonable
            pass  # Add specific validations if needed
        
    except FileNotFoundError:
        errors.append(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        errors.append(f"YAML parsing error: {str(e)}")
    except Exception as e:
        errors.append(f"Configuration validation error: {str(e)}")
    
    return len(errors) == 0, errors

