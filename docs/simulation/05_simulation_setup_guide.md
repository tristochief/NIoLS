# Simulation Setup Guide for NIoLS

## Environment Setup

1. Create Python virtual environment
2. Install simulation dependencies only
3. No GPIO, no I2C required

---

## Simulation-Only Configuration

Create `device_config.sim.yaml`:

- Reduced power budgets
- Fake hardware backend
- Simulation-only safety flags

This file must never be deployed to hardware.

---

## Running Core Simulations

### Electrical
- Run ngspice simulations
- Export envelope bounds
- Store results as reference JSON

### FSM
- Run FSM path exhaustion
- Validate no illegal emission paths exist

### Trace
- Simulate full session
- Verify root hash stability

---

## CI Integration

Simulation must run:
- On every commit
- Before any hardware test
- Before any release

Hardware tests must never run if simulation fails.

