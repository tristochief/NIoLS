"""
Session Bundle Module

Collects and writes session artifacts on shutdown:
- trace.jsonl (hash-chained execution trace)
- config.json (config snapshot with hash)
- calibration.json (calibration snapshot with hash)
- health_start.json (health check at initialization)
- health_end.json (health check at shutdown)
- session_manifest.json (root hash, session metadata, versions)
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .trace import TraceWriter
from .context import SessionContext

logger = logging.getLogger(__name__)


class SessionBundle:
    """
    Session bundle writer for operational closure artifacts.
    """
    
    def __init__(self, session_dir: Path, context: SessionContext, trace_writer: TraceWriter):
        """
        Initialize session bundle.
        
        Args:
            session_dir: Directory for session artifacts
            context: Session context
            trace_writer: Trace writer instance
        """
        self.session_dir = session_dir
        self.context = context
        self.trace_writer = trace_writer
        self.health_start: Optional[Dict[str, Any]] = None
        self.health_end: Optional[Dict[str, Any]] = None
        
        # Ensure directory exists
        self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def set_health_start(self, health_data: Dict[str, Any]):
        """
        Set initial health check data.
        
        Args:
            health_data: Health check results from initialization
        """
        self.health_start = health_data
    
    def set_health_end(self, health_data: Dict[str, Any]):
        """
        Set final health check data.
        
        Args:
            health_data: Health check results from shutdown
        """
        self.health_end = health_data
    
    def write_bundle(self) -> Path:
        """
        Write complete session bundle.
        
        Returns:
            Path to session directory
        """
        logger.info(f"Writing session bundle to {self.session_dir}")
        
        # Write trace (already exists, just verify)
        trace_file = self.session_dir / "trace.jsonl"
        if not trace_file.exists() and self.trace_writer.trace_file.exists():
            # Copy trace file if it's in a different location
            import shutil
            shutil.copy(self.trace_writer.trace_file, trace_file)
        
        # Write config snapshot
        if self.context.config is not None:
            config_file = self.session_dir / "config.json"
            config_snapshot = {
                "config": self.context.config,
                "config_hash": self.context.config_hash,
                "timestamp": time.time(),
                "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
            }
            with open(config_file, 'w') as f:
                json.dump(config_snapshot, f, indent=2, sort_keys=True)
            logger.info(f"Wrote config snapshot: {config_file}")
        
        # Write calibration snapshot
        if self.context.calibration is not None:
            cal_file = self.session_dir / "calibration.json"
            cal_snapshot = {
                "calibration": self.context.calibration,
                "cal_hash": self.context.cal_hash,
                "timestamp": time.time(),
                "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
            }
            with open(cal_file, 'w') as f:
                json.dump(cal_snapshot, f, indent=2, sort_keys=True)
            logger.info(f"Wrote calibration snapshot: {cal_file}")
        
        # Write health snapshots
        if self.health_start is not None:
            health_start_file = self.session_dir / "health_start.json"
            with open(health_start_file, 'w') as f:
                json.dump(self.health_start, f, indent=2, sort_keys=True)
            logger.info(f"Wrote health start snapshot: {health_start_file}")
        
        if self.health_end is not None:
            health_end_file = self.session_dir / "health_end.json"
            with open(health_end_file, 'w') as f:
                json.dump(self.health_end, f, indent=2, sort_keys=True)
            logger.info(f"Wrote health end snapshot: {health_end_file}")
        
        # Write session manifest
        manifest = self._create_manifest()
        manifest_file = self.session_dir / "session_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
        logger.info(f"Wrote session manifest: {manifest_file}")
        
        logger.info(f"Session bundle complete: {self.session_dir}")
        
        return self.session_dir
    
    def _create_manifest(self) -> Dict[str, Any]:
        """
        Create session manifest with root hash and metadata.
        
        Returns:
            Manifest dictionary
        """
        # Compute root hash
        session_metadata = {
            "session_id": self.context.session_id,
            "state": self.context.state.value,
            "config_hash": self.context.config_hash,
            "cal_hash": self.context.cal_hash,
            "simulation_mode": self.context.simulation_mode,
            "fault_reason": self.context.fault_reason,
        }
        
        root_hash = self.trace_writer.get_root_hash(session_metadata)
        
        # Get system info
        import sys
        import platform
        
        manifest = {
            "session_id": self.context.session_id,
            "root_hash": root_hash,
            "created": time.time(),
            "created_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "state": self.context.state.value,
            "config_hash": self.context.config_hash,
            "cal_hash": self.context.cal_hash,
            "simulation_mode": self.context.simulation_mode,
            "fault_reason": self.context.fault_reason,
            "versions": {
                "python": sys.version,
                "platform": platform.platform(),
            },
            "files": {
                "trace": "trace.jsonl",
                "config": "config.json" if self.context.config else None,
                "calibration": "calibration.json" if self.context.calibration else None,
                "health_start": "health_start.json" if self.health_start else None,
                "health_end": "health_end.json" if self.health_end else None,
            },
            "budget_final": {
                "remaining_emit_ms": self.context.budget.remaining_emit_ms if self.context.budget else None,
                "remaining_duty_percent": self.context.budget.remaining_duty_percent if self.context.budget else None,
                "cooldown_remaining_ms": self.context.budget.cooldown_remaining_ms if self.context.budget else None,
            } if self.context.budget else None,
        }
        
        return manifest

