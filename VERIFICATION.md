# Professional Verification Checklist

This document verifies that the EUV Detection & Laser Communication Device is ready for professional operation.

## Installation Verification

- [ ] **Dependencies Installed**
  ```bash
  cd software
  python -c "import streamlit, numpy, plotly, yaml; print('✓ OK')"
  ```

- [ ] **Configuration Valid**
  ```bash
  cd software
  python -c "from hardware_control.system_health import validate_config; \
             is_valid, errors = validate_config('config/device_config.yaml'); \
             print('Valid' if is_valid else f'Errors: {errors}')"
  ```

- [ ] **Tests Pass**
  ```bash
  cd tests
  python run_tests.py
  ```
  Expected: All tests pass (or acceptable failures in simulation mode)

## System Health Verification

- [ ] **Health Check Passes**
  1. Start device: `python software/start_device.py`
  2. Click "Run Health Check" in GUI
  3. All checks should be HEALTHY or WARNING (no ERRORS or CRITICAL)

- [ ] **Hardware Detection**
  - Photodiode: Connected or Simulation Mode
  - Laser: Connected or Simulation Mode
  - Interlock: SAFE status

- [ ] **Calibration Loaded**
  - Calibration data present
  - At least 3 calibration points (recommended: 5-9)

## Functional Verification

- [ ] **Measurement System**
  - Can measure voltage
  - Can calculate wavelength
  - Data logging works
  - History plots display correctly

- [ ] **Laser Control**
  - Enable/disable works
  - Pulse generation works
  - Pattern transmission works (Morse, binary, geometric)
  - Emergency stop works

- [ ] **Safety Systems**
  - Interlock monitoring active
  - Interlock failure disables laser
  - Emergency stop functional
  - Safety warnings displayed

## Professional Features

- [ ] **Error Handling**
  - Graceful degradation when hardware unavailable
  - Clear error messages
  - No crashes on invalid input

- [ ] **Logging**
  - Log files created in `logs/` directory
  - Measurements logged correctly
  - Events logged correctly
  - No permission errors

- [ ] **Configuration**
  - Configuration file loads correctly
  - Validation works
  - Defaults used when config missing

- [ ] **Health Monitoring**
  - Health checks run successfully
  - Status displayed correctly
  - Details available

## Documentation

- [ ] **User Manual** - `docs/user_manual.md` exists and is readable
- [ ] **Safety Compliance** - `docs/safety_compliance.md` exists
- [ ] **Technical Specs** - `docs/technical_specifications.md` exists
- [ ] **Professional Setup** - `PROFESSIONAL_SETUP.md` exists

## Safety Verification

- [ ] **Interlock System**
  - Physical interlock switch functional
  - Software monitoring active
  - Automatic shutdown on interlock failure

- [ ] **Laser Safety**
  - Power verified ≤1 mW
  - Class 1M compliance documented
  - Safety warnings displayed

- [ ] **Emergency Procedures**
  - Emergency stop button functional
  - Shutdown procedures documented
  - Incident reporting procedures available

## Performance Verification

- [ ] **Response Time**
  - Measurements update within 1 second
  - Laser control responds immediately
  - GUI updates smoothly

- [ ] **Stability**
  - No memory leaks
  - No crashes during extended operation
  - Handles errors gracefully

## Operational Closure Verification

- [ ] **FSM State Management**
  - FSM initializes in SAFE state
  - State transitions require predicate validation
  - Illegal transitions rejected
  - FAULT state latches correctly
  - Reset from FAULT works

- [ ] **Envelope Outputs**
  - Measurement endpoints return envelopes (not point values)
  - Wavelength envelope shows min-max range
  - Voltage envelope includes noise estimates
  - Emit envelope validates requests
  - Budget envelope shows remaining resources

- [ ] **Hash Binding**
  - Config hash computed at initialization
  - Calibration hash computed at initialization
  - Hashes stored in session context
  - Config drift detection triggers FAULT
  - Hash stability verified (same config = same hash)

- [ ] **Execution Trace**
  - Trace records written for each transition
  - Hash chaining verified (prev_hash matches)
  - Trace chain integrity check passes
  - Tamper detection works
  - Session root hash computed correctly

- [ ] **Session Bundles**
  - Bundle created on shutdown
  - All required files present (trace, config, calibration, health, manifest)
  - Root hash in manifest matches computed value
  - Bundle location: `logs/sessions/<session_id>/`

