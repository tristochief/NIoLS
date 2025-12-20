"""
Unit tests for SignalProcessor module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
import tempfile
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "software"))

from hardware_control.signal_processor import (
    SignalProcessor, PatternEncoder, SignalFilter, DataLogger
)


class TestPatternEncoder(unittest.TestCase):
    """Test cases for PatternEncoder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.encoder = PatternEncoder()
    
    def test_encode_binary(self):
        """Test binary encoding."""
        pattern = self.encoder.encode_binary("A")
        # 'A' = 65 = 01000001 in binary
        self.assertIsInstance(pattern, list)
        self.assertGreater(len(pattern), 0)
        self.assertTrue(all(isinstance(x, bool) for x in pattern))
    
    def test_encode_binary_multiple_chars(self):
        """Test binary encoding with multiple characters."""
        pattern = self.encoder.encode_binary("HI")
        self.assertGreater(len(pattern), 8)  # At least 8 bits per char
    
    def test_encode_morse(self):
        """Test Morse code encoding."""
        pattern = self.encoder.encode_morse("SOS")
        self.assertIsInstance(pattern, list)
        self.assertGreater(len(pattern), 0)
    
    def test_encode_morse_letters(self):
        """Test Morse code encoding for various letters."""
        pattern = self.encoder.encode_morse("ABC")
        self.assertGreater(len(pattern), 0)
    
    def test_encode_morse_numbers(self):
        """Test Morse code encoding for numbers."""
        pattern = self.encoder.encode_morse("123")
        self.assertGreater(len(pattern), 0)
    
    def test_encode_morse_spaces(self):
        """Test Morse code encoding with spaces."""
        pattern = self.encoder.encode_morse("A B")
        self.assertGreater(len(pattern), 0)
    
    def test_encode_geometric_square(self):
        """Test geometric square pattern."""
        pattern = self.encoder.encode_geometric("square", 10)
        self.assertEqual(len(pattern), 10)
        # Should alternate
        self.assertEqual(pattern[0], True)
        self.assertEqual(pattern[1], False)
    
    def test_encode_geometric_circle(self):
        """Test geometric circle pattern."""
        pattern = self.encoder.encode_geometric("circle", 10)
        self.assertEqual(len(pattern), 10)
    
    def test_encode_geometric_triangle(self):
        """Test geometric triangle pattern."""
        pattern = self.encoder.encode_geometric("triangle", 10)
        self.assertEqual(len(pattern), 10)
    
    def test_encode_geometric_spiral(self):
        """Test geometric spiral pattern."""
        pattern = self.encoder.encode_geometric("spiral", 16)
        self.assertEqual(len(pattern), 16)
    
    def test_encode_geometric_unknown(self):
        """Test geometric encoding with unknown type."""
        pattern = self.encoder.encode_geometric("unknown", 10)
        # Should return default pattern
        self.assertEqual(len(pattern), 10)


