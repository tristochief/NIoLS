# Laser Transmitter Parts List

## Complete Parts List

| Component | Part Number | Quantity | Unit Price (AUD) | Supplier | Notes |
|-----------|-------------|----------|------------------|----------|-------|
| **Laser Module** | | | | | |
| Laser Diode Module | 650 nm, 1 mW, Class 1M | 1 | $15-30 | Element14, RS Components | Red laser, collimated |
| **Driver Circuit** | | | | | |
| Transistor | 2N2222 NPN | 1 | $0.50 | Element14, Jaycar | Modulation switch |
| Current Limiting Resistor | 47 Ω, 0.5W, metal film | 1 | $0.50 | Element14, Jaycar | Adjust for laser current |
| Base Resistor | 1 kΩ, 0.125W, metal film | 1 | $0.50 | Element14, Jaycar | Transistor base |
| **Safety Interlock** | | | | | |
| Safety Switch | SPST, normally closed | 1 | $2-5 | Element14, Jaycar | Emergency stop |
| Pull-up Resistor | 10 kΩ, 0.125W | 1 | $0.50 | Element14, Jaycar | Interlock pull-up |
| Status LED | Red LED, 3mm | 1 | $0.20 | Element14, Jaycar | Interlock indicator |
| LED Resistor | 220 Ω, 0.125W | 1 | $0.20 | Element14, Jaycar | LED current limit |
| **Power Supply** | | | | | |
| Voltage Regulator | LM7805 (5V, 1A) | 1 | $1.50 | Element14, Jaycar | If not using external supply |
| Input Capacitor | 100 μF, 25V, electrolytic | 1 | $0.50 | Element14, Jaycar | Regulator input |
| Output Capacitor | 10 μF, 16V, tantalum | 1 | $1.00 | Element14, Jaycar | Regulator output |
| Decoupling Capacitor | 100 μF, 16V, electrolytic | 1 | $0.50 | Element14, Jaycar | Power supply filter |
| Decoupling Capacitor | 100 nF, 50V, ceramic | 1 | $0.20 | Element14, Jaycar | High-frequency filter |
| Power Supply | 5V, 1A, wall adapter | 1 | $10-15 | Element14, Jaycar | Alternative to regulator |
| **Mechanical** | | | | | |
| Enclosure | Project box, 100×80×50 mm | 1 | $5-10 | Jaycar, Bunnings | For safety |
| Mounting Hardware | M3 screws, standoffs | 4 | $2.00 | Jaycar | PCB mounting |
| Connectors | 2.54 mm pin headers | 2 | $1.00 | Element14 | GPIO and power |
| Heat Sink | Small TO-220 heat sink | 1 | $2.00 | Element14, Jaycar | For regulator (if needed) |
| **Optical** | | | | | |
| Beam Alignment Tool | Laser alignment jig (optional) | 1 | $10-20 | Custom | For precise alignment |

## Alternative Parts

### Laser Module Alternatives
- **532 nm Green Laser:** Similar price, more visible ($15-30)
- **405 nm Violet Laser:** If available in Class 1M ($20-35)
- **Custom Laser Diode:** Requires additional driver circuit ($5-15 for diode only)

### Transistor Alternatives
- **BC547:** General purpose NPN ($0.30)
- **2N3904:** Similar to 2N2222 ($0.40)
- **MOSFET:** IRF540N for higher current ($1.00)

### Driver Alternatives
- **LM317:** Adjustable current source ($1.50)
- **Dedicated Laser Driver:** MAX1556 or similar ($5-10)

## Total Cost Estimate

**Minimum Configuration:** $40-60 AUD
- Basic laser module, driver circuit, power supply

**Recommended Configuration:** $60-90 AUD
- Quality components, proper enclosure, safety interlock

**Professional Configuration:** $90-130 AUD
- Custom PCB, premium components, alignment tools

## Supplier Information (Australia)

1. **Element14 (Farnell):** www.element14.com
   - Professional components, laser modules
   - Fast shipping

2. **RS Components:** www.rs-online.com
   - Similar to Element14
   - Good for bulk orders

3. **Jaycar Electronics:** www.jaycar.com.au
   - Retail stores, common components
   - Limited laser selection

4. **Mouser Electronics:** www.mouser.com.au
   - International supplier
   - Excellent selection

5. **Laser Pointer Suppliers:** Various online retailers
   - May have Class 1M modules
   - Verify compliance before purchase

## Safety Equipment (Recommended)

| Item | Quantity | Price (AUD) | Notes |
|------|----------|-------------|-------|
| Laser Safety Goggles | 1 pair | $20-50 | OD 2+ for 650 nm |
| Laser Power Meter | 1 | $50-200 | For power verification |
| Beam Profiler (optional) | 1 | $100-500 | For beam characterization |

## Notes

- **Class 1M Compliance:** Verify laser module is properly classified
- **Power Verification:** Use calibrated power meter to confirm ≤1 mW
- **Regulatory:** Ensure compliance with Australian laser regulations
- **Safety First:** Always use safety interlock and proper procedures
- Prices are approximate and may vary
- GST (10%) may apply to purchases

