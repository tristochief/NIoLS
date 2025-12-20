"""
Communication Interface GUI

Streamlit-based GUI for EUV detection and laser communication device.
"""

import streamlit as st
import time
import yaml
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from hardware_control.photodiode_reader import PhotodiodeReader
from hardware_control.laser_controller import LaserController, LaserState
from hardware_control.signal_processor import SignalProcessor
from hardware_control.system_health import SystemHealthMonitor, HealthStatus, validate_config

# Page configuration
st.set_page_config(
    page_title="EUV Detection & Laser Communication",
    page_icon="🔭",
    layout="wide"
)

# Initialize session state
if 'photodiode_reader' not in st.session_state:
    st.session_state.photodiode_reader = None
if 'laser_controller' not in st.session_state:
    st.session_state.laser_controller = None
if 'signal_processor' not in st.session_state:
    st.session_state.signal_processor = None
if 'measurement_running' not in st.session_state:
    st.session_state.measurement_running = False
if 'last_measurement' not in st.session_state:
    st.session_state.last_measurement = {'wavelength': None, 'voltage': 0.0}
if 'health_monitor' not in st.session_state:
    st.session_state.health_monitor = SystemHealthMonitor()
if 'last_health_check' not in st.session_state:
    st.session_state.last_health_check = None

# Load configuration
@st.cache_data
def load_config():
    """Load device configuration."""
    config_path = Path(__file__).parent.parent / "config" / "device_config.yaml"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate configuration
            is_valid, errors = validate_config(str(config_path))
            if not is_valid:
                st.warning("Configuration validation errors:")
                for error in errors:
                    st.warning(f"  - {error}")
            
            return config
        except Exception as e:
            st.error(f"Failed to load configuration: {e}")
            return {}
    else:
        st.warning("Configuration file not found. Using defaults.")
        return {}

config = load_config()

# Initialize hardware (with error handling)
def initialize_hardware():
    """Initialize hardware components."""
    try:
        if st.session_state.photodiode_reader is None:
            photodiode_config = config.get('hardware', {}).get('photodiode', {})
            st.session_state.photodiode_reader = PhotodiodeReader(
                i2c_address=photodiode_config.get('i2c_address', 0x48),
                adc_channel=photodiode_config.get('adc_channel', 0),
                gain=photodiode_config.get('gain', 1),
                sample_rate=photodiode_config.get('sample_rate', 250)
            )
        
        if st.session_state.laser_controller is None:
            laser_config = config.get('hardware', {}).get('laser', {})
            st.session_state.laser_controller = LaserController(
                laser_pin=laser_config.get('laser_pin', 18),
                interlock_pin=laser_config.get('interlock_pin', 23),
                pwm_frequency=laser_config.get('pwm_frequency', 1000),
                pulse_duration=laser_config.get('pulse_duration', 0.001)
            )
        
        if st.session_state.signal_processor is None:
            log_dir = config.get('logging', {}).get('log_dir', 'logs')
            st.session_state.signal_processor = SignalProcessor(log_dir=log_dir)
            if config.get('logging', {}).get('auto_start_session', True):
                st.session_state.signal_processor.start_logging_session()
        
        return True
    except Exception as e:
        st.error(f"Failed to initialize hardware: {e}")
        return False

# Main interface
st.title("🔭 EUV Detection & Laser Communication Device")

