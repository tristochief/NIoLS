# Photodiode Detector Assembly Instructions

## Prerequisites

- Basic soldering skills
- Multimeter for testing
- Oscilloscope (optional, for advanced testing)
- ESD-safe work area

## Step-by-Step Assembly

### 1. Prepare PCB/Protoboard

1. **Choose mounting method:**
   - Perfboard with point-to-point wiring
   - Custom PCB (recommended for production)
   - Breadboard (for prototyping only)

2. **Plan component placement:**
   - Keep photodiode separate from electronics (for shielding)
   - Place op-amp close to photodiode
   - Keep feedback path short
   - Provide adequate ground plane

### 2. Install Power Supply Circuit

1. **Install voltage regulator (if using):**
   - Mount LM7805 with heat sink if needed
   - Connect input capacitor (100 μF) to input pin
   - Connect output capacitor (10 μF) to output pin
   - Connect ground pin to ground plane

2. **Test power supply:**
   - Apply input voltage (7-12V DC)
   - Measure output: should be 5.0V ±0.1V
   - Check for ripple: should be <10 mV

### 3. Install Op-Amp Circuit

1. **Mount op-amp (OPA627):**
   - Pin 2: Inverting input (connect to photodiode cathode)
   - Pin 3: Non-inverting input (connect to ground)
   - Pin 4: Negative supply (ground for single supply)
   - Pin 7: Positive supply (+5V)
   - Pin 6: Output

2. **Install feedback components:**
   - Connect 1 MΩ resistor from pin 6 (output) to pin 2 (inverting input)
   - Connect 10 pF capacitor in parallel with resistor
   - Keep leads short to minimize stray capacitance

3. **Install decoupling capacitors:**
   - 100 nF ceramic capacitor from pin 7 to ground (close to op-amp)
   - 100 nF ceramic capacitor from pin 4 to ground (if using dual supply)

### 4. Install Low-Pass Filter (Optional)

1. **Build Sallen-Key filter:**
   - Connect 10 kΩ resistor from TIA output to filter input
   - Connect 1 nF capacitor from filter input to ground
   - Connect second 10 kΩ resistor to op-amp input
   - Connect second 1 nF capacitor from op-amp output to input

2. **Test filter:**
   - Apply test signal
   - Verify cutoff frequency (~10 kHz)

### 5. Install Photodiode

1. **Mount photodiode:**
   - Connect cathode to op-amp inverting input (pin 2)
   - Connect anode to ground
   - Keep leads short and shielded

2. **Install shielding:**
   - Place photodiode in light-tight enclosure
   - Use black anodized aluminum or similar
   - Provide small aperture for light input (if needed)

### 6. Install ADC Interface

1. **Mount ADS1115 module:**
   - Connect VDD to +5V
   - Connect GND to ground
   - Connect SDA to I2C data line
   - Connect SCL to I2C clock line
   - Connect A0 (or appropriate channel) to TIA output

2. **Install pull-up resistors (if not on module):**
   - 4.7 kΩ from SDA to +5V
   - 4.7 kΩ from SCL to +5V

3. **Voltage divider (if needed):**
   - If TIA output exceeds 3.3V, add voltage divider
   - Use 10 kΩ and 5 kΩ resistors for 3.3V/5V ratio

### 7. Final Assembly

1. **Mount in enclosure:**
   - Secure PCB to enclosure base
   - Install photodiode in separate compartment
   - Provide access for light input
   - Install connectors for power and I2C

2. **Cable management:**
   - Route I2C cables away from power lines
   - Use shielded cable for photodiode connection
   - Secure all cables to prevent strain

3. **Labeling:**
   - Label power input polarity
   - Label I2C connector pins
   - Add warning labels if applicable

## Testing Procedure

### 1. Power-On Test

1. **Check power supply:**
   - Measure voltage at op-amp power pins
   - Should be 5.0V ±0.1V
   - Check for oscillations (should be stable)

2. **Check dark current:**
   - Cover photodiode completely
   - Measure output voltage
   - Should be near 0V (may have small offset)

### 2. Functional Test

1. **Apply test light source:**
   - Use LED or flashlight
   - Shine on photodiode
   - Measure output voltage change
   - Should increase with light intensity

2. **Test linearity:**
   - Vary light intensity
   - Verify proportional voltage change
   - Check for saturation at high intensity

### 3. ADC Test

1. **Connect to Raspberry Pi or computer:**
   - Install I2C tools
   - Scan for ADS1115 (should appear at 0x48)
   - Read ADC values

2. **Verify readings:**
   - Compare ADC readings to multimeter measurements
   - Check for noise and stability
   - Verify full-scale range

### 4. Calibration Test

1. **Use known wavelength sources:**
   - Red LED (650 nm)
   - Green LED (530 nm)
   - Blue LED (470 nm)
   - Measure output voltage at each

2. **Create calibration table:**
   - Record wavelength vs. voltage
   - Use for wavelength calculation in software

## Troubleshooting

### Problem: No Output Signal

**Possible Causes:**
- Power supply not connected
- Op-amp not powered
- Photodiode reversed
- Feedback resistor open circuit

**Solutions:**
- Check all power connections
- Verify op-amp pin connections
- Check photodiode polarity
- Measure feedback resistor value

### Problem: Oscillations/Instability

**Possible Causes:**
- Insufficient feedback capacitance
- Long feedback path
- Poor power supply decoupling
- Stray capacitance

**Solutions:**
- Increase feedback capacitor (try 22 pF)
- Shorten feedback path
- Add more decoupling capacitors
- Use ground plane

### Problem: High Noise

**Possible Causes:**
- Poor grounding
- Power supply noise
- Electromagnetic interference
- Photodiode exposed to ambient light

**Solutions:**
- Improve ground connections
- Add power supply filtering
- Shield circuit from interference
- Ensure photodiode is properly shielded

### Problem: Non-Linear Response

**Possible Causes:**
- Op-amp saturation
- Photodiode saturation
- ADC range exceeded

**Solutions:**
- Reduce gain (smaller feedback resistor)
- Reduce light intensity
- Add voltage divider for ADC

## Safety Notes

- **Low Voltage:** Circuit operates at 5V, safe for handling
- **ESD Protection:** Use ESD-safe work area when handling components
- **Photodiode:** Passive component, no high voltage hazards
- **Power Supply:** Ensure proper polarity to avoid damage

## Next Steps

After assembly and testing:
1. Proceed to software calibration
2. Integrate with Raspberry Pi control system
3. Test with known wavelength sources
4. Document calibration data

