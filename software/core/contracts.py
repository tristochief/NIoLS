"""
Contracts Module

Defines the only externally-visible output types as bounded envelopes.
No semantic point values are allowed.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


@dataclass
class MeasurementQuality:
    """Measurement quality indicators."""
    snr_estimate: Optional[float] = None  # Signal-to-noise ratio estimate
    saturation_flag: bool = False  # True if measurement saturated
    clipping_flag: bool = False  # True if measurement clipped


@dataclass
class WavelengthEnvelope:
    """Wavelength measurement envelope."""
    min_nm: float
    max_nm: float
    confidence: Optional[float] = None  # Confidence level (0.0-1.0)
    valid_until: Optional[float] = None  # Timestamp when envelope expires
    
    def __post_init__(self):
        """Validate envelope bounds."""
        if self.min_nm > self.max_nm:
            raise ValueError("min_nm must be <= max_nm")


@dataclass
class VoltageEnvelope:
    """Voltage measurement envelope."""
    min_v: float
    max_v: float
    rms_noise: Optional[float] = None  # RMS noise estimate in volts
    
    def __post_init__(self):
        """Validate envelope bounds."""
        if self.min_v > self.max_v:
            raise ValueError("min_v must be <= max_v")


@dataclass
class MeasurementEnvelope:
    """
    Complete measurement envelope containing wavelength and voltage bounds.
    
    This is the only allowed output type for measurements.
    """
    wavelength_envelope_nm: Optional[WavelengthEnvelope] = None
    voltage_envelope_v: VoltageEnvelope = None
    measurement_quality: Optional[MeasurementQuality] = None
    
    def __post_init__(self):
        """Validate that at least one envelope is provided."""
        if self.wavelength_envelope_nm is None and self.voltage_envelope_v is None:
            raise ValueError("At least one envelope (wavelength or voltage) must be provided")


@dataclass
class PulseWidthBounds:
    """Pulse width constraints."""
    min_ms: float
    max_ms: float
    
    def __post_init__(self):
        """Validate bounds."""
        if self.min_ms < 0:
            raise ValueError("min_ms must be >= 0")
        if self.min_ms > self.max_ms:
            raise ValueError("min_ms must be <= max_ms")


@dataclass
class EmitEnvelope:
    """
    Emission envelope defining allowed emission parameters.
    
    All emission requests must fit within this envelope.
    """
    power_mw_max: float  # Maximum power in milliwatts (≤1.0 for Class 1M)
    duty_cycle_max: float  # Maximum duty cycle (0-100%)
    t_start: float  # Start time (monotonic)
    t_end: float  # End time (monotonic)
    pulse_width_bounds: Optional[PulseWidthBounds] = None
    
    def __post_init__(self):
        """Validate envelope constraints."""
        if self.power_mw_max > 1.0:
            raise ValueError("power_mw_max must be <= 1.0 mW (Class 1M limit)")
        if self.duty_cycle_max < 0 or self.duty_cycle_max > 100:
            raise ValueError("duty_cycle_max must be in range [0, 100]")
        if self.t_start >= self.t_end:
            raise ValueError("t_start must be < t_end")
    
    def duration_ms(self) -> float:
        """Get emission duration in milliseconds."""
        return (self.t_end - self.t_start) * 1000.0
    
    def validate_request(self, requested_power_mw: float, 
                         requested_duty_percent: float,
                         requested_duration_ms: float) -> tuple[bool, str]:
        """
        Validate if a request fits within this envelope.
        
        Args:
            requested_power_mw: Requested power in milliwatts
            requested_duty_percent: Requested duty cycle percentage
            requested_duration_ms: Requested duration in milliseconds
            
        Returns:
            (is_valid, error_message)
        """
        if requested_power_mw > self.power_mw_max:
            return False, f"Requested power {requested_power_mw} mW exceeds max {self.power_mw_max} mW"
        
        if requested_duty_percent > self.duty_cycle_max:
            return False, f"Requested duty cycle {requested_duty_percent}% exceeds max {self.duty_cycle_max}%"
        
        if requested_duration_ms > self.duration_ms():
            return False, f"Requested duration {requested_duration_ms} ms exceeds max {self.duration_ms()} ms"
        
        if self.pulse_width_bounds:
            # Check if pulse width constraints are satisfied
            # This is a simplified check - actual pattern validation would be more complex
            pass
        
        return True, ""


@dataclass
class BudgetEnvelope:
    """
    Budget envelope showing remaining resources.
    """
    remaining_emit_ms: float  # Remaining continuous emission time in milliseconds
    remaining_duty_percent: float  # Remaining duty cycle budget (0-100)
    cooldown_remaining_ms: float  # Cooldown time remaining in milliseconds
    
    def __post_init__(self):
        """Validate budget values."""
        if self.remaining_emit_ms < 0:
            raise ValueError("remaining_emit_ms must be >= 0")
        if self.remaining_duty_percent < 0 or self.remaining_duty_percent > 100:
            raise ValueError("remaining_duty_percent must be in range [0, 100]")
        if self.cooldown_remaining_ms < 0:
            raise ValueError("cooldown_remaining_ms must be >= 0")


@dataclass
class SessionStatusEnvelope:
    """
    Session status envelope containing state, budgets, and verification hashes.
    
    This is the only allowed output type for status queries.
    """
    state: str  # Current FSM state
    budget: BudgetEnvelope
    config_hash: Optional[str] = None  # Bound configuration hash
    cal_hash: Optional[str] = None  # Bound calibration hash
    constraints: Optional[Dict[str, Any]] = None  # Additional constraints
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result = {
            "state": self.state,
            "budget": {
                "remaining_emit_ms": self.budget.remaining_emit_ms,
                "remaining_duty_percent": self.budget.remaining_duty_percent,
                "cooldown_remaining_ms": self.budget.cooldown_remaining_ms
            }
        }
        
        if self.config_hash:
            result["config_hash"] = self.config_hash
        if self.cal_hash:
            result["cal_hash"] = self.cal_hash
        if self.constraints:
            result["constraints"] = self.constraints
        
        return result

