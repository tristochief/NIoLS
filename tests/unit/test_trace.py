"""
Unit tests for trace module.
"""

import unittest
import tempfile
from pathlib import Path
from core.trace import TraceWriter, TraceReader, EventType


class TestTrace(unittest.TestCase):
    """Test trace functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.trace_file = self.temp_dir / "trace.jsonl"
        self.session_id = "test_session_123"
        self.writer = TraceWriter(self.trace_file, self.session_id)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_write_record(self):
        """Test writing trace records."""
        record = self.writer.write_record(
            event_type=EventType.STATE_TRANSITION,
            state_from="SAFE",
            state_to="INITIALIZED",
            predicates={"test": True},
            config_hash="test_config_hash",
            cal_hash="test_cal_hash"
        )
        
        self.assertEqual(record["event_type"], "STATE_TRANSITION")
        self.assertEqual(record["state_from"], "SAFE")
        self.assertEqual(record["state_to"], "INITIALIZED")
        self.assertIn("hash", record)
        self.assertEqual(record["seq"], 1)
    
    def test_hash_chaining(self):
        """Test hash chaining between records."""
        record1 = self.writer.write_record(
            event_type=EventType.STATE_TRANSITION,
            state_from="SAFE",
            state_to="INITIALIZED"
        )
        
        record2 = self.writer.write_record(
            event_type=EventType.STATE_TRANSITION,
            state_from="INITIALIZED",
            state_to="ARMED"
        )
        
        # Second record should reference first record's hash
        self.assertEqual(record2["prev_hash"], record1["hash"])
    
    def test_trace_reader_verify_chain(self):
        """Test trace reader chain verification."""
        # Write some records
        self.writer.write_record(
            event_type=EventType.STATE_TRANSITION,
            state_from="SAFE",
            state_to="INITIALIZED"
        )
        self.writer.write_record(
            event_type=EventType.STATE_TRANSITION,
            state_from="INITIALIZED",
            state_to="ARMED"
        )
        
        # Read and verify
        reader = TraceReader(self.trace_file)
        is_valid, errors = reader.verify_chain()
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_trace_reader_detect_tampering(self):
        """Test trace reader detects tampering."""
        # Write a record
        self.writer.write_record(
            event_type=EventType.STATE_TRANSITION,
            state_from="SAFE",
            state_to="INITIALIZED"
        )
        
        # Tamper with the file
        with open(self.trace_file, 'r') as f:
            lines = f.readlines()
        
        # Modify a record (change state_to)
        import json
        record = json.loads(lines[1])
        record["state_to"] = "TAMPERED"
        
        with open(self.trace_file, 'w') as f:
            f.write(lines[0])  # Header
            f.write(json.dumps(record) + '\n')
        
        # Verify should detect tampering
        reader = TraceReader(self.trace_file)
        is_valid, errors = reader.verify_chain()
        
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_get_root_hash(self):
        """Test root hash computation."""
        self.writer.write_record(
            event_type=EventType.STATE_TRANSITION,
            state_from="SAFE",
            state_to="INITIALIZED"
        )
        
        root_hash = self.writer.get_root_hash()
        self.assertIsNotNone(root_hash)
        self.assertEqual(len(root_hash), 64)  # SHA256 hex string
        
        # With metadata
        metadata = {"session_id": self.session_id, "version": "1.0"}
        root_hash_with_metadata = self.writer.get_root_hash(metadata)
        self.assertNotEqual(root_hash, root_hash_with_metadata)


if __name__ == '__main__':
    unittest.main()

