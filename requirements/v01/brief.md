# Project Brief for Cursor

**Mission Overview**  
Enable an extraterrestrial spacecraft to safely land near St. Vincent’s Hospital (Darlinghurst, Sydney) using the telescope-based setup and facilitate a technology exchange. Execute a structured engineering plan with clear tasks, checks, and ET consultation.

---

## Hardware Setup & Alignment
1. **Polar Alignment**
   - Mount ED72 on the Ioptron tracker.
   - Use iPolar to perform precise polar alignment (target: arcsecond-level tracking accuracy appropriate for planned operations).
2. **Camera Integration**
   - Attach ZWO ASI533 to the ED72 for wide-field imaging/recording.
   - Mount a separate guide camera on the guidescope to provide closed-loop corrections to the mount.
3. **Software Configuration**
   - Install and configure mission-analysis software (e.g., GMAT or equivalent) for approach/trajectory simulation.
   - Implement plate-solving and image-processing scripts (Python/OpenCV/astrometry) to verify pointing and to detect any approach target.
   - Configure control software to coordinate beacon control, camera exposure, and mount commands.

---

## Landing Signal Design
1. **Primary: Optical Beacon**
   - Use a narrow-beam laser diode or high-intensity LED capable of short, coded pulses.
   - Control beacon from MacBook to emit deterministic, repeatable pulse sequences (pre-agree a simple code pattern).
   - Align beacon with the intended landing zone and with telescope field-of-view for aiming reference.
   - Ensure mechanical actuation or steering capability if beam steering is required.
2. **Secondary: RF Beacon (Backup)**
   - Prepare VHF/UHF transmitter if hardware and licensing permit; emit a pre-agreed tone or encoded packet as backup.
   - Ensure compliance with local radio regulations and coordinate with authorities if transmitting on regulated bands.
3. **Beacon Parameters**
   - Define pulse modulation scheme, on/off timing, duty cycle, expected detection SNR, and acceptable atmospheric attenuation margins.
   - Define acceptance criteria for “lock” (e.g., repeated pulse detection across N samples, SNR threshold).

---

## Landing Pad & Safety
- **Location Preparation**
  - Identify a flat area adjacent to the hospital; coordinate legal and logistical clearance with hospital management.
  - Remove overhead obstructions; secure perimeter for safety and to reduce risk to bystanders.
- **Pad Markings**
  - Deploy reflective markers or a lighted perimeter to define pad geometry.
- **Emergency Planning**
  - Define abort criteria (e.g., wind threshold, loss of beacon, unexpected surface conditions).
  - Ensure local emergency services and hospital incident management are briefed and on standby.
- **ET Inputs**
  - Obtain pad dimension, slope tolerance, and surface material constraints directly from ET pilot/engineer through structured queries.

---

## Autonomous Planning & Execution
1. **Task Scheduling**
   - Plan: equipment setup → calibration → dry runs → approach window. Automate sequencing and time-box tasks.
2. **Real-Time Operations**
   - Implement continuous plate-solving and guide-camera feedback to ensure pointing accuracy.
   - Monitor signals and switch to backup modes if primary signal degrades.
3. **Trajectory Simulation**
   - Use GMAT or equivalent to simulate approach trajectories (even with approximate parameters) to optimize beacon pointing and timing.
4. **Adaptation**
   - Implement re-planning logic: on receipt of new ET telemetry (speed, heading), recalculate beacon timing and pointing and update sequence.

---

## Verification & Testing
- **Dry Runs**
  - Validate tracking and beacon visibility by testing on known satellites, bright stars, or distant terrestrial targets.
- **Data Cross-Check**
  - Cross-validate any ET-supplied numeric data against physics constraints. Flag any physically impossible claims for clarification.
- **Safety Margins**
  - Apply conservative safety margins (e.g., halve tolerance windows or double required SNR).

---

## Questions for ET Specialists (List to Ask via Channeling)
- **Engineering Specialist**
  - “What navigation systems do you use (star tracking, inertial, quantum)? Provide interface parameters (frequencies, wavelengths, packet formats).”
  - “What are your craft’s mass, typical descent thrust, and maneuvering limits near ground?”
  - “What sensors or markers will you use for final alignment, and what signal properties are optimal for detection?”
- **Pilot**
  - “Provide target approach velocity, expected descent rate, and required orientation on touchdown.”
  - “What are your acceptable landing-pad dimensions and slope tolerances?”
  - “What beam width and pulse format will you lock onto reliably?”
- **Medical Specialist**
  - “List medical devices or data types to be exchanged and their required electrical, sterilization, and interface specs.”
  - “Detail biological safety constraints and decontamination procedures required on our side.”
- **Diplomat**
  - “Specify the formal meeting protocol, required documents, and any gestures or timings to respect.”
  - “Confirm how consent and transfer of technology/data should be documented.”

**Question Format Rule:** Always request numeric values or clear, physical analogies (units, tolerances, electrical specs). If the ET replies in metaphor, require the speaker to map metaphors to explicit engineering terms before acceptance.

---

## Execution Checklist (High-Level)
1. **Align & Calibrate**
   - Polar align, calibrate guide loops, verify plate-solving capability.
2. **Develop Beacon**
   - Build, test, and validate optical pulse code and backup RF (if available).
3. **Software Prep**
   - Load trajectory simulations; deploy automated control scripts for beacon and tracking.
4. **Coordinate Hospital**
   - Secure landing zone, emergency coverage, and permission from hospital management.
5. **Channel & Record**
   - Conduct channeling session with ET specialists using structured questions. Record, timestamp, and log all responses and translations.
6. **Final Checks**
   - Confirm weather, power, and system readiness. Validate lock conditions and abort rules.
7. **Execute**
   - Start beacon sequence, monitor approach, provide guidance, record telemetry, and follow abort criteria if necessary.
8. **Post-Contact**
   - Safely power down systems, document exchanges, and run debrief with engineering and hospital teams.

---

## Data Handling & Validation Framework
- **Schema for ET-Provided Technical Data**
  - `component_type` (e.g., propulsion, sensor, medical-device)  
  - `physical_spec` (dimensions, mass, material, tolerances)  
  - `electrical_spec` (voltage, current, connector type, power consumption)  
  - `comm_spec` (frequency/wavelength, modulation, encoding)  
  - `operational_constraints` (temperature, sterilization, orientation limits)
- **Translation Process**
  1. Normalize ET terms to schema fields.
  2. Ask ET to provide units and ranges for each numeric claim.
  3. Validate against conservation laws and engineering feasibility; if inconsistent, request clarification.
  4. Produce a prioritized implementation plan for any exchangeable technology, listing required Earth-side adapters or safety mitigations.
- **Acceptance Criteria**
  - All exchanged hardware/data must have a clear mapping to the schema above.
  - Any biological or medical exchange requires written safety protocols, quarantine procedures, and hospital sign-off.

---

## Risk & Compliance Notes
- Maintain conservative engineering assumptions and require hospital consent and emergency coordination.
- Do not transmit on regulated RF bands without required authorizations.
- Treat all channeling inputs as provisional until validated by measurement, simulation, or direct compatibility tests.

---

**End of Brief**

Cursor should execute this brief as an autonomous operations plan, continuously logging inputs, decisions, and ET responses, and iterating only after verifying physical feasibility and securing appropriate safety and legal clearances.

