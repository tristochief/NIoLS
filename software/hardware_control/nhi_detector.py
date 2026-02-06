"""
NHI (Non-Human Intelligence) Signal Detection Module

Envelope-based detection of optical signals in the photodiode band.
No identification or contact is claimed — only that detection envelope
criteria (signal in band, above baseline) are satisfied or not.

Aligned with ET Engineering Interface Model: two-way optical link;
we detect "their light" via photodiode (320–1100 nm). Output is
always envelope-based per NIoLS doctrine.
"""

import time
import logging
from typing import Optional, List, Dict, Any

try:
    from core.contracts import (
        MeasurementEnvelope,
        NHIDetectionEnvelope,
        WavelengthEnvelope,
        VoltageEnvelope,
    )
except ImportError:
    MeasurementEnvelope = None
    NHIDetectionEnvelope = None
    WavelengthEnvelope = None
    VoltageEnvelope = None

logger = logging.getLogger(__name__)

# Default note shown when envelope is satisfied
DEFAULT_NOTE = (
    "Signal above baseline in photodiode band. "
    "No identification claimed. Envelope-based detection only."
)


class NHIDetector:
    """
    Evaluates measurement envelopes against ET interface detection criteria.
    
    Criteria (from device_config et_interface.detection):
    - Voltage envelope min above (dark + baseline_above_dark_v)
    - Wavelength envelope within [wavelength_min_nm, wavelength_max_nm]
    - No point claim of "contact" — only envelope_satisfied true/false
    """

    def __init__(
        self,
        baseline_above_dark_v: float = 0.02,
        wavelength_min_nm: float = 320.0,
        wavelength_max_nm: float = 1100.0,
    ):
        """
        Args:
            baseline_above_dark_v: Minimum voltage above dark to consider "signal present" (V)
            wavelength_min_nm: Lower bound of valid detection band (nm)
            wavelength_max_nm: Upper bound of valid detection band (nm)
        """
        self.baseline_above_dark_v = baseline_above_dark_v
        self.wavelength_min_nm = wavelength_min_nm
        self.wavelength_max_nm = wavelength_max_nm

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "NHIDetector":
        """Build detector from device_config et_interface.detection."""
        et = config.get("et_interface", {}).get("detection", {})
        return cls(
            baseline_above_dark_v=float(et.get("baseline_above_dark_v", 0.02)),
            wavelength_min_nm=float(et.get("wavelength_min_nm", 320.0)),
            wavelength_max_nm=float(et.get("wavelength_max_nm", 1100.0)),
        )

    def evaluate(
        self,
        measurement_envelope: "MeasurementEnvelope",
        dark_voltage: float = 0.0,
    ) -> "NHIDetectionEnvelope":
        """
        Evaluate a single measurement envelope against NHI detection criteria.
        
        Returns NHIDetectionEnvelope with envelope_satisfied True only if:
        - Voltage envelope min >= dark_voltage + baseline_above_dark_v (signal above baseline)
        - Wavelength envelope lies within [wavelength_min_nm, wavelength_max_nm]
        - No saturation/clipping (quality flags)
        
        Args:
            measurement_envelope: Current measurement envelope from photodiode
            dark_voltage: Dark voltage (V) for baseline comparison
            
        Returns:
            NHIDetectionEnvelope (envelope_satisfied, envelopes, timestamp, note)
        """
        if NHIDetectionEnvelope is None or MeasurementEnvelope is None:
            raise ImportError("core.contracts not available")

        timestamp = time.time()
        satisfied = False
        note = "No signal above baseline or out of band."

        if not measurement_envelope.voltage_envelope_v:
            return NHIDetectionEnvelope(
                envelope_satisfied=False,
                wavelength_envelope_nm=measurement_envelope.wavelength_envelope_nm,
                voltage_envelope_v=measurement_envelope.voltage_envelope_v,
                timestamp=timestamp,
                note=note,
            )

        v_env = measurement_envelope.voltage_envelope_v
        threshold_v = dark_voltage + self.baseline_above_dark_v

        # Criterion 1: voltage envelope minimum above baseline
        voltage_above_baseline = v_env.min_v >= threshold_v

        # Criterion 2: wavelength within detection band (if we have wavelength envelope)
        wavelength_in_band = True
        if measurement_envelope.wavelength_envelope_nm:
            w_env = measurement_envelope.wavelength_envelope_nm
            wavelength_in_band = (
                w_env.min_nm >= self.wavelength_min_nm
                and w_env.max_nm <= self.wavelength_max_nm
            )

        # Criterion 3: no saturation/clipping (optional; fail if quality bad)
        quality_ok = True
        if measurement_envelope.measurement_quality:
            q = measurement_envelope.measurement_quality
            quality_ok = not (q.saturation_flag or q.clipping_flag)

        satisfied = voltage_above_baseline and wavelength_in_band and quality_ok
        if satisfied:
            note = DEFAULT_NOTE

        return NHIDetectionEnvelope(
            envelope_satisfied=satisfied,
            wavelength_envelope_nm=measurement_envelope.wavelength_envelope_nm,
            voltage_envelope_v=measurement_envelope.voltage_envelope_v,
            timestamp=timestamp,
            note=note,
        )

    def evaluate_from_voltage_history(
        self,
        voltage_history: List[float],
        dark_voltage: float = 0.0,
        wavelength_range: Optional[tuple] = None,
    ) -> "NHIDetectionEnvelope":
        """
        Evaluate from raw voltage history (e.g. when only voltages are available).
        
        Constructs a minimal voltage envelope from min/max of history and
        checks if min >= dark + baseline. Wavelength envelope set from
        wavelength_range if provided, else None (wavelength_in_band treated as True).
        
        Args:
            voltage_history: List of voltage readings (V)
            dark_voltage: Dark voltage (V)
            wavelength_range: Optional (min_nm, max_nm) for wavelength envelope
            
        Returns:
            NHIDetectionEnvelope
        """
        if NHIDetectionEnvelope is None or VoltageEnvelope is None:
            raise ImportError("core.contracts not available")

        timestamp = time.time()
        if not voltage_history:
            return NHIDetectionEnvelope(
                envelope_satisfied=False,
                voltage_envelope_v=VoltageEnvelope(min_v=0.0, max_v=0.0),
                timestamp=timestamp,
                note="No voltage history.",
            )

        v_min = min(voltage_history)
        v_max = max(voltage_history)
        threshold_v = dark_voltage + self.baseline_above_dark_v
        voltage_above_baseline = v_min >= threshold_v

        wavelength_in_band = True
        w_env = None
        if wavelength_range and len(wavelength_range) == 2:
            w_min, w_max = wavelength_range
            wavelength_in_band = (
                w_min >= self.wavelength_min_nm and w_max <= self.wavelength_max_nm
            )
            w_env = WavelengthEnvelope(min_nm=w_min, max_nm=w_max)

        satisfied = voltage_above_baseline and wavelength_in_band
        note = DEFAULT_NOTE if satisfied else "No signal above baseline or out of band."

        return NHIDetectionEnvelope(
            envelope_satisfied=satisfied,
            wavelength_envelope_nm=w_env,
            voltage_envelope_v=VoltageEnvelope(min_v=v_min, max_v=v_max),
            timestamp=timestamp,
            note=note,
        )
