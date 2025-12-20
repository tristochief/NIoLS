"""
Unit tests for LaserController module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "software"))

from hardware_control.laser_controller import LaserController, LaserState


class TestLaserController(unittest.TestCase):
    """Test cases for LaserController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock hardware availability
        with patch('hardware_control.laser_controller.HARDWARE_AVAILABLE', False):
            self.controller = LaserController()
    
    def test_initialization(self):
        """Test LaserController initialization."""
        self.assertIsNotNone(self.controller)
        self.assertEqual(self.controller.state, LaserState.OFF)
        self.assertFalse(self.controller.hardware_connected)
    
    def test_is_interlock_safe_simulation(self):
        """Test interlock safety check in simulation mode."""
        # In simulation mode, interlock is always safe
        self.assertTrue(self.controller.is_interlock_safe())
    
    def test_enable_laser(self):
        """Test laser enable."""
        # Should succeed in simulation mode
        result = self.controller.enable()
        self.assertTrue(result)
        self.assertEqual(self.controller.state, LaserState.ON)
    
    def test_disable_laser(self):
        """Test laser disable."""
        self.controller.enable()
        self.controller.disable()
        self.assertEqual(self.controller.state, LaserState.OFF)
    
    def test_emergency_stop(self):
        """Test emergency stop."""
        self.controller.enable()
        self.controller.emergency_stop()
        self.assertEqual(self.controller.state, LaserState.ERROR)
    
    def test_pulse(self):
        """Test single pulse."""
        result = self.controller.pulse(0.1)
        self.assertTrue(result)
    
    def test_pulse_with_interlock_unsafe(self):
        """Test pulse fails when interlock is unsafe."""
        # Mock unsafe interlock
        with patch.object(self.controller, 'is_interlock_safe', return_value=False):
            result = self.controller.pulse(0.1)
            self.assertFalse(result)
    
    def test_send_pattern(self):
        """Test sending binary pattern."""
        pattern = [True, False, True, True, False]
        result = self.controller.send_pattern(pattern, 0.1, 0.05)
        self.assertTrue(result)
    
    def test_send_pattern_interlock_failure(self):
        """Test pattern sending stops on interlock failure."""
        pattern = [True, False, True]
        
        # Mock interlock to fail after first element
        call_count = [0]
        def mock_interlock():
            call_count[0] += 1
            return call_count[0] < 2
        
        with patch.object(self.controller, 'is_interlock_safe', side_effect=mock_interlock):
            result = self.controller.send_pattern(pattern, 0.1, 0.05)
            self.assertFalse(result)
            self.assertEqual(self.controller.state, LaserState.OFF)
    
    def test_send_morse_code(self):
        """Test Morse code transmission."""
        result = self.controller.send_morse_code("SOS")
        self.assertTrue(result)
        self.assertEqual(self.controller.state, LaserState.OFF)
    
    def test_send_morse_code_complex(self):
        """Test complex Morse code message."""
        result = self.controller.send_morse_code("HELLO WORLD")
        self.assertTrue(result)
    
    def test_set_pwm_duty_cycle(self):
        """Test PWM duty cycle setting."""
        result = self.controller.set_pwm_duty_cycle(50.0)
        self.assertTrue(result)
        self.assertEqual(self.controller.state, LaserState.ON)
        
        result = self.controller.set_pwm_duty_cycle(0.0)
        self.assertTrue(result)
        self.assertEqual(self.controller.state, LaserState.OFF)
    
    def test_set_pwm_duty_cycle_clamping(self):
        """Test PWM duty cycle clamping to 0-100."""
        # Test values outside range
        self.controller.set_pwm_duty_cycle(-10.0)
        self.controller.set_pwm_duty_cycle(150.0)
        # Should not raise error, values should be clamped
    
    def test_set_pwm_duty_cycle_interlock_unsafe(self):
        """Test PWM setting fails when interlock is unsafe."""
        with patch.object(self.controller, 'is_interlock_safe', return_value=False):
            result = self.controller.set_pwm_duty_cycle(50.0)
            self.assertFalse(result)
    
    def test_get_state(self):
        """Test getting laser state."""
        self.assertEqual(self.controller.get_state(), LaserState.OFF)
        self.controller.enable()
        self.assertEqual(self.controller.get_state(), LaserState.ON)
    
    def test_set_interlock_callback(self):
        """Test setting interlock callback."""
        callback_called = [False]
        
        def test_callback(safe):
            callback_called[0] = True
        
        self.controller.set_interlock_callback(test_callback)
        self.controller._interlock_callback(23)  # Simulate interlock change
        self.assertTrue(callback_called[0])
    
    def test_cleanup(self):
        """Test cleanup method."""
        # Should not raise error even without hardware
        self.controller.cleanup()


class TestLaserState(unittest.TestCase):
    """Test cases for LaserState enum."""
    
    def test_laser_state_values(self):
        """Test LaserState enum values."""
        self.assertEqual(LaserState.OFF.value, "off")
        self.assertEqual(LaserState.ON.value, "on")
        self.assertEqual(LaserState.PULSING.value, "pulsing")
        self.assertEqual(LaserState.ERROR.value, "error")


if __name__ == '__main__':
    unittest.main()

