# Test Suite Documentation

This directory contains unit tests, integration tests, and HDL (Hardware Description Language) tests for the EUV Detection & Laser Communication Device.

## Test Structure

```
tests/
├── unit/              # Unit tests for individual modules
│   ├── test_photodiode_reader.py
│   ├── test_laser_controller.py
│   └── test_signal_processor.py
├── integration/        # Integration tests for complete system
│   └── test_system_integration.py
├── hdl/               # Hardware Description Language tests
│   ├── photodiode_amplifier_tb.v
│   ├── laser_driver_tb.v
│   └── adc_interface_tb.v
├── run_tests.py       # Test runner script
└── README.md          # This file
```

## Running Tests

### All Tests

Run all unit and integration tests:

```bash
cd tests
python run_tests.py
```

### Unit Tests Only

Run unit tests for a specific module:

```bash
cd tests/unit
python -m unittest test_photodiode_reader.py
python -m unittest test_laser_controller.py
python -m unittest test_signal_processor.py
```

Or run all unit tests:

```bash
cd tests/unit
python -m unittest discover
```

### Integration Tests

Run integration tests:

```bash
cd tests/integration
python -m unittest test_system_integration.py
```

## HDL Tests

The HDL tests are written in Verilog and test the hardware circuits:

- **photodiode_amplifier_tb.v**: Tests the transimpedance amplifier circuit
- **laser_driver_tb.v**: Tests the laser driver with PWM and interlock
- **adc_interface_tb.v**: Tests the I2C ADC interface

### Running HDL Tests

HDL tests require a Verilog simulator (e.g., ModelSim, Verilator, Icarus Verilog):

```bash
# Using Icarus Verilog
cd tests/hdl
iverilog -o photodiode_amplifier_tb photodiode_amplifier_tb.v
vvp photodiode_amplifier_tb

# Using Verilator
verilator --cc --exe --build photodiode_amplifier_tb.v
```

## Test Coverage

### Unit Tests

- **PhotodiodeReader**: Calibration, voltage measurement, wavelength calculation
- **LaserController**: Enable/disable, pulse generation, pattern transmission, interlock
- **SignalProcessor**: Pattern encoding, signal filtering, data logging

### Integration Tests

- Complete measurement and logging workflow
- Pattern encoding and transmission
- Continuous measurement operations
- Safety interlock workflow
- Emergency stop procedures
- Calibration workflow
- Signal filtering
- Data persistence

### HDL Tests

- Photodiode amplifier response to various current levels
- Laser driver PWM generation
- Safety interlock functionality
- ADC interface I2C communication
- Timing and response characteristics

## Test Requirements

### Python Tests

- Python 3.8+
- unittest (standard library)
- Mock hardware libraries (tests run in simulation mode)

### HDL Tests

- Verilog simulator (ModelSim, Verilator, Icarus Verilog, etc.)
- Verilog-2001 compatible

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    cd tests
    python run_tests.py
```

## Writing New Tests

### Unit Test Template

```python
import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "software"))

from hardware_control.module_name import ModuleClass

class TestModuleClass(unittest.TestCase):
    def setUp(self):
        self.module = ModuleClass()
    
    def test_feature(self):
        # Test implementation
        pass

if __name__ == '__main__':
    unittest.main()
```

### Integration Test Template

```python
import unittest
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "software"))

from hardware_control.module1 import Module1
from hardware_control.module2 import Module2

class TestIntegration(unittest.TestCase):
    def setUp(self):
        with patch('hardware_control.module1.HARDWARE_AVAILABLE', False):
            self.module1 = Module1()
            self.module2 = Module2()
    
    def test_integration(self):
        # Integration test implementation
        pass
```

## Notes

- All tests run in simulation mode (no hardware required)
- Hardware-dependent tests are mocked
- HDL tests are simplified models for circuit verification
- Real hardware testing should be performed separately

## Troubleshooting

### Import Errors

If you get import errors, ensure the software directory is in the Python path:

```python
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "software"))
```

### Hardware Library Errors

Tests are designed to run without hardware. If you see hardware library errors, the mocks may not be working correctly.

### HDL Simulation Errors

Ensure your Verilog simulator supports the features used in the testbenches (Verilog-2001 standard).

