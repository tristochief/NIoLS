 # Simulation Rationale for NIoLS

## Purpose

This document explains **why simulation is structurally required for NIoLS**, not optional, and how simulation directly enforces the historical, physical, institutional, and safety constraints already embedded in the system.

Simulation in NIoLS is not about optimization for speed or cost alone.
It exists to **prevent collapse modes** identified throughout the embedded research.

---

## Why Physical Iteration Is Forbidden by Design

From the embedded research:

- Repeated physical iteration invites:
  - institutional attention
  - uncontrolled replication
  - parameter drift
  - militarization risk
- Physical trial-and-error recreates Lyra-style escalation patterns

Therefore:

> **NIoLS must converge before hardware exists.**

Simulation is the only lawful convergence mechanism.

---

## Simulation as Constraint Enforcement

Simulation replaces physical iteration in the following areas:

| Constraint | Simulation Role |
|-----------|-----------------|
| Laser safety (Class 1M) | Envelope validation before emission |
| Determinism | FSM path simulation |
| Non-replicability | Hash-bound configuration simulation |
| No false certainty | Envelope-based signal modeling |
| Auditability | Trace replay and verification |
| Minimal energy footprint | Emission budget simulation |

---

## Simulation Is the “Pre-Hardware FSM”

NIoLS already enforces a runtime FSM:

SAFE → INITIALIZED → ARMED → EMIT_READY → EMITTING → FAULT

Simulation is the **pre-runtime mirror** of this FSM.

No hardware state should ever be entered unless its simulation state has already converged.

---

## Conclusion

Simulation is not a development convenience.

It is how NIoLS:
- avoids historical failure modes
- avoids unsafe iteration
- avoids epistemic overreach
- avoids institutional capture

Without simulation, NIoLS cannot exist lawfully.

