"""
Signal Processor Module

This module handles signal processing, pattern encoding (Morse, binary, geometric),
and data logging.
"""

import time
import logging
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import json
import csv
from pathlib import Path

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available. Some features may be limited.")


class PatternEncoder:
    """Pattern encoder for various signal formats."""
    
    @staticmethod
    def encode_binary(message: str, bits_per_char: int = 8) -> List[bool]:
        """
        Encode text message as binary pattern.
        
        Args:
            message: Text message to encode
            bits_per_char: Bits per character (typically 8 for ASCII)
            
        Returns:
            List of booleans (True = on, False = off)
        """
        pattern = []
        for char in message:
            # Convert to ASCII
            ascii_val = ord(char)
            # Convert to binary
            binary = format(ascii_val, f'0{bits_per_char}b')
            # Add to pattern
            for bit in binary:
                pattern.append(bit == '1')
            # Add separator
            pattern.append(False)
        return pattern
    
    @staticmethod
    def encode_morse(message: str) -> List[bool]:
        """
        Encode text message as Morse code pattern.
        
        Args:
            message: Text message to encode
            
        Returns:
            List of booleans (True = on, False = off)
        """
        morse_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
            'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
            'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
            'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
            'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
            '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
            '9': '----.', ' ': ' '
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
        
        return pattern
    
    @staticmethod
    def encode_geometric(pattern_type: str, size: int = 10) -> List[bool]:
        """
        Encode geometric pattern.
        
        Args:
            pattern_type: Type of pattern ('square', 'circle', 'triangle', 'spiral')
            size: Pattern size (number of elements)
            
        Returns:
            List of booleans representing pattern
        """
        pattern = []
        
        if pattern_type == 'square':
            # Square pattern: on-off-on-off...
            for i in range(size):
                pattern.append(i % 2 == 0)
        
        elif pattern_type == 'circle':
            # Circular pattern: gradual on-off
            for i in range(size):
                # Simulate circular pattern with sine wave
                if NUMPY_AVAILABLE:
                    value = np.sin(2 * np.pi * i / size)
                else:
                    import math
                    value = math.sin(2 * math.pi * i / size)
                pattern.append(value > 0)
        
        elif pattern_type == 'triangle':
            # Triangle pattern: increasing then decreasing
            for i in range(size):
                mid = size // 2
                pattern.append(i < mid)
        
        elif pattern_type == 'spiral':
            # Spiral pattern: expanding square
            side_length = int(np.sqrt(size))
            for i in range(size):
                row = i // side_length
                col = i % side_length
                # Create spiral effect
                pattern.append((row + col) % 2 == 0)
        
        else:
            # Default: simple alternating pattern
            pattern = [i % 2 == 0 for i in range(size)]
        
        return pattern


