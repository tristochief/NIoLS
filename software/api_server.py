"""
FastAPI Backend Server for EUV Detection & Laser Communication Device

Provides REST API endpoints for hardware control and data access.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Optional, Dict, List
import sys

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yaml

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from hardware_control.photodiode_reader import PhotodiodeReader
from hardware_control.laser_controller import LaserController, LaserState
from hardware_control.signal_processor import SignalProcessor
from hardware_control.system_health import SystemHealthMonitor, HealthStatus, validate_config

# Import core modules
try:
    from core import (
        SessionContext, FSMState, FSM, FSMEvent, FSMError,
        TraceWriter, EventType, SessionBundle,
        load_config_and_hash, load_calibration_and_hash,
        detect_config_drift, detect_calibration_drift,
        MeasurementEnvelope, EmitEnvelope, BudgetEnvelope, SessionStatusEnvelope,
        PulseWidthBounds
    )
    CORE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Core modules not available: {e}")
    CORE_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EUV Detection & Laser Communication API",
    description="REST API for hardware control and data access",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global FSM-based state
class AppState:
    def __init__(self):
        self.photodiode_reader: Optional[PhotodiodeReader] = None
        self.laser_controller: Optional[LaserController] = None
        self.signal_processor: Optional[SignalProcessor] = None
        self.measurement_running: bool = False
        self.last_measurement_envelope: Optional[MeasurementEnvelope] = None
        self.health_monitor: SystemHealthMonitor = SystemHealthMonitor()
        self.last_health_check: Optional[List] = None
        self.config: Dict = {}
        self._measurement_task: Optional[asyncio.Task] = None
        
        # FSM-based state management
        self.context: Optional[SessionContext] = None
        self.fsm: Optional[FSM] = None
        self.trace_writer: Optional[TraceWriter] = None
        self.session_bundle: Optional[SessionBundle] = None

app_state = AppState()

# Trace writer callback for FSM transitions
def trace_transition_callback(transition_info: Dict[str, Any]):
    """Callback for FSM transitions to write trace records."""
    if app_state.trace_writer and CORE_AVAILABLE:
        try:
            event_type = EventType.STATE_TRANSITION
            if transition_info.get('fault_reason'):
                event_type = EventType.FAULT
            
            app_state.trace_writer.write_record(
                event_type=event_type,
                state_from=transition_info.get('from_state'),
                state_to=transition_info.get('to_state'),
                predicates=transition_info.get('predicates'),
                event_data=transition_info.get('event_data'),
                config_hash=app_state.context.config_hash if app_state.context else None,
                cal_hash=app_state.context.cal_hash if app_state.context else None
            )
        except Exception as e:
            logger.error(f"Trace write error: {e}")

# Load configuration
def load_config() -> Dict:
    """Load device configuration."""
    config_path = Path(__file__).parent / "config" / "device_config.yaml"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate configuration
            is_valid, errors = validate_config(str(config_path))
            if not is_valid:
                logger.warning(f"Configuration validation errors: {errors}")
            
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}
    else:
        logger.warning("Configuration file not found. Using defaults.")
        return {}

app_state.config = load_config()

# Pydantic models for request/response
class InitializeRequest(BaseModel):
    pass

class MeasurementControl(BaseModel):
    running: bool

class LaserControl(BaseModel):
    action: str  # "enable", "disable", "emergency_stop"

class PulseRequest(BaseModel):
    duration: float

class PatternRequest(BaseModel):
    pattern_type: str  # "morse", "binary", "geometric"
    message: Optional[str] = None
    geometric_type: Optional[str] = None
    size: Optional[int] = None

class HealthCheckResponse(BaseModel):
    overall_status: str
    overall_message: str
    checks: List[Dict]

class StatusResponse(BaseModel):
    photodiode: Dict
    laser: Dict
    measurement: Dict

# Background task for continuous measurements
async def measurement_loop():
    """Background task for continuous measurements."""
    while app_state.measurement_running:
        try:
            if app_state.photodiode_reader:
                wavelength = app_state.photodiode_reader.get_wavelength()
                voltage = app_state.photodiode_reader.get_voltage()
                
                app_state.last_measurement = {
                    'wavelength': wavelength,
                    'voltage': voltage
                }
                
                # Update processor
                laser_state = "off"
                if app_state.laser_controller:
                    laser_state = app_state.laser_controller.get_state().value
                
                if app_state.signal_processor:
                    app_state.signal_processor.add_measurement(
                        wavelength, voltage, laser_state
                    )
            
            update_rate = app_state.config.get('preferences', {}).get('update_rate', 1.0)
            await asyncio.sleep(update_rate)
        except Exception as e:
            logger.error(f"Measurement error: {e}")
            app_state.measurement_running = False
            break

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "EUV Detection & Laser Communication API",
        "version": "1.0.0"
    }

@app.get("/api/config")
async def get_config():
    """Get device configuration."""
    return app_state.config

@app.post("/api/initialize")
async def initialize_hardware():
    """
    Initialize hardware and transition to INITIALIZED state.
    
    This endpoint triggers SAFE→INITIALIZED transition:
    - Loads config and calibration
    - Computes and binds hashes
    - Initializes hardware components
    - Sets up FSM and trace writer
    """
    if not CORE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Core modules not available")
    
    try:
        # Initialize hardware components first
        if app_state.photodiode_reader is None:
            photodiode_config = app_state.config.get('hardware', {}).get('photodiode', {})
            app_state.photodiode_reader = PhotodiodeReader(
                i2c_address=photodiode_config.get('i2c_address', 0x48),
                adc_channel=photodiode_config.get('adc_channel', 0),
                gain=photodiode_config.get('gain', 1),
                sample_rate=photodiode_config.get('sample_rate', 250)
            )
        
        if app_state.laser_controller is None:
            laser_config = app_state.config.get('hardware', {}).get('laser', {})
            app_state.laser_controller = LaserController(
                laser_pin=laser_config.get('laser_pin', 18),
                interlock_pin=laser_config.get('interlock_pin', 23),
                pwm_frequency=laser_config.get('pwm_frequency', 1000),
                pulse_duration=laser_config.get('pulse_duration', 0.001)
            )
        
        if app_state.signal_processor is None:
            log_dir = app_state.config.get('logging', {}).get('log_dir', 'logs')
            app_state.signal_processor = SignalProcessor(log_dir=log_dir)
            if app_state.config.get('logging', {}).get('auto_start_session', True):
                app_state.signal_processor.start_logging_session()
        
        # Initialize FSM context if not exists
        if app_state.context is None:
            config_path = Path(__file__).parent / "config" / "device_config.yaml"
            
            # Load config and compute hash
            config, config_hash = load_config_and_hash(config_path)
            
            # Load calibration and compute hash
            calibration, cal_hash = load_calibration_and_hash(app_state.photodiode_reader)
            
            # Create session context
            app_state.context = SessionContext(
                config=config,
                config_hash=config_hash,
                calibration=calibration,
                cal_hash=cal_hash,
                photodiode_reader=app_state.photodiode_reader,
                laser_controller=app_state.laser_controller,
                signal_processor=app_state.signal_processor,
                health_monitor=app_state.health_monitor,
                simulation_mode=config.get('advanced', {}).get('simulation_mode', False)
            )
            
            # Set up trace writer
            session_dir = Path(log_dir) / "sessions" / app_state.context.session_id
            trace_file = session_dir / "trace.jsonl"
            app_state.trace_writer = TraceWriter(trace_file, app_state.context.session_id)
            
            # Create FSM with trace callback
            app_state.fsm = FSM(app_state.context, trace_transition_callback)
            
            # Create session bundle
            app_state.session_bundle = SessionBundle(session_dir, app_state.context, app_state.trace_writer)
            
            # Record initial health check
            health_checks = app_state.health_monitor.run_all_checks(
                app_state.photodiode_reader,
                app_state.laser_controller,
                log_dir
            )
            health_data = {
                "overall_status": app_state.health_monitor.get_overall_status()[0].value,
                "overall_message": app_state.health_monitor.get_overall_status()[1],
                "checks": [
                    {
                        "name": c.name,
                        "status": c.status.value,
                        "message": c.message,
                        "details": c.details
                    }
                    for c in health_checks
                ],
                "timestamp": time.time()
            }
            app_state.session_bundle.set_health_start(health_data)
        
        # Transition SAFE → INITIALIZED
        if app_state.context.state != FSMState.SAFE:
            raise HTTPException(status_code=400, detail=f"Must be in SAFE state, currently {app_state.context.state.value}")
        
        success, message, transition_info = app_state.fsm.transition(FSMEvent.INITIALIZE)
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Initialization failed: {message}")
        
        return {
            "status": "success",
            "message": message,
            "state": app_state.context.state.value,
            "config_hash": app_state.context.config_hash,
            "cal_hash": app_state.context.cal_hash,
            "session_id": app_state.context.session_id
        }
    except FSMError as e:
        logger.error(f"FSM error during initialization: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to initialize hardware: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/arm")
async def arm_system():
    """
    Arm the system: transition INITIALIZED → ARMED.
    
    Requires: interlock safe, no outstanding faults, cooldown satisfied.
    """
    if not CORE_AVAILABLE or app_state.fsm is None:
        raise HTTPException(status_code=400, detail="System not initialized")
    
    try:
        if app_state.context.state != FSMState.INITIALIZED:
            raise HTTPException(status_code=400, detail=f"Must be in INITIALIZED state, currently {app_state.context.state.value}")
        
        success, message, transition_info = app_state.fsm.transition(FSMEvent.ARM)
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Arming failed: {message}")
        
        return {
            "status": "success",
            "message": message,
            "state": app_state.context.state.value
        }
    except FSMError as e:
        logger.error(f"FSM error during arming: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to arm system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/arm/confirm")
async def confirm_arm():
    """
    Confirm arm: transition ARMED → EMIT_READY.
    
    Must be called within arming window.
    """
    if not CORE_AVAILABLE or app_state.fsm is None:
        raise HTTPException(status_code=400, detail="System not initialized")
    
    try:
        if app_state.context.state != FSMState.ARMED:
            raise HTTPException(status_code=400, detail=f"Must be in ARMED state, currently {app_state.context.state.value}")
        
        success, message, transition_info = app_state.fsm.transition(FSMEvent.ARM_CONFIRM)
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Arm confirmation failed: {message}")
        
        return {
            "status": "success",
            "message": message,
            "state": app_state.context.state.value
        }
    except FSMError as e:
        logger.error(f"FSM error during arm confirmation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to confirm arm: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stop")
async def stop_system():
    """
    Stop system: transition to safer state or reset from FAULT.
    
    EMITTING → EMIT_READY
    EMIT_READY → ARMED
    ARMED → INITIALIZED
    INITIALIZED → SAFE
    FAULT → SAFE (reset)
    """
    if not CORE_AVAILABLE or app_state.fsm is None:
        raise HTTPException(status_code=400, detail="System not initialized")
    
    try:
        current_state = app_state.context.state
        
        # Determine event based on current state
        if current_state == FSMState.FAULT:
            event = FSMEvent.RESET
        else:
            event = FSMEvent.STOP
        
        success, message, transition_info = app_state.fsm.transition(event)
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Stop failed: {message}")
        
        return {
            "status": "success",
            "message": message,
            "state": app_state.context.state.value
        }
    except FSMError as e:
        logger.error(f"FSM error during stop: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to stop system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """
    Get system status as SessionStatusEnvelope.
    
    Returns state, budgets, and verification hashes.
    """
    if not CORE_AVAILABLE or app_state.context is None:
        # Fallback to legacy status
        photodiode_status = {
            "initialized": app_state.photodiode_reader is not None,
            "connected": app_state.photodiode_reader.is_connected() if app_state.photodiode_reader else False,
        }
        laser_status = {
            "initialized": app_state.laser_controller is not None,
            "connected": app_state.laser_controller.is_connected() if app_state.laser_controller else False,
        }
        return {
            "photodiode": photodiode_status,
            "laser": laser_status,
            "state": "LEGACY"
        }
    
    # Create budget envelope
    if app_state.context.budget:
        budget = BudgetEnvelope(
            remaining_emit_ms=app_state.context.budget.remaining_emit_ms,
            remaining_duty_percent=app_state.context.budget.remaining_duty_percent,
            cooldown_remaining_ms=app_state.context.budget.cooldown_remaining_ms
        )
    else:
        budget = BudgetEnvelope(0.0, 0.0, 0.0)
    
    # Create session status envelope
    status_envelope = SessionStatusEnvelope(
        state=app_state.context.state.value,
        budget=budget,
        config_hash=app_state.context.config_hash,
        cal_hash=app_state.context.cal_hash
    )
    
    return status_envelope.to_dict()

@app.post("/api/measurement/start")
async def start_measurement():
    """Start continuous measurement."""
    if app_state.measurement_running:
        return {"status": "already_running"}
    
    app_state.measurement_running = True
    
    # Start background task
    app_state._measurement_task = asyncio.create_task(measurement_loop())
    
    return {"status": "started"}

@app.post("/api/measurement/stop")
async def stop_measurement():
    """Stop continuous measurement."""
    app_state.measurement_running = False
    
    if app_state._measurement_task:
        app_state._measurement_task.cancel()
        try:
            await app_state._measurement_task
        except asyncio.CancelledError:
            pass
    
    return {"status": "stopped"}

@app.post("/api/measurement/calibrate-dark")
async def calibrate_dark():
    """Calibrate dark voltage."""
    if not app_state.photodiode_reader:
        raise HTTPException(status_code=400, detail="Photodiode reader not initialized")
    
    try:
        dark_voltage = app_state.photodiode_reader.measure_dark_voltage()
        return {"status": "success", "dark_voltage": dark_voltage}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/measurement/current")
async def get_current_measurement():
    """
    Get current measurement envelope.
    
    Returns MeasurementEnvelope with wavelength and voltage bounds.
    """
    if not app_state.photodiode_reader:
        raise HTTPException(status_code=400, detail="Photodiode reader not initialized")
    
    try:
        # Get measurement envelope
        envelope = app_state.photodiode_reader.get_measurement_envelope()
        app_state.last_measurement_envelope = envelope
        
        # Convert to dict for JSON response
        result = {}
        if envelope.wavelength_envelope_nm:
            result["wavelength_envelope_nm"] = {
                "min_nm": envelope.wavelength_envelope_nm.min_nm,
                "max_nm": envelope.wavelength_envelope_nm.max_nm,
                "confidence": envelope.wavelength_envelope_nm.confidence,
                "valid_until": envelope.wavelength_envelope_nm.valid_until
            }
        if envelope.voltage_envelope_v:
            result["voltage_envelope_v"] = {
                "min_v": envelope.voltage_envelope_v.min_v,
                "max_v": envelope.voltage_envelope_v.max_v,
                "rms_noise": envelope.voltage_envelope_v.rms_noise
            }
        if envelope.measurement_quality:
            result["measurement_quality"] = {
                "snr_estimate": envelope.measurement_quality.snr_estimate,
                "saturation_flag": envelope.measurement_quality.saturation_flag,
                "clipping_flag": envelope.measurement_quality.clipping_flag
            }
        
        return result
    except Exception as e:
        logger.error(f"Failed to get measurement envelope: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/measurement/history")
async def get_measurement_history():
    """Get measurement history."""
    if not app_state.signal_processor:
        return {"wavelengths": [], "voltages": []}
    
    history_length = app_state.config.get('preferences', {}).get('history_length', 100)
    wavelengths = app_state.signal_processor.get_wavelength_history(history_length)
    voltages = app_state.signal_processor.get_voltage_history(history_length)
    
    return {
        "wavelengths": wavelengths,
        "voltages": voltages
    }

@app.post("/api/laser/enable")
async def enable_laser():
    """Enable laser."""
    if not app_state.laser_controller:
        raise HTTPException(status_code=400, detail="Laser controller not initialized")
    
    if not app_state.laser_controller.is_interlock_safe():
        raise HTTPException(status_code=400, detail="Safety interlock is not engaged")
    
    success = app_state.laser_controller.enable()
    if success:
        return {"status": "success", "message": "Laser enabled"}
    else:
        raise HTTPException(status_code=500, detail="Failed to enable laser")

@app.post("/api/laser/disable")
async def disable_laser():
    """Disable laser."""
    if not app_state.laser_controller:
        raise HTTPException(status_code=400, detail="Laser controller not initialized")
    
    app_state.laser_controller.disable()
    return {"status": "success", "message": "Laser disabled"}

@app.post("/api/laser/emergency-stop")
async def emergency_stop():
    """Emergency stop laser."""
    if not app_state.laser_controller:
        raise HTTPException(status_code=400, detail="Laser controller not initialized")
    
    app_state.laser_controller.emergency_stop()
    return {"status": "success", "message": "EMERGENCY STOP ACTIVATED"}

@app.post("/api/laser/pulse")
async def send_pulse(request: PulseRequest):
    """Send a single pulse."""
    if not app_state.laser_controller:
        raise HTTPException(status_code=400, detail="Laser controller not initialized")
    
    if not app_state.laser_controller.is_interlock_safe():
        raise HTTPException(status_code=400, detail="Safety interlock is not engaged")
    
    success = app_state.laser_controller.pulse(request.duration)
    if success:
        return {"status": "success", "message": f"Pulse sent ({request.duration*1000:.1f} ms)"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send pulse")

@app.post("/api/emit")
async def emit_pattern(request: PatternRequest):
    """
    Emit pattern: transition EMIT_READY → EMITTING → EMIT_READY.
    
    Validates pattern against emit envelope and budget constraints.
    All emission must go through FSM.
    """
    if not CORE_AVAILABLE or app_state.fsm is None:
        raise HTTPException(status_code=400, detail="System not initialized")
    
    if app_state.context.state != FSMState.EMIT_READY:
        raise HTTPException(status_code=400, detail=f"Must be in EMIT_READY state, currently {app_state.context.state.value}")
    
    if not app_state.laser_controller:
        raise HTTPException(status_code=400, detail="Laser controller not initialized")
    
    if not app_state.signal_processor:
        raise HTTPException(status_code=400, detail="Signal processor not initialized")
    
    try:
        # Encode pattern
        if request.pattern_type == "geometric":
            if not request.geometric_type:
                raise HTTPException(status_code=400, detail="geometric_type required for geometric patterns")
            pattern = app_state.signal_processor.encode_message(
                request.geometric_type, "geometric"
            )
            if request.size:
                pattern = pattern[:request.size] if len(pattern) >= request.size else pattern
        else:
            if not request.message:
                raise HTTPException(status_code=400, detail="message required for morse/binary patterns")
            pattern = app_state.signal_processor.encode_message(request.message, request.pattern_type)
        
        # Get timing parameters
        pulse_dur = app_state.config.get('signal_processing', {}).get('encoding', {}).get('pulse_duration', 0.1)
        gap_dur = app_state.config.get('signal_processing', {}).get('encoding', {}).get('gap_duration', 0.1)
        
        # Calculate pattern parameters
        total_pulses = sum(1 for p in pattern if p)
        total_gaps = sum(1 for p in pattern if not p)
        total_duration = (total_pulses * pulse_dur) + (total_gaps * gap_dur)
        total_duration_ms = total_duration * 1000.0
        
        # Calculate duty cycle
        pulse_time = total_pulses * pulse_dur
        duty_cycle_percent = (pulse_time / total_duration * 100.0) if total_duration > 0 else 0.0
        
        # Create emit envelope
        t_start = time.monotonic()
        t_end = t_start + total_duration
        
        safety = app_state.config.get('safety', {})
        max_power_mw = safety.get('max_power_mw', 1.0)
        
        emit_envelope = EmitEnvelope(
            power_mw_max=max_power_mw,
            duty_cycle_max=100.0,  # Will be constrained by budget
            t_start=t_start,
            t_end=t_end,
            pulse_width_bounds=PulseWidthBounds(
                min_ms=pulse_dur * 1000.0,
                max_ms=pulse_dur * 1000.0
            )
        )
        
        # Validate envelope
        is_valid, error_msg = app_state.laser_controller.validate_emit_envelope(emit_envelope)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid emit envelope: {error_msg}")
        
        # Check budget availability
        from core.predicates import PredicateEvaluator
        evaluator = PredicateEvaluator()
        budget_ok, budget_info = evaluator.check_budget_available(
            app_state.context,
            required_emit_ms=total_duration_ms,
            required_duty_percent=duty_cycle_percent
        )
        
        if not budget_ok:
            raise HTTPException(status_code=400, detail=f"Insufficient budget: {budget_info}")
        
        # Transition EMIT_READY → EMITTING
        success, message, transition_info = app_state.fsm.transition(
            FSMEvent.EMIT_REQUEST,
            event_data={
                'required_emit_ms': total_duration_ms,
                'required_duty_percent': duty_cycle_percent,
                'emit_duration_ms': total_duration_ms,
                'duty_percent': duty_cycle_percent
            }
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Emit transition failed: {message}")
        
        # Send pattern
        pattern_success = app_state.laser_controller.send_pattern(pattern, pulse_dur, gap_dur)
        
        # Transition EMITTING → EMIT_READY
        app_state.fsm.transition(FSMEvent.EMIT_COMPLETE, event_data={
            'emit_duration_ms': total_duration_ms,
            'duty_percent': duty_cycle_percent
        })
        
        if not pattern_success:
            raise HTTPException(status_code=500, detail="Pattern send failed")
        
        # Log event
        if app_state.signal_processor:
            app_state.signal_processor.log_event(
                "pattern_sent",
                f"Sent {request.pattern_type} pattern: {request.message or request.geometric_type}"
            )
        
        # Write emit result trace
        if app_state.trace_writer:
            app_state.trace_writer.write_record(
                event_type=EventType.EMIT_RESULT,
                state_from=FSMState.EMITTING.value,
                state_to=FSMState.EMIT_READY.value,
                event_data={
                    'pattern_type': request.pattern_type,
                    'duration_ms': total_duration_ms,
                    'duty_percent': duty_cycle_percent,
                    'success': pattern_success
                },
                config_hash=app_state.context.config_hash,
                cal_hash=app_state.context.cal_hash
            )
        
        return {
            "status": "success",
            "message": f"Pattern sent",
            "emit_envelope": {
                "power_mw_max": emit_envelope.power_mw_max,
                "duty_cycle_max": emit_envelope.duty_cycle_max,
                "duration_ms": emit_envelope.duration_ms(),
            },
            "trace_seq": transition_info.get('seq')
        }
    except FSMError as e:
        logger.error(f"FSM error during emit: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to emit pattern: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoint for backward compatibility
@app.post("/api/laser/pattern")
async def send_pattern(request: PatternRequest):
    """Legacy endpoint - redirects to /api/emit."""
    return await emit_pattern(request)

@app.post("/api/health/check")
async def run_health_check():
    """Run health check."""
    checks = app_state.health_monitor.run_all_checks(
        app_state.photodiode_reader,
        app_state.laser_controller,
        app_state.config.get('logging', {}).get('log_dir', 'logs')
    )
    app_state.last_health_check = checks
    
    overall_status, overall_message = app_state.health_monitor.get_overall_status()
    
    return {
        "overall_status": overall_status.value,
        "overall_message": overall_message,
        "checks": [
            {
                "name": check.name,
                "status": check.status.value,
                "message": check.message,
                "details": check.details
            }
            for check in checks
        ]
    }

@app.get("/api/health/status")
async def get_health_status():
    """Get health status."""
    if not app_state.last_health_check:
        return {
            "overall_status": "unknown",
            "overall_message": "No health check performed",
            "checks": []
        }
    
    overall_status, overall_message = app_state.health_monitor.get_overall_status()
    
    return {
        "overall_status": overall_status.value,
        "overall_message": overall_message,
        "checks": [
            {
                "name": check.name,
                "status": check.status.value,
                "message": check.message,
                "details": check.details
            }
            for check in app_state.last_health_check
        ]
    }

@app.get("/api/session/bundle")
async def get_session_bundle():
    """
    Get session bundle path after shutdown.
    
    Returns path to session artifact directory.
    """
    if not CORE_AVAILABLE or app_state.session_bundle is None:
        raise HTTPException(status_code=400, detail="Session bundle not available")
    
    return {
        "session_id": app_state.context.session_id if app_state.context else None,
        "session_dir": str(app_state.session_bundle.session_dir) if app_state.session_bundle else None
    }

@app.on_event("startup")
async def startup_event():
    """Initialize FSM in SAFE state on startup."""
    if CORE_AVAILABLE:
        try:
            # Initialize context in SAFE state
            if app_state.context is None:
                config_path = Path(__file__).parent / "config" / "device_config.yaml"
                config, _ = load_config_and_hash(config_path) if config_path.exists() else ({}, "")
                
                app_state.context = SessionContext(
                    config=config,
                    simulation_mode=config.get('advanced', {}).get('simulation_mode', False)
                )
                
                # Set up trace writer (will be initialized properly on /api/initialize)
                log_dir = config.get('logging', {}).get('log_dir', 'logs')
                session_dir = Path(log_dir) / "sessions" / app_state.context.session_id
                trace_file = session_dir / "trace.jsonl"
                app_state.trace_writer = TraceWriter(trace_file, app_state.context.session_id)
                
                # Create FSM
                app_state.fsm = FSM(app_state.context, trace_transition_callback)
                
                logger.info(f"FSM initialized in SAFE state, session_id: {app_state.context.session_id}")
        except Exception as e:
            logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Write session bundle on shutdown."""
    if CORE_AVAILABLE and app_state.session_bundle:
        try:
            # Record final health check
            if app_state.health_monitor and app_state.photodiode_reader and app_state.laser_controller:
                log_dir = app_state.config.get('logging', {}).get('log_dir', 'logs') if app_state.config else 'logs'
                health_checks = app_state.health_monitor.run_all_checks(
                    app_state.photodiode_reader,
                    app_state.laser_controller,
                    log_dir
                )
                health_data = {
                    "overall_status": app_state.health_monitor.get_overall_status()[0].value,
                    "overall_message": app_state.health_monitor.get_overall_status()[1],
                    "checks": [
                        {
                            "name": c.name,
                            "status": c.status.value,
                            "message": c.message,
                            "details": c.details
                        }
                        for c in health_checks
                    ],
                    "timestamp": time.time()
                }
                app_state.session_bundle.set_health_end(health_data)
            
            # Write bundle
            bundle_path = app_state.session_bundle.write_bundle()
            logger.info(f"Session bundle written to: {bundle_path}")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

# Serve static files (frontend) in production
# In development, frontend runs separately
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

