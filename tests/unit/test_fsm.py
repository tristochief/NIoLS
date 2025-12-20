"""
Unit tests for FSM module.
"""

import unittest
import time
from unittest.mock import Mock, MagicMock
from core import SessionContext, FSMState, FSM, FSMEvent, FSMError


class TestFSM(unittest.TestCase):
    """Test FSM transitions and state management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = SessionContext()
        self.trace_writer = Mock()
        self.fsm = FSM(self.context, self.trace_writer)
    
    def test_initial_state(self):
        """Test FSM starts in SAFE state."""
        self.assertEqual(self.fsm.get_state(), FSMState.SAFE)
    
    def test_illegal_transition(self):
        """Test illegal transitions raise FSMError."""
        with self.assertRaises(FSMError):
            self.fsm.transition(FSMEvent.ARM)  # Can't arm from SAFE
    
    def test_safe_to_initialized_requires_predicates(self):
        """Test SAFE→INITIALIZED requires valid predicates."""
        # Mock predicate evaluator to return False
        self.fsm.predicate_evaluator.check_config_valid = Mock(return_value=(False, {"error": "test"}))
        
        # Should transition to FAULT on predicate failure
        success, message, _ = self.fsm.transition(FSMEvent.INITIALIZE)
        self.assertTrue(success)
        self.assertEqual(self.context.state, FSMState.FAULT)
    
    def test_legal_transitions(self):
        """Test all legal transitions work."""
        # Setup context for INITIALIZED
        self.context.config = {"hardware": {}, "safety": {}}
        self.context.config_hash = "test_hash"
        self.context.calibration = {"points": [{"wavelength": 400, "voltage": 0.1}]}
        self.context.cal_hash = "test_cal_hash"
        self.context.health_monitor = Mock()
        self.context.health_monitor.check_dependencies = Mock(return_value=Mock(status=Mock(value="healthy")))
        
        # Mock all predicates to pass
        self.fsm.predicate_evaluator.check_config_valid = Mock(return_value=(True, {}))
        self.fsm.predicate_evaluator.check_calibration_valid = Mock(return_value=(True, {}))
        self.fsm.predicate_evaluator.check_dependencies_ok = Mock(return_value=(True, {}))
        self.fsm.predicate_evaluator.check_hardware_health = Mock(return_value=(True, {}))
        
        # SAFE → INITIALIZED
        success, _, _ = self.fsm.transition(FSMEvent.INITIALIZE)
        self.assertTrue(success)
        self.assertEqual(self.context.state, FSMState.INITIALIZED)
        self.assertIsNotNone(self.context.budget)
    
    def test_fault_latching(self):
        """Test FAULT state latches."""
        self.context.state = FSMState.FAULT
        
        # Can't transition from FAULT except via RESET
        with self.assertRaises(FSMError):
            self.fsm.transition(FSMEvent.ARM)
        
        # RESET should work
        success, _, _ = self.fsm.transition(FSMEvent.RESET)
        self.assertTrue(success)
        self.assertEqual(self.context.state, FSMState.SAFE)
    
    def test_any_to_fault(self):
        """Test ANY state can transition to FAULT."""
        for state in [FSMState.SAFE, FSMState.INITIALIZED, FSMState.ARMED, 
                      FSMState.EMIT_READY, FSMState.EMITTING]:
            self.context.state = state
            success, _, _ = self.fsm.transition(FSMEvent.FAULT)
            self.assertTrue(success)
            self.assertEqual(self.context.state, FSMState.FAULT)
    
    def test_can_transition(self):
        """Test can_transition method."""
        self.assertEqual(self.fsm.can_transition(FSMEvent.INITIALIZE), True)
        self.assertEqual(self.fsm.can_transition(FSMEvent.ARM), False)  # Not in right state


if __name__ == '__main__':
    unittest.main()

