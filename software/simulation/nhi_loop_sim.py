"""
Deterministic NHI loop simulation (detect and send).

End-to-end two-way optical link: downlink (detection envelope) and uplink
(send response). Runs the full NHI loop once with mock photodiode and laser,
real NHIDetector and FSM, and prints each step for legible verification.
No identification or contact claimed — envelope-based only. No hardware required.

Specs: docs/NHI_Detection_Prototype.md, docs/ET_Engineering_Interface_Model.md

Usage:
  From NIoLS repo root:  python -m software.simulation.nhi_loop_sim
  From software/:        python -m simulation.nhi_loop_sim
  Or:                    python software/simulation/nhi_loop_sim.py
"""

import sys
from pathlib import Path

# Ensure software/ is on path so core and hardware_control can be imported
_software_dir = Path(__file__).resolve().parent.parent
if str(_software_dir) not in sys.path:
    sys.path.insert(0, str(_software_dir))

from core.contracts import (
    MeasurementEnvelope,
    VoltageEnvelope,
    WavelengthEnvelope,
    MeasurementQuality,
)
from core.context import SessionContext, FSMState
from core.fsm import FSM, FSMEvent
from core.hash_binding import load_config_and_hash, load_calibration_and_hash
from hardware_control.nhi_detector import NHIDetector
from hardware_control.signal_processor import SignalProcessor
from hardware_control.laser_controller import LaserState
from hardware_control.system_health import HealthCheck, HealthStatus
import time as _time


# --- Defaults for synthetic envelope when config not yet loaded (fallback only) ---
_DEFAULT_BASELINE_ABOVE_DARK_V = 0.02
_DEFAULT_WAVELENGTH_MIN_NM = 320.0
_DEFAULT_WAVELENGTH_MAX_NM = 1100.0
_DEFAULT_DARK_V = 0.0


def make_synthetic_measurement_envelope(config: dict, dark_voltage: float) -> MeasurementEnvelope:
    """
    Build a measurement envelope that satisfies NHI detection (above baseline, in band).
    Uses et_interface.detection for wavelength band; voltage above dark_voltage + baseline.
    """
    et_det = config.get("et_interface", {}).get("detection", {})
    baseline_v = float(et_det.get("baseline_above_dark_v", _DEFAULT_BASELINE_ABOVE_DARK_V))
    w_min = float(et_det.get("wavelength_min_nm", _DEFAULT_WAVELENGTH_MIN_NM))
    w_max = float(et_det.get("wavelength_max_nm", _DEFAULT_WAVELENGTH_MAX_NM))
    threshold_v = dark_voltage + baseline_v
    # Synthetic voltage clearly above threshold, within band
    synthetic_min_v = threshold_v + 0.03
    synthetic_max_v = threshold_v + 0.10
    return MeasurementEnvelope(
        voltage_envelope_v=VoltageEnvelope(min_v=synthetic_min_v, max_v=synthetic_max_v),
        wavelength_envelope_nm=WavelengthEnvelope(min_nm=w_min, max_nm=w_max),
        measurement_quality=MeasurementQuality(saturation_flag=False, clipping_flag=False),
    )


