# Complete Deployment Guide: From Budget to Operational

This guide is for a **complete beginner** — no soldering, no Linux, and no programming experience assumed. It takes you step by step from budgeting and buying parts through delivery, assembly, software setup, calibration, and daily operation until the system is live and you have completed the two-way optical link at least once. The narrative end state of this process is **system deployed and operational; ETs having landed on Earth** — meaning you have the hardware and procedures in place and have successfully run the detect-and-respond loop.

**What you will have at the end:** Hardware deployed (photodiode, laser, Raspberry Pi, pan-tilt), software running, and the ability to run the NHI detection loop: when the detection envelope is satisfied, you click "Send response (uplink)" to complete the two-way link. No identification or contact is claimed — only envelope-based detection and controlled emission per NIoLS doctrine.

**Time:** Allow several weeks for ordering, delivery, and (if you get help) assembly. Software setup and calibration can be done in a day or two once hardware is ready.

**Budget:** See Phase 1. Total is approximately **$600 minimum**, **$800–$1400 recommended** (with safety goggles), and **under $2000** for full spec including laser power meter. All figures in Australian dollars (AUD); check suppliers for current stock and prices.

---

## Phase 0: Before You Start

1. **Who this is for.** You do not need any technical skills. Where a step requires soldering, circuit reading, or command-line use, the guide either explains the minimal action in plain language or tells you to give specific documents to a technician or experienced friend.

2. **What you will have at the end.** A working NIoLS system: photodiode detects light in the 320–1100 nm band; the software shows when the "detection envelope" is satisfied (signal above a baseline); you arm the system and, when the envelope is satisfied, click "Send response (uplink)" to send the laser pattern. That completes the two-way optical link once. You then have the hardware and procedures for ongoing operation per the ET Engineering Interface Model.

3. **Safety.** The system uses a **Class 1M laser** (≤1 mW). In Australia, Class 1M does not require a licence for general use, but you must never point the laser at people, animals, or aircraft (pointing at aircraft is illegal and can result in serious penalties). See [docs/safety_compliance.md](safety_compliance.md) and [hardware/laser_transmitter/safety_protocols.md](../hardware/laser_transmitter/safety_protocols.md). Safety is called out again at purchase, assembly, and operation.

---

## Phase 1: Budget

Use the ranges below to plan your spending. Prices are approximate; check each supplier for current AUD and availability.

| Category | Minimum (AUD) | Recommended (AUD) | Full spec (AUD) |
|----------|---------------|--------------------|-----------------|
| Control board + PSU + storage (Raspberry Pi 4, 5V PSU, microSD) | 120 | 140 | 165 |
| Photodiode subsystem (photodiode, op-amp, ADC, passives, enclosure) | 200 | 250 | 290 |
| Laser subsystem (650 nm 1 mW module, driver parts, interlock, enclosure) | 20 | 50 | 80 |
| Time-varying pointing (pan-tilt bracket + servos) | 25 | 35 | 40 |
| Safety (laser goggles 650 nm; optional power meter) | 0 | 250 | 500 |
| Miscellaneous (cables, headers, solder, enclosures, shipping) | 50 | 80 | 120 |
| **Total** | **~600** | **~800–1400** | **< 2000** |

- **Minimum:** No goggles or power meter; basic laser and photodiode parts; you assume responsibility for eye safety and power verification.
- **Recommended:** Laser safety goggles (650 nm, OD as per AS/NZS); quality parts; still under $2000.
- **Full spec:** Add laser power meter (~$50–200) for verifying ≤1 mW; premium components; all under $2000.

Detailed parts and suppliers are in [hardware/photodiode_detector/parts_list.md](../hardware/photodiode_detector/parts_list.md) and [hardware/laser_transmitter/parts_list.md](../hardware/laser_transmitter/parts_list.md). Physical deployment (time-varying pointing) is described in [docs/technical_specifications.md](technical_specifications.md).

---

## Phase 2: Purchase

Order the following from Australian suppliers or those that ship to Australia. Add items to cart, checkout, and pay with a credit or debit card. If an item is out of stock, check the supplier’s website for alternatives or order from another supplier in the list.

**Approximate prices below are in AUD including GST where applicable; confirm on the supplier’s site.**

### Core Electronics (core-electronics.com.au)

