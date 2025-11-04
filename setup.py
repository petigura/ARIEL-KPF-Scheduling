#!/usr/bin/env python3
"""
Setup script for ARIEL-KPF Scheduling Package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="ariel-kpf",
    version="0.1.0",
    author="Erik Petigura",
    author_email="petigura@astro.ucla.edu",
    description="ARIEL target scheduling tools for KPF observations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/petigura/ARIEL-KPF-Scheduling",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "astropy>=5.0.0",
        "matplotlib>=3.4.0",
        "requests>=2.26.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
