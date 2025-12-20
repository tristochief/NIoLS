"""
NIoLS Core Module

Provides the finite state machine, predicates, contracts, and session management
for operational closure and structural constraints.
"""

from .context import SessionContext, FSMState, Budget
from .fsm import FSM, FSMEvent, FSMError
from .predicates import PredicateEvaluator
from .hash_binding import (
    compute_config_hash,
    compute_calibration_hash,
    load_config_and_hash,
    load_calibration_and_hash,
    detect_config_drift,
    detect_calibration_drift,
)
from .trace import TraceWriter, TraceReader, EventType
from .session_bundle import SessionBundle
from .contracts import (
    MeasurementEnvelope,
    WavelengthEnvelope,
    VoltageEnvelope,
    MeasurementQuality,
    EmitEnvelope,
    PulseWidthBounds,
    BudgetEnvelope,
    SessionStatusEnvelope,
)

__all__ = [
    'SessionContext',
    'FSMState',
    'Budget',
    'FSM',
    'FSMEvent',
    'FSMError',
    'PredicateEvaluator',
    'compute_config_hash',
    'compute_calibration_hash',
    'load_config_and_hash',
    'load_calibration_and_hash',
    'detect_config_drift',
    'detect_calibration_drift',
    'TraceWriter',
    'TraceReader',
    'EventType',
    'SessionBundle',
    'MeasurementEnvelope',
    'WavelengthEnvelope',
    'VoltageEnvelope',
    'MeasurementQuality',
    'EmitEnvelope',
    'PulseWidthBounds',
    'BudgetEnvelope',
    'SessionStatusEnvelope',
]

