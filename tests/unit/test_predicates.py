"""
Unit tests for predicates module.
"""

import unittest
from unittest.mock import Mock, MagicMock
from core import SessionContext, FSMState
from core.predicates import PredicateEvaluator


class TestPredicates(unittest.TestCase):
    """Test predicate evaluation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = SessionContext()
        self.evaluator = PredicateEvaluator()
    
    def test_check_config_valid(self):
        """Test config validation predicate."""
        # No config
        passed, bounds = self.evaluator.check_config_valid(self.context)
        self.assertFalse(passed)
        
        # Valid config
        self.context.config = {"hardware": {}, "safety": {}}
        self.context.config_hash = "test_hash"
        passed, bounds = self.evaluator.check_config_valid(self.context)
        self.assertTrue(passed)
        self.assertEqual(bounds["config_hash"], "test_hash")
    
    def test_check_calibration_valid(self):
        """Test calibration validation predicate."""
        # No calibration
        passed, bounds = self.evaluator.check_calibration_valid(self.context)
        self.assertFalse(passed)
        
        # Valid calibration
        self.context.calibration = {"points": [
            {"wavelength": 400, "voltage": 0.1},
            {"wavelength": 650, "voltage": 0.9}
        ]}
        self.context.cal_hash = "test_cal_hash"
        passed, bounds = self.evaluator.check_calibration_valid(self.context)
        self.assertTrue(passed)
        self.assertEqual(bounds["cal_hash"], "test_cal_hash")
    
    def test_check_interlock_safe(self):
        """Test interlock safety predicate."""
        # No laser controller
        passed, bounds = self.evaluator.check_interlock_safe(self.context)
        self.assertFalse(passed)
        
        # Mock laser controller
        mock_laser = Mock()
        mock_laser.is_interlock_safe = Mock(return_value=True)
        self.context.laser_controller = mock_laser
        
        passed, bounds = self.evaluator.check_interlock_safe(self.context)
        self.assertTrue(passed)
        self.assertTrue(bounds["interlock_safe"])
    
    def test_check_budget_available(self):
        """Test budget availability predicate."""
        from core.context import Budget
        
        # No budget
        passed, bounds = self.evaluator.check_budget_available(self.context)
        self.assertFalse(passed)
        
        # Budget with sufficient resources
        self.context.budget = Budget(
            remaining_emit_ms=1000.0,
            remaining_duty_percent=50.0,
            cooldown_remaining_ms=0.0
        )
        
        passed, bounds = self.evaluator.check_budget_available(
            self.context, required_emit_ms=500.0, required_duty_percent=25.0
        )
        self.assertTrue(passed)
        
        # Insufficient budget
        passed, bounds = self.evaluator.check_budget_available(
            self.context, required_emit_ms=2000.0, required_duty_percent=75.0
        )
        self.assertFalse(passed)
    
    def test_check_cooldown_satisfied(self):
        """Test cooldown satisfaction predicate."""
        from core.context import Budget
        import time
        
        # No budget
        passed, bounds = self.evaluator.check_cooldown_satisfied(self.context)
        self.assertFalse(passed)
        
        # Budget with cooldown remaining
        self.context.budget = Budget(
            remaining_emit_ms=1000.0,
            remaining_duty_percent=100.0,
            cooldown_remaining_ms=5000.0,
            last_emit_end_time=time.monotonic() - 1.0
        )
        self.context.config = {"safety": {"cooldown_time": 10.0}}
        
        passed, bounds = self.evaluator.check_cooldown_satisfied(self.context)
        self.assertFalse(passed)  # Cooldown not satisfied yet
    
    def test_check_no_outstanding_faults(self):
        """Test fault check predicate."""
        # No faults
        passed, bounds = self.evaluator.check_no_outstanding_faults(self.context)
        self.assertTrue(passed)
        
        # In FAULT state
        self.context.state = FSMState.FAULT
        self.context.fault_reason = "Test fault"
        passed, bounds = self.evaluator.check_no_outstanding_faults(self.context)
        self.assertFalse(passed)


if __name__ == '__main__':
    unittest.main()

