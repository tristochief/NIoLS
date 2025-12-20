# User Manual: EUV Detection & Laser Communication Device

## Overview

The EUV Detection & Laser Communication Device is a hybrid hardware/software system designed to measure optical wavelengths (400-1100 nm) and transmit laser signals to unidentified flying objects (UFOs) based on user input. The system uses a silicon photodiode for detection and a Class 1M laser for transmission, both compliant with Australian regulations.

## System Components

### Hardware
- **Photodiode Detector:** Silicon photodiode with transimpedance amplifier and ADC interface
- **Laser Transmitter:** Class 1M laser diode (≤1 mW) with pulse modulation capability
- **Control Hardware:** Raspberry Pi or similar microcontroller
- **Safety Interlock:** Hardware safety switch for emergency shutdown

### Software
- **GUI Application:** Streamlit-based web interface
- **Hardware Control:** Python modules for photodiode and laser control
- **Signal Processing:** Pattern encoding and data logging
- **Configuration:** YAML-based configuration system

## Installation

### Prerequisites

1. **Python 3.8+** installed
2. **Hardware assembled** according to assembly instructions
3. **Raspberry Pi** (or compatible) with GPIO access
4. **I2C enabled** on Raspberry Pi (for ADC communication)

### Software Installation

1. **Install Python dependencies:**
```bash
cd /path/to/NIoLS/software
pip install -r requirements.txt
```

2. **Install frontend dependencies:**
```bash
cd /path/to/NIoLS/frontend
npm install
```

3. **Configure the device:**
   - Edit `software/config/device_config.yaml` with your hardware settings
   - Adjust GPIO pins, I2C addresses, and other parameters as needed

4. **Start the application:**

   **Option A: Development mode (recommended for development)**
   - Terminal 1 - Start backend API:
   ```bash
   cd /path/to/NIoLS/software
   python start_device.py
   ```
   - Terminal 2 - Start frontend:
   ```bash
   cd /path/to/NIoLS/frontend
   npm run dev
   ```
   - Open browser to `http://localhost:3000`

   **Option B: Production mode**
   - Build the frontend:
   ```bash
   cd /path/to/NIoLS/frontend
   npm run build
   ```
   - Start the backend (it will serve the built frontend):
   ```bash
   cd /path/to/NIoLS/software
   python start_device.py
   ```
   - Open browser to `http://localhost:8000`

## Quick Start Guide

### 1. Initial Setup

1. **Power on the system:**
   - Connect power supply to hardware
   - Ensure Raspberry Pi is powered and booted

2. **Launch the GUI:**
   - Start the backend API server (see Installation section)
   - Start the frontend development server or open the production build
   - Open the web interface in your browser

3. **Initialize Hardware:**
   - Click "Initialize Hardware" in the sidebar
   - Verify that both photodiode and laser show "Connected" status
   - Check that interlock shows "SAFE"

### 2. Calibration

1. **Measure Dark Voltage:**
   - Cover the photodiode completely (no light)
   - Click "Calibrate Dark" button
   - Wait for measurement to complete
   - Note the dark voltage value

2. **Calibrate Wavelength Points (Optional):**
   - Use known wavelength sources (LEDs, lasers)
   - For each wavelength, expose photodiode and record voltage
   - Update calibration data in configuration file

### 3. Taking Measurements

1. **Start Measurement:**
   - Click "Start Measurement" button
   - System will continuously measure wavelength and voltage
   - View real-time plots in the main window

2. **Monitor Readings:**
   - Current wavelength and voltage displayed at top
   - History plots show trends over time
   - Data is automatically logged to CSV files

3. **Stop Measurement:**
   - Click "Stop Measurement" when done

### 4. Sending Laser Signals

1. **Verify Safety:**
   - Ensure interlock shows "SAFE" status
   - Check that no people or aircraft are in beam path
   - Review safety warnings in sidebar

2. **Select Pattern Type:**
   - Choose from: Morse code, Binary, or Geometric patterns

3. **Enter Message (for Morse/Binary):**
   - Type your message in the text input
   - Click "Send Message" to transmit

4. **Configure Geometric Pattern:**
   - Select pattern type (square, circle, triangle, spiral)
   - Adjust pattern size with slider
   - Click "Send Geometric Pattern"