def run_nhi_loop_simulation() -> bool:
    """
    Run one full NHI loop: SAFE -> ... -> EMIT_READY, detect (envelope satisfied), send, EMIT_COMPLETE.
    Returns True if the loop completed successfully.
    """
    config_path = _software_dir / "config" / "device_config.yaml"
    if not config_path.exists():
        print(f"ERROR: Config not found: {config_path}")
        return False

    print("=" * 60)
    print("NHI LOOP SIMULATION (Send and Detect)")
    print("=" * 60)

    # --- Load config and calibration ---
    config, config_hash = load_config_and_hash(config_path)
    print(f"\n1. Config loaded  config_hash={config_hash[:16]}...")

    # Config validation: et_interface.detection and et_interface.response required
    et_detection = config.get("et_interface", {}).get("detection")
    et_response = config.get("et_interface", {}).get("response")
    if not et_detection:
        print("ERROR: config et_interface.detection missing (required for NHI sim)")
        return False
    if not et_response:
        print("ERROR: config et_interface.response missing (required for NHI sim)")
        return False

    # ET interface parameters (traceability to ET Engineering Interface Model)
    et = config.get("et_interface", {})
    timing_str = f"timing_hz={et.get('timing_hz')}" if et.get("timing_hz") is not None else f"revolution_rate={et.get('revolution_rate_per_ms')} rev/ms"
    tol = f", tol_deg={et.get('approach_bearing_tolerance_deg')}, tol_nm={et.get('elevation_band_tolerance_nm')}, tol_km={et.get('standoff_tolerance_km')}" if et.get("approach_bearing_tolerance_deg") is not None or et.get("elevation_band_tolerance_nm") is not None or et.get("standoff_tolerance_km") is not None else ""
    pt = ", time_varying_pointing=" + str(et.get("time_varying_pointing_required", "")) if et.get("time_varying_pointing_required") is not None else ""
    print(f"   ET interface: bearing={et.get('approach_bearing_deg')} deg, "
          f"elevation_band={et.get('elevation_band_nm')} nm, standoff={et.get('standoff_km')} km, "
          f"slope_deg={et.get('slope_deg')}, {timing_str}{tol}{pt}")

    dark_voltage = float(config.get("calibration", {}).get("dark_voltage", _DEFAULT_DARK_V))
    baseline_above_dark_v = float(et_detection.get("baseline_above_dark_v", _DEFAULT_BASELINE_ABOVE_DARK_V))
    wavelength_min_nm = float(et_detection.get("wavelength_min_nm", _DEFAULT_WAVELENGTH_MIN_NM))
    wavelength_max_nm = float(et_detection.get("wavelength_max_nm", _DEFAULT_WAVELENGTH_MAX_NM))
    threshold_v = dark_voltage + baseline_above_dark_v

    # Mock photodiode: returns synthetic above-baseline envelope; provides cal for hash
    # Calibration table includes 320 nm for alignment with detection band 320-1100 nm
    _cal_table = {
        320: 0.08, 400: 0.1, 470: 0.3, 530: 0.5, 590: 0.7, 650: 0.9,
        700: 1.1, 850: 1.5, 950: 1.8, 1100: 2.0,
    }
    _dark_v_ref = dark_voltage

    class MockPhotodiode:
        calibration_table = _cal_table
        dark_voltage = _dark_v_ref

        def __init__(self, cfg: dict, dark_v: float):
            self._config = cfg
            self._dark_v = dark_v

        def get_measurement_envelope(self, samples: int = 10) -> MeasurementEnvelope:
            return make_synthetic_measurement_envelope(self._config, self._dark_v)

    mock_photodiode = MockPhotodiode(config, dark_voltage)
    calibration, cal_hash = load_calibration_and_hash(mock_photodiode)
    print(f"2. Calibration loaded  cal_hash={cal_hash[:16]}...")

    # Mock laser: records that send was called, satisfies predicates
    uplink_sent = []

    class MockLaser:
        def is_interlock_safe(self) -> bool:
            return True

        def validate_emit_envelope(self, envelope) -> tuple:
            return True, ""

        def send_pattern(self, pattern, pulse_duration: float = 0.1, gap_duration: float = 0.1) -> bool:
            uplink_sent.append({"pattern_len": len(pattern), "pulse_dur": pulse_duration, "gap_dur": gap_duration})
            return True

        def is_connected(self) -> bool:
            return True

        def get_state(self):
            return LaserState.OFF

    mock_laser = MockLaser()

    # Mock health monitor so INITIALIZE predicates pass without real deps
    class MockHealthMonitor:
        def check_dependencies(self):
            return HealthCheck("dependencies", HealthStatus.HEALTHY, "OK", _time.time())

        def run_all_checks(self, _pd, _laser, _log_dir):
            return [
                HealthCheck("dependencies", HealthStatus.HEALTHY, "OK", _time.time()),
                HealthCheck("hardware", HealthStatus.HEALTHY, "simulated", _time.time()),
            ]

    signal_processor = SignalProcessor()
    health_monitor = MockHealthMonitor()

    # Session context (simulation_mode=True)
    context = SessionContext(
        config=config,
        config_hash=config_hash,
        calibration=calibration,
        cal_hash=cal_hash,
        photodiode_reader=mock_photodiode,
        laser_controller=mock_laser,
        signal_processor=signal_processor,
        health_monitor=health_monitor,
        simulation_mode=True,
    )

    def trace_cb(transition_info: dict) -> None:
        """Print each FSM transition for legible verification."""
        from_s = transition_info.get("from_state", "?")
        ev = transition_info.get("event", "?")
        if "fault_reason" in transition_info:
            print(f"   [trace] {from_s} --{ev}--> FAULT: {transition_info['fault_reason']}")
        else:
            to_state = transition_info.get("to_state", "?")
            print(f"   [trace] {from_s} --{ev}--> {to_state}")

    fsm = FSM(context, trace_writer=trace_cb)

    # --- FSM: SAFE -> INITIALIZED -> ARMED -> EMIT_READY ---
    print("\n3. FSM transitions")
    for event, label in [
        (FSMEvent.INITIALIZE, "SAFE -> INITIALIZED"),
        (FSMEvent.ARM, "INITIALIZED -> ARMED"),
        (FSMEvent.ARM_CONFIRM, "ARMED -> EMIT_READY"),
    ]:
        ok, msg, _ = fsm.transition(event)
        if not ok:
            print(f"   FAILED at {label}: {msg}")
            return False
        print(f"   {label}  state={context.state.value}")

    # --- Detect: evaluate measurement envelope ---
    measurement_envelope = mock_photodiode.get_measurement_envelope()
    nhi_detector = NHIDetector.from_config(config)
    nhi_result = nhi_detector.evaluate(measurement_envelope, dark_voltage=dark_voltage)

    print("\n4. NHI Detection (downlink)")
    v_env = measurement_envelope.voltage_envelope_v
    w_env = measurement_envelope.wavelength_envelope_nm
    print(f"   Voltage envelope:     {v_env.min_v:.4f} - {v_env.max_v:.4f} V")
    if w_env:
        print(f"   Wavelength envelope:  {w_env.min_nm:.1f} - {w_env.max_nm:.1f} nm")
    print(f"   Baseline threshold:   {threshold_v:.4f} V (dark={dark_voltage:.4f} + baseline={baseline_above_dark_v:.4f})")
    print(f"   Detection band:       {wavelength_min_nm:.0f} - {wavelength_max_nm:.0f} nm")
    print(f"   Envelope satisfied:   {nhi_result.envelope_satisfied}")
    print(f"   Note: {nhi_result.note}")

    require_envelope = et_response.get("require_envelope_for_response", True)
    if require_envelope and not nhi_result.envelope_satisfied:
        print("   FAILED: require_envelope_for_response is true and envelope not satisfied.")
        return False
    if nhi_result.envelope_satisfied and require_envelope:
        print("   require_envelope_for_response: true (respecting; envelope satisfied)")

    # --- Send (uplink): EMIT_READY -> EMITTING -> EMIT_READY ---
    resp_cfg = config.get("et_interface", {}).get("response", {})
    pattern_type = resp_cfg.get("pattern_type", "geometric")
    geometric_type = resp_cfg.get("geometric_type", "circle")
    size = resp_cfg.get("size", 12)
    pulse_dur = config.get("signal_processing", {}).get("encoding", {}).get("pulse_duration", 0.1)
    gap_dur = config.get("signal_processing", {}).get("encoding", {}).get("gap_duration", 0.1)

    if pattern_type == "geometric":
        pattern = signal_processor.encode_message(geometric_type, "geometric")
        pattern = pattern[:size] if len(pattern) >= size else pattern
    else:
        message = resp_cfg.get("message", "OK")
        pattern = signal_processor.encode_message(message, pattern_type)
        pattern = pattern[:size] if size else pattern

    total_pulses = sum(1 for p in pattern if p)
    total_gaps = sum(1 for p in pattern if not p)
    total_duration_s = (total_pulses * pulse_dur) + (total_gaps * gap_dur)
    total_duration_ms = total_duration_s * 1000.0
    duty_percent = (total_pulses * pulse_dur / total_duration_s * 100.0) if total_duration_s > 0 else 0.0

    event_data = {
        "required_emit_ms": total_duration_ms,
        "required_duty_percent": duty_percent,
        "emit_duration_ms": total_duration_ms,
        "duty_percent": duty_percent,
    }

    print("\n5. Send response (uplink)")
    ok, msg, _ = fsm.transition(FSMEvent.EMIT_REQUEST, event_data=event_data)
    if not ok:
        print(f"   FAILED EMIT_REQUEST: {msg}")
        return False
    print(f"   EMIT_READY -> EMITTING  state={context.state.value}")

    mock_laser.send_pattern(pattern, pulse_dur, gap_dur)
    fsm.transition(FSMEvent.EMIT_COMPLETE, event_data=event_data)
    print(f"   EMITTING -> EMIT_READY  state={context.state.value}")
    print(f"   Uplink sent: pattern_type={pattern_type}, pattern_len={len(pattern)}, duration_ms={total_duration_ms:.1f}")

    # --- Timeline summary ---
    print("\n" + "-" * 60)
    print("NHI LOOP TIMELINE")
    print("-" * 60)
    print("  1. Detect (downlink)  -> envelope_satisfied = True")
    print("  2. Send (uplink)      -> EMIT_REQUEST -> EMITTING -> EMIT_COMPLETE -> EMIT_READY")
    print("  3. Loop complete. Envelope-based only.")
    print("  Disclaimer: Detection envelope satisfied = optical signal in band above baseline. No identification claimed.")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_nhi_loop_simulation()
    sys.exit(0 if success else 1)
