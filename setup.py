#!/usr/bin/env python3
"""
Setup script for ARIEL-KPF Scheduling Tool
Helps verify Google Sheets API connection and provides setup guidance.
"""

import os
import sys


def check_credentials():
    """Check if credentials.json exists and provide guidance."""
    creds_file = "credentials.json"
    
    if os.path.exists(creds_file):
        print("✓ credentials.json found")
        return True
    else:
        print("✗ credentials.json not found")
        print("\nTo set up Google Sheets API access:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Sheets API")
        print("4. Create a service account")
        print("5. Download the JSON key file")
        print("6. Rename it to 'credentials.json' and place in this directory")
        print("7. Share your Google Spreadsheet with the service account email")
        return False


def check_conda_environment():
    """Check if we're in the correct conda environment."""
    import os
    
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', '')
    if conda_env == 'ariel-kpf-scheduling':
        print(f"✓ Running in conda environment: {conda_env}")
        return True
    elif conda_env:
        print(f"⚠ Running in conda environment: {conda_env}")
        print("  Consider activating: conda activate ariel-kpf-scheduling")
        return True
    else:
        print("⚠ No conda environment detected")
        print("  Create and activate environment: conda env create -f environment.yml && conda activate ariel-kpf-scheduling")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'astropy',
        'pandas', 
        'matplotlib',
        'gspread',
        'google.oauth2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with: conda env create -f environment.yml")
        return False
    
    return True


def main():
    """Main setup verification function."""
    print("ARIEL-KPF Scheduling Tool - Setup Verification")
    print("=" * 50)
    
    print("\nChecking conda environment...")
    env_ok = check_conda_environment()
    
    print("\nChecking dependencies...")
    deps_ok = check_dependencies()
    
    print("\nChecking credentials...")
    creds_ok = check_credentials()
    
    print("\n" + "=" * 50)
    if env_ok and deps_ok and creds_ok:
        print("✓ Setup complete! You can now run: python main.py")
    else:
        print("✗ Setup incomplete. Please address the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
