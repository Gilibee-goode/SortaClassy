#!/bin/bash

echo ""
echo "🎓 MESHACHVETZ INSTALLATION - macOS/Linux"
echo "========================================"
echo ""
echo "This will install Meshachvetz on your computer."
echo "Please wait while we set everything up..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo ""
    echo "Please install Python 3.8+ from:"
    echo "  • macOS: https://python.org or 'brew install python3'"
    echo "  • Linux: 'sudo apt install python3' or 'sudo yum install python3'"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the installation script
echo "📦 Running installation script..."
python3 install.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Installation failed. Please check the errors above."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "You can now use Meshachvetz by:"
echo "  1. Running: ./run_meshachvetz.sh"
echo "  2. Or in terminal: ./run_meshachvetz.sh score your_students.csv"
echo ""
echo "📖 For help, see: docs/CLI_USER_GUIDE.md"
echo ""
read -p "Press Enter to continue..." 