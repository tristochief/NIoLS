"""
Hash Binding Module

Functions for computing config/calibration hashes using SHA256 of canonical JSON.
Ensures immutability during sessions.
"""

import hashlib
import json
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


def canonical_json(obj: Any) -> str:
    """
    Convert object to canonical JSON string (deterministic).
    
    Args:
        obj: Object to serialize
        
    Returns:
        Canonical JSON string with sorted keys
    """
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def compute_hash(data: str) -> str:
    """
    Compute SHA256 hash of data.
    
    Args:
        data: String data to hash
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def compute_config_hash(config: Dict[str, Any]) -> str:
    """
    Compute hash of configuration dictionary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Hexadecimal hash string
    """
    canonical = canonical_json(config)
    return compute_hash(canonical)


def compute_calibration_hash(calibration: Dict[str, Any]) -> str:
    """
    Compute hash of calibration dictionary.
    
    Args:
        calibration: Calibration dictionary
        
    Returns:
        Hexadecimal hash string
    """
    canonical = canonical_json(calibration)
    return compute_hash(canonical)


def load_config_and_hash(config_path: Path) -> Tuple[Dict[str, Any], str]:
    """
    Load configuration file and compute hash.
    
    Args:
        config_path: Path to configuration YAML file
        
    Returns:
        (config_dict, config_hash)
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            config = {}
        
        config_hash = compute_config_hash(config)
        
        logger.info(f"Loaded config from {config_path}, hash: {config_hash[:16]}...")
        
        return config, config_hash
    
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error: {e}")
        raise
    except Exception as e:
        logger.error(f"Config load error: {e}")
        raise


def load_calibration_and_hash(calibration_source: Any) -> Tuple[Dict[str, Any], str]:
    """
    Load calibration data and compute hash.
    
    Args:
        calibration_source: Either a dict, Path to file, or PhotodiodeReader instance
        
    Returns:
        (calibration_dict, cal_hash)
        
    Raises:
        ValueError: If calibration source is invalid
    """
    if isinstance(calibration_source, dict):
        # Direct dictionary
        calibration = calibration_source
    elif isinstance(calibration_source, Path) or isinstance(calibration_source, str):
        # File path
        cal_path = Path(calibration_source)
        if not cal_path.exists():
            raise FileNotFoundError(f"Calibration file not found: {cal_path}")
        
        # Try to load as YAML first, then CSV
        try:
            with open(cal_path, 'r') as f:
                if cal_path.suffix in ['.yaml', '.yml']:
                    calibration = yaml.safe_load(f)
                else:
                    # Assume CSV format
                    import csv
                    calibration = {"points": []}
                    with open(cal_path, 'r') as csvf:
                        reader = csv.reader(csvf)
                        next(reader, None)  # Skip header if present
                        for row in reader:
                            if len(row) >= 2:
                                calibration["points"].append({
                                    "wavelength": float(row[0]),
                                    "voltage": float(row[1])
                                })
        except Exception as e:
            logger.error(f"Calibration load error: {e}")
            raise
    elif hasattr(calibration_source, 'calibration_table'):
        # PhotodiodeReader instance
        cal_table = calibration_source.calibration_table
        calibration = {
            "points": [
                {"wavelength": w, "voltage": v}
                for w, v in sorted(cal_table.items())
            ],
            "dark_voltage": getattr(calibration_source, 'dark_voltage', 0.0)
        }
    else:
        raise ValueError(f"Invalid calibration source type: {type(calibration_source)}")
    
    if calibration is None:
        calibration = {}
    
    cal_hash = compute_calibration_hash(calibration)
    
    logger.info(f"Loaded calibration, hash: {cal_hash[:16]}...")
    
    return calibration, cal_hash


def detect_config_drift(bound_hash: str, current_config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Detect if configuration has drifted from bound hash.
    
    Args:
        bound_hash: Hash that was bound at initialization
        current_config: Current configuration dictionary
        
    Returns:
        (has_drifted, current_hash)
    """
    current_hash = compute_config_hash(current_config)
    has_drifted = bound_hash != current_hash
    
    if has_drifted:
        logger.warning(f"Config drift detected: bound={bound_hash[:16]}..., current={current_hash[:16]}...")
    
    return has_drifted, current_hash


def detect_calibration_drift(bound_hash: str, current_calibration: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Detect if calibration has drifted from bound hash.
    
    Args:
        bound_hash: Hash that was bound at initialization
        current_calibration: Current calibration dictionary
        
    Returns:
        (has_drifted, current_hash)
    """
    current_hash = compute_calibration_hash(current_calibration)
    has_drifted = bound_hash != current_hash
    
    if has_drifted:
        logger.warning(f"Calibration drift detected: bound={bound_hash[:16]}..., current={current_hash[:16]}...")
    
    return has_drifted, current_hash

