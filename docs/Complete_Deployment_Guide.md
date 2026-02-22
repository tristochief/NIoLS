# Complete Deployment Guide: From Budget to Operational

This document is a **comprehensive deployment plan** that incorporates every answer provided in our conversation.  It combines the original NIoLS guide with modifications to accommodate a **Sky‑Watcher ED72 telescope**, **no soldering**, **no helper**, and **component selections and vendor references exclusively from the chat history**.  The guide maintains the full structure of the original (Phases 0 through 8) while integrating explicit vendor and part information gathered from prior messages.

---

## Phase 0: Before You Start

- **Target audience:** Complete beginners with no technical skills.  Where the original guide suggested handing circuits to a technician, this version replaces those circuits with prebuilt modules or specifies how to avoid soldering altogether.  
- **Outcome:** A functioning NIoLS system built on an ED72 telescope, capable of detecting optical signals in the 320–1100 nm band and sending a low‑power laser response when the detection envelope is satisfied.  
- **Safety:** The system uses a **Class 1M laser (≤ 1 mW)**.  Do not point the laser at people, animals or aircraft.  Always use the supplied **key‑switch interlock** and wear **650 nm safety goggles**.  

---

## Phase 1: Budget

The original guide categorised budget into control electronics, photodiode subsystem, laser subsystem, pan‑tilt, safety and miscellaneous costs.  The table below integrates all items from our discussion, including the heavy‑duty pan‑tilt head and tripod required for the ED72.  Prices are approximate in AUD and taken directly from our earlier answers.

| Category | Typical cost (AUD) | Notes |
|---|:---:|---|
| **Control (RPi 4 kit)** | 140 – 170 | Raspberry Pi 4 (4 GB) kit from Little Bird Electronics with PSU & microSD. |
| **Photodiode subsystem** | 100 – 150 | Hamamatsu S1223‑01 photodiode from RS Components【69213331202698†L80-L88】 plus pre‑built transimpedance amplifier module from eBay (AU $63.55). |
| **Laser subsystem** | 40 – 80 | ≤ 1 mW 650 nm laser module (Global Laser) with TTL enable. |
| **Motorised pan‑tilt & mount** | 850 – 1 000 | ZIFON PT‑5000 pan‑tilt head (eBay) and a 10 kg KentFaith tripod. |
| **ADS1115 ADC** | 30 – 40 | DFRobot Gravity I²C ADS1115 (Core Electronics). |
| **Interlock & wiring** | 20 – 40 | Key switch, Dupont leads and screw‑terminal adapters. |
| **Battery & buck converter** | 120 – 160 | RS PRO 12 V NiMH pack (1.3 Ah) plus 12 V → 5 V DC‑DC converter. |
| **Safety goggles** | 200 – 300 | 650 nm OD‑rated goggles (laserglasses.com.au). |

**Total:** Approximately **$1.5 k AUD**.  This aligns with the recommended range in the original guide (AU $800–$1 400) when adding the heavy‑duty mount.

---

## Phase 2: Purchase

The original guide split purchasing by supplier (Core Electronics, Altronics, Jaycar, Element14/Mouser).  In this update, we strictly reference vendors and product names from our discussion:

- **ZIFON PT‑5000 motorised pan‑tilt head** – eBay AU listing.  
- **KentFaith 10 kg tripod** – KentFaith product page.  
- **Hamamatsu S1223‑01 photodiode** – RS Components stock no. 415‑5722 (price ~$35.62 inc GST)【69213331202698†L80-L88】.  
- **Very Low Noise Large Area Photodiode Amplifier Module** – eBay AU listing, AU $63.55.  
- **DFRobot Gravity I²C ADS1115 module** – Core Electronics.  
- **Global Laser 650 nm module (≤ 1 mW, TTL/EN)** – RS Components.  
- **RS PRO 12 V NiMH battery pack** – RS Components (AU $99.59).  
- **Raspberry Pi 4 Model B kit** – Little Bird Electronics (AU $228.88).  
- **Miscellaneous wiring & enclosures** – project boxes and Dupont leads (Jaycar or equivalent).  
- **650 nm laser safety goggles** – lasersafetyglasses.com.au.  

These parts replace the original guide’s lists that required discrete resistors, op‑amps and transistors.

---

## Phase 3: Delivery

Unchanged from the original guide: track each shipment; verify all items upon arrival; inspect for damage; store parts safely and label small components.  Use vendor support if anything is missing or defective.

---

## Phase 4: Assembly (revised)

The original guide provided two paths: “get help” (hand circuits to a technician) and “do it yourself” with soldering.  **This version removes the helper path and eliminates soldering**:

1. **Mounting:** attach the ZIFON PT‑5000 to the KentFaith tripod; mount the ED72 on the pan‑tilt using its rings or dovetail; add an accessory plate for the photodiode and laser enclosures.

2. **Electronics housing:** place the ADS1115 and amplifier in small project boxes; mount the laser module and interlock in their own enclosure; secure the Raspberry Pi and battery pack near the base.

3. **Wiring:** use Dupont jumper wires and screw‑terminal adapters.  Connect the photodiode to the amplifier, amplifier to ADS1115, ADS1115 to Pi (SDA → GPIO 2, SCL → GPIO 3), laser EN to GPIO 18, interlock status to GPIO 23, and distribute power via the buck converter.  No soldering or component assembly is required.

4. **Safety & testing:** keep the interlock off during the smoke test; power up; verify the ADS1115 is detected at address 0x48; check dark voltage; only enable the laser once software is installed and calibrated.  This follows the smoke test instructions from the original Phase 4.

---

## Phase 5: Software setup (unchanged)

The software process matches the original guide: flash Raspberry Pi OS; boot and configure the Pi; enable I²C; clone the NIoLS project; install Python and Node.js dependencies; adjust `device_config.yaml` for your wiring (I²C address, GPIO pins); run `python3 start_device.py` and access the frontend at `http://localhost:8000`.

---

## Phase 6: Calibration

The calibration instructions remain the same: cover the photodiode; measure dark voltage; set `dark_voltage` and `baseline_above_dark_v` in the config; optionally add wavelength calibration points; restart the device to load new values.  The precise band coverage (320–1100 nm) comes from the S1223‑01 datasheet【69213331202698†L167-L171】.

---

## Phase 7: Operation

Operation follows the original guide’s finite‑state machine: initialise hardware, arm the system (interlock closed), start measurement, watch for envelope satisfaction, send the uplink, then disarm.  The only additions are:

- Use the pan‑tilt controls to aim the ED72; the heavy mount enables smooth motion with the telescope and accessories.  
- Always keep the **interlock key** to cut laser power in an emergency.  

---

## Phase 8: Success & next steps

Upon completing a single detect → response cycle, your ED72‑based NIoLS system is deployed.  Maintain the hardware, keep software up to date, recharge the battery pack, and consult the ET Engineering Interface Model for ongoing operational guidance.  The system is ready for repeated sessions at your discretion.