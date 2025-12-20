"""
Session Context Module

Manages session state, configuration hashes, calibration hashes, and budgets.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class FSMState(Enum):
    """FSM state enumeration."""
    SAFE = "SAFE"
    INITIALIZED = "INITIALIZED"
    ARMED = "ARMED"
    EMIT_READY = "EMIT_READY"
    EMITTING = "EMITTING"
    FAULT = "FAULT"


@dataclass
class Budget:
    """Laser emission budget tracking."""
    remaining_emit_ms: float  # Remaining continuous emission time in milliseconds
    remaining_duty_percent: float  # Remaining duty cycle budget (0-100)
    cooldown_remaining_ms: float  # Cooldown time remaining in milliseconds
    last_emit_end_time: Optional[float] = None  # Monotonic time of last emission end
    
    def update_cooldown(self, current_time: float, cooldown_time_ms: float):
        """Update cooldown remaining based on current time."""
        if self.last_emit_end_time is None:
            self.cooldown_remaining_ms = 0.0
        else:
            elapsed_ms = (current_time - self.last_emit_end_time) * 1000.0
            self.cooldown_remaining_ms = max(0.0, cooldown_time_ms - elapsed_ms)
    
    def consume_emit_time(self, duration_ms: float):
        """Consume emission time from budget."""
        self.remaining_emit_ms = max(0.0, self.remaining_emit_ms - duration_ms)
    
    def consume_duty_cycle(self, duty_percent: float):
        """Consume duty cycle from budget."""
        self.remaining_duty_percent = max(0.0, self.remaining_duty_percent - duty_percent)
    
    def record_emit_end(self, current_time: float):
        """Record the end of an emission for cooldown tracking."""
        self.last_emit_end_time = current_time


@dataclass
class SessionContext:
    """
    Session context containing state, configuration, and budgets.
    
    This context is immutable during a session once INITIALIZED.
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: FSMState = FSMState.SAFE
    config_hash: Optional[str] = None
    cal_hash: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    calibration: Optional[Dict[str, Any]] = None
    budget: Optional[Budget] = None
    arming_window_start: Optional[float] = None  # Monotonic time when ARMED state entered
    arming_window_duration_ms: float = 5000.0  # 5 second arming window
    simulation_mode: bool = False
    fault_reason: Optional[str] = None  # Reason for FAULT state
    
    # Hardware references (not part of hash-bound state)
    photodiode_reader: Any = None
    laser_controller: Any = None
    signal_processor: Any = None
    health_monitor: Any = None
    
    def initialize_budget(self, config: Dict[str, Any]):
        """
        Initialize budget from configuration.
        
        Args:
            config: Device configuration dictionary
        """
        safety = config.get('safety', {})
        max_continuous_time_s = safety.get('max_continuous_time', 3600.0)
        max_duty_percent = 100.0  # Start with full duty cycle budget
        
        self.budget = Budget(
            remaining_emit_ms=max_continuous_time_s * 1000.0,
            remaining_duty_percent=max_duty_percent,
            cooldown_remaining_ms=0.0
        )
    
    def is_arming_window_valid(self, current_time: Optional[float] = None) -> bool:
        """
        Check if arming window is still valid.
        
        Args:
            current_time: Current monotonic time (uses time.monotonic() if None)
            
        Returns:
            True if within arming window, False otherwise
        """
        if self.arming_window_start is None:
            return False
        
        if current_time is None:
            current_time = time.monotonic()
        
        elapsed_ms = (current_time - self.arming_window_start) * 1000.0
        return elapsed_ms < self.arming_window_duration_ms
    
    def start_arming_window(self):
        """Start the arming window timer."""
        self.arming_window_start = time.monotonic()
    
    def clear_arming_window(self):
        """Clear the arming window."""
        self.arming_window_start = None

