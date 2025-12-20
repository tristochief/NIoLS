# NIoLS Week 4 - Running and Testing Instructions

## Overview
This guide provides step-by-step instructions for running the Andromedan Spacecraft Simulation and testing the Streamlit web application with Playwright.

## Prerequisites

### 1. Environment Setup
```bash
# Navigate to the NIoLS project directory
cd /Users/tristanberry/Documents/NIoLS

# Activate the conda environment
conda activate niols

# Navigate to week4 folder
cd week4
```

### 2. Dependencies Installation
```bash
# Install all required dependencies
pip install -r src/requirements_streamlit.txt

# Install Playwright for browser testing
pip install playwright
playwright install chromium
```

## Running the Simulation

### Option 1: Direct Simulation (Command Line)
```bash
# Run the simulation directly
python src/main.py

# Run compliance tests
python src/test_simulation.py
```

### Option 2: Streamlit Web Application
```bash
# Start the Streamlit app
streamlit run src/streamlit_app.py

# The app will be available at:
# Local URL: http://localhost:8501
# Network URL: http://10.40.0.54:8501
```

## Testing with Playwright

### Automated Browser Testing
```bash
# Run the Playwright test script
python src/test_streamlit_with_playwright.py
```

**Expected Output:**
```
🧪 NIoLS Streamlit App Playwright Test
========================================
🚀 Starting Streamlit app...
⏳ Waiting for Streamlit app to start...
🧪 Testing Streamlit app with Playwright...
🌐 Navigating to http://localhost:8502
📸 Taking screenshot...
🔍 Testing basic functionality...
✅ Found header: Simulation Controls
✅ Sidebar found
✅ Run Simulation button found
🖱️  Clicking Run Simulation button...
✅ Playwright testing completed successfully!
🛑 Stopping Streamlit app...
✅ Streamlit app stopped
```

## Key Features to Test

### 1. Simulation Controls
- **Altitude Slider**: Adjust initial altitude (10-100m)
- **Mass Slider**: Adjust spacecraft mass (10-30kg)
- **Glideslope Slider**: Adjust descent angle (30-80 degrees)
- **Run Simulation Button**: Execute the simulation

### 2. Visualization Tabs
- **3D Trajectory**: Interactive 3D plot of spacecraft path
- **Telemetry Dashboard**: Real-time sensor data visualization
- **Video Generation**: Create simulation video clips
- **Compliance Tests**: Run automated test suite
- **Social Media**: Generate content for platforms

### 3. Expected Simulation Results
- **Landing Precision**: < 0.5m from target (current: ~0.586m)
- **Control Rate**: 300 Hz
- **Thermal Array**: 64x64 sensor grid
- **Failure Modes**: Sensor dropout, control latency, thruster misfire

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill processes on port 8501
lsof -ti:8501 | xargs kill -9

# Or use a different port
streamlit run src/streamlit_app.py --server.port 8502
```

#### 2. Missing Dependencies
```bash
# Reinstall dependencies
pip install -r src/requirements_streamlit.txt

# Install specific missing packages
pip install moviepy==1.0.3
pip install playwright
playwright install chromium
```

#### 3. PyBullet Connection Issues
```bash
# Restart the simulation
python src/main.py

# Check for multiple spacecraft IDs in output
# Should see: "Spacecraft created with ID: 1" (only once)
```

#### 4. Module Import Errors
The Streamlit app includes graceful error handling for missing modules:
- `moviepy.editor`: Video generation disabled
- `main`/`test_simulation`: Simulation features disabled

### Performance Optimization
```bash
# Install Watchdog for better performance
xcode-select --install
pip install watchdog
```

## File Structure

```
week4/
├── src/
│   ├── main.py                    # Core simulation
│   ├── test_simulation.py         # Compliance tests
│   ├── streamlit_app.py          # Web application
│   ├── test_streamlit_with_playwright.py  # Browser testing
│   └── requirements_streamlit.txt # Dependencies
├── references/
│   └── week4_instructions.md     # This file
└── week4_deployment/             # Deployed package (if created)
```

## Testing Checklist

### Manual Testing
- [ ] Streamlit app starts without errors
- [ ] All sliders and controls are responsive
- [ ] Simulation runs and completes successfully
- [ ] Landing precision is within acceptable range
- [ ] Visualizations generate correctly
- [ ] Social media content is created

### Automated Testing
- [ ] Playwright test runs successfully
- [ ] Screenshots are captured
- [ ] UI elements are found and clickable
- [ ] Simulation executes via automated interaction

### Compliance Testing
- [ ] 10/10 randomized runs pass
- [ ] Landing precision < 0.5m
- [ ] Stability below 10m < 0.05m
- [ ] Telemetry data quality checks pass
- [ ] Failure modes work correctly

## Performance Metrics

### Current Performance (Latest Test)
- **Landing Precision**: 0.586m (target: <0.5m)
- **Simulation Time**: ~3.85 seconds
- **Control Rate**: 300 Hz
- **Thermal Array**: 64x64 pixels
- **Failure Modes**: Implemented and tested

### Areas for Improvement
1. **Landing Precision**: Fine-tune PID gains for sub-0.5m accuracy
2. **Stability**: Improve position control below 10m altitude
3. **Sensor Dropout**: Adjust dropout rate calculation
4. **UI Responsiveness**: Optimize Streamlit app performance

## Deployment

### Creating Deployment Package
```bash
# Run deployment script
cd src
python deploy.py --clean
cd ..

# This creates week4_deployment/ with:
# - Complete source code
# - Social media assets
# - Documentation
# - Launch scripts
```

### Virtual Environment Setup
```bash
# Create dedicated environment
python3 -m venv niols_week4_env
source niols_week4_env/bin/activate

# Install dependencies
pip install -r src/requirements_streamlit.txt

# Run tests
python src/test_streamlit_with_playwright.py
```

## Notes for Future Development

1. **Always use a new terminal** when testing to avoid port conflicts
2. **Check conda environment** is activated before running commands
3. **Monitor simulation output** for landing precision and stability metrics
4. **Use Playwright screenshots** to verify UI functionality
5. **Test failure modes** to ensure robustness
6. **Update requirements** when adding new dependencies

## Contact and Support

For issues or questions:
- Check the troubleshooting section above
- Review simulation logs for error messages
- Verify all dependencies are installed correctly
- Ensure proper environment activation

---

**Last Updated**: Based on successful Playwright test with Chromium
**Test Status**: ✅ PASSED - All core functionality working
**Next Steps**: Fine-tune landing precision and stability metrics
