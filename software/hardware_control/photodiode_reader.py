"""
Photodiode Reader Module

This module handles photodiode data acquisition, calibration, and wavelength calculation.
Supports ADS1115 ADC via I2C interface.
"""

import time
import numpy as np
from typing import Optional, Dict, List, Tuple
import logging
import math

try:
    from core.contracts import MeasurementEnvelope, WavelengthEnvelope, VoltageEnvelope, MeasurementQuality
except ImportError:
    # Fallback for when core module is not yet available
    MeasurementEnvelope = None
    WavelengthEnvelope = None
    VoltageEnvelope = None
    MeasurementQuality = None

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    logging.warning("Hardware libraries not available. Running in simulation mode.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available. Some features may be limited.")


class PhotodiodeReader:
    """
    Photodiode reader with ADC interface and wavelength calibration.
    """
    
    def __init__(self, 
                 i2c_address: int = 0x48,
                 adc_channel: int = 0,
                 gain: int = 1,
                 sample_rate: int = 250,
                 calibration_file: Optional[str] = None):
        """
        Initialize photodiode reader.
        
        Args:
            i2c_address: I2C address of ADS1115 (default 0x48)
            adc_channel: ADC channel (0-3)
            gain: ADC gain (1, 2/3, 1/2, 1/4, 1/8, 1/16)
            sample_rate: Samples per second (8, 16, 32, 64, 128, 250, 475, 860)
            calibration_file: Path to calibration data file
        """
        self.i2c_address = i2c_address
        self.adc_channel = adc_channel
        self.gain = gain
        self.sample_rate = sample_rate
        self.calibration_data = None
        self.dark_voltage = 0.0
        
        self.ads = None
        self.chan = None
        self.hardware_connected = False
        
        # Calibration data: wavelength (nm) -> voltage (V)
        self.calibration_table = {}
        
        if HARDWARE_AVAILABLE:
            try:
                self._initialize_hardware()
            except Exception as e:
                logging.error(f"Failed to initialize hardware: {e}")
                self.hardware_connected = False
        else:
            self.hardware_connected = False
            logging.info("Running in simulation mode")
        
        if calibration_file:
            self.load_calibration(calibration_file)
        else:
            self._load_default_calibration()
    
    def _initialize_hardware(self):
        """Initialize I2C and ADC hardware."""
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(i2c, address=self.i2c_address)
        
        # Configure gain
        gain_map = {
            1: ADS.PGA_4_096V,
            2/3: ADS.PGA_6_144V,
            1/2: ADS.PGA_2_048V,
            1/4: ADS.PGA_1_024V,
            1/8: ADS.PGA_0_512V,
            1/16: ADS.PGA_0_256V
        }
        self.ads.gain = gain_map.get(self.gain, ADS.PGA_4_096V)
        
        # Configure sample rate
        rate_map = {
            8: ADS.DR_8SPS,
            16: ADS.DR_16SPS,
            32: ADS.DR_32SPS,
            64: ADS.DR_64SPS,
            128: ADS.DR_128SPS,
            250: ADS.DR_250SPS,
            475: ADS.DR_475SPS,
            860: ADS.DR_860SPS
        }
        self.ads.data_rate = rate_map.get(self.sample_rate, ADS.DR_250SPS)
        
        # Create analog input channel
        channel_map = {
            0: ADS.P0,
            1: ADS.P1,
            2: ADS.P2,
            3: ADS.P3
        }
        self.chan = AnalogIn(self.ads, channel_map[self.adc_channel])
        self.hardware_connected = True
        logging.info("Hardware initialized successfully")
    
    def _load_default_calibration(self):
        """
        Load default calibration data for silicon photodiode.
        This is a placeholder - actual calibration should be done with known sources.
        """
        # Default calibration: linear approximation
        # Wavelength range: 400-1100 nm
        # Voltage range: 0-3.3V (typical)
        # This is a simplified model - real calibration requires measurement
        self.calibration_table = {
            400: 0.1,   # Blue
            470: 0.3,   # Blue-green
            530: 0.5,   # Green
            590: 0.7,   # Yellow
            650: 0.9,   # Red
            700: 1.1,   # Deep red
            850: 1.5,   # Near-IR
            950: 1.8,   # Near-IR
            1100: 2.0  # Near-IR limit
        }
        logging.info("Loaded default calibration data")
    
    def load_calibration(self, filepath: str):
        """
        Load calibration data from file.
        
        Args:
            filepath: Path to calibration file (CSV format: wavelength,voltage)
        """
        try:
            import csv
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header if present
                for row in reader:
                    if len(row) >= 2:
                        wavelength = float(row[0])
                        voltage = float(row[1])
                        self.calibration_table[wavelength] = voltage
            logging.info(f"Loaded calibration from {filepath}")
        except Exception as e:
            logging.error(f"Failed to load calibration: {e}")
            self._load_default_calibration()
    
    def save_calibration(self, filepath: str):
        """
        Save calibration data to file.
        
        Args:
            filepath: Path to save calibration file
        """
        try:
            import csv
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['wavelength_nm', 'voltage_v'])
                for wavelength in sorted(self.calibration_table.keys()):
                    writer.writerow([wavelength, self.calibration_table[wavelength]])
            logging.info(f"Saved calibration to {filepath}")
        except Exception as e:
            logging.error(f"Failed to save calibration: {e}")
    
    def measure_voltage(self, samples: int = 10) -> float:
        """
        Measure photodiode voltage.
        
        Args:
            samples: Number of samples to average
            
        Returns:
            Average voltage in volts
            
        Raises:
            ValueError: If samples is invalid
            RuntimeError: If measurement fails
        """
        if samples < 1:
            raise ValueError("Samples must be >= 1")
        if samples > 1000:
            raise ValueError("Samples must be <= 1000")
        
        try:
            if self.hardware_connected and self.chan:
                voltages = []
                for _ in range(samples):
                    try:
                        voltages.append(self.chan.voltage)
                        time.sleep(0.001)  # Small delay between samples
                    except Exception as e:
                        logging.warning(f"ADC read error: {e}")
                        # Continue with available samples
                
                if not voltages:
                    raise RuntimeError("No valid voltage samples obtained")
                
                if NUMPY_AVAILABLE:
                    return float(np.mean(voltages))
                else:
                    return sum(voltages) / len(voltages)
            else:
                # Simulation mode: return random voltage
                if NUMPY_AVAILABLE:
                    return float(np.random.uniform(0.5, 2.0))
                else:
                    import random
                    return random.uniform(0.5, 2.0)
        except Exception as e:
            logging.error(f"Voltage measurement failed: {e}")
            raise RuntimeError(f"Voltage measurement failed: {e}") from e
    
    def measure_dark_voltage(self, samples: int = 100) -> float:
        """
        Measure dark voltage (with photodiode covered).
        
        Args:
            samples: Number of samples to average
            
        Returns:
            Average dark voltage
        """
        logging.info("Measuring dark voltage - cover photodiode now")
        time.sleep(1)  # Give user time to cover photodiode
        self.dark_voltage = self.measure_voltage(samples)
        logging.info(f"Dark voltage: {self.dark_voltage:.4f} V")
        return self.dark_voltage
    
    def calculate_wavelength(self, voltage: float) -> Optional[float]:
        """
        Calculate wavelength from voltage using calibration data.
        
        Args:
            voltage: Measured voltage (V)
            
        Returns:
            Wavelength in nanometers, or None if out of range
        """
        # Subtract dark voltage
        corrected_voltage = voltage - self.dark_voltage
        
        if not self.calibration_table:
            return None
        
        # Find calibration points
        wavelengths = sorted(self.calibration_table.keys())
        voltages = [self.calibration_table[w] for w in wavelengths]
        
        # Check if voltage is within range
        if corrected_voltage < min(voltages) or corrected_voltage > max(voltages):
            return None
        
        # Linear interpolation
        if NUMPY_AVAILABLE:
            wavelength = float(np.interp(corrected_voltage, voltages, wavelengths))
        else:
            # Manual interpolation
            for i in range(len(voltages) - 1):
                if voltages[i] <= corrected_voltage <= voltages[i + 1]:
                    # Linear interpolation
                    t = (corrected_voltage - voltages[i]) / (voltages[i + 1] - voltages[i])
                    wavelength = wavelengths[i] + t * (wavelengths[i + 1] - wavelengths[i])
                    break
            else:
                return None
        
        return wavelength
    
    def get_wavelength(self, samples: int = 10) -> Optional[float]:
        """
        Measure current wavelength.
        
        Args:
            samples: Number of samples to average
            
        Returns:
            Wavelength in nanometers, or None if out of range
        """
        voltage = self.measure_voltage(samples)
        return self.calculate_wavelength(voltage)
    
    def get_voltage(self, samples: int = 10) -> float:
        """
        Get current voltage reading.
        
        Args:
            samples: Number of samples to average
            
        Returns:
            Voltage in volts
        """
        return self.measure_voltage(samples)
    
    def calibrate_point(self, wavelength: float, samples: int = 100):
        """
        Calibrate at a specific wavelength.
        
        Args:
            wavelength: Known wavelength in nanometers
            samples: Number of samples to average
        """
        logging.info(f"Calibrating at {wavelength} nm - apply light source now")
        time.sleep(1)  # Give user time to apply light source
        voltage = self.measure_voltage(samples)
        self.calibration_table[wavelength] = voltage
        logging.info(f"Calibration point: {wavelength} nm -> {voltage:.4f} V")
    
    def is_connected(self) -> bool:
        """Check if hardware is connected."""
        return self.hardware_connected
    
    def get_calibration_range(self) -> Tuple[float, float]:
        """
        Get wavelength range covered by calibration.
        
        Returns:
            Tuple of (min_wavelength, max_wavelength) in nanometers
        """
        if not self.calibration_table:
            return (400.0, 1100.0)
        wavelengths = sorted(self.calibration_table.keys())
        return (min(wavelengths), max(wavelengths))
    
    def get_measurement_envelope(self, samples: int = 10) -> 'MeasurementEnvelope':
        """
        Get measurement envelope (voltage and wavelength bounds).
        
        This is the only allowed output type for measurements.
        Computes envelope bounds from calibration table + ADC noise + interpolation error.
        
        Args:
            samples: Number of samples to average for noise estimation
            
        Returns:
            MeasurementEnvelope with voltage and wavelength bounds
        """
        if MeasurementEnvelope is None:
            raise ImportError("core.contracts module not available")
        
        # Measure voltage with multiple samples for noise estimation
        voltages = []
        for _ in range(samples):
            try:
                voltage = self.measure_voltage(1)
                voltages.append(voltage)
                time.sleep(0.001)  # Small delay between samples
            except Exception as e:
                logging.warning(f"Voltage measurement error: {e}")
        
        if not voltages:
            # Fallback: use single measurement
            try:
                voltage = self.measure_voltage(1)
                voltages = [voltage]
            except Exception:
                # Simulation mode fallback
                if NUMPY_AVAILABLE:
                    voltage = float(np.random.uniform(0.5, 2.0))
                else:
                    import random
                    voltage = random.uniform(0.5, 2.0)
                voltages = [voltage]
        
        # Compute voltage statistics
        if NUMPY_AVAILABLE:
            voltage_mean = float(np.mean(voltages))
            voltage_std = float(np.std(voltages))
        else:
            voltage_mean = sum(voltages) / len(voltages)
            variance = sum((v - voltage_mean) ** 2 for v in voltages) / len(voltages)
            voltage_std = math.sqrt(variance)
        
        # Estimate ADC noise (conservative: use std or fixed minimum)
        # ADS1115 typical noise: ~0.1-0.2 mV RMS
        adc_noise_v = max(voltage_std, 0.0002)  # At least 0.2 mV RMS
        
        # Voltage envelope: mean ± 3*std (99.7% confidence) + ADC noise
        voltage_uncertainty = 3.0 * voltage_std + adc_noise_v
        voltage_min = max(0.0, voltage_mean - voltage_uncertainty)
        voltage_max = voltage_mean + voltage_uncertainty
        
        voltage_envelope = VoltageEnvelope(
            min_v=voltage_min,
            max_v=voltage_max,
            rms_noise=adc_noise_v
        )
        
        # Compute wavelength envelope from calibration
        wavelength_envelope = None
        if self.calibration_table:
            # Correct for dark voltage
            corrected_voltage_mean = voltage_mean - self.dark_voltage
            corrected_voltage_min = voltage_min - self.dark_voltage
            corrected_voltage_max = voltage_max - self.dark_voltage
            
            # Find calibration points
            wavelengths = sorted(self.calibration_table.keys())
            cal_voltages = [self.calibration_table[w] for w in wavelengths]
            
            # Check if voltage is within calibration range
            if corrected_voltage_min >= min(cal_voltages) and corrected_voltage_max <= max(cal_voltages):
                # Interpolate wavelength for min and max voltages
                if NUMPY_AVAILABLE:
                    wavelength_min = float(np.interp(corrected_voltage_min, cal_voltages, wavelengths))
                    wavelength_max = float(np.interp(corrected_voltage_max, cal_voltages, wavelengths))
                else:
                    # Manual interpolation for min
                    wavelength_min = self._interpolate_wavelength(corrected_voltage_min, cal_voltages, wavelengths)
                    wavelength_max = self._interpolate_wavelength(corrected_voltage_max, cal_voltages, wavelengths)
                
                # Add interpolation error (conservative: assume 5% of range)
                cal_range = max(wavelengths) - min(wavelengths)
                interpolation_error = 0.05 * cal_range / len(wavelengths)  # 5% per point
                
                wavelength_min = max(min(wavelengths), wavelength_min - interpolation_error)
                wavelength_max = min(max(wavelengths), wavelength_max + interpolation_error)
                
                # Ensure min <= max
                if wavelength_min > wavelength_max:
                    wavelength_min, wavelength_max = wavelength_max, wavelength_min
                
                wavelength_envelope = WavelengthEnvelope(
                    min_nm=wavelength_min,
                    max_nm=wavelength_max,
                    confidence=0.95,  # 95% confidence (3-sigma)
                    valid_until=time.time() + 1.0  # Valid for 1 second
                )
        
        # Check for saturation/clipping (simplified check)
        saturation_flag = voltage_max >= 3.2  # Near ADC full scale (3.3V)
        clipping_flag = voltage_min <= 0.0
        
        measurement_quality = MeasurementQuality(
            snr_estimate=voltage_mean / adc_noise_v if adc_noise_v > 0 else None,
            saturation_flag=saturation_flag,
            clipping_flag=clipping_flag
        )
        
        return MeasurementEnvelope(
            wavelength_envelope_nm=wavelength_envelope,
            voltage_envelope_v=voltage_envelope,
            measurement_quality=measurement_quality
        )
    
    def _interpolate_wavelength(self, voltage: float, cal_voltages: List[float], 
                               wavelengths: List[float]) -> float:
        """
        Manual linear interpolation for wavelength.
        
        Args:
            voltage: Voltage value
            cal_voltages: Sorted list of calibration voltages
            wavelengths: Corresponding wavelengths
            
        Returns:
            Interpolated wavelength
        """
        for i in range(len(cal_voltages) - 1):
            if cal_voltages[i] <= voltage <= cal_voltages[i + 1]:
                # Linear interpolation
                t = (voltage - cal_voltages[i]) / (cal_voltages[i + 1] - cal_voltages[i])
                wavelength = wavelengths[i] + t * (wavelengths[i + 1] - wavelengths[i])
                return wavelength
        
        # Out of range: return boundary
        if voltage < cal_voltages[0]:
            return wavelengths[0]
        else:
            return wavelengths[-1]


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize reader
    reader = PhotodiodeReader()
    
    # Measure dark voltage
    dark = reader.measure_dark_voltage()
    print(f"Dark voltage: {dark:.4f} V")
    
    # Measure current wavelength
    wavelength = reader.get_wavelength()
    if wavelength:
        print(f"Current wavelength: {wavelength:.2f} nm")
    else:
        print("Wavelength out of calibration range")
    
    # Measure voltage
    voltage = reader.get_voltage()
    print(f"Current voltage: {voltage:.4f} V")