### Trace Integrity Verification

To verify trace integrity:

```python
from core.trace import TraceReader
from pathlib import Path

trace_file = Path("logs/sessions/<session_id>/trace.jsonl")
reader = TraceReader(trace_file)
is_valid, errors = reader.verify_chain()

if is_valid:
    print("✓ Trace chain is valid")
else:
    print("✗ Trace chain errors:")
    for error in errors:
        print(f"  - {error}")
```

### Session Bundle Verification

To verify session bundle:

```python
import json
from pathlib import Path

session_dir = Path("logs/sessions/<session_id>/")
manifest_file = session_dir / "session_manifest.json"

with open(manifest_file) as f:
    manifest = json.load(f)

# Check required files
required_files = ["trace.jsonl", "config.json", "calibration.json", 
                 "health_start.json", "health_end.json", "session_manifest.json"]

for file in required_files:
    if manifest.get("files", {}).get(file.replace(".json", "").replace(".jsonl", "")):
        print(f"✓ {file} present")
    else:
        print(f"✗ {file} missing")

# Verify root hash
print(f"Root hash: {manifest.get('root_hash', 'MISSING')}")
```

## NHI Signal Capture (Prototype)

- [ ] **ET Interface Config**
  - `et_interface` in `device_config.yaml`: approach_bearing_deg 13°, elevation_band_nm 12 (vertical at 98.5 km), slope_deg 12°, standoff_km 98.5, **timing_hz 130**; tolerances 0± for bearing, elevation, standoff; time_varying_pointing_required
  - Detection: baseline_above_dark_v, wavelength_min_nm 320, wavelength_max_nm 1100
  - Response: pattern_type (geometric/morse), geometric_type, message, size, require_envelope_for_response

- [ ] **NHI Detection Envelope**
  - Envelope-based only: voltage above baseline (dark + baseline_above_dark_v), wavelength in band, no saturation/clipping
  - No identification or contact claimed — only "envelope_satisfied" true/false
  - GET `/api/nhi/detection` returns NHIDetectionEnvelope; frontend panel shows status and disclaimer

- [ ] **NHI Response (Uplink) — End-to-End**
  - POST `/api/nhi/response` emits configured pattern when envelope_satisfied and state EMIT_READY; all emission via FSM and budget
  - Frontend "Send response (uplink)" button enabled when envelope satisfied and EMIT_READY; completes two-way optical link
  - No identification or contact claimed; response is envelope-triggered emission only

- [ ] **Two-Way Optical Link (Model)**
  - Downlink: "their light" detected by photodiode (320–1100 nm); detection is envelope-based per NIoLS doctrine
  - Uplink: our laser (532/650 nm, ≤1 mW) sends response pattern; specific pointing (bearing 13°, etc.) in physical deployment; time-varying pointing required for membrane

- [ ] **Protocol (ET Diplomat)**
  - Do not interfere with human detection systems
  - No direct-fear language in UI, runbooks, or docs (indirect fear acceptable)
  - Review user- and external-facing strings (UI labels, runbook text, log messages, doc phrases) for (1) risk of interfering with human detection systems, (2) direct fear-inducing language

- [ ] **Timing 130 Hz (phase-in/sync from ET)**
  - Use `timing_hz: 130` in config; 12 rev/ms is deprecated. Harmonic verification at 12 kHz remains disabled (`harmonic_verification_enabled: false`); current sample rate 250 SPS; 12 kHz would require >> 24 kHz sampling.

## Professional Readiness

- [ ] **Code Quality**
  - No linter errors
  - Proper error handling
  - Type hints where appropriate
  - Documentation strings

- [ ] **Testing**
  - Unit tests pass (FSM, predicates, hash binding, trace)
  - Integration tests pass (full flow, fault conditions)
  - Simulation mode works
  - Tests cover envelope validation

- [ ] **Deployment**
  - Verification script (`verify.py`) passes
  - Startup script works with SIGTERM handler
  - Session bundles written on shutdown
  - Systemd unit configured (if applicable)
  - Configuration validated
  - Logging configured

## Sign-Off

**System Verified By:** _________________  
**Date:** _________________  
**Status:** ☐ Ready for Professional Use  ☐ Issues Found (see notes)

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**Version:** 1.0  
**Last Updated:** [Current Date]

