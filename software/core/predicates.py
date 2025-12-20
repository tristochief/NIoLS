"""
Predicate Evaluator Module

Pure functions evaluating all guard conditions for FSM transitions.
Returns boolean results and numeric bounds for envelope computation.
"""

import time
import logging
from typing import Dict, Any, Tuple, Optional
from .context import SessionContext, FSMState

logger = logging.getLogger(__name__)


class PredicateEvaluator:
    """
    Evaluates guard predicates for FSM transitions.
    
    All predicates are pure functions that take context and return
    (bool, Dict[str, Any]) where the dict contains numeric bounds.
    """
    
    @staticmethod
    def check_config_valid(context: SessionContext) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if configuration is valid and loaded.
        
        Returns:
            (is_valid, bounds_dict)
        """
        if context.config is None:
            return False, {"error": "config_not_loaded"}
        
        if context.config_hash is None:
            return False, {"error": "config_hash_not_computed"}
        
        # Check required sections
        required_sections = ['hardware', 'safety']
        for section in required_sections:
            if section not in context.config:
                return False, {"error": f"missing_section_{section}"}
        
        return True, {"config_hash": context.config_hash}
    
    @staticmethod
    def check_calibration_valid(context: SessionContext) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if calibration is valid and loaded.
        
        Returns:
            (is_valid, bounds_dict)
        """
        if context.calibration is None:
            return False, {"error": "calibration_not_loaded"}
        
        if context.cal_hash is None:
            return False, {"error": "cal_hash_not_computed"}
        
        # Check calibration has points
        points = context.calibration.get('points', [])
        if not points or len(points) < 2:
            return False, {"error": "insufficient_calibration_points", "points": len(points)}
        
        return True, {"cal_hash": context.cal_hash, "points": len(points)}
    
    @staticmethod
    def check_dependencies_ok(context: SessionContext) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if all dependencies are available.
        
        Returns:
            (is_valid, bounds_dict)
        """
        if context.health_monitor is None:
            return False, {"error": "health_monitor_not_available"}
        
        try:
            check = context.health_monitor.check_dependencies()
            is_ok = check.status.value == "healthy"
            return is_ok, {
                "status": check.status.value,
                "message": check.message,
                "details": check.details or {}
            }
        except Exception as e:
            logger.error(f"Dependency check failed: {e}")
            return False, {"error": str(e)}
    
    @staticmethod
    def check_interlock_safe(context: SessionContext) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if safety interlock is engaged.
        
        Returns:
            (is_safe, bounds_dict)
        """
        if context.laser_controller is None:
            # In simulation mode, allow if no hardware
            if context.simulation_mode:
                return True, {"simulation": True, "interlock_safe": True}
            return False, {"error": "laser_controller_not_available"}
        
        try:
            is_safe = context.laser_controller.is_interlock_safe()
            return is_safe, {"interlock_safe": is_safe}
        except Exception as e:
            logger.error(f"Interlock check failed: {e}")
            return False, {"error": str(e)}
    
    @staticmethod
    def check_no_outstanding_faults(context: SessionContext) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if there are no outstanding faults.
        
        Returns:
            (no_faults, bounds_dict)
        """
        if context.state == FSMState.FAULT:
            return False, {
                "fault_state": True,
                "fault_reason": context.fault_reason or "unknown"
            }
        
        return True, {"faults": 0}
    
    @staticmethod
    def check_cooldown_satisfied(context: SessionContext) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if cooldown period is satisfied.
        
        Returns:
            (cooldown_satisfied, bounds_dict with remaining_ms)
        """
        if context.budget is None:
            return False, {"error": "budget_not_initialized"}
        
        config = context.config or {}
        safety = config.get('safety', {})
        cooldown_time_ms = safety.get('cooldown_time', 60.0) * 1000.0
        
        current_time = time.monotonic()
        context.budget.update_cooldown(current_time, cooldown_time_ms)
        
        is_satisfied = context.budget.cooldown_remaining_ms <= 0.0
        
        return is_satisfied, {
            "cooldown_satisfied": is_satisfied,
            "cooldown_remaining_ms": context.budget.cooldown_remaining_ms,
            "cooldown_required_ms": cooldown_time_ms
        }
    
    @staticmethod
    def check_arm_confirmation_within_window(context: SessionContext) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if arm confirmation is within the arming window.
        
        Returns:
            (within_window, bounds_dict)
        """
        is_valid = context.is_arming_window_valid()
        
        if context.arming_window_start is None:
            return False, {"error": "arming_window_not_started"}
        
        elapsed_ms = (time.monotonic() - context.arming_window_start) * 1000.0
        remaining_ms = max(0.0, context.arming_window_duration_ms - elapsed_ms)
        
        return is_valid, {
            "within_window": is_valid,
            "elapsed_ms": elapsed_ms,
            "remaining_ms": remaining_ms,
            "window_duration_ms": context.arming_window_duration_ms
        }
    
    @staticmethod
    def check_budget_available(context: SessionContext, 
                              required_emit_ms: float = 0.0,
                              required_duty_percent: float = 0.0) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if sufficient budget is available for emission.
        
        Args:
            context: Session context
            required_emit_ms: Required emission time in milliseconds
            required_duty_percent: Required duty cycle percentage
            
        Returns:
            (budget_available, bounds_dict with remaining budgets)
        """
        if context.budget is None:
            return False, {"error": "budget_not_initialized"}
        
        has_emit_time = context.budget.remaining_emit_ms >= required_emit_ms
        has_duty_cycle = context.budget.remaining_duty_percent >= required_duty_percent
        
        budget_available = has_emit_time and has_duty_cycle
        
        return budget_available, {
            "budget_available": budget_available,
            "remaining_emit_ms": context.budget.remaining_emit_ms,
            "required_emit_ms": required_emit_ms,
            "remaining_duty_percent": context.budget.remaining_duty_percent,
            "required_duty_percent": required_duty_percent,
            "has_emit_time": has_emit_time,
            "has_duty_cycle": has_duty_cycle
        }
    
    @staticmethod
    def check_hardware_health(context: SessionContext) -> Tuple[bool, Dict[str, Any]]:
        """
        Check hardware health status.
        
        Returns:
            (is_healthy, bounds_dict)
        """
        if context.health_monitor is None:
            # In simulation, allow if no monitor
            if context.simulation_mode:
                return True, {"simulation": True, "hardware_health": "simulated"}
            return False, {"error": "health_monitor_not_available"}
        
        try:
            checks = context.health_monitor.run_all_checks(
                context.photodiode_reader,
                context.laser_controller,
                context.config.get('logging', {}).get('log_dir', 'logs') if context.config else 'logs'
            )
            
            # Check for critical or error status
            has_critical = any(c.status.value == "critical" for c in checks)
            has_error = any(c.status.value == "error" for c in checks)
            is_healthy = not (has_critical or has_error)
            
            return is_healthy, {
                "hardware_healthy": is_healthy,
                "has_critical": has_critical,
                "has_error": has_error,
                "checks": [
                    {
                        "name": c.name,
                        "status": c.status.value,
                        "message": c.message
                    }
                    for c in checks
                ]
            }
        except Exception as e:
            logger.error(f"Hardware health check failed: {e}")
            return False, {"error": str(e)}
    
    @staticmethod
    def check_config_hash_match(context: SessionContext, current_config_hash: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if current config hash matches the bound hash.
        
        Args:
            context: Session context
            current_config_hash: Current computed config hash
            
        Returns:
            (hash_matches, bounds_dict)
        """
        if context.config_hash is None:
            return False, {"error": "config_hash_not_bound"}
        
        matches = context.config_hash == current_config_hash
        
        return matches, {
            "hash_matches": matches,
            "bound_hash": context.config_hash,
            "current_hash": current_config_hash
        }
    
    @staticmethod
    def check_cal_hash_match(context: SessionContext, current_cal_hash: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if current calibration hash matches the bound hash.
        
        Args:
            context: Session context
            current_cal_hash: Current computed calibration hash
            
        Returns:
            (hash_matches, bounds_dict)
        """
        if context.cal_hash is None:
            return False, {"error": "cal_hash_not_bound"}
        
        matches = context.cal_hash == current_cal_hash
        
        return matches, {
            "hash_matches": matches,
            "bound_hash": context.cal_hash,
            "current_hash": current_cal_hash
        }

