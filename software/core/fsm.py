"""
Finite State Machine Module

Strict FSM with explicit states, transition table, guard predicates,
side-effect hooks, and fault latching.
"""

import logging
import time
from typing import Dict, Any, Optional, Callable, List, Tuple
from enum import Enum
from .context import SessionContext, FSMState, Budget
from .predicates import PredicateEvaluator

logger = logging.getLogger(__name__)


class FSMEvent(Enum):
    """FSM event enumeration."""
    INITIALIZE = "INITIALIZE"
    ARM = "ARM"
    ARM_CONFIRM = "ARM_CONFIRM"
    EMIT_REQUEST = "EMIT_REQUEST"
    EMIT_COMPLETE = "EMIT_COMPLETE"
    STOP = "STOP"
    RESET = "RESET"
    FAULT = "FAULT"


class FSMError(Exception):
    """FSM operation error."""
    pass


class FSM:
    """
    Strict finite state machine for NIoLS operational control.
    
    States: SAFE → INITIALIZED → ARMED → EMIT_READY → EMITTING → EMIT_READY (or FAULT)
    
    All state transitions must go through transition() which writes trace records.
    """
    
    # Valid transition table: (from_state, event) -> (to_state, required_predicates)
    TRANSITION_TABLE: Dict[Tuple[FSMState, FSMEvent], Tuple[FSMState, List[str]]] = {
        # SAFE → INITIALIZED
        (FSMState.SAFE, FSMEvent.INITIALIZE): (
            FSMState.INITIALIZED,
            ['check_config_valid', 'check_calibration_valid', 'check_dependencies_ok', 'check_hardware_health']
        ),
        
        # INITIALIZED → ARMED
        (FSMState.INITIALIZED, FSMEvent.ARM): (
            FSMState.ARMED,
            ['check_interlock_safe', 'check_no_outstanding_faults', 'check_cooldown_satisfied']
        ),
        
        # ARMED → EMIT_READY
        (FSMState.ARMED, FSMEvent.ARM_CONFIRM): (
            FSMState.EMIT_READY,
            ['check_arm_confirmation_within_window']
        ),
        
        # EMIT_READY → EMITTING
        (FSMState.EMIT_READY, FSMEvent.EMIT_REQUEST): (
            FSMState.EMITTING,
            ['check_budget_available', 'check_interlock_safe']
        ),
        
        # EMITTING → EMIT_READY
        (FSMState.EMITTING, FSMEvent.EMIT_COMPLETE): (
            FSMState.EMIT_READY,
            []
        ),
        
        # EMITTING → EMIT_READY (via STOP)
        (FSMState.EMITTING, FSMEvent.STOP): (
            FSMState.EMIT_READY,
            []
        ),
        
        # EMIT_READY → ARMED (via STOP)
        (FSMState.EMIT_READY, FSMEvent.STOP): (
            FSMState.ARMED,
            []
        ),
        
        # ARMED → INITIALIZED (via STOP)
        (FSMState.ARMED, FSMEvent.STOP): (
            FSMState.INITIALIZED,
            []
        ),
        
        # INITIALIZED → SAFE (via STOP)
        (FSMState.INITIALIZED, FSMEvent.STOP): (
            FSMState.SAFE,
            []
        ),
        
        # FAULT → SAFE (via RESET)
        (FSMState.FAULT, FSMEvent.RESET): (
            FSMState.SAFE,
            []
        ),
        
        # ANY → FAULT (via FAULT event)
        (FSMState.SAFE, FSMEvent.FAULT): (FSMState.FAULT, []),
        (FSMState.INITIALIZED, FSMEvent.FAULT): (FSMState.FAULT, []),
        (FSMState.ARMED, FSMEvent.FAULT): (FSMState.FAULT, []),
        (FSMState.EMIT_READY, FSMEvent.FAULT): (FSMState.FAULT, []),
        (FSMState.EMITTING, FSMEvent.FAULT): (FSMState.FAULT, []),
    }
    
    def __init__(self, context: SessionContext, trace_writer: Optional[Callable] = None):
        """
        Initialize FSM.
        
        Args:
            context: Session context
            trace_writer: Optional callback function to write trace records
        """
        self.context = context
        self.trace_writer = trace_writer
        self.predicate_evaluator = PredicateEvaluator()
        self._side_effect_hooks: Dict[str, List[Callable]] = {}
    
    def add_side_effect_hook(self, event: str, hook: Callable[[FSMState, FSMState, Dict], None]):
        """
        Add a side-effect hook for state transitions.
        
        Args:
            event: Event name or state transition identifier
            hook: Function(state_from, state_to, transition_data) -> None
        """
        if event not in self._side_effect_hooks:
            self._side_effect_hooks[event] = []
        self._side_effect_hooks[event].append(hook)
    
    def transition(self, event: FSMEvent, event_data: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Attempt state transition.
        
        Args:
            event: FSM event
            event_data: Optional event-specific data
            
        Returns:
            (success, message, transition_info)
            
        Raises:
            FSMError: If transition is illegal or predicates fail
        """
        if event_data is None:
            event_data = {}
        
        from_state = self.context.state
        transition_key = (from_state, event)
        
        # Check if transition is legal
        if transition_key not in self.TRANSITION_TABLE:
            error_msg = f"Illegal transition: {from_state.value} --{event.value}--> ?"
            logger.error(error_msg)
            raise FSMError(error_msg)
        
        to_state, required_predicates = self.TRANSITION_TABLE[transition_key]
        
        # Evaluate all required predicates
        predicate_results = {}
        all_predicates_pass = True
        
        for pred_name in required_predicates:
            pred_method = getattr(self.predicate_evaluator, pred_name, None)
            if pred_method is None:
                logger.error(f"Predicate method not found: {pred_name}")
                all_predicates_pass = False
                predicate_results[pred_name] = {
                    "passed": False,
                    "error": "predicate_method_not_found"
                }
                continue
            
            try:
                # Handle predicates that need additional arguments
                if pred_name == 'check_budget_available':
                    required_emit_ms = event_data.get('required_emit_ms', 0.0)
                    required_duty_percent = event_data.get('required_duty_percent', 0.0)
                    passed, bounds = pred_method(self.context, required_emit_ms, required_duty_percent)
                elif pred_name in ['check_config_hash_match', 'check_cal_hash_match']:
                    # These will be called separately for drift detection
                    passed, bounds = True, {}  # Skip for now, handled in drift detection
                else:
                    passed, bounds = pred_method(self.context)
                
                predicate_results[pred_name] = {
                    "passed": passed,
                    "bounds": bounds
                }
                
                if not passed:
                    all_predicates_pass = False
                    logger.warning(f"Predicate failed: {pred_name}, bounds: {bounds}")
            
            except Exception as e:
                logger.error(f"Predicate evaluation error for {pred_name}: {e}")
                all_predicates_pass = False
                predicate_results[pred_name] = {
                    "passed": False,
                    "error": str(e)
                }
        
        # If predicates fail, transition to FAULT (except if already in FAULT or going to SAFE)
        if not all_predicates_pass and to_state != FSMState.SAFE:
            logger.error(f"Predicate failures, transitioning to FAULT: {predicate_results}")
            fault_reason = f"Predicate failures: {[k for k, v in predicate_results.items() if not v.get('passed', False)]}"
            return self._transition_to_fault(fault_reason, predicate_results)
        
        # Execute transition
        return self._execute_transition(from_state, to_state, event, event_data, predicate_results)
    
    def _execute_transition(self, from_state: FSMState, to_state: FSMState, 
                           event: FSMEvent, event_data: Dict[str, Any],
                           predicate_results: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Execute state transition with side effects.
        
        Returns:
            (success, message, transition_info)
        """
        try:
            # Update context state
            self.context.state = to_state
            
            # Execute state-specific side effects
            self._execute_side_effects(from_state, to_state, event, event_data)
            
            # Write trace record
            transition_info = {
                "from_state": from_state.value,
                "to_state": to_state.value,
                "event": event.value,
                "event_data": event_data,
                "predicates": predicate_results,
                "timestamp": time.monotonic(),
                "wall_clock": time.time()
            }
            
            if self.trace_writer:
                try:
                    self.trace_writer(transition_info)
                except Exception as e:
                    logger.error(f"Trace writer error: {e}")
            
            logger.info(f"State transition: {from_state.value} --{event.value}--> {to_state.value}")
            
            return True, f"Transitioned {from_state.value} -> {to_state.value}", transition_info
        
        except Exception as e:
            logger.error(f"Transition execution error: {e}")
            # Transition to FAULT on execution error
            return self._transition_to_fault(f"Transition execution error: {str(e)}", {})
    
    def _execute_side_effects(self, from_state: FSMState, to_state: FSMState,
                               event: FSMEvent, event_data: Dict[str, Any]):
        """Execute side effects for state transitions."""
        
        # INITIALIZED: Initialize budget
        if to_state == FSMState.INITIALIZED and self.context.config:
            self.context.initialize_budget(self.context.config)
        
        # ARMED: Start arming window
        if to_state == FSMState.ARMED:
            self.context.start_arming_window()
        
        # EMIT_READY: Clear arming window
        if to_state == FSMState.EMIT_READY:
            self.context.clear_arming_window()
        
        # EMITTING: Consume budget (if provided in event_data)
        if to_state == FSMState.EMITTING and self.context.budget:
            emit_duration_ms = event_data.get('emit_duration_ms', 0.0)
            duty_percent = event_data.get('duty_percent', 0.0)
            
            if emit_duration_ms > 0:
                self.context.budget.consume_emit_time(emit_duration_ms)
            if duty_percent > 0:
                self.context.budget.consume_duty_cycle(duty_percent)
        
        # EMIT_COMPLETE: Record emission end for cooldown
        if event == FSMEvent.EMIT_COMPLETE and self.context.budget:
            self.context.budget.record_emit_end(time.monotonic())
        
        # Call registered hooks
        hook_key = f"{from_state.value}->{to_state.value}"
        if hook_key in self._side_effect_hooks:
            for hook in self._side_effect_hooks[hook_key]:
                try:
                    hook(from_state, to_state, event_data)
                except Exception as e:
                    logger.error(f"Side effect hook error: {e}")
    
    def _transition_to_fault(self, reason: str, predicate_results: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Transition to FAULT state.
        
        Args:
            reason: Reason for fault
            predicate_results: Predicate evaluation results
            
        Returns:
            (success, message, transition_info)
        """
        from_state = self.context.state
        to_state = FSMState.FAULT
        
        self.context.state = to_state
        self.context.fault_reason = reason
        
        transition_info = {
            "from_state": from_state.value,
            "to_state": to_state.value,
            "event": FSMEvent.FAULT.value,
            "fault_reason": reason,
            "predicates": predicate_results,
            "timestamp": time.monotonic(),
            "wall_clock": time.time()
        }
        
        if self.trace_writer:
            try:
                self.trace_writer(transition_info)
            except Exception as e:
                logger.error(f"Trace writer error: {e}")
        
        logger.error(f"FAULT transition: {reason}")
        
        return True, f"Fault: {reason}", transition_info
    
    def get_state(self) -> FSMState:
        """Get current FSM state."""
        return self.context.state
    
    def can_transition(self, event: FSMEvent) -> bool:
        """
        Check if a transition is legal from current state.
        
        Args:
            event: FSM event
            
        Returns:
            True if transition is legal
        """
        transition_key = (self.context.state, event)
        return transition_key in self.TRANSITION_TABLE