# Sidebar for controls
with st.sidebar:
    st.header("System Status")
    
    # Initialize hardware button
    if st.button("Initialize Hardware"):
        if initialize_hardware():
            st.success("Hardware initialized")
        else:
            st.error("Hardware initialization failed")
    
    # Hardware status
    if st.session_state.photodiode_reader:
        photodiode_status = "✅ Connected" if st.session_state.photodiode_reader.is_connected() else "⚠️ Simulation Mode"
        st.write(f"**Photodiode:** {photodiode_status}")
    else:
        st.write("**Photodiode:** ❌ Not Initialized")
    
    if st.session_state.laser_controller:
        laser_status = "✅ Connected" if st.session_state.laser_controller.is_connected() else "⚠️ Simulation Mode"
        st.write(f"**Laser:** {laser_status}")
        
        # Interlock status
        if st.session_state.laser_controller.is_interlock_safe():
            st.success("🔒 Interlock: SAFE")
        else:
            st.error("🔓 Interlock: UNSAFE")
    else:
        st.write("**Laser:** ❌ Not Initialized")
    
    st.divider()
    
    # Health monitoring
    st.divider()
    st.subheader("System Health")
    
    if st.button("Run Health Check", use_container_width=True):
        with st.spinner("Running health checks..."):
            checks = st.session_state.health_monitor.run_all_checks(
                st.session_state.photodiode_reader,
                st.session_state.laser_controller,
                config.get('logging', {}).get('log_dir', 'logs')
            )
            st.session_state.last_health_check = checks
    
    if st.session_state.last_health_check:
        overall_status, overall_message = st.session_state.health_monitor.get_overall_status()
        
        # Display overall status
        if overall_status == HealthStatus.HEALTHY:
            st.success(f"✓ {overall_message}")
        elif overall_status == HealthStatus.WARNING:
            st.warning(f"⚠ {overall_message}")
        elif overall_status == HealthStatus.ERROR:
            st.error(f"✗ {overall_message}")
        else:  # CRITICAL
            st.error(f"🚨 CRITICAL: {overall_message}")
        
        # Show individual checks
        with st.expander("Detailed Health Checks"):
            for check in st.session_state.last_health_check:
                status_icon = {
                    HealthStatus.HEALTHY: "✓",
                    HealthStatus.WARNING: "⚠",
                    HealthStatus.ERROR: "✗",
                    HealthStatus.CRITICAL: "🚨"
                }.get(check.status, "?")
                
                st.write(f"{status_icon} **{check.name}**: {check.message}")
                if check.details:
                    st.json(check.details)
    
    st.divider()
    
    # Safety warnings
    st.warning("⚠️ **Safety Reminders:**")
    st.write("- Never point laser at people or aircraft")
    st.write("- Ensure interlock is engaged before operation")
    st.write("- Class 1M laser: ≤1 mW output")
    st.write("- Follow all safety protocols")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Wavelength Measurement")
    
    # Measurement controls
    col1a, col1b, col1c = st.columns(3)
    with col1a:
        if st.button("Start Measurement", disabled=st.session_state.measurement_running):
            st.session_state.measurement_running = True
            st.rerun()
    
    with col1b:
        if st.button("Stop Measurement", disabled=not st.session_state.measurement_running):
            st.session_state.measurement_running = False
            st.rerun()
    
    with col1c:
        if st.button("Calibrate Dark"):
            if st.session_state.photodiode_reader:
                dark_voltage = st.session_state.photodiode_reader.measure_dark_voltage()
                st.success(f"Dark voltage: {dark_voltage:.4f} V")
    
    # Current measurement display
    if st.session_state.photodiode_reader and st.session_state.measurement_running:
        try:
            wavelength = st.session_state.photodiode_reader.get_wavelength()
            voltage = st.session_state.photodiode_reader.get_voltage()
            
            st.session_state.last_measurement = {
                'wavelength': wavelength,
                'voltage': voltage
            }
            
            # Update processor
            laser_state = "off"
            if st.session_state.laser_controller:
                laser_state = st.session_state.laser_controller.get_state().value
            
            st.session_state.signal_processor.add_measurement(
                wavelength, voltage, laser_state
            )
        except Exception as e:
            st.error(f"Measurement error: {e}")
            st.session_state.measurement_running = False
    
    # Display current values
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        wavelength_val = st.session_state.last_measurement.get('wavelength')
        if wavelength_val:
            st.metric("Wavelength", f"{wavelength_val:.2f} nm")
        else:
            st.metric("Wavelength", "N/A")
    
    with metric_col2:
        voltage_val = st.session_state.last_measurement.get('voltage', 0.0)
        st.metric("Voltage", f"{voltage_val:.4f} V")
    
    # Measurement history plot
    if st.session_state.signal_processor:
        history_length = config.get('preferences', {}).get('history_length', 100)
        wavelengths = st.session_state.signal_processor.get_wavelength_history(history_length)
        voltages = st.session_state.signal_processor.get_voltage_history(history_length)
        
        if wavelengths:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=wavelengths,
                mode='lines+markers',
                name='Wavelength (nm)',
                line=dict(color='blue')
            ))
            fig.update_layout(
                title="Wavelength History",
                xaxis_title="Measurement",
                yaxis_title="Wavelength (nm)",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        
        if voltages:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                y=voltages,
                mode='lines+markers',
                name='Voltage (V)',
                line=dict(color='green')
            ))
            fig2.update_layout(
                title="Voltage History",
                xaxis_title="Measurement",
                yaxis_title="Voltage (V)",
                height=300
            )
            st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.header("Laser Control")
    
    if not st.session_state.laser_controller:
        st.warning("Laser controller not initialized")
    else:
        # Interlock check
        if not st.session_state.laser_controller.is_interlock_safe():
            st.error("⚠️ Safety interlock is not engaged!")
            st.stop()
        
        # Laser state
        laser_state = st.session_state.laser_controller.get_state()
        st.write(f"**Laser State:** {laser_state.value.upper()}")
        
        # Control buttons
        col2a, col2b = st.columns(2)
        with col2a:
            if st.button("Enable Laser"):
                if st.session_state.laser_controller.enable():
                    st.success("Laser enabled")
                else:
                    st.error("Failed to enable laser")
        
        with col2b:
            if st.button("Disable Laser"):
                st.session_state.laser_controller.disable()
                st.info("Laser disabled")
        
        if st.button("Emergency Stop", type="primary"):
            st.session_state.laser_controller.emergency_stop()
            st.error("EMERGENCY STOP ACTIVATED")
        
        st.divider()
        
        # Pattern transmission
        st.subheader("Send Pattern")
        
        pattern_type = st.selectbox(
            "Pattern Type",
            ["morse", "binary", "geometric"],
            index=0
        )
        
        if pattern_type == "morse" or pattern_type == "binary":
            message = st.text_input("Message", value="SOS")
            
            if st.button("Send Message"):
                if st.session_state.laser_controller and st.session_state.signal_processor:
                    pattern = st.session_state.signal_processor.encode_message(message, pattern_type)
                    pulse_dur = config.get('signal_processing', {}).get('encoding', {}).get('pulse_duration', 0.1)
                    gap_dur = config.get('signal_processing', {}).get('encoding', {}).get('gap_duration', 0.1)
                    
                    if st.session_state.laser_controller.send_pattern(pattern, pulse_dur, gap_dur):
                        st.success(f"Message '{message}' sent")
                        st.session_state.signal_processor.log_event(
                            "pattern_sent",
                            f"Sent {pattern_type} pattern: {message}"
                        )
                    else:
                        st.error("Failed to send pattern")
        
        elif pattern_type == "geometric":
            geom_type = st.selectbox(
                "Geometric Pattern",
                ["square", "circle", "triangle", "spiral"]
            )
            size = st.slider("Pattern Size", 5, 50, 10)
            
            if st.button("Send Geometric Pattern"):
                if st.session_state.laser_controller and st.session_state.signal_processor:
                    pattern = st.session_state.signal_processor.encode_message(
                        geom_type, "geometric"
                    )
                    # Adjust pattern size
                    pattern = pattern[:size] if len(pattern) >= size else pattern
                    
                    pulse_dur = config.get('signal_processing', {}).get('encoding', {}).get('pulse_duration', 0.1)
                    gap_dur = config.get('signal_processing', {}).get('encoding', {}).get('gap_duration', 0.1)
                    
                    if st.session_state.laser_controller.send_pattern(pattern, pulse_dur, gap_dur):
                        st.success(f"Geometric pattern '{geom_type}' sent")
                    else:
                        st.error("Failed to send pattern")
        
        # Single pulse
        st.divider()
        st.subheader("Single Pulse")
        pulse_duration = st.slider("Pulse Duration (s)", 0.001, 1.0, 0.1, 0.001)
        
        if st.button("Send Pulse"):
            if st.session_state.laser_controller:
                if st.session_state.laser_controller.pulse(pulse_duration):
                    st.success(f"Pulse sent ({pulse_duration*1000:.1f} ms)")
                else:
                    st.error("Failed to send pulse")

# Auto-refresh for measurements
if st.session_state.measurement_running:
    time.sleep(config.get('preferences', {}).get('update_rate', 1.0))
    st.rerun()

# Footer
st.divider()
st.caption("EUV Detection & Laser Communication Device v1.0 | Class 1M Laser | Australian Compliant")

