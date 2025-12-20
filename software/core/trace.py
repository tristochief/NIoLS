"""
Execution Trace Module

Hash-chained append-only event log for FSM transitions and events.
Provides tamper detection through hash chaining.
"""

import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Trace event type enumeration."""
    STATE_TRANSITION = "STATE_TRANSITION"
    FAULT = "FAULT"
    EMIT_REQUEST = "EMIT_REQUEST"
    EMIT_RESULT = "EMIT_RESULT"
    MEASUREMENT_ENVELOPE_SNAPSHOT = "MEASUREMENT_ENVELOPE_SNAPSHOT"
    CONFIG_DRIFT = "CONFIG_DRIFT"


class TraceWriter:
    """
    Hash-chained append-only trace writer.
    
    Each record contains a hash of the previous record, creating
    an immutable chain that can detect tampering.
    """
    
    def __init__(self, trace_file: Path, session_id: str):
        """
        Initialize trace writer.
        
        Args:
            trace_file: Path to trace JSONL file
            session_id: Session identifier
        """
        self.trace_file = trace_file
        self.session_id = session_id
        self.sequence = 0
        self.prev_hash: Optional[str] = None
        
        # Ensure directory exists
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize trace file if it doesn't exist
        if not self.trace_file.exists():
            self._write_header()
        else:
            # Load existing trace to get last hash
            self._load_last_hash()
    
    def _write_header(self):
        """Write trace file header."""
        header = {
            "trace_version": "1.0",
            "session_id": self.session_id,
            "created": time.time(),
            "created_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        }
        
        with open(self.trace_file, 'w') as f:
            f.write(json.dumps(header, sort_keys=True) + '\n')
        
        logger.info(f"Initialized trace file: {self.trace_file}")
    
    def _load_last_hash(self):
        """Load the last record hash from existing trace file."""
        try:
            with open(self.trace_file, 'r') as f:
                lines = f.readlines()
                # Skip header, find last record
                for line in reversed(lines[1:]):
                    if line.strip():
                        try:
                            record = json.loads(line)
                            if 'hash' in record:
                                self.prev_hash = record['hash']
                                # Get sequence number
                                self.sequence = record.get('seq', 0)
                                break
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.warning(f"Could not load last hash: {e}")
            self.prev_hash = None
            self.sequence = 0
    
    def _canonical_json(self, obj: Dict[str, Any]) -> str:
        """
        Convert object to canonical JSON string (deterministic).
        
        Args:
            obj: Dictionary to serialize
            
        Returns:
            Canonical JSON string
        """
        return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    
    def _compute_hash(self, data: str) -> str:
        """
        Compute SHA256 hash of data.
        
        Args:
            data: String data to hash
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def write_record(self, event_type: EventType, state_from: Optional[str] = None,
                    state_to: Optional[str] = None, predicates: Optional[Dict[str, Any]] = None,
                    event_data: Optional[Dict[str, Any]] = None,
                    config_hash: Optional[str] = None,
                    cal_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Write a trace record.
        
        Args:
            event_type: Type of event
            state_from: Source state (for transitions)
            state_to: Target state (for transitions)
            predicates: Predicate evaluation results
            event_data: Event-specific data
            config_hash: Configuration hash
            cal_hash: Calibration hash
            
        Returns:
            Written record dictionary
        """
        self.sequence += 1
        
        # Build record (without hash field)
        record = {
            "ts": time.monotonic(),
            "wall_clock": time.time(),
            "seq": self.sequence,
            "prev_hash": self.prev_hash or "0" * 64,  # 64 hex chars for SHA256
            "event_type": event_type.value,
            "session_id": self.session_id,
        }
        
        if state_from is not None:
            record["state_from"] = state_from
        if state_to is not None:
            record["state_to"] = state_to
        if predicates is not None:
            record["predicates"] = predicates
        if event_data is not None:
            record["event_data"] = event_data
        if config_hash is not None:
            record["config_hash"] = config_hash
        if cal_hash is not None:
            record["cal_hash"] = cal_hash
        
        # Compute hash of canonical record (without hash field)
        canonical = self._canonical_json(record)
        record_hash = self._compute_hash(canonical)
        
        # Add hash to record
        record["hash"] = record_hash
        
        # Write to file (append mode)
        with open(self.trace_file, 'a') as f:
            f.write(json.dumps(record, sort_keys=True) + '\n')
        
        # Update previous hash for next record
        self.prev_hash = record_hash
        
        logger.debug(f"Trace record written: seq={self.sequence}, hash={record_hash[:16]}...")
        
        return record
    
    def get_root_hash(self, session_metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Compute session root hash.
        
        Args:
            session_metadata: Optional session metadata to include
            
        Returns:
            Root hash string
        """
        if self.prev_hash is None:
            # No records yet
            return "0" * 64
        
        # Root hash = last record hash + session metadata hash
        if session_metadata:
            metadata_hash = self._compute_hash(self._canonical_json(session_metadata))
            # Combine hashes
            combined = self.prev_hash + metadata_hash
            return self._compute_hash(combined)
        else:
            return self.prev_hash


class TraceReader:
    """
    Trace reader for verification and analysis.
    """
    
    def __init__(self, trace_file: Path):
        """
        Initialize trace reader.
        
        Args:
            trace_file: Path to trace JSONL file
        """
        self.trace_file = trace_file
        self.records: List[Dict[str, Any]] = []
        self._load_records()
    
    def _load_records(self):
        """Load all records from trace file."""
        if not self.trace_file.exists():
            logger.warning(f"Trace file not found: {self.trace_file}")
            return
        
        try:
            with open(self.trace_file, 'r') as f:
                lines = f.readlines()
                # Skip header (first line)
                for line in lines[1:]:
                    if line.strip():
                        try:
                            record = json.loads(line)
                            self.records.append(record)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse trace record: {e}")
        except Exception as e:
            logger.error(f"Failed to load trace records: {e}")
    
    def verify_chain(self) -> tuple[bool, List[str]]:
        """
        Verify hash chain integrity.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.records:
            return True, []
        
        prev_hash = None
        
        for i, record in enumerate(self.records):
            seq = record.get('seq', i + 1)
            
            # Check prev_hash matches
            record_prev_hash = record.get('prev_hash')
            if prev_hash is not None and record_prev_hash != prev_hash:
                errors.append(f"Record {seq}: prev_hash mismatch (expected {prev_hash[:16]}..., got {record_prev_hash[:16]}...)")
            
            # Verify hash
            record_hash = record.get('hash')
            if record_hash:
                # Recompute hash (without hash field)
                record_without_hash = {k: v for k, v in record.items() if k != 'hash'}
                canonical = json.dumps(record_without_hash, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
                computed_hash = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
                
                if computed_hash != record_hash:
                    errors.append(f"Record {seq}: hash mismatch (computed {computed_hash[:16]}..., stored {record_hash[:16]}...)")
            
            prev_hash = record_hash
        
        return len(errors) == 0, errors
    
    def get_records(self) -> List[Dict[str, Any]]:
        """Get all loaded records."""
        return self.records
    
    def get_state_transitions(self) -> List[Dict[str, Any]]:
        """Get all state transition records."""
        return [
            r for r in self.records
            if r.get('event_type') == EventType.STATE_TRANSITION.value
        ]

