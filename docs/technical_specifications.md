# Technical Specifications

## System Overview

The EUV Detection & Laser Communication Device is a hybrid hardware/software system for measuring optical wavelengths and transmitting laser signals. The system operates in the visible to near-infrared spectrum (400-1100 nm) with a path for future EUV (12-13 nm) detection capability.

## Hardware Specifications

### Photodiode Detector

**Photodiode:**
- **Type:** Silicon photodiode (Hamamatsu S1227-1010BR or equivalent)
- **Wavelength Range:** 320-1100 nm
- **Active Area:** 10×10 mm
- **Dark Current:** <1 nA
- **Capacitance:** 320 pF (at 0V bias)
- **Spectral Response:** Peak at ~900 nm

**Amplifier Circuit:**
- **Type:** Transimpedance amplifier (TIA)
- **Op-Amp:** OPA627 or equivalent (low noise, low bias current)
- **Gain:** 1 MΩ feedback resistor (adjustable)
- **Bandwidth:** DC to 10 kHz (with filter)
- **Noise:** <10 mV RMS (typical)

**ADC Interface:**
- **Type:** ADS1115 (16-bit I2C ADC)
- **Resolution:** 16 bits (65,536 levels)
- **Input Range:** ±4.096V (programmable)
- **Sampling Rate:** 8-860 samples/second
- **Interface:** I2C (address 0x48 default)
- **Channels:** 4 differential or 8 single-ended

**Power Supply:**
- **Voltage:** 5V DC
- **Current:** <100 mA
- **Regulation:** ±1%
- **Noise:** <100 μV RMS

### Laser Transmitter

**Laser Module:**
- **Type:** Class 1M laser diode module
- **Wavelength:** 650 nm (red) or 532 nm (green)
- **Power Output:** ≤1 mW (0.5-1.0 mW typical)
- **Beam Divergence:** <1 mrad
- **Operating Current:** 20-40 mA
- **Operating Voltage:** 2.5-3.5V
- **Modulation Bandwidth:** Up to 1 MHz

**Driver Circuit:**
- **Type:** Current-limited driver with pulse modulation
- **Modulation:** Transistor switch (2N2222 or equivalent)
- **PWM Frequency:** 1-100 kHz (adjustable)
- **Pulse Duration:** 0.001-1.0 seconds
- **Duty Cycle:** 0-100% (for intensity control)

**Safety Interlock:**
- **Type:** Hardware switch (normally closed)
- **Response Time:** <10 ms
- **Monitoring:** Continuous software monitoring
- **Status Indication:** LED indicator

**Power Supply:**
- **Voltage:** 5V DC
- **Current:** <200 mA (including laser)
- **Regulation:** ±1%

### Control Hardware

**Microcontroller:**
- **Type:** Raspberry Pi 4 (or compatible)
- **GPIO:** 40-pin header
- **I2C:** Hardware I2C interface
- **PWM:** Hardware PWM support
- **Interface:** USB, Ethernet, WiFi

**Connections:**
- **Photodiode ADC:** I2C (SDA, SCL)
- **Laser Control:** GPIO pin 18 (PWM capable)
- **Interlock:** GPIO pin 23 (input with pull-up)
- **Power:** 5V via USB or dedicated supply

## Software Specifications

### Operating System

- **Platform:** Linux (Raspberry Pi OS recommended)
- **Python Version:** 3.8 or higher
- **Architecture:** ARM (Raspberry Pi) or x86_64 (development)

### Dependencies

**Core Libraries:**
- Python 3.8+
- NumPy 1.20+
- FastAPI 0.104+
- Uvicorn 0.24+
- React 18+ (frontend)
- TypeScript 5+ (frontend)
- Plotly 5.0+
- PyYAML 6.0+

**Hardware Libraries:**
- Adafruit CircuitPython ADS1x15 (for ADC)
- RPi.GPIO (for GPIO control)
- Board (for I2C interface)

**Optional:**
- SciPy (for advanced signal processing)
- Matplotlib (alternative plotting)

### Software Architecture

**Modules:**
1. **photodiode_reader.py:** ADC interface and wavelength calculation
2. **laser_controller.py:** GPIO control and pattern generation
3. **signal_processor.py:** Pattern encoding and data logging
4. **api_server.py:** FastAPI REST API server
5. **Frontend (TypeScript/React):** Web-based user interface

**Configuration:**
- YAML-based configuration file
- Calibration data storage
- User preferences

**Data Logging:**
- CSV format for measurements
- JSON Lines for events
- Timestamped session files

## Performance Specifications

### Measurement Performance

**Wavelength Measurement:**
- **Range:** 400-1100 nm (calibrated)
- **Resolution:** Depends on calibration points
- **Accuracy:** ±5 nm (typical, with calibration)
- **Update Rate:** 1-10 Hz (configurable)

