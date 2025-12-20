"""
Setup script for EUV Detection & Laser Communication Device
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README for long description
readme_path = Path(__file__).parent.parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, 'r') as f:
        long_description = f.read()

setup(
    name="euv-laser-communication",
    version="1.0.0",
    description="EUV Detection & Laser Communication Device",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NIoLS Project",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'euv-device=software.gui.communication_interface:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

