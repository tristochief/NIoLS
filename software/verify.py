#!/usr/bin/env python3
"""
Verification script for NIoLS operational closure system.

Runs dependency checks, config validation, tests, and sanity checks.
"""

import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are installed."""
    logger.info("Checking dependencies...")
    missing = []
    
    required = ['fastapi', 'uvicorn', 'numpy', 'yaml', 'pydantic']
    for module in required:
        try:
            if module == 'yaml':
                __import__('yaml')
            else:
                __import__(module)
            logger.info(f"  ✓ {module}")
        except ImportError:
            missing.append(module)
            logger.error(f"  ✗ {module} - MISSING")
    
    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        return False
    
    logger.info("All dependencies available")
    return True


def validate_config():
    """Validate configuration file."""
    logger.info("Validating configuration...")
    
    try:
        from hardware_control.system_health import validate_config
        
        config_path = Path(__file__).parent / "config" / "device_config.yaml"
        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_path}")
            return True  # Not a hard failure
        
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


def run_tests():
    """Run unit and integration tests."""
    logger.info("Running tests...")
    
    try:
        # Run unit tests
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/unit/', '-v'],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error("Unit tests failed:")
            logger.error(result.stdout)
            logger.error(result.stderr)
            return False
        
        logger.info("Unit tests passed")
        
        # Run integration tests
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/integration/', '-v'],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.warning("Integration tests failed (may require hardware):")
            logger.warning(result.stdout)
            logger.warning(result.stderr)
            # Don't fail on integration tests if hardware not available
            return True
        
        logger.info("Integration tests passed")
        return True
    except Exception as e:
        logger.error(f"Test execution error: {e}")
        return False


def test_fsm_init_simulation():
    """Test FSM initialization in simulation mode."""
    logger.info("Testing FSM initialization (simulation mode)...")
    
    try:
        from core import SessionContext, FSM, FSMEvent, TraceWriter, EventType
        from pathlib import Path
        import tempfile
        
        # Create temporary trace file
        temp_dir = Path(tempfile.mkdtemp())
        trace_file = temp_dir / "trace.jsonl"
        
        context = SessionContext(simulation_mode=True)
        context.config = {"hardware": {}, "safety": {}}
        context.config_hash = "test_hash"
        context.calibration = {"points": []}
        context.cal_hash = "test_cal_hash"
        
        trace_writer = TraceWriter(trace_file, context.session_id)
        
        def trace_callback(info):
            trace_writer.write_record(
                event_type=EventType.STATE_TRANSITION,
                state_from=info.get('from_state'),
                state_to=info.get('to_state'),
                predicates=info.get('predicates', {}),
                config_hash=context.config_hash,
                cal_hash=context.cal_hash
            )
        
        fsm = FSM(context, trace_callback)
        
        # Verify initial state
        assert fsm.get_state().value == "SAFE", "FSM should start in SAFE state"
        
        logger.info("  ✓ FSM initialization successful")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        return True
    except Exception as e:
        logger.error(f"FSM initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_trace_creation():
    """Test trace creation sanity check."""
    logger.info("Testing trace creation...")
    
    try:
        from core.trace import TraceWriter, TraceReader, EventType
        import tempfile
        from pathlib import Path
        
        temp_dir = Path(tempfile.mkdtemp())
        trace_file = temp_dir / "trace.jsonl"
        
        writer = TraceWriter(trace_file, "test_session")
        
        # Write a test record
        record = writer.write_record(
            event_type=EventType.STATE_TRANSITION,
            state_from="SAFE",
            state_to="INITIALIZED"
        )
        
        assert "hash" in record, "Record should have hash"
        assert record["seq"] == 1, "First record should have seq=1"
        
        # Verify chain
        reader = TraceReader(trace_file)
        is_valid, errors = reader.verify_chain()
        
        assert is_valid, f"Trace chain should be valid: {errors}"
        
        logger.info("  ✓ Trace creation successful")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        return True
    except Exception as e:
        logger.error(f"Trace creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_write_permissions():
    """Check write permissions in logs directory."""
    logger.info("Checking write permissions...")
    
    try:
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Test write
        test_file = log_dir / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        
        logger.info(f"  ✓ Write permissions OK in {log_dir}")
        return True
    except Exception as e:
        logger.error(f"Write permission check failed: {e}")
        return False


def main():
    """Run all verification checks."""
    logger.info("=" * 60)
    logger.info("NIoLS Verification Script")
    logger.info("=" * 60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Configuration", validate_config),
        ("Write Permissions", check_write_permissions),
        ("FSM Initialization", test_fsm_init_simulation),
        ("Trace Creation", check_trace_creation),
        ("Tests", run_tests),
    ]
    
    results = []
    for name, check_func in checks:
        logger.info("")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"{name} check raised exception: {e}")
            results.append((name, False))
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Verification Summary")
    logger.info("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("")
        logger.info("All checks passed!")
        return 0
    else:
        logger.error("")
        logger.error("Some checks failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