| Item | Part / description | Approx. price (AUD) |
|------|--------------------|----------------------|
| Raspberry Pi 4 Model B 4GB | Control computer; use Pi 4 (not Pi 5) for software compatibility | 94–100 |
| Official 5V 3A USB-C power supply | For Raspberry Pi | 15–20 |
| microSD card 32GB or larger | For Raspberry Pi OS | 10–15 |
| ADS1115 16-bit I2C ADC breakout | Adafruit or equivalent; 4-channel, I2C address 0x48 | 28–31 |
| Pan-tilt bracket kit (with servos) | 2-axis mount for time-varying pointing (e.g. SparkFun ROB-14391 or similar) | 23–28 |

**If ADS1115 is out of stock:** Altronics sells an ADS1115 module (see below). You can also search Core Electronics for "ADS1115" or "16-bit ADC I2C".

### Altronics (altronics.com.au)

| Item | Part / description | Approx. price (AUD) |
|------|--------------------|----------------------|
| 650 nm 1 mW red laser module | e.g. Z1692; Class 1M compatible; verify ≤1 mW with power meter if possible | 5–8 |
| ADS1115 16-bit ADC module | Alternative if not bought from Core Electronics | ~21 |

### Jaycar Electronics (jaycar.com.au)

| Item | Part / description | Approx. price (AUD) |
|------|--------------------|----------------------|
| Resistors (1 MΩ, 10 kΩ, 4.7 kΩ, 1 kΩ, 220 Ω, 47 Ω) | Metal film 1% where specified in parts lists | 5–10 |
| Capacitors (10 pF, 1 nF, 100 nF, 100 μF, 10 μF ceramic/electrolytic) | As per [hardware/photodiode_detector/parts_list.md](../hardware/photodiode_detector/parts_list.md) and laser parts list | 5–10 |
| OPA627 or alternative op-amp | Low-noise op-amp for photodiode amplifier; if not at Jaycar, use Element14/Mouser | 2–25 |
| 2N2222 NPN transistor | For laser driver | under 1 |
| SPST normally closed switch | Safety interlock | 3–6 |
| Red LED 3 mm + 220 Ω resistor | Interlock status indicator | under 1 |
| Project boxes (e.g. 100×80×50 mm) | One for photodiode board, one for laser board | 10–20 |
| M3 screws and standoffs | PCB mounting | 2–4 |
| 5V 1A wall adapter (if not using regulator on board) | Optional; can use same as Pi if current is sufficient | 10–15 |

### Element14 Australia (au.element14.com) or Mouser Australia (mouser.com.au)

| Item | Part / description | Approx. price (AUD) |
|------|--------------------|----------------------|
| Hamamatsu S1227-1010BR photodiode | Silicon, 320–1100 nm, 10×10 mm; or equivalent from parts list | 35–80 |
| OPA627AP op-amp | Low-noise, for photodiode transimpedance amplifier | 25–40 |

**If S1227-1010BR is unavailable:** Contact **Stantron** (stantron.com.au), the Hamamatsu distributor in Australia, or order an equivalent silicon photodiode (400–1100 nm) from the alternatives in [hardware/photodiode_detector/parts_list.md](../hardware/photodiode_detector/parts_list.md).

### Laser safety (recommended)

| Item | Where | Approx. price (AUD) |
|------|--------|----------------------|
| Laser safety goggles, 650 nm, OD suitable for Class 1M | e.g. lasersafetyglasses.com.au, laserglasses.com.au | 200–310 |

### Optional: laser power meter

| Item | Where | Approx. price (AUD) |
|------|--------|----------------------|
| Laser power meter (to verify ≤1 mW) | Altronics, Element14, or online | 50–200 |

**What to do if something is out of stock:** Try the same supplier’s search or "alternatives"; use another supplier from the list; or refer to the "Alternative Parts" sections in [hardware/photodiode_detector/parts_list.md](../hardware/photodiode_detector/parts_list.md) and [hardware/laser_transmitter/parts_list.md](../hardware/laser_transmitter/parts_list.md).

---

## Phase 3: Delivery

1. **Track your orders.** Use the tracking links in the confirmation emails from each supplier. Note expected delivery dates.

2. **When each parcel arrives:** Open it and check the contents against the packing slip or order summary. Verify that nothing is obviously damaged (crushed, wet, or broken).

3. **List what each box should contain** (by supplier):
   - **Core Electronics:** Raspberry Pi 4, PSU, microSD, ADS1115 breakout, pan-tilt kit (and any other items you ordered).
   - **Altronics:** Laser module, and if ordered, ADS1115 module.
   - **Jaycar:** Resistors, capacitors, transistor, switch, LED, enclosures, screws/standoffs, and any other small parts.
   - **Element14 / Mouser:** Photodiode, OPA627 (or equivalent).
   - **Laser safety:** Goggles (and optional power meter).

