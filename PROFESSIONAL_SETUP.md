# Professional Setup Guide

This guide ensures the EUV Detection & Laser Communication Device is properly configured for professional operation.

## Pre-Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Hardware assembled according to documentation
- [ ] Raspberry Pi 4 (or compatible) with GPIO access
- [ ] I2C enabled on Raspberry Pi
- [ ] Network connectivity (for updates and logging)

## Installation Steps

### 1. Environment Setup

**Option A: Using Conda (Recommended)**
```bash
# Activate conda environment (if using)
conda activate niols  # or your preferred environment

# Or create new environment
conda create -n euv-device python=3.8 -y
conda activate euv-device
```

**Option B: Using Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

**Quick Install:**
```bash
cd software
./install.sh
```

**Manual Install:**
```bash
cd software
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Run dependency check
python -c "import streamlit, numpy, plotly, yaml; print('✓ All dependencies OK')"

# Run tests
cd ../tests
python run_tests.py
```

### 4. Configuration

1. **Edit configuration file:**
   ```bash
   nano software/config/device_config.yaml
   ```

2. **Verify configuration:**
   ```bash
   cd software
   python -c "from hardware_control.system_health import validate_config; \
              is_valid, errors = validate_config('config/device_config.yaml'); \
              print('Valid' if is_valid else f'Errors: {errors}')"
   ```

### 5. Start Device

**Professional Startup (Recommended):**
```bash
cd software
python start_device.py
```

**Direct Startup:**
```bash
cd software
streamlit run gui/communication_interface.py
```

## System Health Checks

### Initial Health Check

1. Start the device
2. Click "Run Health Check" in the sidebar
3. Review all health check results
4. Address any warnings or errors before operation

### Regular Health Checks

- **Before each session:** Run health check
- **Weekly:** Full system diagnostics
- **After hardware changes:** Re-run health check

## Professional Operation Guidelines

### Pre-Operation Checklist

- [ ] Health check passed
- [ ] Configuration validated
- [ ] Safety interlock engaged
- [ ] Calibration verified
- [ ] Log directory accessible
- [ ] Emergency stop accessible

### During Operation

- Monitor system health indicators
- Check interlock status regularly
- Review measurement data quality
- Monitor log files for errors
- Keep emergency stop accessible

### Post-Operation

- Review session logs
- Check for errors or warnings
- Verify data integrity
- Document any issues
- Run health check

## Troubleshooting

### Common Issues

**1. Dependencies Missing**
```bash
pip install -r software/requirements.txt
```

**2. Configuration Errors**
- Check YAML syntax
- Verify all required sections present
- Review error messages in health check

**3. Hardware Not Detected**
- Verify I2C is enabled: `sudo raspi-config`
- Check GPIO permissions
- Review hardware connections

**4. Interlock Issues**
- Verify physical switch is closed
- Check GPIO pin connections
- Review interlock wiring

### Getting Help

1. Check logs: `device.log` and `logs/` directory
2. Run health check for diagnostics
3. Review error messages in GUI
4. Check documentation in `docs/` directory

## Maintenance

### Daily
- Visual inspection
- Health check
- Review logs

### Weekly
- Full system test
- Calibration verification
- Log file cleanup

### Monthly
- Complete health audit
- Configuration review
- Software updates (if available)

## Safety Compliance

- Always follow safety protocols
- Never bypass safety interlock
- Keep emergency stop accessible
- Document all incidents
- Review safety documentation regularly

## Support

For professional support:
- Review `docs/user_manual.md`
- Check `docs/safety_compliance.md`
- Review `docs/technical_specifications.md`
- Check log files for detailed error information

---

**Version:** 1.0  
**Last Updated:** [Current Date]

