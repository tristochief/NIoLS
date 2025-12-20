# EUV Detector Specifications (12-13 nm)

## Overview

This document outlines the technical requirements and integration path for extreme ultraviolet (EUV) detectors capable of measuring wavelengths in the 12-13 nanometer range. These detectors are not currently available as commercial off-the-shelf components and require specialized research-grade equipment.

## Technical Requirements

### Wavelength Range
- **Target Range:** 12-13 nanometers (extreme ultraviolet/X-ray boundary)
- **Spectral Bandwidth:** <1 nm resolution desired
- **Operating Environment:** Atmospheric (requires vacuum or specialized window materials)

### Detector Technologies

#### 1. Silicon Carbide (SiC) Photodiodes
- **Wavelength Range:** 1-200 nm (includes EUV)
- **Quantum Efficiency:** ~10-30% at 12-13 nm (varies with device design)
- **Response Time:** Nanosecond to microsecond range
- **Availability:** Research-grade only, custom fabrication required
- **Manufacturers:** Limited to specialized research institutions and semiconductor foundries
- **Cost Estimate:** $5,000-$50,000+ per device (research pricing)

**Technical Specifications:**
- Active area: Typically 1-10 mm²
- Dark current: <1 pA at room temperature
- Responsivity: ~0.01-0.1 A/W at 12-13 nm
- Bias voltage: 0-50V reverse bias
- Operating temperature: -20°C to +80°C

#### 2. Multilayer-Coated Silicon Detectors
- **Coating Type:** Mo/Si or Mo/Be multilayer mirrors optimized for EUV
- **Wavelength Range:** 10-20 nm (narrow band, coating-dependent)
- **Quantum Efficiency:** 5-20% at peak wavelength
- **Availability:** Custom fabrication, research institutions only
- **Cost Estimate:** $10,000-$100,000+ per device

**Technical Specifications:**
- Coating reflectivity: >50% at target wavelength
- Bandwidth: 1-2 nm FWHM
- Active area: 1-25 mm²
- Response time: <100 ns
- Requires vacuum operation or specialized EUV-transparent windows

#### 3. Microchannel Plate (MCP) Detectors
- **Wavelength Range:** 1-200 nm (broadband)
- **Quantum Efficiency:** 10-50% at 12-13 nm
- **Gain:** 10³-10⁷ (electron multiplication)
- **Availability:** Limited commercial sources (Photonis, Hamamatsu)
- **Cost Estimate:** $2,000-$20,000 per device

**Technical Specifications:**
- Active area: 18-40 mm diameter
- Spatial resolution: 10-50 μm
- Time resolution: <1 ns
- Requires high voltage: 1-3 kV
- Vacuum operation required

#### 4. X-ray CCD Detectors
- **Wavelength Range:** 0.1-50 nm
- **Quantum Efficiency:** 20-80% at 12-13 nm
- **Spatial Resolution:** Pixel-based imaging
- **Availability:** Limited commercial sources (Andor, Princeton Instruments)
- **Cost Estimate:** $15,000-$100,000+ per device

**Technical Specifications:**
- Pixel size: 13-24 μm
- Array size: 512×512 to 2048×2048 pixels
- Readout speed: 1-100 frames/second
- Cooling: Thermoelectric or liquid nitrogen
- Vacuum operation required

## Integration Requirements

### Vacuum System
- **Pressure Requirement:** <10⁻⁴ Torr (for EUV transmission)
- **Window Material:** Silicon (transparent to EUV) or thin metal foils
- **Sealing:** Ultra-high vacuum (UHV) compatible materials

### Signal Conditioning
- **Amplification:** Low-noise transimpedance amplifier (TIA)
- **Bandwidth:** DC to 10 MHz (depending on detector type)
- **Noise Floor:** <1 pA RMS
- **ADC Resolution:** 16-24 bits recommended

### Calibration Sources
- **EUV Light Sources:** Synchrotron radiation, laser-produced plasma, or discharge sources
- **Wavelength Standards:** Requires access to calibrated EUV monochromator
- **Calibration Facility:** National metrology institutes or specialized research facilities

## Current Limitations

1. **Commercial Availability:** No off-the-shelf photodiodes exist for 12-13 nm detection
2. **Cost:** Research-grade detectors cost $5,000-$100,000+
3. **Infrastructure:** Requires vacuum systems, specialized calibration equipment
4. **Expertise:** Requires specialized knowledge in EUV optics and detector physics
5. **Regulatory:** EUV radiation is ionizing and requires radiation safety protocols

## Integration Path

### Phase 1: Research and Procurement
1. Contact specialized detector manufacturers (Photonis, Hamamatsu, Andor)
2. Consult with research institutions using EUV detectors
3. Obtain quotes and delivery timelines (typically 6-12 months)
4. Identify calibration facilities (National Measurement Institute, synchrotron facilities)

### Phase 2: System Design
1. Design vacuum chamber or window assembly
2. Specify signal conditioning electronics
3. Design cooling system (if required)
4. Plan calibration procedure

### Phase 3: Integration
1. Integrate detector with vacuum system
2. Install signal conditioning electronics
3. Develop calibration routines
4. Test with known EUV sources

### Phase 4: Software Integration
1. Modify `photodiode_reader.py` to support EUV detector interface
2. Add EUV-specific calibration routines
3. Update GUI to display EUV wavelength measurements
4. Implement data logging for EUV range

## Alternative Approach: Indirect Detection

If direct EUV detection is not feasible, consider:

1. **Fluorescence Conversion:** Use EUV-to-visible converter (phosphor screen) with standard photodiode
2. **Grating Spectrometer:** Use EUV grating to disperse light, detect with position-sensitive detector
3. **Ionization Chamber:** Measure EUV intensity via gas ionization (requires calibration)

## References

- ARPANSA: Australian Radiation Protection and Nuclear Safety Agency
- IEC 60825.1: Laser safety standards
- NIST: National Institute of Standards and Technology (EUV metrology)
- Synchrotron facilities: Australian Synchrotron (Melbourne) for calibration access

## Notes

- All EUV detectors require careful handling due to ionizing radiation
- Vacuum systems add complexity and cost
- Calibration requires access to specialized facilities
- Current implementation uses visible/near-IR photodiodes (400-1100 nm) as functional prototype
- EUV detection capability is documented here for future integration when detectors become available or budget permits

