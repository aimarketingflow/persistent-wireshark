#!/usr/bin/env python3
"""
StealthShark Setup Script
Network monitoring and packet capture system
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="stealthshark",
    version="1.0.0",
    description="Stealth network monitoring and packet capture system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="StealthShark Project",
    author_email="contact@stealthshark.dev",
    url="https://github.com/yourusername/stealthshark",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psutil>=5.9.0",
        "PyQt6>=6.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "enhanced": [
            "requests>=2.28.0",
            "cryptography>=3.4.8",
            "scapy>=2.4.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "stealthshark=enhanced_memory_monitor:main",
            "stealthshark-gui=gui_memory_monitor:main",
            "stealthshark-simple=simple_tshark_monitor:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
