"""
Laser Controller Module

This module handles laser control, pulse pattern generation, and safety interlock monitoring.
Supports GPIO control for laser driver and safety interlock.
"""

import time
import logging
from typing import List, Optional, Callable
from enum import Enum

try:
    from core.contracts import EmitEnvelope
except ImportError:
    # Fallback for when core module is not yet available
    EmitEnvelope = None

try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    logging.warning("RPi.GPIO not available. Running in simulation mode.")


class LaserState(Enum):
    """Laser state enumeration."""
    OFF = "off"
    ON = "on"
    PULSING = "pulsing"
    ERROR = "error"


class LaserController:
    """
    Laser controller with pulse modulation and safety interlock.
    """
    
    def __init__(self,
                 laser_pin: int = 18,
                 interlock_pin: int = 23,
                 pwm_frequency: int = 1000,
                 pulse_duration: float = 0.001):
        """
        Initialize laser controller.
        
        Args:
            laser_pin: GPIO pin for laser control
            interlock_pin: GPIO pin for safety interlock (normally high = safe)
            pwm_frequency: PWM frequency in Hz
            pulse_duration: Default pulse duration in seconds
        """
        self.laser_pin = laser_pin
        self.interlock_pin = interlock_pin
        self.pwm_frequency = pwm_frequency
        self.pulse_duration = pulse_duration
        
        self.state = LaserState.OFF
        self.pwm = None
        self.hardware_connected = False
        self.interlock_callback = None
        
        if HARDWARE_AVAILABLE:
            try:
                self._initialize_hardware()
            except Exception as e:
                logging.error(f"Failed to initialize hardware: {e}")
                self.hardware_connected = False
        else:
            self.hardware_connected = False
            logging.info("Running in simulation mode")
    
    def _initialize_hardware(self):
        """Initialize GPIO hardware."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Configure laser pin
        GPIO.setup(self.laser_pin, GPIO.OUT)
        GPIO.output(self.laser_pin, GPIO.LOW)
        
        # Configure interlock pin (input with pull-up)
        GPIO.setup(self.interlock_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Set up PWM
        self.pwm = GPIO.PWM(self.laser_pin, self.pwm_frequency)
        self.pwm.start(0)  # Start with 0% duty cycle (off)
        
        # Set up interlock interrupt
        GPIO.add_event_detect(self.interlock_pin, GPIO.BOTH, 
                             callback=self._interlock_callback, 
                             bouncetime=10)
        
        self.hardware_connected = True
        logging.info("Hardware initialized successfully")
    
    def _interlock_callback(self, channel):
        """Callback for interlock state change."""
        if not self.is_interlock_safe():
            logging.warning("Safety interlock opened - disabling laser")
            self.emergency_stop()
            if self.interlock_callback:
                self.interlock_callback(False)
        else:
            logging.info("Safety interlock closed")
            if self.interlock_callback:
                self.interlock_callback(True)
    
    def set_interlock_callback(self, callback: Callable[[bool], None]):
        """
        Set callback function for interlock state changes.
        
        Args:
            callback: Function that takes bool (True = safe, False = unsafe)
        """
        self.interlock_callback = callback
    
    def is_interlock_safe(self) -> bool:
        """
        Check if safety interlock is engaged (safe to operate).
        
        Returns:
            True if interlock is safe, False otherwise
        """
        if self.hardware_connected:
            # Interlock pin high = safe (normally closed switch)
            return GPIO.input(self.interlock_pin) == GPIO.HIGH
        else:
            # Simulation mode: always safe
            return True
    
    def enable(self) -> bool:
        """
        Enable laser (continuous output).
        
        Returns:
            True if enabled, False if interlock prevents operation
        """
        if not self.is_interlock_safe():
            logging.error("Cannot enable laser - interlock not safe")
            self.state = LaserState.ERROR
            return False
        
        if self.hardware_connected:
            if self.pwm:
                self.pwm.ChangeDutyCycle(100)  # 100% duty cycle = continuous
            else:
                GPIO.output(self.laser_pin, GPIO.HIGH)
        else:
            logging.info("SIMULATION: Laser enabled")
        
        self.state = LaserState.ON
        logging.info("Laser enabled")
        return True
    
    def disable(self):
        """Disable laser."""
        if self.hardware_connected:
            if self.pwm:
                self.pwm.ChangeDutyCycle(0)  # 0% duty cycle = off
            else:
                GPIO.output(self.laser_pin, GPIO.LOW)
        else:
            logging.info("SIMULATION: Laser disabled")
        
        self.state = LaserState.OFF
        logging.info("Laser disabled")
    
    def emergency_stop(self):
        """Emergency stop - immediately disable laser."""
        self.disable()
        self.state = LaserState.ERROR
        logging.warning("EMERGENCY STOP activated")
    
    def pulse(self, duration: Optional[float] = None) -> bool:
        """
        Send a single pulse.
        
        Args:
            duration: Pulse duration in seconds (uses default if None)
            
        Returns:
            True if pulse sent, False if interlock prevents operation
        """
        if not self.is_interlock_safe():
            logging.error("Cannot pulse laser - interlock not safe")
            return False
        
        pulse_dur = duration or self.pulse_duration
        
        if self.hardware_connected:
            if self.pwm:
                self.pwm.ChangeDutyCycle(100)
                time.sleep(pulse_dur)
                self.pwm.ChangeDutyCycle(0)
            else:
                GPIO.output(self.laser_pin, GPIO.HIGH)
                time.sleep(pulse_dur)
                GPIO.output(self.laser_pin, GPIO.LOW)
        else:
            logging.info(f"SIMULATION: Laser pulse ({pulse_dur*1000:.1f} ms)")
            time.sleep(pulse_dur)
        
        return True
    
    def send_pattern(self, pattern: List[bool], pulse_duration: float = 0.001, 
                    gap_duration: float = 0.001) -> bool:
        """
        Send a binary pattern (list of on/off states).
        
        Args:
            pattern: List of booleans (True = on, False = off)
            pulse_duration: Duration of each pulse in seconds
            gap_duration: Duration of gap between pulses in seconds
            
        Returns:
            True if pattern sent, False if interlock prevents operation
        """
        if not self.is_interlock_safe():
            logging.error("Cannot send pattern - interlock not safe")
            return False
        
        self.state = LaserState.PULSING
        
        for state in pattern:
            if not self.is_interlock_safe():
                logging.warning("Interlock opened during pattern - stopping")
                self.disable()
                return False
            
            if state:
                self.pulse(pulse_duration)
            else:
                time.sleep(gap_duration)
        
        self.state = LaserState.OFF
        return True
    
    def send_morse_code(self, message: str, dot_duration: float = 0.1,
                       dash_duration: float = 0.3, gap_duration: float = 0.1) -> bool:
        """
        Send Morse code message.
        
        Args:
            message: Text message to encode
            dot_duration: Duration of dot in seconds
            dash_duration: Duration of dash in seconds
            gap_duration: Duration of gap between symbols in seconds
            
        Returns:
            True if message sent, False if interlock prevents operation
        """
        morse_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
            'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
            'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
            'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
            'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
            '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
            '9': '----.', ' ': ' '  # Space for word gap
        }
        
        pattern = []
        for char in message.upper():
            if char in morse_dict:
                code = morse_dict[char]
                for symbol in code:
                    if symbol == '.':
                        pattern.append(True)
                        pattern.append(False)  # Gap after dot
                    elif symbol == '-':
                        pattern.append(True)
                        pattern.append(True)  # Dash is longer
                        pattern.append(False)  # Gap after dash
                    elif symbol == ' ':
                        pattern.append(False)
                        pattern.append(False)  # Word gap
                
                pattern.append(False)  # Gap after letter
                pattern.append(False)  # Extra gap
        
        # Convert pattern to durations
        pulse_pattern = []
        for i, state in enumerate(pattern):
            if state:
                # Determine if dot or dash based on duration
                if i > 0 and pattern[i-1] and not pattern[i-2] if i > 1 else True:
                    pulse_pattern.append((True, dot_duration))
                else:
                    pulse_pattern.append((True, dash_duration))
            else:
                pulse_pattern.append((False, gap_duration))
        
        # Send pattern
        self.state = LaserState.PULSING
        for state, duration in pulse_pattern:
            if not self.is_interlock_safe():
                logging.warning("Interlock opened during transmission - stopping")
                self.disable()
                return False
            
            if state:
                self.pulse(duration)
            else:
                time.sleep(duration)
        
        self.state = LaserState.OFF
        return True
    
    def set_pwm_duty_cycle(self, duty_cycle: float) -> bool:
        """
        Set PWM duty cycle (for intensity control).
        
        Args:
            duty_cycle: Duty cycle 0-100%
            
        Returns:
            True if set, False if interlock prevents operation
        """
        if not self.is_interlock_safe():
            logging.error("Cannot set PWM - interlock not safe")
            return False
        
        duty_cycle = max(0, min(100, duty_cycle))  # Clamp to 0-100
        
        if self.hardware_connected and self.pwm:
            self.pwm.ChangeDutyCycle(duty_cycle)
        else:
            logging.info(f"SIMULATION: PWM duty cycle set to {duty_cycle}%")
        
        if duty_cycle > 0:
            self.state = LaserState.ON
        else:
            self.state = LaserState.OFF
        
        return True
    
    def get_state(self) -> LaserState:
        """Get current laser state."""
        return self.state
    
    def is_connected(self) -> bool:
        """Check if hardware is connected."""
        return self.hardware_connected
    
    def validate_emit_envelope(self, envelope: 'EmitEnvelope') -> tuple[bool, str]:
        """
        Validate if an emit envelope is acceptable.
        
        Args:
            envelope: EmitEnvelope to validate
            
        Returns:
            (is_valid, error_message)
        """
        if EmitEnvelope is None:
            raise ImportError("core.contracts module not available")
        
        # Check power limit (Class 1M: ≤1 mW)
        if envelope.power_mw_max > 1.0:
            return False, f"Power {envelope.power_mw_max} mW exceeds Class 1M limit (1.0 mW)"
        
        # Check duty cycle
        if envelope.duty_cycle_max < 0 or envelope.duty_cycle_max > 100:
            return False, f"Duty cycle {envelope.duty_cycle_max}% is out of range [0, 100]"
        
        # Check time bounds
        if envelope.t_start >= envelope.t_end:
            return False, "t_start must be < t_end"
        
        # Check pulse width bounds if provided
        if envelope.pulse_width_bounds:
            if envelope.pulse_width_bounds.min_ms < 0:
                return False, "Pulse width min_ms must be >= 0"
            if envelope.pulse_width_bounds.min_ms > envelope.pulse_width_bounds.max_ms:
                return False, "Pulse width min_ms must be <= max_ms"
        
        return True, ""
    
    def send_pattern_with_envelope(self, pattern: List[bool], envelope: 'EmitEnvelope',
                                   pulse_duration: float = 0.001,
                                   gap_duration: float = 0.001) -> tuple[bool, str]:
        """
        Send a binary pattern with envelope validation.
        
        This is the preferred method that enforces envelope constraints.
        
        Args:
            pattern: List of booleans (True = on, False = off)
            envelope: EmitEnvelope defining constraints
            pulse_duration: Duration of each pulse in seconds
            gap_duration: Duration of gap between pulses in seconds
            
        Returns:
            (success, error_message)
        """
        if EmitEnvelope is None:
            raise ImportError("core.contracts module not available")
        
        # Validate envelope
        is_valid, error_msg = self.validate_emit_envelope(envelope)
        if not is_valid:
            return False, error_msg
        
        # Check interlock
        if not self.is_interlock_safe():
            return False, "Safety interlock is not engaged"
        
        # Calculate pattern parameters
        total_pulses = sum(1 for p in pattern if p)
        total_gaps = sum(1 for p in pattern if not p)
        total_duration = (total_pulses * pulse_duration) + (total_gaps * gap_duration)
        total_duration_ms = total_duration * 1000.0
        
        # Calculate duty cycle
        pulse_time = total_pulses * pulse_duration
        duty_cycle_percent = (pulse_time / total_duration * 100.0) if total_duration > 0 else 0.0
        
        # Validate against envelope
        if total_duration_ms > envelope.duration_ms():
            return False, f"Pattern duration {total_duration_ms} ms exceeds envelope {envelope.duration_ms()} ms"
        
        if duty_cycle_percent > envelope.duty_cycle_max:
            return False, f"Pattern duty cycle {duty_cycle_percent}% exceeds envelope {envelope.duty_cycle_max}%"
        
        # Check pulse width bounds if provided
        if envelope.pulse_width_bounds:
            pulse_width_ms = pulse_duration * 1000.0
            if pulse_width_ms < envelope.pulse_width_bounds.min_ms:
                return False, f"Pulse width {pulse_width_ms} ms below minimum {envelope.pulse_width_bounds.min_ms} ms"
            if pulse_width_ms > envelope.pulse_width_bounds.max_ms:
                return False, f"Pulse width {pulse_width_ms} ms above maximum {envelope.pulse_width_bounds.max_ms} ms"
        
        # Send pattern (reuse existing implementation)
        success = self.send_pattern(pattern, pulse_duration, gap_duration)
        
        if success:
            return True, ""
        else:
            return False, "Pattern send failed (interlock may have opened)"
    
    def cleanup(self):
        """Clean up GPIO resources."""
        if self.hardware_connected:
            self.disable()
            if self.pwm:
                self.pwm.stop()
            GPIO.cleanup()
            logging.info("GPIO cleaned up")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize controller
    controller = LaserController()
    
    # Check interlock
    if controller.is_interlock_safe():
        print("Interlock is safe")
        
        # Send a pulse
        controller.pulse(0.1)
        
        # Send Morse code
        controller.send_morse_code("SOS")
        
        # Enable continuous
        controller.enable()
        time.sleep(1)
        controller.disable()
    else:
        print("Interlock not safe - cannot operate laser")
    
    # Cleanup
    controller.cleanup()

