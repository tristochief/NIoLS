# Using Simulation to Advance NIoLS

## Simulation as the Primary Development Loop

NIoLS evolves through:

Simulation → Verification → Limited Hardware Validation → Freeze

Hardware is not exploratory.
Simulation is.

---

## Adding New Capabilities

When adding any feature:

1. Extend simulation envelopes
2. Update FSM simulation
3. Prove no new unsafe paths
4. Only then modify hardware code

---

## Improving Detection

Detection improvements must be:
- Replay-tested on prior sessions
- Envelope-widening, never narrowing
- Backward-compatible with session bundles

Simulation enables safe post-run analysis without altering history.

---

## Long-Horizon Stability

Simulation prevents:
- feature creep
- authority drift
- precision inflation
- institutional capture

The system remains lawful because simulation enforces restraint.

---

## Final Principle

> **If it cannot be simulated, it cannot exist in NIoLS.**