4. **If anything is missing or damaged:** Contact the supplier’s customer service with your order number and description. Keep the packaging until the matter is resolved.

5. **Store everything** in a dry, safe place until you are ready for assembly. Keep small parts in labelled bags so you can find them later.

---

## Phase 4: Assembly

You have two paths: **get help** (no soldering or circuit experience) or **do it yourself** (you are willing to follow circuit diagrams and solder).

### Path A: Get help

If you do **not** solder or read circuit diagrams:

1. Gather these documents from the NIoLS repo:
   - [hardware/photodiode_detector/assembly_instructions.md](../hardware/photodiode_detector/assembly_instructions.md)
   - [hardware/photodiode_detector/parts_list.md](../hardware/photodiode_detector/parts_list.md)
   - [hardware/laser_transmitter/circuit_design.md](../hardware/laser_transmitter/circuit_design.md)
   - [hardware/laser_transmitter/parts_list.md](../hardware/laser_transmitter/parts_list.md)
   - [docs/safety_compliance.md](safety_compliance.md) (for laser safety and legal requirements)

2. Take these documents and **all the parts you purchased** to an electronics technician or an experienced friend. Ask them to:
   - Build the **photodiode module** (photodiode + op-amp circuit + ADC) per the photodiode assembly instructions and parts list.
   - Build the **laser module** (laser + driver circuit + safety interlock) per the laser circuit design and parts list.
   - Mount the photodiode module and laser module on the **pan-tilt** so that the laser and photodiode can be pointed (time-varying pointing for physical deployment).

3. When you get the assembled units back, you will still need to **connect them to the Raspberry Pi** (Phase 4, "Connecting to the Raspberry Pi" below). You can do that with jumper wires and pin headers; if you prefer, ask the same person to do the wiring using the pin assignments in the next section.

### Path B: Do it yourself

If you are willing to solder and follow circuit diagrams:

1. **Tools you need:** Soldering iron, solder, multimeter, wire cutters/strippers, small screwdriver. Optional: helping hands, magnifier.

2. **Photodiode module:** Follow [hardware/photodiode_detector/assembly_instructions.md](../hardware/photodiode_detector/assembly_instructions.md) step by step. Use [hardware/photodiode_detector/parts_list.md](../hardware/photodiode_detector/parts_list.md) for part numbers and values. Build the transimpedance amplifier (op-amp + feedback resistor/capacitor), connect the photodiode, add the low-pass filter if desired, and connect the output to the ADS1115 input. Mount the ADS1115 breakout and photodiode board in an enclosure.

3. **Laser module:** Follow [hardware/laser_transmitter/circuit_design.md](../hardware/laser_transmitter/circuit_design.md) and [hardware/laser_transmitter/parts_list.md](../hardware/laser_transmitter/parts_list.md). Build the laser driver (current-limiting resistor, transistor, base resistor), the safety interlock circuit (switch, pull-up, status LED), and connect the laser module. Mount everything in an enclosure. **Never point the laser at people, animals, or aircraft.**

4. **Pan-tilt:** Assemble the pan-tilt kit according to its instructions. Mount the photodiode enclosure and the laser enclosure on the pan-tilt so that both can be aimed together (time-varying pointing). You will drive the servos from the Raspberry Pi later if required; for the first pass, manual alignment is enough.

5. **Connecting to the Raspberry Pi:** With power **off**:
   - **ADS1115 (photodiode):** Connect VDD to 3.3 V, GND to GND, SDA to Pi GPIO 2 (SDA), SCL to Pi GPIO 3 (SCL). I2C address is 0x48 by default.
   - **Laser:** Connect laser driver control input to **GPIO 18** (PWM). Connect laser power supply and ground as per your driver circuit.
   - **Interlock:** Connect the interlock signal to **GPIO 23** (and pull-up to 3.3 V as in the circuit design). When the safety switch is closed, the Pi will see a "safe" state and allow arming.
   - **Power:** Supply 5 V to the Pi and to any regulator on the photodiode/laser boards as needed.

6. **Smoke test:** With the safety interlock **closed** (safe to enable), power on the Raspberry Pi and the photodiode/laser boards. There should be no smoke or smell. Check that the interlock LED (if fitted) shows "safe" when the switch is closed. Do not enable the laser yet; that happens from the software after calibration and arming.

---

## Phase 5: Software setup

Assume you have a **Raspberry Pi 4** with no prior Linux experience. Do the following in order.

