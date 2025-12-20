"""
Unit tests for hash binding module.
"""

import unittest
import tempfile
import json
from pathlib import Path
import yaml
from core.hash_binding import (
    compute_config_hash, compute_calibration_hash,
    load_config_and_hash, load_calibration_and_hash,
    detect_config_drift, detect_calibration_drift,
    canonical_json
)


class TestHashBinding(unittest.TestCase):
    """Test hash binding functionality."""
    
    def test_canonical_json_deterministic(self):
        """Test canonical JSON is deterministic."""
        obj = {"b": 2, "a": 1, "c": 3}
        result1 = canonical_json(obj)
        result2 = canonical_json(obj)
        self.assertEqual(result1, result2)
        
        # Should be sorted
        self.assertIn('"a":1', result1)
        self.assertIn('"b":2', result1)
        self.assertIn('"c":3', result1)
    
    def test_compute_config_hash(self):
        """Test config hash computation."""
        config1 = {"hardware": {}, "safety": {}}
        config2 = {"hardware": {}, "safety": {}}
        
        hash1 = compute_config_hash(config1)
        hash2 = compute_config_hash(config2)
        
        self.assertEqual(hash1, hash2)  # Same config = same hash
        
        # Different config = different hash
        config3 = {"hardware": {}, "safety": {"max_power_mw": 2.0}}
        hash3 = compute_config_hash(config3)
        self.assertNotEqual(hash1, hash3)
    
    def test_load_config_and_hash(self):
        """Test loading config and computing hash."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config = {"hardware": {"laser": {"laser_pin": 18}}, "safety": {"max_power_mw": 1.0}}
            yaml.dump(config, f)
            config_path = Path(f.name)
        
        try:
            loaded_config, config_hash = load_config_and_hash(config_path)
            self.assertEqual(loaded_config["hardware"]["laser"]["laser_pin"], 18)
            self.assertIsNotNone(config_hash)
            self.assertEqual(len(config_hash), 64)  # SHA256 hex string
        finally:
            config_path.unlink()
    
    def test_detect_config_drift(self):
        """Test config drift detection."""
        config1 = {"hardware": {}, "safety": {}}
        config2 = {"hardware": {}, "safety": {"max_power_mw": 2.0}}
        
        bound_hash = compute_config_hash(config1)
        
        # No drift
        has_drift, current_hash = detect_config_drift(bound_hash, config1)
        self.assertFalse(has_drift)
        self.assertEqual(current_hash, bound_hash)
        
        # Drift detected
        has_drift, current_hash = detect_config_drift(bound_hash, config2)
        self.assertTrue(has_drift)
        self.assertNotEqual(current_hash, bound_hash)
    
    def test_load_calibration_from_dict(self):
        """Test loading calibration from dictionary."""
        calibration = {
            "points": [
                {"wavelength": 400, "voltage": 0.1},
                {"wavelength": 650, "voltage": 0.9}
            ]
        }
        
        loaded_cal, cal_hash = load_calibration_and_hash(calibration)
        self.assertEqual(len(loaded_cal["points"]), 2)
        self.assertIsNotNone(cal_hash)
    
    def test_load_calibration_from_photodiode_reader(self):
        """Test loading calibration from PhotodiodeReader instance."""
        mock_reader = Mock()
        mock_reader.calibration_table = {400: 0.1, 650: 0.9}
        mock_reader.dark_voltage = 0.0
        
        loaded_cal, cal_hash = load_calibration_and_hash(mock_reader)
        self.assertEqual(len(loaded_cal["points"]), 2)
        self.assertIsNotNone(cal_hash)


if __name__ == '__main__':
    from unittest.mock import Mock
    unittest.main()

