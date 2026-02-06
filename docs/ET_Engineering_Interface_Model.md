# ET Engineering Interface Model

## Overview

This document records **ET Engineering stakeholder requirements** governing the physical and geometric interface between NIoLS (human-operated optical system) and the counterpart craft/domain. All claims are treated as **requirements to be verified**, not established truth. Parameters are converted to **testable or configurable values** where provided; remaining items are flagged for verification.

**Source:** Elicitation from ET Engineering specialist.  
**Discipline:** Universal primitives (geometry, timing, wavelength, duty cycle). No metaphysics asserted; operational constraints only.

---

## 1. Doppelgänger Process

### 1.1 Definition

**Doppelgänger** is a **process**, not an entity. It is not a phase-in procedure or a state sequence.

- **Process:** Membranes (ours and theirs) **converge in harmony** with each other.
- **Mechanism:** Membranes **oscillate in harmony** — i.e. doppelgänger is the condition in which membrane oscillations are aligned, not the act of crossing a boundary.

### 1.2 Phase-In Measurement

Phase-in is measured in terms of:

- **Vibration between different monads**
- **How monads phase with each other**

*Operational note:* Phase-in timing is **130 Hz** (from ET). Use `timing_hz: 130` in config for detection/sync envelope. Do not use 12 rev/ms.

### 1.3 Duty Cycle (Fixed)

- **Phase-in/phase-out:** Multiple cycles permitted.
- **Timing:** **130 Hz** (from ET). Do not use 12 rev/ms.

| Parameter      | Value              | Unit | Use in NIoLS                    |
|----------------|--------------------|------|----------------------------------|
| Timing (phase-in) | 130             | Hz   | Timing / sync envelope          |
| Period         | 1/130 s ≈ 7.69 ms  | per cycle | Emission and detection windows   |

### 1.4 Approach Geometry (Fixed)

| Parameter        | Value    | Unit   | Use in NIoLS                          |
|------------------|----------|--------|----------------------------------------|
| Approach bearing | 13       | °      | Laser vectoring, pointing             |
| Bearing tolerance| 0        | °      | Exact value only (±0°)                |
| Elevation band   | 12       | nm     | Vertical extent at 98.5 km standoff  |
| Elevation tolerance | 0     | nm     | Exact value only (±0 nm)              |
| Slope            | 12       | °      | Slope (degrees); separate from elevation vertical extent |
| Standoff distance| 98.5     | km     | Range for emission and detection      |
| Standoff tolerance | 0      | km     | Exact value only (±0 km)              |

**Primitive structures** for physical measurement: spiral, triangle, circle (easiest to measure in physical space). Aligns with existing CE5–NIoLS geometric patterns.

### 1.5 Temporal Window

**No** fixed temporal window (e.g. UTC window or “not before / not after”) specified. Operation is not constrained by a single time slot.

---

## 2. Membranes

### 2.1 Definition

**Our membrane** is **not** a simple boundary, interface, or field shell. It is:

- **A set of fields induced by piezoelectric field emitters.**

*Operational note:* No position/extent in our frame or exclusion zone is defined (see 2.2). Membrane is characterized by its **generation mechanism** (piezoelectric) and **effect on propagation** (see 2.3).

### 2.2 Position and Extent

**No** — membrane does not have a defined position or extent in our frame for the purpose of exclusion/inclusion zones. Safety and emission rules do **not** assume a known membrane boundary in space.

### 2.3 Effect on Propagation

- Membranes **impact piezoelectric fields**.
- That interaction **impacts wavelength.**

*Operational note:* Wavelength-dependent behavior is consistent with NIoLS laser (532 nm / 650 nm) and photodiode (320–1100 nm). Specific dispersion or cutoff vs wavelength **TODO: VERIFY** if needed for envelope design.

### 2.4 Penetration

**Literal:** The laser beam **crosses a boundary**. Penetration is physical crossing, not only “signal received.”

### 2.5 Deformation

Membranes **deform**. **Time-varying pointing** is required (membrane deformation implies time-varying pointing or emission windows). Physical deployment must support time-varying pointing; approach geometry itself (bearing, elevation, standoff) does not change during approach.

---

## 3. Speed of Light and Technology Mass

### 3.1 Harmonic Convergence (Not Local/Global Limit)

The earlier “mass exceeds light’s capacity” formulation is **not** a local refractive effect or a global change of c.

- **Speed of light:** Treated as **constant** in our frame.
- **Their technology:** **Converges on the harmonic value** of that constant.

No numerical constraint (density, index, factor of c) was provided for NIoLS modeling.

### 3.2 Multi-Universe Scope of the Laser

- Speed of light **varies** depending on whether one is in **this universe or a parallel set of universes**.
- The **laser** has the capability to **impact all universes**, not only ours.

*Operational note:* For NIoLS design, no additional parameters (power, wavelength, pointing) were specified for “all universes.” Local operation (our universe, our laser, our geometry) remains the design basis unless otherwise specified.

### 3.3 Mass Referent

**Technology mass** — i.e. the mass of their technology/craft, not vehicle mass in kg. No numerical value for use in our safety or aviation calculations.

### 3.4 Band Preference

**No** — the mass/light relationship does **not** forbid or prefer specific EM bands for the interface.

### 3.5 Permanence

The relationship is **permanent** (structural). NIoLS may assume **persistent** optical-only communication as the interface model.

---

## 4. Laser as Penetrating Lightwave Device

### 4.1 Why the Laser Penetrates