class SignalFilter:
    """Signal filtering utilities."""
    
    @staticmethod
    def moving_average(data: List[float], window_size: int = 10) -> List[float]:
        """
        Apply moving average filter.
        
        Args:
            data: Input data
            window_size: Size of moving average window
            
        Returns:
            Filtered data
        """
        if len(data) < window_size:
            return data
        
        filtered = []
        for i in range(len(data)):
            start = max(0, i - window_size // 2)
            end = min(len(data), i + window_size // 2 + 1)
            window = data[start:end]
            if NUMPY_AVAILABLE:
                filtered.append(float(np.mean(window)))
            else:
                filtered.append(sum(window) / len(window))
        
        return filtered
    
    @staticmethod
    def low_pass_filter(data: List[float], cutoff: float = 0.1) -> List[float]:
        """
        Apply simple low-pass filter.
        
        Args:
            data: Input data
            cutoff: Cutoff frequency (normalized)
            
        Returns:
            Filtered data
        """
        if len(data) < 2:
            return data
        
        filtered = [data[0]]
        alpha = cutoff
        
        for i in range(1, len(data)):
            filtered.append(alpha * data[i] + (1 - alpha) * filtered[i-1])
        
        return filtered
    
    @staticmethod
    def remove_outliers(data: List[float], threshold: float = 3.0) -> List[float]:
        """
        Remove outliers using standard deviation.
        
        Args:
            data: Input data
            threshold: Number of standard deviations
            
        Returns:
            Data with outliers removed
        """
        if len(data) < 3:
            return data
        
        if NUMPY_AVAILABLE:
            mean = float(np.mean(data))
            std = float(np.std(data))
        else:
            # Manual calculation
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / len(data)
            std = variance ** 0.5
        
        filtered = [x for x in data if abs(x - mean) < threshold * std]
        
        # If too many outliers, return original
        if len(filtered) < len(data) * 0.5:
            return data
        
        return filtered


class DataLogger:
    """Data logging utility."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize data logger.
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.current_log_file = None
    
    def start_session(self, session_name: Optional[str] = None):
        """
        Start a new logging session.
        
        Args:
            session_name: Optional session name (uses timestamp if None)
        """
        if session_name is None:
            session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.current_log_file = self.log_dir / f"session_{session_name}.csv"
        
        # Create CSV file with headers
        with open(self.current_log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'wavelength_nm', 'voltage_v', 'laser_state', 'pattern_sent'])
        
        logging.info(f"Started logging session: {self.current_log_file}")
    
    def log_measurement(self, wavelength: Optional[float], voltage: float,
                       laser_state: str, pattern_sent: Optional[str] = None):
        """
        Log a measurement.
        
        Args:
            wavelength: Wavelength in nanometers
            voltage: Voltage in volts
            laser_state: Current laser state
            pattern_sent: Pattern that was sent (if any)
        """
        if self.current_log_file is None:
            self.start_session()
        
        timestamp = datetime.now().isoformat()
        
        with open(self.current_log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                wavelength if wavelength else '',
                voltage,
                laser_state,
                pattern_sent if pattern_sent else ''
            ])
    
    def log_event(self, event_type: str, description: str, data: Optional[Dict] = None):
        """
        Log an event.
        
        Args:
            event_type: Type of event
            description: Event description
            data: Optional event data
        """
        event_file = self.log_dir / "events.jsonl"
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'description': description,
            'data': data or {}
        }
        
        with open(event_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        logging.info(f"Event logged: {event_type} - {description}")
    
    def get_recent_measurements(self, count: int = 100) -> List[Dict]:
        """
        Get recent measurements.
        
        Args:
            count: Number of measurements to retrieve
            
        Returns:
            List of measurement dictionaries
        """
        if self.current_log_file is None or not self.current_log_file.exists():
            return []
        
        measurements = []
        with open(self.current_log_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            for row in rows[-count:]:
                measurements.append({
                    'timestamp': row['timestamp'],
                    'wavelength': float(row['wavelength_nm']) if row['wavelength_nm'] else None,
                    'voltage': float(row['voltage_v']),
                    'laser_state': row['laser_state'],
                    'pattern_sent': row['pattern_sent'] if row['pattern_sent'] else None
                })
        
        return measurements


class SignalProcessor:
    """Main signal processor class."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize signal processor.
        
        Args:
            log_dir: Directory for log files
        """
        self.encoder = PatternEncoder()
        self.filter = SignalFilter()
        self.logger = DataLogger(log_dir)
        
        self.measurement_history = []
        self.max_history = 1000
    
    def encode_message(self, message: str, encoding: str = 'morse') -> List[bool]:
        """
        Encode a message using specified encoding.
        
        Args:
            message: Message to encode
            encoding: Encoding type ('morse', 'binary', 'geometric')
            
        Returns:
            Encoded pattern as list of booleans
        """
        if encoding == 'morse':
            return self.encoder.encode_morse(message)
        elif encoding == 'binary':
            return self.encoder.encode_binary(message)
        elif encoding == 'geometric':
            return self.encoder.encode_geometric(message)
        else:
            logging.warning(f"Unknown encoding: {encoding}, using Morse")
            return self.encoder.encode_morse(message)
    
    def filter_signal(self, data: List[float], filter_type: str = 'moving_average',
                     **kwargs) -> List[float]:
        """
        Filter signal data.
        
        Args:
            data: Input data
            filter_type: Type of filter ('moving_average', 'low_pass', 'remove_outliers')
            **kwargs: Filter parameters
            
        Returns:
            Filtered data
        """
        if filter_type == 'moving_average':
            window_size = kwargs.get('window_size', 10)
            return self.filter.moving_average(data, window_size)
        elif filter_type == 'low_pass':
            cutoff = kwargs.get('cutoff', 0.1)
            return self.filter.low_pass_filter(data, cutoff)
        elif filter_type == 'remove_outliers':
            threshold = kwargs.get('threshold', 3.0)
            return self.filter.remove_outliers(data, threshold)
        else:
            logging.warning(f"Unknown filter type: {filter_type}")
            return data
    
    def add_measurement(self, wavelength: Optional[float], voltage: float,
                       laser_state: str, pattern_sent: Optional[str] = None):
        """
        Add a measurement to history and log it.
        
        Args:
            wavelength: Wavelength in nanometers
            voltage: Voltage in volts
            laser_state: Current laser state
            pattern_sent: Pattern that was sent (if any)
        """
        measurement = {
            'timestamp': time.time(),
            'wavelength': wavelength,
            'voltage': voltage,
            'laser_state': laser_state,
            'pattern_sent': pattern_sent
        }
        
        self.measurement_history.append(measurement)
        
        # Keep only recent measurements
        if len(self.measurement_history) > self.max_history:
            self.measurement_history = self.measurement_history[-self.max_history:]
        
        # Log measurement
        self.logger.log_measurement(wavelength, voltage, laser_state, pattern_sent)
    
    def get_wavelength_history(self, count: Optional[int] = None) -> List[float]:
        """
        Get wavelength history.
        
        Args:
            count: Number of measurements to return (None = all)
            
        Returns:
            List of wavelengths
        """
        history = self.measurement_history[-count:] if count else self.measurement_history
        return [m['wavelength'] for m in history if m['wavelength'] is not None]
    
    def get_voltage_history(self, count: Optional[int] = None) -> List[float]:
        """
        Get voltage history.
        
        Args:
            count: Number of measurements to return (None = all)
            
        Returns:
            List of voltages
        """
        history = self.measurement_history[-count:] if count else self.measurement_history
        return [m['voltage'] for m in history]
    
    def start_logging_session(self, session_name: Optional[str] = None):
        """Start a new logging session."""
        self.logger.start_session(session_name)
    
    def log_event(self, event_type: str, description: str, data: Optional[Dict] = None):
        """Log an event."""
        self.logger.log_event(event_type, description, data)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    processor = SignalProcessor()
    
    # Encode messages
    morse_pattern = processor.encode_message("SOS", "morse")
    print(f"Morse pattern length: {len(morse_pattern)}")
    
    binary_pattern = processor.encode_message("HI", "binary")
    print(f"Binary pattern length: {len(binary_pattern)}")
    
    # Filter data
    test_data = [1.0, 1.1, 1.2, 5.0, 1.3, 1.4, 1.5]  # With outlier
    filtered = processor.filter_signal(test_data, 'remove_outliers')
    print(f"Filtered data: {filtered}")
    
    # Log measurements
    processor.start_logging_session("test")
    processor.add_measurement(650.0, 1.5, "on", "SOS")
    processor.add_measurement(532.0, 1.2, "off", None)