5. **Send Single Pulse:**
   - Adjust pulse duration with slider
   - Click "Send Pulse" for single pulse

6. **Emergency Stop:**
   - If needed, click "Emergency Stop" button immediately
   - Laser will shut down instantly

## Advanced Features

### Pattern Encoding

#### Morse Code
- Standard international Morse code
- Supports letters, numbers, and spaces
- Configurable dot/dash durations

#### Binary Encoding
- ASCII text to binary conversion
- 8 bits per character
- Suitable for digital communication

#### Geometric Patterns
- Predefined geometric sequences
- Square, circle, triangle, spiral patterns
- Adjustable pattern size

### Signal Filtering

The system includes signal processing capabilities:
- **Moving Average:** Smooths noisy measurements
- **Low-Pass Filter:** Removes high-frequency noise
- **Outlier Removal:** Eliminates spurious readings

Configure filters in `device_config.yaml` under `signal_processing.filter`

### Data Logging

All measurements are automatically logged:
- **CSV Files:** Timestamped session files in `logs/` directory
- **Event Logs:** JSON Lines format for events
- **History:** In-memory history for real-time display

### Configuration

Edit `config/device_config.yaml` to customize:
- Hardware pin assignments
- Signal processing parameters
- Display preferences
- Safety settings

## Troubleshooting

### Hardware Not Detected

**Problem:** Photodiode or laser shows "Not Initialized"

**Solutions:**
- Check hardware connections
- Verify I2C is enabled: `sudo raspi-config` → Interface Options → I2C
- Check GPIO permissions: `sudo usermod -a -G gpio $USER`
- Restart the application

### Interlock Not Safe

**Problem:** Interlock shows "UNSAFE"

**Solutions:**
- Check physical interlock switch is closed
- Verify interlock GPIO pin connection
- Check wiring for loose connections
- Review safety protocols

### No Wavelength Reading

**Problem:** Wavelength shows "N/A"

**Solutions:**
- Verify photodiode is exposed to light
- Check calibration data is loaded
- Measure dark voltage first
- Verify ADC is reading correctly

### Laser Not Transmitting

**Problem:** Laser doesn't respond to commands

**Solutions:**
- Verify interlock is safe
- Check laser power supply
- Verify GPIO connections
- Check laser driver circuit
- Review error messages in console

### GUI Not Updating

**Problem:** Display doesn't refresh

**Solutions:**
- Check measurement is running
- Verify update rate in configuration
- Refresh browser page
- Check for error messages in console

## Safety Reminders

⚠️ **CRITICAL SAFETY RULES:**

1. **Never point laser at:**
   - People or animals
   - Aircraft or vehicles
   - Reflective surfaces

2. **Always verify:**
   - Interlock is engaged before operation
   - Beam path is clear
   - No unauthorized persons in area

3. **Emergency Procedures:**
   - Use "Emergency Stop" button immediately if needed
   - Power off system if interlock fails
   - Follow all safety protocols

4. **Regulatory Compliance:**
   - Class 1M laser: ≤1 mW output
   - No special licensing required for general use
   - Must comply with Australian laser regulations

## Maintenance

### Regular Checks

- **Weekly:**
  - Test safety interlock
  - Verify laser power output
  - Check hardware connections
  - Review log files

- **Monthly:**
  - Calibrate photodiode with known sources
  - Clean optical components
  - Update software if available
  - Review safety procedures

### Calibration

1. **Dark Voltage:**
   - Measure monthly or when conditions change
   - Cover photodiode completely
   - Record value in configuration

2. **Wavelength Calibration:**
   - Use known wavelength sources
   - Measure at multiple points (400, 530, 650, 850 nm)
   - Update calibration table in configuration

## Support

For technical support or questions:
- Review hardware documentation in `hardware/` directory
- Check safety protocols in `hardware/laser_transmitter/safety_protocols.md`
- Review configuration file for settings
- Check log files for error messages

## Version Information

- **Version:** 1.0
- **Last Updated:** [Current Date]
- **Compatibility:** Python 3.8+, Raspberry Pi 4+

---

**Important:** This device is for research and communication purposes only. Always follow safety protocols and local regulations. Never point lasers at aircraft or people.