**Voltage Measurement:**
- **Range:** 0-3.3V (or 0-5V with divider)
- **Resolution:** 16 bits (0.05 mV at 3.3V range)
- **Accuracy:** ±0.1% (typical)
- **Noise:** <10 mV RMS

### Laser Performance

**Pulse Characteristics:**
- **Rise Time:** <100 ns (laser dependent)
- **Fall Time:** <100 ns (laser dependent)
- **Pulse Width:** 0.001-1.0 seconds (adjustable)
- **Repetition Rate:** Up to 1 MHz (theoretical)

**Pattern Transmission:**
- **Morse Code:** Standard international code
- **Binary:** 8 bits per character (ASCII)
- **Geometric:** Predefined patterns (square, circle, triangle, spiral)
- **Pattern Length:** Up to 1000 elements

### System Performance

**Response Time:**
- **Measurement Update:** <100 ms
- **Laser Control:** <10 ms
- **Interlock Response:** <10 ms
- **GUI Update:** 1 second (configurable)

**Data Logging:**
- **Measurement Rate:** Up to 10 Hz
- **File Size:** ~1 KB per 100 measurements
- **Storage:** Unlimited (disk space dependent)

## Calibration Specifications

### Photodiode Calibration

**Calibration Points:**
- Minimum: 3 points (400, 650, 1100 nm)
- Recommended: 5-9 points across range
- Method: Linear interpolation between points

**Calibration Sources:**
- Monochromatic LEDs (470, 530, 590, 650 nm)
- Laser pointers (532, 650 nm)
- Calibrated light sources (if available)

**Calibration Accuracy:**
- Wavelength accuracy: ±2 nm (source dependent)
- Voltage measurement: ±0.1% (ADC accuracy)
- Interpolation error: <1% (typical)

### Laser Calibration

**Power Verification:**
- **Method:** Laser power meter (calibrated)
- **Frequency:** Monthly or after modifications
- **Target:** ≤1 mW output
- **Tolerance:** ±10%

**Pulse Calibration:**
- **Method:** Oscilloscope measurement
- **Parameters:** Pulse width, rise/fall time
- **Frequency:** As needed

## Environmental Specifications

### Operating Conditions

**Temperature:**
- **Operating Range:** 0°C to +50°C
- **Storage Range:** -20°C to +70°C
- **Optimal:** +20°C to +25°C

**Humidity:**
- **Operating:** 10-90% RH (non-condensing)
- **Storage:** 5-95% RH

**Power:**
- **Input:** 5V DC, 500 mA minimum
- **Regulation:** ±5%
- **Protection:** Reverse polarity protection recommended

### Physical Specifications

**Dimensions:**
- **Photodiode Module:** ~50×50×30 mm (with enclosure)
- **Laser Module:** ~30×20×15 mm (typical)
- **Control Box:** Depends on enclosure choice

**Weight:**
- **Photodiode Module:** ~100 g
- **Laser Module:** ~50 g
- **Control Hardware:** ~50 g (Raspberry Pi)

## Safety Specifications

### Laser Safety

**Classification:** Class 1M
- **Power:** ≤1 mW
- **Wavelength:** 400-700 nm (visible)
- **Hazard:** Safe under normal conditions
- **Special Risk:** Hazardous if viewed with optical instruments

**Safety Features:**
- Hardware interlock
- Software monitoring
- Emergency stop
- Power limiting

### Electrical Safety

**Voltage Levels:**
- **Low Voltage:** <50V (safe for handling)
- **Isolation:** No high voltage present
- **Protection:** Fuses recommended for power supply

**EMC:**
- **Emissions:** Should comply with local EMC regulations
- **Immunity:** Basic protection against interference

## Future Enhancements

### EUV Detection (12-13 nm)

**Detector Options:**
- Silicon carbide (SiC) photodiodes
- Multilayer-coated silicon detectors
- Microchannel plate (MCP) detectors
- X-ray CCD detectors

**Requirements:**
- Vacuum system (<10⁻⁴ Torr)
- Specialized calibration sources
- Radiation safety protocols
- Cost: $5,000-$100,000+

**Integration Path:**
- Documented in `hardware/euv_detector_specs.md`
- Software support ready for integration
- Calibration procedures defined

## Compliance and Standards

### Regulatory Compliance

**Australia:**
- AS/NZS IEC 60825.1 (Laser safety)
- ARPANSA guidelines
- CASA aviation safety regulations
- State WHS regulations

**International:**
- IEC 60825.1 (Laser safety)
- CE marking (if exported to EU)
- FCC Part 15 (if applicable)

### Quality Standards

**Design:**
- Engineering best practices
- Safety-first approach
- Documentation standards
- Testing procedures

## Version Information

- **Hardware Version:** 1.0
- **Software Version:** 1.0
- **Document Version:** 1.0
- **Last Updated:** [Current Date]

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | [Current] | Initial release |

---

**Note:** Specifications are subject to change. Refer to latest documentation for current specifications.