1. **Flash Raspberry Pi OS to the microSD card.**
   - On another computer, download **Raspberry Pi Imager** from the official Raspberry Pi website.
   - Install and open it. Select **Raspberry Pi OS** (recommended: 32-bit or 64-bit with desktop).
   - Select your microSD card as the target. Click "Write" and wait until it finishes.
   - Eject the microSD card and insert it into the Raspberry Pi.

2. **Boot the Pi and connect it.**
   - Connect keyboard, mouse, and monitor (HDMI). Connect the Pi to your network (Ethernet or Wi-Fi).
   - Power on the Pi. Follow the first-run wizard: set language, time zone, and a password. Connect to Wi-Fi if you use it.

3. **Enable I2C** (needed for the ADS1115).
   - Open the main menu → Preferences → Raspberry Pi Configuration (or run `sudo raspi-config` in a terminal).
   - Under **Interfaces**, enable **I2C**. Reboot if asked.
   - Optional: enable **SSH** if you want to control the Pi from another computer.

4. **Copy the NIoLS project onto the Pi.**
   - If you have the NIoLS repo on a USB stick or another computer: copy the whole `NIoLS` folder onto the Pi (e.g. into your home folder or `~/NIoLS`).
   - If you use Git: open a terminal and run:  
     `git clone <repository-URL> NIoLS`  
     (replace `<repository-URL>` with the actual repo URL.)

5. **Install Python and project dependencies.**
   - Open a terminal. Go to the software folder and install Python packages:
     ```bash
     cd ~/NIoLS/software
     pip install -r requirements.txt
     ```
     (If the system says `pip` not found, try `pip3` instead of `pip`, or install Python 3.8+ first.)
   - Check that key packages are there:
     ```bash
     python3 -c "import yaml, numpy; print('OK')"
     ```

6. **Install Node.js and frontend dependencies.**
   - Install Node.js 18 or newer if not already installed (e.g. from nodejs.org or your Pi’s package manager).
   - Then:
     ```bash
     cd ~/NIoLS/frontend
     npm install
     ```

7. **Configuration file.**
   - The config file is `NIoLS/software/config/device_config.yaml`. For a first run, you can leave it as-is. Defaults assume: I2C address 0x48, laser on GPIO 18, interlock on GPIO 23. If your wiring is different, edit the `hardware.photodiode` and `hardware.laser` sections with the correct pins and I2C address.

8. **Verify and start the device.**
   - From a terminal:
     ```bash
     cd ~/NIoLS/software
     python3 start_device.py
     ```
   - If the backend starts without errors, open a **web browser on the same machine** and go to:  
     **http://localhost:8000**  
   - If you run the frontend separately for development (e.g. `npm run dev` in the `frontend` folder), the app may be at `http://localhost:3000` and will talk to the API on port 8000. For normal operation, `start_device.py` can serve the built frontend; see [README.md](../README.md) and [PROFESSIONAL_SETUP.md](../PROFESSIONAL_SETUP.md).

9. **Optional: run tests.**  
   From the project root:  
   `cd ~/NIoLS/tests && python3 run_tests.py`  
   This checks that the software and config are consistent. Some tests may require hardware to be connected.

You should now see the NIoLS interface in the browser. Next is calibration, then operation.

---

## Phase 6: Calibration

Calibration sets the "dark" level and the baseline above which the system considers the detection envelope satisfied. See [docs/technical_specifications.md](technical_specifications.md) for more detail.

1. **Dark voltage (photodiode with no light).**
   - Cover the photodiode completely (e.g. with opaque material). Run the device and note the voltage shown for the photodiode channel (or read it from the measurement display).
   - Open `NIoLS/software/config/device_config.yaml`. In the **calibration** section, set **dark_voltage** to that value (e.g. `0.0` or whatever you measured). Save the file.

2. **Baseline above dark (detection threshold).**
   - In the same config file, find **et_interface** → **detection**. Set **baseline_above_dark_v** to the minimum voltage above dark that should count as "signal present" (e.g. `0.02` for 20 mV). Save the file.
   - The detection envelope is satisfied when the measured voltage is at least dark_voltage + baseline_above_dark_v and the wavelength is in the 320–1100 nm band (see config).

3. **Optional: wavelength calibration.**  
   If you have known light sources (e.g. LEDs or lasers at known wavelengths), you can add calibration points to **calibration.points** in `device_config.yaml` (wavelength in nm, voltage in V). This improves wavelength display; it is not required for the NHI envelope logic.

Restart the device after any config change so the new calibration is loaded.