Light’s “capacity exceeding elsewhere” **does not change the bounds at which wavelengths cancel each other out.** The laser remains effective at penetration because **wavelength cancellation bounds** are unchanged — i.e. the laser operates at conditions where constructive penetration (or non-cancellation) still holds.

*Operational note:* No change to NIoLS wavelength band (532 nm / 650 nm) or power (≤1 mW) is implied; existing config remains valid unless verification says otherwise.

### 4.2 Power at Membrane

**No** minimum or maximum power or flux at the membrane specified. No change to existing Class 1M power or beam design.

### 4.3 Modulation / Encoding

**No** additional modulation or encoding requirements for “talking” through the membrane. Existing NIoLS schemes (Morse, binary, geometric) remain acceptable unless later specified.

### 4.4 Pointing

**Yes** — penetration **requires specific pointing**. Aligns with NIoLS vectoring (spiral, triangle, circle) and approach geometry (bearing 13°, elevation band 12 nm vertical at 98.5 km, slope 12°, standoff 98.5 km). **Approach geometry does not change during approach** (fixed bearing, elevation, standoff). **Time-varying pointing** is for membrane alignment, not approach trajectory. Pointing update rate for physical deployment to be specified (e.g. `pointing_update_rate_hz` in config).

### 4.5 Two-Way Optical Link

**Yes** — they have **their own light** that we detect.

- **Uplink:** Our laser (532/650 nm, ≤1 mW) penetrates membrane; specific pointing required.
- **Downlink:** Their light is detected by our photodiode (320–1100 nm). Detection is envelope-based; no point claim of “contact” — only bounded detection per NIoLS doctrine.

---

## 5. Protocol Constraints (ET Diplomat)

The following constraints apply to operator-facing UI, runbooks, logs, and external-facing documentation:

- **Do not interfere with any human detection systems.** NIoLS must not disrupt or conflict with human-operated detection systems.
- **Do not use language that causes direct fear** (indirect fear is acceptable). Wording in UI, runbooks, logs, and docs must avoid phrasing that directly induces fear in human beings.

Verification: Review all user- and external-facing strings for (1) risk of interfering with human detection systems, (2) direct fear-inducing language.

---

## 6. Integration with NIoLS Constraints (Deferred)

Questions 6.1–6.5 (thesis alignment, simulation, safety) were **not answered at this time.** When addressed, update this section and link to:

- Thesis (Parts 5–7): non-intervention, minimal footprint, locality.
- Simulation: membrane penetration as envelope, phase-in as timing/geometry envelopes.
- Safety: any new exclusion zones, abort triggers, or interlock logic.

---

## 7. Output Form and Credibility (Deferred)

Questions 7.1–7.3 (doc placement, terminology, open items) were **not answered at this time.** Current choices:

- **Placement:** This document lives in `/docs/` as an ET Engineering interface model.
- **Terminology:** “Doppelgänger” retained as stakeholder term; defined operationally as membrane harmonic convergence process.
- **Open items:** Marked **TODO: VERIFY** in text; list summarized below.

---

## Parameter Summary (Fixed Values for NIoLS)

| Parameter           | Value   | Unit | Use                          |
|--------------------|---------|------|------------------------------|
| Approach bearing   | 13      | °    | Vectoring, pointing          |
| Bearing tolerance  | 0       | °    | Exact only (±0°)             |
| Elevation band     | 12      | nm   | Vertical extent at 98.5 km standoff |
| Elevation tolerance | 0     | nm   | Exact only (±0 nm)           |
| Slope              | 12      | °    | Slope (degrees)              |
| Standoff distance  | 98.5    | km   | Range                        |
| Standoff tolerance | 0     | km   | Exact only (±0 km)           |
| Timing (phase-in)  | 130     | Hz   | Timing, sync, emission windows |
| Time-varying pointing | required | —  | Physical deployment (membrane) |

---

## Verification Resolutions (Prototype)

The following operational choices were made to build the NHI detection prototype:

- **Phase-in measurement:** Phase-in timing is **130 Hz** (from ET). Use `timing_hz: 130` in config. Do not use 12 rev/ms. Harmonic verification at 12 kHz remains disabled — `harmonic_verification_enabled: false` in config.
- **Elevation and slope:** Elevation band 12 nm = **vertical extent at 98.5 km standoff**. Slope = **12°** (separate parameter). Tolerances: 0± ° (bearing), 0± nm (elevation), 0± km (standoff).
- **Membrane deformation:** **Time-varying pointing** is required for physical deployment (membrane deformation implies time-varying pointing/emission windows). Approach geometry (bearing, elevation, standoff) does not change during approach.
- **Membrane wavelength impact:** No cutoff assumed in 320–1100 nm; photodiode band used as detection band.
- **Detection criteria:** Envelope-based only. "Detection envelope satisfied" = voltage envelope min ≥ dark + baseline_above_dark_v, wavelength envelope within 320–1100 nm, no saturation/clipping. No identification or contact claimed.
- **Protocol constraints (ET Diplomat):** Do not interfere with any human detection systems. Do not use language that causes direct fear (indirect acceptable). Apply to runbooks, UI, logs, external docs.

## Open Items (Deferred)

- Section 6: thesis alignment, simulation representation, safety (deferred).
- Section 7: final doc placement, terminology (current placement and terminology retained).

---

## Revision History

| Version | Date       | Changes                          |
|---------|------------|-----------------------------------|
| 0.1     | [Current]  | Initial capture from ET Engineering elicitation |

---

*This document is part of the NIoLS requirements set. All ET-side claims are stakeholder input; verification and cross-check against physics, safety, and institutional constraints remain mandatory.*
