"""
Integration tests for the complete system.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
import tempfile
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "software"))

from hardware_control.photodiode_reader import PhotodiodeReader
from hardware_control.laser_controller import LaserController, LaserState
from hardware_control.signal_processor import SignalProcessor


class TestSystemIntegration(unittest.TestCase):
    """Integration tests for complete system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock hardware availability
        with patch('hardware_control.photodiode_reader.HARDWARE_AVAILABLE', False), \
             patch('hardware_control.laser_controller.HARDWARE_AVAILABLE', False):
            
            self.temp_dir = tempfile.mkdtemp()
            
            self.photodiode = PhotodiodeReader()
            self.laser = LaserController()
            self.processor = SignalProcessor(log_dir=self.temp_dir)
            
            # Start logging session
            self.processor.start_logging_session("integration_test")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)
        if hasattr(self, 'laser'):
            self.laser.cleanup()
    
    def test_measurement_and_logging(self):
        """Test complete measurement and logging workflow."""
        # Take measurement
        wavelength = self.photodiode.get_wavelength()
        voltage = self.photodiode.get_voltage()
        
        # Get laser state
        laser_state = self.laser.get_state().value
        
        # Log measurement
        self.processor.add_measurement(wavelength, voltage, laser_state)
        
        # Verify measurement was logged
        self.assertEqual(len(self.processor.measurement_history), 1)
        
        # Verify data in history
        measurement = self.processor.measurement_history[0]
        self.assertIsNotNone(measurement['timestamp'])
        self.assertEqual(measurement['voltage'], voltage)
        self.assertEqual(measurement['laser_state'], laser_state)
    
    def test_pattern_encoding_and_transmission(self):
        """Test pattern encoding and laser transmission workflow."""
        # Encode message
        message = "SOS"
        pattern = self.processor.encode_message(message, "morse")
        
        # Verify pattern is valid
        self.assertIsInstance(pattern, list)
        self.assertGreater(len(pattern), 0)
        
        # Send pattern via laser
        result = self.laser.send_pattern(pattern, 0.1, 0.05)
        
        # Verify transmission succeeded
        self.assertTrue(result)
        
        # Log event
        self.processor.log_event("pattern_sent", f"Sent: {message}", {"pattern": pattern})
    
    def test_continuous_measurement_workflow(self):
        """Test continuous measurement workflow."""
        measurements = []
        
        for i in range(5):
            # Measure
            wavelength = self.photodiode.get_wavelength()
            voltage = self.photodiode.get_voltage()
            laser_state = self.laser.get_state().value
            
            # Log
            self.processor.add_measurement(wavelength, voltage, laser_state)
            measurements.append((wavelength, voltage))
            
            # Small delay
            time.sleep(0.1)
        
        # Verify all measurements logged
        self.assertEqual(len(self.processor.measurement_history), 5)
        
        # Verify history retrieval
        wavelengths = self.processor.get_wavelength_history()
        voltages = self.processor.get_voltage_history()
        
        self.assertEqual(len(wavelengths), len([m for m in measurements if m[0] is not None]))
        self.assertEqual(len(voltages), 5)
    
    def test_safety_interlock_workflow(self):
        """Test safety interlock workflow."""
        # Verify interlock is safe
        self.assertTrue(self.laser.is_interlock_safe())
        
        # Should be able to enable laser
        result = self.laser.enable()
        self.assertTrue(result)
        self.assertEqual(self.laser.get_state(), LaserState.ON)
        
        # Disable laser
        self.laser.disable()
        self.assertEqual(self.laser.get_state(), LaserState.OFF)
    
    def test_emergency_stop_workflow(self):
        """Test emergency stop workflow."""
        # Enable laser
        self.laser.enable()
        self.assertEqual(self.laser.get_state(), LaserState.ON)
        
        # Emergency stop
        self.laser.emergency_stop()
        self.assertEqual(self.laser.get_state(), LaserState.ERROR)
        
        # Verify laser is disabled
        self.laser.disable()
        self.assertEqual(self.laser.get_state(), LaserState.OFF)
    
    def test_calibration_workflow(self):
        """Test calibration workflow."""
        # Measure dark voltage
        dark_voltage = self.photodiode.measure_dark_voltage()
        self.assertIsNotNone(dark_voltage)
        
        # Calibrate at known wavelength
        test_wavelength = 650.0
        with patch.object(self.photodiode, 'measure_voltage', return_value=0.9):
            self.photodiode.calibrate_point(test_wavelength)
        
        # Verify calibration point added
        self.assertIn(test_wavelength, self.photodiode.calibration_table)
        
        # Test wavelength calculation
        with patch.object(self.photodiode, 'measure_voltage', return_value=0.9):
            calculated_wavelength = self.photodiode.calculate_wavelength(0.9)
            self.assertIsNotNone(calculated_wavelength)
    
    def test_signal_filtering_workflow(self):
        """Test signal filtering workflow."""
        # Generate test data with noise
        noisy_data = [1.0, 1.1, 1.2, 5.0, 1.3, 1.4, 1.5]  # 5.0 is outlier
        
        # Filter data
        filtered = self.processor.filter_signal(
            noisy_data, 
            "remove_outliers", 
            threshold=3.0
        )
        
        # Verify outlier removed
        self.assertNotIn(5.0, filtered)
        
        # Apply moving average
        smoothed = self.processor.filter_signal(
            filtered,
            "moving_average",
            window_size=3
        )
        
        # Verify smoothing
        self.assertEqual(len(smoothed), len(filtered))
    
    def test_multiple_pattern_types(self):
        """Test multiple pattern encoding types."""
        message = "TEST"
        
        # Morse code
        morse_pattern = self.processor.encode_message(message, "morse")
        self.assertGreater(len(morse_pattern), 0)
        
        # Binary
        binary_pattern = self.processor.encode_message(message, "binary")
        self.assertGreater(len(binary_pattern), 0)
        
        # Geometric
        geom_pattern = self.processor.encode_message("square", "geometric")
        self.assertGreater(len(geom_pattern), 0)
    
    def test_data_persistence(self):
        """Test data persistence through logging."""
        # Add multiple measurements
        for i in range(10):
            self.processor.add_measurement(600.0 + i, 1.0 + i*0.1, "on")
        
        # Verify measurements in history
        self.assertEqual(len(self.processor.measurement_history), 10)
        
        # Verify recent measurements can be retrieved
        recent = self.processor.logger.get_recent_measurements(5)
        self.assertEqual(len(recent), 5)
    
    def test_error_handling(self):
        """Test error handling in integrated system."""
        # Test with invalid wavelength (out of range)
        voltage = 10.0  # Out of calibration range
        wavelength = self.photodiode.calculate_wavelength(voltage)
        self.assertIsNone(wavelength)  # Should return None, not raise error
        
        # Test with interlock unsafe (simulated)
        with patch.object(self.laser, 'is_interlock_safe', return_value=False):
            result = self.laser.enable()
            self.assertFalse(result)  # Should fail gracefully
    
    def test_performance_under_load(self):
        """Test system performance under load."""
        start_time = time.time()
        
        # Perform many operations
        for i in range(100):
            wavelength = self.photodiode.get_wavelength()
            voltage = self.photodiode.get_voltage()
            self.processor.add_measurement(wavelength, voltage, "on")
        
        elapsed_time = time.time() - start_time
        
        # Should complete in reasonable time (< 5 seconds for 100 operations)
        self.assertLess(elapsed_time, 5.0)
        
        # Verify all measurements logged
        self.assertEqual(len(self.processor.measurement_history), 100)


if __name__ == '__main__':
    unittest.main()