---

## Phase 7: Operation

This is the daily or session procedure to run the NHI detection loop and complete the two-way link when the envelope is satisfied. It follows [docs/NHI_Detection_Prototype.md](NHI_Detection_Prototype.md) "How to Run".

1. **Start the device.**  
   Run `python3 start_device.py` from `NIoLS/software` and open the browser to the URL shown (e.g. http://localhost:8000).

2. **Initialize hardware.**  
   In the sidebar, click **Initialize** (or equivalent). The system should move to state **INITIALIZED** (config and calibration loaded).

3. **Arm the system.**  
   Click **Arm**, then **Confirm arm**. The system should move to **EMIT_READY**. The safety interlock must be closed (switch engaged); otherwise arming will not succeed.

4. **Start measurement.**  
   Start the measurement loop so the photodiode is read and the detection envelope is updated each cycle.

5. **Open the NHI Detection Envelope panel.**  
   In the GUI, find the **NHI Detection Envelope** section (below Wavelength Measurement). It shows:
   - **Envelope status:** Satisfied or Not satisfied.
   - **Envelope satisfied** means: optical signal in the 320–1100 nm band is above the baseline (dark + baseline_above_dark_v). **No identification or contact is claimed** — only that the envelope condition is met.

6. **Send response when the envelope is satisfied.**  
   When the panel shows **Envelope: Satisfied** and the state is **EMIT_READY**, click **Send response (uplink)**. The system will emit the configured laser pattern (e.g. geometric circle, size 12) and complete the two-way optical link once.

**Session checklist:** Power on → Check interlock closed → Start device → Initialize → Arm → Confirm arm → Start measurement → Open NHI panel → When envelope satisfied and EMIT_READY, click "Send response (uplink)".

**Safety:** Never point the laser at people, animals, or aircraft. Keep the safety interlock engaged except when intentionally testing. See [docs/safety_compliance.md](safety_compliance.md) and [hardware/laser_transmitter/safety_protocols.md](../hardware/laser_transmitter/safety_protocols.md).

---

## Phase 8: Success / End state

**"ETs having landed on Earth"** in this guide means: **the system is deployed and operational, and you have completed the two-way optical link at least once** — i.e. the detection envelope was satisfied and you clicked "Send response (uplink)" to send the laser pattern.

You are now in the state where:
- Hardware is in place (photodiode, laser, Raspberry Pi, time-varying pointing).
- Software is running and calibration is set.
- You can run the NHI loop whenever you want: initialize → arm → measure → respond when the envelope is satisfied.

**Next steps:**
- Operate per the **protocol constraints** in [docs/ET_Engineering_Interface_Model.md](ET_Engineering_Interface_Model.md): do not interfere with any human detection systems; do not use language that causes direct fear (indirect fear is acceptable) in UI, runbooks, logs, or docs.
- Maintain **safety**: interlock, power limit (≤1 mW), goggles when appropriate, and never point at aircraft or people.
- Run the loop as needed; the system is ready for ongoing operation per the ET Engineering Interface Model.

---

## Reference summary

| Phase | Key documents |
|-------|----------------|
| Budget & parts | [hardware/photodiode_detector/parts_list.md](../hardware/photodiode_detector/parts_list.md), [hardware/laser_transmitter/parts_list.md](../hardware/laser_transmitter/parts_list.md), [docs/technical_specifications.md](technical_specifications.md) |
| Assembly | [hardware/photodiode_detector/assembly_instructions.md](../hardware/photodiode_detector/assembly_instructions.md), [hardware/laser_transmitter/circuit_design.md](../hardware/laser_transmitter/circuit_design.md), [hardware/laser_transmitter/parts_list.md](../hardware/laser_transmitter/parts_list.md), [docs/safety_compliance.md](safety_compliance.md) |
| Software & config | [README.md](../README.md), [PROFESSIONAL_SETUP.md](../PROFESSIONAL_SETUP.md), [docs/user_manual.md](user_manual.md), [software/config/device_config.yaml](../software/config/device_config.yaml) |
| Operation & NHI | [docs/NHI_Detection_Prototype.md](NHI_Detection_Prototype.md), [docs/ET_Engineering_Interface_Model.md](ET_Engineering_Interface_Model.md) |
| Safety | [docs/safety_compliance.md](safety_compliance.md), [hardware/laser_transmitter/safety_protocols.md](../hardware/laser_transmitter/safety_protocols.md) |

---

*This document is part of the NIoLS project. All claims about detection and response are envelope-based; no identification or contact is claimed.*
