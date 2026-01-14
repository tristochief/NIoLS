# NIoLS Simulation Concept Model

## Overview

This document defines the **conceptual simulation model** for NIoLS.

The goal is not high-fidelity physics everywhere, but **bounded correctness**:
simulation must prove that nothing unsafe, non-deterministic, or non-auditable can occur.

---

## Simulation Domains in NIoLS

NIoLS simulation is divided into **five constrained domains**:

### 1. Electrical Domain
- Photodiode + TIA behavior
- ADC voltage ranges
- Noise envelopes
- Saturation limits

### 2. Emission Domain
- Laser duty cycle
- Pulse timing
- Power envelope compliance
- Thermal accumulation limits

### 3. FSM Domain
- State transitions
- Predicate evaluation
- Fault latching
- Irreversibility rules

### 4. Configuration Domain
- Canonical serialization
- Hash stability
- Drift detection
- Safe/unsafe transitions

### 5. Detection Domain
- Signal filtering
- Envelope widening
- Outlier rejection
- Confidence decay over time

---

## What Simulation Explicitly Does NOT Do

Simulation in NIoLS must **never**:

- Predict ET behavior
- Claim contact certainty
- Produce point estimates
- Infer intent or meaning

Simulation ends at **bounded physical and logical behavior**.

---

## Envelope-First Simulation Principle

All simulated outputs are envelopes:

- VoltageEnvelope
- WavelengthEnvelope
- TimingEnvelope
- PowerEnvelope

If a simulation produces a scalar value, it is invalid.

---

## Conceptual Outcome

After simulation convergence:

- Hardware becomes a verification artifact
- Runtime becomes a replay of a known-safe path
- Unexpected behavior always faults safely

