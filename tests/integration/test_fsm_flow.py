"""
Integration tests for full FSM flow.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock
from core import (
    SessionContext, FSMState, FSM, FSMEvent,
    TraceWriter, EventType, load_config_and_hash, load_calibration_and_hash
)


class TestFSMFlow(unittest.TestCase):
    """Test complete FSM state flow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.context = SessionContext()
        self.context.simulation_mode = True
        
        # Setup trace writer
        trace_file = self.temp_dir / "trace.jsonl"
        self.trace_writer = TraceWriter(trace_file, self.context.session_id)
        
        # Setup FSM
        self.fsm = FSM(self.context, lambda info: self.trace_writer.write_record(
            event_type=EventType.STATE_TRANSITION,
            state_from=info.get('from_state'),
            state_to=info.get('to_state'),
            predicates=info.get('predicates'),
            event_data=info.get('event_data'),
            config_hash=self.context.config_hash,
            cal_hash=self.context.cal_hash
        ))
        
        # Mock hardware
        self.context.photodiode_reader = Mock()
        self.context.laser_controller = Mock()
        self.context.laser_controller.is_interlock_safe = Mock(return_value=True)
        self.context.health_monitor = Mock()
        self.context.health_monitor.check_dependencies = Mock(return_value=Mock(status=Mock(value="healthy")))
        self.context.health_monitor.run_all_checks = Mock(return_value=[])
        self.context.health_monitor.get_overall_status = Mock(return_value=(Mock(value="healthy"), "OK"))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_flow_safe_to_emit_ready(self):
        """Test complete flow: SAFE → INITIALIZED → ARMED → EMIT_READY."""
        # Setup config and calibration
        self.context.config = {
            "hardware": {"laser": {"laser_pin": 18}},
            "safety": {"max_continuous_time": 3600.0, "cooldown_time": 60.0}
        }
        self.context.config_hash = "test_config_hash"
        self.context.calibration = {"points": [{"wavelength": 400, "voltage": 0.1}]}
        self.context.cal_hash = "test_cal_hash"
        
        # Mock all predicates to pass
        for pred_name in ['check_config_valid', 'check_calibration_valid', 
                         'check_dependencies_ok', 'check_hardware_health',
                         'check_interlock_safe', 'check_no_outstanding_faults',
                         'check_cooldown_satisfied', 'check_arm_confirmation_within_window']:
            setattr(self.fsm.predicate_evaluator, pred_name, 
                   Mock(return_value=(True, {})))
        
        # SAFE → INITIALIZED
        success, _, _ = self.fsm.transition(FSMEvent.INITIALIZE)
        self.assertTrue(success)
        self.assertEqual(self.context.state, FSMState.INITIALIZED)
        self.assertIsNotNone(self.context.budget)
        
        # INITIALIZED → ARMED
        success, _, _ = self.fsm.transition(FSMEvent.ARM)
        self.assertTrue(success)
        self.assertEqual(self.context.state, FSMState.ARMED)
        self.assertIsNotNone(self.context.arming_window_start)
        
        # ARMED → EMIT_READY
        success, _, _ = self.fsm.transition(FSMEvent.ARM_CONFIRM)
        self.assertTrue(success)
        self.assertEqual(self.context.state, FSMState.EMIT_READY)
    
    def test_emit_flow(self):
        """Test emission flow: EMIT_READY → EMITTING → EMIT_READY."""
        # Setup for EMIT_READY state
        self.context.state = FSMState.EMIT_READY
        self.context.config = {"safety": {"max_continuous_time": 3600.0}}
        self.context.initialize_budget(self.context.config)
        
        # Mock predicates
        self.fsm.predicate_evaluator.check_budget_available = Mock(
            return_value=(True, {"budget_available": True})
        )
        self.fsm.predicate_evaluator.check_interlock_safe = Mock(
            return_value=(True, {"interlock_safe": True})
        )
        
        # EMIT_READY → EMITTING
        success, _, _ = self.fsm.transition(
            FSMEvent.EMIT_REQUEST,
            event_data={'required_emit_ms': 100.0, 'required_duty_percent': 10.0,
                       'emit_duration_ms': 100.0, 'duty_percent': 10.0}
        )
        self.assertTrue(success)
        self.assertEqual(self.context.state, FSMState.EMITTING)
        
        # EMITTING → EMIT_READY
        success, _, _ = self.fsm.transition(FSMEvent.EMIT_COMPLETE)
        self.assertTrue(success)
        self.assertEqual(self.context.state, FSMState.EMIT_READY)
    
    def test_fault_on_interlock_open(self):
        """Test fault transition when interlock opens."""
        self.context.state = FSMState.EMITTING
        self.context.laser_controller.is_interlock_safe = Mock(return_value=False)
        
        # Should transition to FAULT
        success, _, _ = self.fsm.transition(FSMEvent.FAULT, event_data={'reason': 'Interlock opened'})
        self.assertTrue(success)
        self.assertEqual(self.context.state, FSMState.FAULT)
        self.assertIsNotNone(self.context.fault_reason)


if __name__ == '__main__':
    unittest.main()