class TestSignalFilter(unittest.TestCase):
    """Test cases for SignalFilter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.filter = SignalFilter()
    
    def test_moving_average(self):
        """Test moving average filter."""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        filtered = self.filter.moving_average(data, window_size=3)
        self.assertEqual(len(filtered), len(data))
        self.assertIsInstance(filtered[0], float)
    
    def test_moving_average_small_data(self):
        """Test moving average with small dataset."""
        data = [1.0, 2.0]
        filtered = self.filter.moving_average(data, window_size=10)
        # Should return original data if too small
        self.assertEqual(len(filtered), len(data))
    
    def test_low_pass_filter(self):
        """Test low-pass filter."""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        filtered = self.filter.low_pass_filter(data, cutoff=0.1)
        self.assertEqual(len(filtered), len(data))
        self.assertIsInstance(filtered[0], float)
    
    def test_low_pass_filter_single_value(self):
        """Test low-pass filter with single value."""
        data = [1.0]
        filtered = self.filter.low_pass_filter(data)
        self.assertEqual(filtered, data)
    
    def test_remove_outliers(self):
        """Test outlier removal."""
        data = [1.0, 1.1, 1.2, 10.0, 1.3, 1.4]  # 10.0 is outlier
        filtered = self.filter.remove_outliers(data, threshold=3.0)
        self.assertNotIn(10.0, filtered)
    
    def test_remove_outliers_small_data(self):
        """Test outlier removal with small dataset."""
        data = [1.0, 2.0]
        filtered = self.filter.remove_outliers(data)
        # Should return original if too small
        self.assertEqual(len(filtered), len(data))


class TestDataLogger(unittest.TestCase):
    """Test cases for DataLogger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = DataLogger(log_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test DataLogger initialization."""
        self.assertIsNotNone(self.logger)
        self.assertEqual(self.logger.log_dir, Path(self.temp_dir))
    
    def test_start_session(self):
        """Test starting a logging session."""
        self.logger.start_session("test_session")
        self.assertIsNotNone(self.logger.current_log_file)
        self.assertTrue(self.logger.current_log_file.exists())
    
    def test_log_measurement(self):
        """Test logging a measurement."""
        self.logger.start_session("test")
        self.logger.log_measurement(650.0, 1.5, "on", "SOS")
        
        # Verify file was written
        self.assertTrue(self.logger.current_log_file.exists())
        with open(self.logger.current_log_file, 'r') as f:
            content = f.read()
            self.assertIn("650.0", content)
            self.assertIn("1.5", content)
    
    def test_log_event(self):
        """Test logging an event."""
        self.logger.log_event("test_event", "Test description", {"key": "value"})
        
        event_file = self.logger.log_dir / "events.jsonl"
        self.assertTrue(event_file.exists())
        
        with open(event_file, 'r') as f:
            line = f.readline()
            self.assertIn("test_event", line)
            self.assertIn("Test description", line)
    
    def test_get_recent_measurements(self):
        """Test retrieving recent measurements."""
        self.logger.start_session("test")
        
        # Log some measurements
        for i in range(5):
            self.logger.log_measurement(600.0 + i, 1.0 + i*0.1, "on")
        
        measurements = self.logger.get_recent_measurements(3)
        self.assertEqual(len(measurements), 3)
        self.assertEqual(measurements[-1]['wavelength'], 604.0)


class TestSignalProcessor(unittest.TestCase):
    """Test cases for SignalProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = SignalProcessor(log_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test SignalProcessor initialization."""
        self.assertIsNotNone(self.processor)
        self.assertIsNotNone(self.processor.encoder)
        self.assertIsNotNone(self.processor.filter)
        self.assertIsNotNone(self.processor.logger)
    
    def test_encode_message_morse(self):
        """Test encoding message as Morse code."""
        pattern = self.processor.encode_message("SOS", "morse")
        self.assertIsInstance(pattern, list)
        self.assertGreater(len(pattern), 0)
    
    def test_encode_message_binary(self):
        """Test encoding message as binary."""
        pattern = self.processor.encode_message("HI", "binary")
        self.assertIsInstance(pattern, list)
        self.assertGreater(len(pattern), 0)
    
    def test_encode_message_geometric(self):
        """Test encoding geometric pattern."""
        pattern = self.processor.encode_message("square", "geometric")
        self.assertIsInstance(pattern, list)
        self.assertGreater(len(pattern), 0)
    
    def test_filter_signal_moving_average(self):
        """Test signal filtering with moving average."""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        filtered = self.processor.filter_signal(data, "moving_average", window_size=3)
        self.assertEqual(len(filtered), len(data))
    
    def test_filter_signal_low_pass(self):
        """Test signal filtering with low-pass."""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        filtered = self.processor.filter_signal(data, "low_pass", cutoff=0.1)
        self.assertEqual(len(filtered), len(data))
    
    def test_add_measurement(self):
        """Test adding measurement to history."""
        self.processor.add_measurement(650.0, 1.5, "on", "SOS")
        self.assertEqual(len(self.processor.measurement_history), 1)
        
        measurement = self.processor.measurement_history[0]
        self.assertEqual(measurement['wavelength'], 650.0)
        self.assertEqual(measurement['voltage'], 1.5)
        self.assertEqual(measurement['laser_state'], "on")
    
    def test_get_wavelength_history(self):
        """Test retrieving wavelength history."""
        for i in range(5):
            self.processor.add_measurement(600.0 + i, 1.0, "on")
        
        history = self.processor.get_wavelength_history()
        self.assertEqual(len(history), 5)
        self.assertEqual(history[0], 600.0)
        self.assertEqual(history[-1], 604.0)
    
    def test_get_voltage_history(self):
        """Test retrieving voltage history."""
        for i in range(5):
            self.processor.add_measurement(600.0, 1.0 + i*0.1, "on")
        
        history = self.processor.get_voltage_history()
        self.assertEqual(len(history), 5)
        self.assertEqual(history[0], 1.0)
        self.assertEqual(history[-1], 1.4)
    
    def test_start_logging_session(self):
        """Test starting logging session."""
        self.processor.start_logging_session("test_session")
        # Should not raise error


if __name__ == '__main__':
    unittest.main()

