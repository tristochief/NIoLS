# Photodiode Detector Circuit Design

## Overview

This circuit design provides signal conditioning for a silicon photodiode to measure optical wavelengths in the 400-1100 nm range. The circuit converts photodiode current to a voltage signal suitable for ADC sampling.

## Circuit Architecture

### Components

1. **Photodiode:** Hamamatsu S1227-1010BR (or equivalent)
   - Wavelength range: 320-1100 nm
   - Active area: 10×10 mm
   - Dark current: <1 nA
   - Capacitance: 320 pF (at 0V bias)

2. **Transimpedance Amplifier (TIA):**
   - Op-amp: OPA627 or AD795 (low noise, low bias current)
   - Feedback resistor: 1 MΩ (adjustable for gain)
   - Feedback capacitor: 10 pF (for stability)

3. **Low-Pass Filter:**
   - Cutoff frequency: 10 kHz (reduces noise)
   - Second-order Sallen-Key filter

4. **ADC Interface:**
   - ADC: ADS1115 (16-bit, I2C interface) or MCP3008 (10-bit, SPI)
   - Reference voltage: 3.3V or 5V
   - Sampling rate: Up to 860 samples/second (ADS1115)

## Circuit Schematic

```
                    +Vcc (5V)
                     |
                     |
        Photodiode   |   R1 (1MΩ)
        (Cathode)----+----/\/\/\----+
                     |              |
                     |              |
        Photodiode   |              |  Output to ADC
        (Anode)------+--------------+------> Vout
                     |              |
                     |              |
                     |              C1 (10pF)
                     |              |
                     |              |
                    GND            GND
                     |
                     |
                  Op-Amp
                  (OPA627)
                  Pin 2: Inverting Input
                  Pin 3: Non-inverting Input (GND)
                  Pin 7: +Vcc
                  Pin 4: -Vcc (or GND for single supply)
                  Pin 6: Output
```

### Detailed TIA Circuit

```
                    +5V
                     |
                     R2 (10kΩ)
                     |
                     +---[Op-Amp +Input]---+
                     |                     |
                     |                     |
        Photodiode   |                     |
        (Cathode)----+---[Op-Amp -Input]--+---[Output]---> Vout
                     |                     |
                     |                     |
        Photodiode   |                     |
        (Anode)------+---------------------+
                     |                     |
                     |                     |
                     R1 (1MΩ)             C1 (10pF)
                     |                     |
                     |                     |
                    GND                   GND
```

### Low-Pass Filter (Optional, for noise reduction)

```
Vout (from TIA) ---[R3: 10kΩ]---+
                                |
                                C2 (1nF)
                                |
                                +---[Op-Amp +Input]---+
                                |                     |
                                |                     |
                               GND                    |
                                                      |
                                                      +---> Filtered Output
                                                      |
                                                    [R4: 10kΩ]
                                                      |
                                                    [C3: 1nF]
                                                      |
                                                     GND
```

## Component Specifications

### Op-Amp (OPA627)
- Input bias current: <1 pA
- Input offset voltage: <100 μV
- Gain bandwidth product: 16 MHz
- Slew rate: 55 V/μs
- Supply voltage: ±4.5V to ±18V (or single supply 9V to 36V)

### Feedback Resistor (R1)
- Value: 1 MΩ (adjustable: 100kΩ to 10MΩ for different gain)
- Type: Metal film, 1% tolerance
- Power rating: 0.125W minimum

### Feedback Capacitor (C1)
- Value: 10 pF (adjustable for stability)
- Type: Ceramic, NPO/C0G
- Voltage rating: 50V minimum

### Power Supply
- Voltage: +5V (single supply) or ±5V (dual supply)
- Current: <10 mA per op-amp
- Regulation: ±1% or better
- Noise: <100 μV RMS

## Gain Calculation

The transimpedance gain is:
```
Vout = I_photodiode × R1
```

For a photodiode current of 1 μA and R1 = 1 MΩ:
```
Vout = 1 μA × 1 MΩ = 1 V
```

## ADC Interface

### ADS1115 Configuration
- I2C address: 0x48 (default)
- Input range: ±4.096V (programmable)
- Resolution: 16 bits (65,536 levels)
- Sampling rate: 8-860 samples/second
- Interface: I2C (SDA, SCL)

### Voltage Scaling
If ADC reference is 3.3V and photodiode output is 0-5V:
- Add voltage divider: 3.3V / 5V = 0.66 ratio
- Use 10kΩ and 5kΩ resistors in series

## Calibration Procedure

1. **Dark Current Measurement:**
   - Cover photodiode completely
   - Measure output voltage (should be near 0V)
   - Record as baseline offset

2. **Known Wavelength Sources:**
   - Use monochromatic LED sources at known wavelengths
   - Measure output voltage at each wavelength
   - Create calibration table: wavelength vs. voltage

3. **Wavelength Calculation:**
   - Interpolate measured voltage to find corresponding wavelength
   - Use polynomial fit or lookup table

## PCB Layout Considerations

1. **Shielding:** Place photodiode in shielded enclosure to reduce ambient light
2. **Ground Plane:** Use ground plane for noise reduction
3. **Component Placement:** Keep op-amp close to photodiode
4. **Power Decoupling:** Add 100nF ceramic capacitor near op-amp power pins
5. **Trace Routing:** Keep feedback path short to minimize capacitance

## Testing

1. **Functional Test:**
   - Apply known light source
   - Verify output voltage changes proportionally
   - Check for oscillations (should be stable)

2. **Noise Test:**
   - Measure output with photodiode covered
   - RMS noise should be <10 mV

3. **Linearity Test:**
   - Vary light intensity
   - Verify linear relationship between current and voltage

## Parts List

| Component | Part Number | Quantity | Notes |
|-----------|-------------|----------|-------|
| Photodiode | Hamamatsu S1227-1010BR | 1 | 320-1100 nm range |
| Op-Amp | OPA627AP | 1 | Low noise, low bias current |
| Feedback Resistor | 1 MΩ, 1%, 0.125W | 1 | Metal film |
| Feedback Capacitor | 10 pF, NPO, 50V | 1 | Ceramic |
| Filter Resistor | 10 kΩ, 1%, 0.125W | 2 | For low-pass filter |
| Filter Capacitor | 1 nF, NPO, 50V | 2 | For low-pass filter |
| ADC | ADS1115 | 1 | 16-bit I2C ADC |
| Power Supply | 5V, 500mA | 1 | Regulated supply |
| Decoupling Capacitor | 100 nF, 50V | 2 | Ceramic, near op-amp |

## Alternative Components

- **Op-Amp Alternatives:** AD795, LMC662, TL071
- **ADC Alternatives:** MCP3008 (SPI), ADS1015 (12-bit I2C)
- **Photodiode Alternatives:** Any silicon photodiode with 400-1100 nm range

## Safety Notes

- Photodiode is passive component, no high voltage hazards
- Op-amp operates at low voltage (5V), safe for handling
- Ensure proper power supply polarity to avoid damage
- Use ESD protection when handling components

