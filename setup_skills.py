#!/usr/bin/env python3
"""
OA-3D-Skill Setup Script
========================
Initializes and installs all dependencies for Glass & Boundary Analysis Skills.

Run this script when setting up the skills for the first time:
    python setup_skills.py

Or trigger via Claude Code with:
    "setup OA-3D-Skills"
"""

import subprocess
import sys
import os
from pathlib import Path

# =============================================================
# CONFIGURATION
# =============================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
REQUIREMENTS_FILE = SCRIPT_DIR / "requirements.txt"
SKILLS_DIR = SCRIPT_DIR / "skills" / "glass-manufacturing"
OUTPUTS_DIR = SCRIPT_DIR / "outputs"
INPUTS_DIR = SCRIPT_DIR / "inputs"

# Required directories
REQUIRED_DIRS = [
    OUTPUTS_DIR,
    INPUTS_DIR,
    OUTPUTS_DIR / "Glass-Skill-1",
    OUTPUTS_DIR / "Boundary-Skill-1",
]

# Core packages to verify
CORE_PACKAGES = [
    "shapely",
    "numpy",
    "scipy",
]


# =============================================================
# SETUP FUNCTIONS
# =============================================================

def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(step: int, total: int, text: str):
    """Print a formatted step indicator."""
    print(f"\n[{step}/{total}] {text}")


def check_python_version():
    """Verify Python version is 3.8+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"ERROR: Python 3.8+ required. Found: {version.major}.{version.minor}")
        return False
    print(f"  Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def create_directories():
    """Create required directories if they don't exist."""
    created = []
    for dir_path in REQUIRED_DIRS:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            created.append(str(dir_path.relative_to(SCRIPT_DIR)))

    if created:
        print(f"  Created directories: {', '.join(created)}")
    else:
        print("  All directories already exist")
    return True


def install_requirements():
    """Install Python dependencies from requirements.txt."""
    if not REQUIREMENTS_FILE.exists():
        print(f"  ERROR: requirements.txt not found at {REQUIREMENTS_FILE}")
        return False

    print(f"  Installing from: {REQUIREMENTS_FILE}")

    try:
        # Upgrade pip first
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("  Dependencies installed successfully")
            return True
        else:
            print(f"  WARNING: Some packages may have failed")
            print(f"  {result.stderr[:500] if result.stderr else ''}")
            return True  # Continue anyway

    except subprocess.CalledProcessError as e:
        print(f"  ERROR: Installation failed: {e}")
        return False


def verify_core_packages():
    """Verify core packages are importable."""
    success = True
    for package in CORE_PACKAGES:
        try:
            __import__(package)
            print(f"    {package}")
        except ImportError:
            print(f"    {package} - NOT FOUND")
            success = False
    return success


def verify_skills_files():
    """Verify skill documentation files exist."""
    required_files = [
        SKILLS_DIR / "SKILL.md",
        SKILLS_DIR / "SKILL-glass.md",
        SKILLS_DIR / "SKILL-boundary.md",
        SKILLS_DIR / "boundary_utils.py",
    ]

    missing = []
    for file_path in required_files:
        if file_path.exists():
            print(f"    {file_path.name}")
        else:
            print(f"    {file_path.name} - MISSING")
            missing.append(file_path.name)

    return len(missing) == 0


def print_usage_guide():
    """Print usage instructions after setup."""
    print("""
  USAGE GUIDE
  -----------

  1. GLASS PANEL ANALYSIS:
     - Place glass panel sketch in: inputs/
     - Use SKILL-glass.md methodology
     - Output generated in: outputs/Glass-Skill-N/

  2. PLOT BOUNDARY ANALYSIS:
     - Place boundary sketch in: inputs/
     - Use SKILL-boundary.md methodology
     - Output generated in: outputs/Boundary-Skill-N/

  3. WORKFLOW:
     - Phase 1: Section-by-section image extraction (10+ steps)
     - Phase 2: Output generation (HTML, SVG, JSON, Reports)

  4. COMMANDS:
     - "analyze glass panel" - Start glass analysis
     - "analyze plot boundary" - Start boundary analysis
     - "verify measurements" - Run validation checks
""")


# =============================================================
# MAIN SETUP
# =============================================================

def main():
    """Run the complete setup process."""
    print_header("OA-3D-SKILL SETUP")
    print("  Initializing Glass & Boundary Analysis Skills...")

    total_steps = 5
    all_success = True

    # Step 1: Check Python version
    print_step(1, total_steps, "Checking Python version...")
    if not check_python_version():
        all_success = False

    # Step 2: Create directories
    print_step(2, total_steps, "Creating required directories...")
    if not create_directories():
        all_success = False

    # Step 3: Install requirements
    print_step(3, total_steps, "Installing Python dependencies...")
    if not install_requirements():
        all_success = False

    # Step 4: Verify core packages
    print_step(4, total_steps, "Verifying core packages...")
    if not verify_core_packages():
        print("  WARNING: Some core packages missing. Manual install may be required.")

    # Step 5: Verify skill files
    print_step(5, total_steps, "Verifying skill documentation...")
    if not verify_skills_files():
        print("  WARNING: Some skill files missing.")

    # Final status
    print_header("SETUP COMPLETE" if all_success else "SETUP COMPLETED WITH WARNINGS")

    if all_success:
        print_usage_guide()
        print("  Ready to analyze glass panels and plot boundaries!")
    else:
        print("\n  Some steps had warnings. Please review above.")
        print("  You may need to manually install missing packages.")

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
