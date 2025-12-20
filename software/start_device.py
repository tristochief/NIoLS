#!/usr/bin/env python3
"""
Professional startup script for EUV Detection & Laser Communication Device

Performs system checks, validates configuration, and starts the device.
Includes FSM initialization and session bundle management.
"""

import sys
import logging
import signal
import atexit
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('device.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Global session bundle reference for cleanup
_session_bundle = None

def check_dependencies():
    """Check if all required dependencies are installed."""
    logger.info("Checking dependencies...")
    missing = []
    
    required = ['fastapi', 'uvicorn', 'numpy', 'yaml']
    for module in required:
        try:
            __import__(module if module != 'yaml' else 'yaml')
            logger.info(f"  ✓ {module}")
        except ImportError:
            missing.append(module)
            logger.error(f"  ✗ {module} - MISSING")
    
    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.error("Please run: pip install -r requirements.txt")
        return False
    
    logger.info("All dependencies available")
    return True

def validate_configuration():
    """Validate configuration file."""
    logger.info("Validating configuration...")
    
    try:
        from hardware_control.system_health import validate_config
        
        config_path = Path(__file__).parent / "config" / "device_config.yaml"
        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_path}")
            logger.warning("Using default configuration")
            return True
        
        is_valid, errors = validate_config(str(config_path))
        if not is_valid:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("Configuration valid")
        return True
    except Exception as e:
        logger.error(f"Configuration validation error: {e}")
        return False

def run_health_check():
    """Run initial health check."""
    logger.info("Running initial health check...")
    
    try:
        from hardware_control.system_health import SystemHealthMonitor
        
        monitor = SystemHealthMonitor()
        checks = monitor.run_all_checks()
        
        overall_status, overall_message = monitor.get_overall_status()
        
        if overall_status.value == "healthy":
            logger.info(f"System health: {overall_message}")
        elif overall_status.value == "warning":
            logger.warning(f"System health: {overall_message}")
        else:
            logger.error(f"System health: {overall_message}")
        
        return overall_status.value in ["healthy", "warning"]
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

def run_verify_gate():
    """Run verification gate before startup."""
    logger.info("Running verification gate...")
    
    try:
        verify_script = Path(__file__).parent / "verify.py"
        if verify_script.exists():
            import subprocess
            result = subprocess.run(
                [sys.executable, str(verify_script)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error("Verification gate failed:")
                logger.error(result.stdout)
                logger.error(result.stderr)
                return False
            
            logger.info("Verification gate passed")
            return True
        else:
            logger.warning("verify.py not found, skipping verification gate")
            return True
    except Exception as e:
        logger.error(f"Verification gate error: {e}")
        return False


def write_session_bundle_on_exit():
    """Write session bundle on exit."""
    global _session_bundle
    if _session_bundle:
        try:
            logger.info("Writing session bundle on exit...")
            _session_bundle.write_bundle()
            logger.info("Session bundle written successfully")
        except Exception as e:
            logger.error(f"Failed to write session bundle: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    write_session_bundle_on_exit()
    sys.exit(0)


def main():
    """Main startup function."""
    global _session_bundle
    
    logger.info("=" * 60)
    logger.info("EUV Detection & Laser Communication Device")
    logger.info("Professional Startup (Operational Closure)")
    logger.info("=" * 60)
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    atexit.register(write_session_bundle_on_exit)
    
    # Run verification gate
    if not run_verify_gate():
        logger.error("Startup aborted due to verification gate failure")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Startup aborted due to missing dependencies")
        sys.exit(1)
    
    # Validate configuration
    if not validate_configuration():
        logger.error("Startup aborted due to configuration errors")
        sys.exit(1)
    
    # Run health check
    if not run_health_check():
        logger.warning("Health check issues detected, but continuing...")
    
    # Start FastAPI server
    logger.info("Starting FastAPI server...")
    logger.info("=" * 60)
    logger.info("API server will be available at http://localhost:8000")
    logger.info("Frontend should be running at http://localhost:3000 (or build and serve from /api)")
    logger.info("Session bundles will be written to logs/sessions/<session_id>/")
    logger.info("=" * 60)
    
    import uvicorn
    
    try:
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        write_session_bundle_on_exit()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        write_session_bundle_on_exit()
        sys.exit(1)

if __name__ == "__main__":
    main()

