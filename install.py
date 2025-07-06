#!/usr/bin/env python3
"""
Meshachvetz Installation Script
==============================

This script automatically sets up Meshachvetz with a virtual environment
and installs all required dependencies.

Works on Windows, macOS, and Linux.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_banner():
    """Print installation banner."""
    print("🎓 MESHACHVETZ INSTALLATION")
    print("=" * 50)
    print("Setting up your Student Assignment Scoring System")
    print("=" * 50)

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please install Python 3.8+ from https://python.org")
        sys.exit(1)
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")

def get_venv_path():
    """Get the virtual environment path."""
    return Path("meshachvetz_env")

def get_activation_script():
    """Get the activation script path for the current OS."""
    venv_path = get_venv_path()
    
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "activate.bat"
    else:
        return venv_path / "bin" / "activate"

def get_python_executable():
    """Get the Python executable path in the virtual environment."""
    venv_path = get_venv_path()
    
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def create_virtual_environment():
    """Create a virtual environment."""
    venv_path = get_venv_path()
    
    if venv_path.exists():
        print("🔄 Virtual environment already exists, removing old one...")
        shutil.rmtree(venv_path)
    
    print("📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], 
                      check=True, capture_output=True)
        print("✅ Virtual environment created successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        sys.exit(1)

def install_dependencies():
    """Install Meshachvetz and its dependencies."""
    python_exe = get_python_executable()
    
    print("📥 Installing Meshachvetz and dependencies...")
    print("   This may take a few minutes...")
    
    try:
        # Upgrade pip first
        subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install the package in development mode
        subprocess.run([str(python_exe), "-m", "pip", "install", "-e", "."], 
                      check=True, capture_output=True)
        
        print("✅ Installation completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def test_installation():
    """Test if the installation works."""
    venv_path = get_venv_path()
    
    # Get the meshachvetz executable path
    if platform.system() == "Windows":
        meshachvetz_exe = venv_path / "Scripts" / "meshachvetz.exe"
    else:
        meshachvetz_exe = venv_path / "bin" / "meshachvetz"
    
    print("🧪 Testing installation...")
    
    try:
        result = subprocess.run([str(meshachvetz_exe), "--help"], 
                              check=True, capture_output=True, text=True)
        
        if "Meshachvetz - Student Class Assignment Optimizer" in result.stdout:
            print("✅ Installation test passed!")
            return True
        else:
            print("❌ Installation test failed - CLI not working properly")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation test failed: {e}")
        return False
    except FileNotFoundError:
        # Fallback to python -c method if executable not found
        python_exe = get_python_executable()
        try:
            result = subprocess.run([str(python_exe), "-c", "from meshachvetz.cli.main import main; main()"], 
                                  input="--help\n", check=True, capture_output=True, text=True)
            
            if "Meshachvetz - Student Class Assignment Optimizer" in result.stdout:
                print("✅ Installation test passed!")
                return True
            else:
                print("❌ Installation test failed - CLI not working properly")
                return False
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation test failed: {e}")
            return False

def create_run_script():
    """Create a simple run script for the CLI."""
    venv_path = get_venv_path()
    
    # Get the meshachvetz executable path
    if platform.system() == "Windows":
        meshachvetz_exe = venv_path / "Scripts" / "meshachvetz.exe"
        script_content = f"""@echo off
cd /d "{os.getcwd()}"
"{meshachvetz_exe}" %*
"""
        script_path = Path("run_meshachvetz.bat")
    else:
        meshachvetz_exe = venv_path / "bin" / "meshachvetz"
        script_content = f"""#!/bin/bash
cd "{os.getcwd()}"
"{meshachvetz_exe}" "$@"
"""
        script_path = Path("run_meshachvetz.sh")
    
    with open(script_path, "w") as f:
        f.write(script_content)
    
    if platform.system() != "Windows":
        os.chmod(script_path, 0o755)
    
    print(f"✅ Created run script: {script_path}")

def print_usage_instructions():
    """Print usage instructions for the user."""
    print("\n" + "=" * 50)
    print("🎉 INSTALLATION COMPLETE!")
    print("=" * 50)
    
    print("\n📋 How to use Meshachvetz:")
    
    if platform.system() == "Windows":
        print("   Method 1 (Easy): Double-click 'run_meshachvetz.bat'")
        print("   Method 2 (Command): run_meshachvetz.bat score your_students.csv")
    else:
        print("   Method 1 (Easy): ./run_meshachvetz.sh")
        print("   Method 2 (Command): ./run_meshachvetz.sh score your_students.csv")
    
    print("\n🎯 Quick Start:")
    print("   1. Create a CSV file with your student data")
    print("   2. Run: run_meshachvetz score your_students.csv")
    print("   3. Review the results and generated reports")
    
    print("\n📖 Documentation:")
    print("   • User Guide: docs/CLI_USER_GUIDE.md")
    print("   • Sample Data: examples/test_data/")
    print("   • Data Format: docs/02_data_format_specification.md")
    
    print("\n🧪 Test with sample data:")
    if platform.system() == "Windows":
        print("   run_meshachvetz.bat score examples/test_data/perfect_score_test.csv")
    else:
        print("   ./run_meshachvetz.sh score examples/test_data/perfect_score_test.csv")

def main():
    """Main installation function."""
    print_banner()
    
    # Check prerequisites
    check_python_version()
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    
    # Create run script
    create_run_script()
    
    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    main() 