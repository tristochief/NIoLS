# Photodiode Detector Parts List

## Complete Parts List

| Component | Part Number | Quantity | Unit Price (AUD) | Supplier | Notes |
|-----------|-------------|----------|------------------|----------|-------|
| **Photodiode** | | | | | |
| Silicon Photodiode | Hamamatsu S1227-1010BR | 1 | $25-40 | Element14, RS Components | 320-1100 nm, 10×10 mm |
| **Amplifier Circuit** | | | | | |
| Op-Amp | OPA627AP | 1 | $15-25 | Element14, Mouser | Low noise, low bias current |
| Feedback Resistor | 1 MΩ, 1%, 0.125W, metal film | 1 | $0.50 | Element14, Jaycar | |
| Feedback Capacitor | 10 pF, NPO, 50V, ceramic | 1 | $0.30 | Element14, Jaycar | |
| Filter Resistor | 10 kΩ, 1%, 0.125W, metal film | 2 | $0.50 | Element14, Jaycar | For low-pass filter |
| Filter Capacitor | 1 nF, NPO, 50V, ceramic | 2 | $0.30 | Element14, Jaycar | For low-pass filter |
| Decoupling Capacitor | 100 nF, 50V, ceramic | 2 | $0.20 | Element14, Jaycar | Power supply decoupling |
| **ADC Interface** | | | | | |
| ADC Module | ADS1115 (16-bit I2C) | 1 | $8-15 | Adafruit, SparkFun | Breakout board preferred |
| Pull-up Resistors | 4.7 kΩ, 0.125W | 2 | $0.20 | Element14, Jaycar | I2C pull-ups (if not on module) |
| **Power Supply** | | | | | |
| Voltage Regulator | LM7805 (5V, 1A) | 1 | $1.50 | Element14, Jaycar | If not using external supply |
| Input Capacitor | 100 μF, 25V, electrolytic | 1 | $0.50 | Element14, Jaycar | Regulator input |
| Output Capacitor | 10 μF, 16V, tantalum | 1 | $1.00 | Element14, Jaycar | Regulator output |
| Power Supply | 5V, 1A, wall adapter | 1 | $10-15 | Element14, Jaycar | Alternative to regulator |
| **Mechanical** | | | | | |
| Enclosure | Project box, 100×80×50 mm | 1 | $5-10 | Jaycar, Bunnings | For shielding |
| Mounting Hardware | M3 screws, standoffs | 4 | $2.00 | Jaycar | PCB mounting |
| Connectors | 2.54 mm pin headers | 2 | $1.00 | Element14 | I2C and power |
| **PCB** | | | | | |
| Prototype Board | Perfboard or custom PCB | 1 | $5-20 | Element14, PCBWay | Depending on approach |

## Alternative Parts

### Op-Amp Alternatives
- **AD795:** Similar performance, lower cost ($8-12)
- **LMC662:** CMOS, lower power ($2-4)
- **TL071:** General purpose, very low cost ($1-2)

### ADC Alternatives
- **ADS1015:** 12-bit version, lower cost ($5-8)
- **MCP3008:** 10-bit SPI ADC ($3-5)
- **Built-in ADC:** Raspberry Pi has ADC via MCP3008 or similar

### Photodiode Alternatives
- **BPW21:** General purpose silicon photodiode ($2-5)
- **SFH 203:** High-speed photodiode ($3-6)
- **Any silicon photodiode** with 400-1100 nm spectral range

## Total Cost Estimate

**Minimum Configuration:** $60-80 AUD
- Basic photodiode, op-amp, ADC, power supply

**Recommended Configuration:** $80-120 AUD
- Quality components, proper enclosure, connectors

**Professional Configuration:** $120-180 AUD
- Custom PCB, premium components, calibration sources

## Supplier Information (Australia)

1. **Element14 (Farnell):** www.element14.com
   - Wide selection, professional components
   - Fast shipping, good for one-off orders

2. **RS Components:** www.rs-online.com
   - Similar to Element14
   - Good for bulk orders

3. **Jaycar Electronics:** www.jaycar.com.au
   - Retail stores, good for common components
   - Limited selection for specialized parts

4. **Mouser Electronics:** www.mouser.com.au
   - International supplier, ships to Australia
   - Excellent selection, competitive pricing

5. **Adafruit/SparkFun:** www.adafruit.com, www.sparkfun.com
   - Breakout boards and modules
   - Good for ADC modules and development boards

## Notes

- Prices are approximate and may vary
- Consider buying spares for critical components
- Some components may require minimum order quantities
- Shipping costs not included in estimates
- GST (10%) may apply to purchases

