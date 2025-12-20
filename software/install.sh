#!/bin/bash
# Installation script for EUV Detection & Laser Communication Device

set -e  # Exit on error

echo "=========================================="
echo "EUV Detection & Laser Communication Device"
echo "Installation Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✓ Python version: $python_version"
echo ""

# Check if conda environment should be used
if command -v conda &> /dev/null; then
    echo "Conda detected. Do you want to use a conda environment? (y/n)"
    read -r use_conda
    if [ "$use_conda" = "y" ] || [ "$use_conda" = "Y" ]; then
        echo "Enter conda environment name (or press Enter for 'euv-device'):"
        read -r env_name
        env_name=${env_name:-euv-device}
        
        if conda env list | grep -q "^$env_name "; then
            echo "Activating existing environment: $env_name"
            eval "$(conda shell.bash hook)"
            conda activate "$env_name"
        else
            echo "Creating new conda environment: $env_name"
            conda create -n "$env_name" python=3.8 -y
            eval "$(conda shell.bash hook)"
            conda activate "$env_name"
        fi
    fi
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✓ Dependencies installed"
echo ""

# Verify installation
echo "Verifying installation..."
python3 -c "import streamlit; import numpy; import plotly; import yaml; print('✓ All core dependencies verified')" || {
    echo "ERROR: Dependency verification failed"
    exit 1
}

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "To run the device:"
echo "  cd software"
echo "  streamlit run gui/communication_interface.py"
echo ""
echo "To run tests:"
echo "  cd tests"
echo "  python run_tests.py"
echo ""

