# NIoLS Simulation Tool Stack

## Selection Philosophy

Tools are chosen based on:
- determinism
- inspectability
- offline replay capability
- non-dependence on cloud services

---

## Electrical Simulation

- KiCad + ngspice
  - Photodiode TIA modeling
  - ADC range verification
  - Noise envelope estimation

All SPICE models must be version-pinned and stored locally.

---

## Software Simulation

- pytest
- Hypothesis (property-based testing)
- Fake hardware interfaces

Simulation must run without Raspberry Pi hardware.

---

## FSM & Logic Simulation

- Pure Python FSM runner
- No GPIO access
- No timing shortcuts

FSM simulation must be runnable inside CI.

---

## Trace & Hash Simulation

- Canonical JSON serialization
- SHA-256 hashing
- Replay verification tools

Hash mismatches are treated as simulation failures.

---

## Observability Simulation

- OpenTelemetry (local exporter only)
- Session ID correlation
- FSM transition spans

No remote telemetry is required or permitted.

