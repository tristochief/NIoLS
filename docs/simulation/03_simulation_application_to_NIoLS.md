# Applying Simulation to the NIoLS Architecture

## Mapping Simulation to Existing NIoLS Components

This document maps simulation directly onto **existing NIoLS modules**, not hypothetical ones.

---

## Photodiode Subsystem

### Simulated Properties
- Dark voltage distribution
- Noise floor vs bandwidth
- Saturation thresholds
- ADC quantization error

### Required Guarantees
- ADC input never exceeds configured bounds
- Envelope always includes worst-case noise
- Calibration drift detectable

---

## Laser Subsystem

### Simulated Properties
- Pulse timing jitter
- Duty cycle accumulation
- Power envelope compliance

### Required Guarantees
- Emission impossible outside EMITTING state
- Interlock override impossible in simulation
- Emergency stop dominance verified

---

## FSM Simulation

Simulation must validate:

- No illegal transitions exist
- All FAULT conditions latch
- No path allows emission without prior hash lock

FSM simulation is a **proof**, not a test.

---

## Trace Simulation

Before runtime:

- Simulate trace generation
- Verify hash chaining
- Verify root hash reproducibility

Trace simulation ensures **audit closure** exists before hardware runs.

---

## Outcome

If simulation passes:
- Hardware execution is allowed
If simulation fails:
- Hardware execution is forbidden

