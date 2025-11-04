"""
Centralized path management for ARIEL-KPF Scheduling

This module provides Path objects for all data directories in the project.
Paths are resolved relative to the project root, allowing scripts to run
from any directory after package installation.
"""

from pathlib import Path

# Get the project root directory (parent of ariel_kpf/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Define all data directories relative to project root
TARGETS_DIR = PROJECT_ROOT / "targets"
OBS_DIR = PROJECT_ROOT / "obs"
PLOTS_DIR = PROJECT_ROOT / "plots"
BIN_DIR = PROJECT_ROOT / "bin"

# Ensure directories exist
TARGETS_DIR.mkdir(exist_ok=True)
OBS_DIR.mkdir(exist_ok=True)
PLOTS_DIR.mkdir(exist_ok=True)

# Specific file paths
OB_TEMPLATE = OBS_DIR / "ob-template.json"

def get_latest_targets_file(prefix="ariel_targets"):
    """
    Get the most recent targets CSV file.
    
    Parameters:
    -----------
    prefix : str
        Filename prefix to search for (default: "ariel_targets")
        
    Returns:
    --------
    Path : Path to the most recent matching file, or None if not found
    """
    files = list(TARGETS_DIR.glob(f"{prefix}_*.csv"))
    if not files:
        return None
    # Sort by modification time and return the most recent
    return max(files, key=lambda p: p.stat().st_mtime)

def get_latest_kpf_targets_file():
    """
    Get the most recent KPF targets CSV file.
    
    Returns:
    --------
    Path : Path to the most recent KPF targets file, or None if not found
    """
    return get_latest_targets_file(prefix="ariel_kpf_targets")

__all__ = [
    'PROJECT_ROOT',
    'TARGETS_DIR',
    'OBS_DIR',
    'PLOTS_DIR',
    'BIN_DIR',
    'OB_TEMPLATE',
    'get_latest_targets_file',
    'get_latest_kpf_targets_file'
]

