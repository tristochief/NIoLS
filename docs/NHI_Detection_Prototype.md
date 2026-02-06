# NHI Detection Prototype

## Purpose

This document describes the **NHI (non-human intelligence) signal capture prototype** built on NIoLS. The prototype provides an **end-to-end two-way optical link**: it captures optical signals that satisfy a **detection envelope** (downlink) and allows the operator to **send a response** (uplink) via laser when the envelope is satisfied. **No identification or contact is claimed** — only envelope-based detection and controlled emission per NIoLS doctrine.

## What It Does

1. **ET interface parameters** from the ET Engineering Interface Model are stored in config (`et_interface` in `device_config.yaml`):
   - Approach bearing 13°, elevation band 12 nm (vertical at 98.5 km standoff), slope 12°, standoff 98.5 km
   - Tolerances: 0± ° (bearing), 0± nm (elevation), 0± km (standoff)
   - Timing envelope 130 Hz (phase-in/sync); do not use 12 rev/ms
   - Time-varying pointing required for physical deployment (membrane); approach geometry fixed during approach
   - Detection band 320–1100 nm; baseline above dark voltage (configurable)
   - **Response (uplink):** pattern type (geometric/morse), geometric_type (circle/spiral/triangle), message, size; optional `require_envelope_for_response: true`

2. **Envelope-based detection** evaluates each measurement envelope against:
   - Voltage envelope min ≥ dark voltage + baseline_above_dark_v
   - Wavelength envelope within 320–1100 nm
   - No saturation or clipping (measurement quality)

3. **API**
   - `GET /api/nhi/detection` returns: `envelope_satisfied`, wavelength/voltage envelopes, timestamp, note.
   - `POST /api/nhi/response` sends the configured response pattern (uplink) when detection envelope is satisfied and FSM is EMIT_READY. All emission goes through FSM and budget; no identification claimed.

4. **Frontend** shows an **NHI Detection Envelope** panel with:
   - Envelope status (Satisfied / Not satisfied)
   - Wavelength and voltage envelope bounds
   - **Send response (uplink)** button: enabled when envelope satisfied and state is EMIT_READY; completes the two-way link.
   - Disclaimer: "Detection envelope satisfied = optical signal in band above baseline. No identification claimed."

## What It Does Not Do

- Does **not** claim identification of any intelligence or "contact"
- Timing envelope is **130 Hz** (from ET); harmonic verification at 12 kHz remains disabled (current sample rate 250 SPS; 12 kHz would require >> 24 kHz sampling)
- Does **not** assert cause of detected light (ambient, reflection, or other)

## Two-Way Optical Link (End-to-End)

Per ET Engineering Interface Model:

- **Downlink:** Their light is detected by our photodiode (320–1100 nm). When the detection envelope is satisfied (signal in band, above baseline), the panel shows "Envelope: Satisfied".
- **Uplink:** Our laser (532/650 nm, ≤1 mW) sends the configured response pattern (e.g. geometric circle, size 12). The operator arms the system (SAFE → … → EMIT_READY), and when the envelope is satisfied, clicks **Send response (uplink)** to emit the pattern. All emission is via FSM and budget. **Physical deployment:** Specific pointing (bearing 13°, etc.) is required; **time-varying pointing** is required for membrane alignment. **Approach geometry is fixed** during approach (bearing, elevation, standoff do not change).

The prototype implements **both** downlink detection and uplink response so a real physical setup can receive optical signal and send it back in one operational loop.

## How to Run (End-to-End)

1. Start the device: `python software/start_device.py` (or run API server and frontend as in user manual).
2. Initialize hardware (sidebar) → state becomes INITIALIZED.
3. Arm: Arm → Confirm arm → state becomes EMIT_READY.
4. Start measurement. The measurement loop updates the measurement envelope and the NHI detector evaluates it each cycle.
5. Open the **NHI Detection Envelope** panel (below Wavelength Measurement). It polls `/api/nhi/detection` every second.
6. When the detection envelope is satisfied (e.g. real light in band above baseline, or in simulation when voltage exceeds baseline) and state is EMIT_READY, click **Send response (uplink)** to emit the configured pattern and complete the two-way link.

## Config Reference

```yaml
# device_config.yaml
et_interface:
  approach_bearing_deg: 13
  approach_bearing_tolerance_deg: 0
  elevation_band_nm: 12
  elevation_band_tolerance_nm: 0
  slope_deg: 12
  standoff_km: 98.5
  standoff_tolerance_km: 0
  timing_hz: 130                    # phase-in/sync envelope (do not use revolution_rate_per_ms)
  time_varying_pointing_required: true
  detection:
    baseline_above_dark_v: 0.02   # V above dark to consider "signal present"
    wavelength_min_nm: 320
    wavelength_max_nm: 1100
    harmonic_verification_enabled: false
  response:
    pattern_type: geometric       # geometric | morse
    geometric_type: circle         # circle | spiral | triangle
    message: "OK"                  # for morse
    size: 12                       # pattern length for geometric
    require_envelope_for_response: true  # only emit when envelope_satisfied
```

## Verification

See **VERIFICATION.md** section "NHI Signal Capture (Prototype)" for checklist. ET Engineering Interface Model open items resolved for the prototype are documented in **docs/ET_Engineering_Interface_Model.md** (Verification Resolutions).

## Revision History

| Version | Date       | Changes                |
|---------|------------|------------------------|
| 0.1     | [Current]  | Initial prototype doc |
