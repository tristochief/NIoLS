"""
Unit tests for PhotodiodeReader module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "software"))

from hardware_control.photodiode_reader import PhotodiodeReader


class TestPhotodiodeReader(unittest.TestCase):
    """Test cases for PhotodiodeReader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock hardware availability
        with patch('hardware_control.photodiode_reader.HARDWARE_AVAILABLE', False):
            self.reader = PhotodiodeReader()
    
    def test_initialization(self):
        """Test PhotodiodeReader initialization."""
        self.assertIsNotNone(self.reader)
        self.assertFalse(self.reader.hardware_connected)
        self.assertIsNotNone(self.reader.calibration_table)
    
    def test_default_calibration(self):
        """Test default calibration data loading."""
        self.assertGreater(len(self.reader.calibration_table), 0)
        # Check that calibration has expected wavelengths
        self.assertIn(400, self.reader.calibration_table)
        self.assertIn(650, self.reader.calibration_table)
        self.assertIn(1100, self.reader.calibration_table)
    
    def test_measure_voltage_simulation(self):
        """Test voltage measurement in simulation mode."""
        voltage = self.reader.measure_voltage()
        self.assertIsInstance(voltage, float)
        self.assertGreaterEqual(voltage, 0.0)
        self.assertLessEqual(voltage, 5.0)
    
    def test_measure_dark_voltage(self):
        """Test dark voltage measurement."""
        with patch.object(self.reader, 'measure_voltage', return_value=0.05):
            dark_voltage = self.reader.measure_dark_voltage(samples=10)
            self.assertEqual(dark_voltage, 0.05)
            self.assertEqual(self.reader.dark_voltage, 0.05)
    
    def test_calculate_wavelength(self):
        """Test wavelength calculation from voltage."""
        # Test with known calibration point
        voltage = self.reader.calibration_table[650]
        wavelength = self.reader.calculate_wavelength(voltage)
        self.assertAlmostEqual(wavelength, 650, delta=5.0)
    
    def test_calculate_wavelength_out_of_range(self):
        """Test wavelength calculation with out-of-range voltage."""
        # Very high voltage
        wavelength = self.reader.calculate_wavelength(10.0)
        self.assertIsNone(wavelength)
        
        # Very low voltage (negative after dark subtraction)
        wavelength = self.reader.calculate_wavelength(-1.0)
        self.assertIsNone(wavelength)
    
    def test_get_wavelength(self):
        """Test get_wavelength method."""
        with patch.object(self.reader, 'measure_voltage', return_value=0.9):
            with patch.object(self.reader, 'calculate_wavelength', return_value=650.0):
                wavelength = self.reader.get_wavelength()
                self.assertEqual(wavelength, 650.0)
    
    def test_calibrate_point(self):
        """Test calibration point addition."""
        initial_count = len(self.reader.calibration_table)
        
        with patch.object(self.reader, 'measure_voltage', return_value=1.5):
            self.reader.calibrate_point(800.0, samples=10)
            
            self.assertIn(800.0, self.reader.calibration_table)
            self.assertEqual(self.reader.calibration_table[800.0], 1.5)
    
    def test_get_calibration_range(self):
        """Test calibration range retrieval."""
        min_wl, max_wl = self.reader.get_calibration_range()
        self.assertIsInstance(min_wl, float)
        self.assertIsInstance(max_wl, float)
        self.assertLess(min_wl, max_wl)
    
    def test_load_calibration_from_file(self):
        """Test loading calibration from CSV file."""
        import tempfile
        import csv
        
        # Create temporary calibration file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            writer = csv.writer(f)
            writer.writerow(['wavelength_nm', 'voltage_v'])
            writer.writerow([500, 0.6])
            writer.writerow([600, 0.8])
            temp_file = f.name
        
        try:
            self.reader.load_calibration(temp_file)
            self.assertIn(500, self.reader.calibration_table)
            self.assertIn(600, self.reader.calibration_table)
            self.assertEqual(self.reader.calibration_table[500], 0.6)
            self.assertEqual(self.reader.calibration_table[600], 0.8)
        finally:
            import os
            os.unlink(temp_file)
    
    def test_save_calibration_to_file(self):
        """Test saving calibration to CSV file."""
        import tempfile
        import os
        
        # Add some calibration points
        self.reader.calibration_table[500] = 0.6
        self.reader.calibration_table[600] = 0.8
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        
        try:
            self.reader.save_calibration(temp_file)
            
            # Verify file was created and contains data
            self.assertTrue(os.path.exists(temp_file))
            with open(temp_file, 'r') as f:
                content = f.read()
                self.assertIn('500', content)
                self.assertIn('0.6', content)
        finally:
            os.unlink(temp_file)
    
    def test_is_connected(self):
        """Test hardware connection status."""
        self.assertFalse(self.reader.is_connected())
        
        # Simulate connected hardware
        self.reader.hardware_connected = True
        self.assertTrue(self.reader.is_connected())


if __name__ == '__main__':
    unittest.main()

