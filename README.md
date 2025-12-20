# Nicatoöu Instrument and optical Landing System (NIoLS)
*pronounced "naɪlz"*

---

## Copyright and License Information

Copyright (c) 2025 Tristan Claude Berry  
Licensed under the Non-Commercial Open Source License (NC-OSL) v1.4  
[Full text of the License can be found here](https://github.com/tristochief/NIoLS/blob/main/LICENSE.md)

---

# EUV Detection & Laser Communication Device

A hybrid hardware/software system for measuring optical wavelengths (400-1100 nm) and transmitting laser signals to unidentified flying objects (UFOs) based on user input. The system uses a silicon photodiode for detection and a Class 1M laser (≤1 mW) for transmission, both compliant with Australian regulations.

## Features

- **Wavelength Detection:** Silicon photodiode with 400-1100 nm range
- **Laser Communication:** Class 1M laser with pulse modulation
- **Pattern Encoding:** Morse code, binary, and geometric patterns
- **Real-time GUI:** TypeScript/React web interface with FastAPI backend
- **Safety Interlock:** Hardware safety switch with automatic shutdown
- **Data Logging:** Automatic measurement and event logging
- **Australian Compliant:** No licensing required for Class 1M operation

## Project Structure

```
NIoLS/
├── hardware/
│   ├── photodiode_detector/
│   │   ├── circuit_design.md
│   │   ├── parts_list.md
│   │   └── assembly_instructions.md
│   ├── laser_transmitter/
│   │   ├── circuit_design.md
│   │   ├── parts_list.md
│   │   └── safety_protocols.md
│   └── euv_detector_specs.md
├── software/
│   ├── api_server.py
│   ├── hardware_control/
│   │   ├── photodiode_reader.py
│   │   ├── laser_controller.py
│   │   └── signal_processor.py
│   ├── config/
│   │   └── device_config.yaml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.tsx
│   │   └── api.ts
│   ├── package.json
│   └── vite.config.ts
└── docs/
    ├── user_manual.md
    ├── safety_compliance.md
    └── technical_specifications.md
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+ and npm
- Raspberry Pi 4 (or compatible)
- Hardware assembled according to documentation
- I2C enabled on Raspberry Pi

### Installation

1. **Install dependencies:**
```bash
cd software
pip install -r requirements.txt
```

2. **Configure device:**
   - Edit `config/device_config.yaml` with your hardware settings

3. **Install frontend dependencies:**
```bash
cd ../frontend
npm install
```

4. **Build frontend (optional, for production):**
```bash
npm run build
```

5. **Start the application:**
   - Backend API: Run `python start_device.py` from the `software` directory
   - Frontend (development): Run `npm run dev` from the `frontend` directory
   - The frontend will be available at `http://localhost:3000`
   - The API will be available at `http://localhost:8000`

## Documentation

- **User Manual:** `docs/user_manual.md` - Complete usage guide
- **Safety Compliance:** `docs/safety_compliance.md` - Australian regulations and safety
- **Technical Specifications:** `docs/technical_specifications.md` - Detailed technical info
- **Hardware Documentation:** `hardware/` - Circuit designs, parts lists, assembly instructions

## Safety

⚠️ **IMPORTANT SAFETY REMINDERS:**

- Never point laser at people or aircraft
- Always verify safety interlock is engaged
- Class 1M laser: ≤1 mW output
- Follow all safety protocols in documentation

## Operational Closure

NIoLS implements **operational closure** through structural constraints that ensure system behavior is deterministic and verifiable:

### Finite State Machine (FSM)

All system operations are controlled by a strict FSM with states:
- **SAFE**: System inert, laser disabled
- **INITIALIZED**: Config and calibration loaded and hash-bound
- **ARMED**: Interlock safe, arming window active
- **EMIT_READY**: Ready for emission, budgets computed
- **EMITTING**: Emission in progress within envelope constraints
- **FAULT**: Latched fault state (requires reset)

All state transitions must pass through the FSM with predicate validation. Emission is **impossible** outside the FSM path.

### Envelope-Based Outputs

The system **never** returns point values (e.g., "wavelength = 650 nm"). All outputs are **bounded envelopes**:
- **MeasurementEnvelope**: Wavelength and voltage bounds with confidence intervals
- **EmitEnvelope**: Emission constraints (power, duty cycle, time windows)
- **BudgetEnvelope**: Remaining resources (time, duty cycle, cooldown)

This ensures honest uncertainty representation and prevents false precision claims.

### Hash-Bound Configuration

Configuration and calibration are **hash-bound** at initialization:
- Config hash computed from canonical JSON representation
- Calibration hash computed from calibration table
- Hashes stored in session context and trace records
- **Config drift detection**: Any change to config/calibration during a session triggers FAULT

Configuration edits are only allowed in SAFE state.

### Hash-Chained Execution Trace

Every FSM transition writes a **hash-chained trace record**:
- Each record contains hash of previous record
- Creates immutable audit trail
- **Tamper detection**: Any modification breaks the hash chain
- Session root hash computed from final record + metadata

Trace records include: state transitions, predicate results, event data, config/calibration hashes.

### Session Bundles

On shutdown, the system generates a **session bundle** containing:
- `trace.jsonl`: Hash-chained execution trace
- `config.json`: Config snapshot with hash
- `calibration.json`: Calibration snapshot with hash
- `health_start.json`: Health check at initialization
- `health_end.json`: Health check at shutdown
- `session_manifest.json`: Root hash, session metadata, versions

Session bundles are stored in `logs/sessions/<session_id>/` and provide complete operational closure artifacts.

### Verification

Run the verification script before deployment:
```bash
cd software
python verify.py
```

This checks dependencies, config validation, tests, FSM initialization, trace creation, and write permissions.

## EUV Detection (Future)

The system is designed with a path for future EUV (12-13 nm) detection capability. See `hardware/euv_detector_specs.md` for details on specialized detectors and integration requirements.

## License

This project is for research and communication purposes. Always comply with local regulations and safety requirements.

## Version

- **Version:** 1.0
- **Last Updated:** [Current Date]

---

**Note:** This device complies with Australian Class 1M laser regulations. No special licensing required for general use. Always follow safety procedures and local regulations.
