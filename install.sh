#!/bin/bash

echo "Mouse Curve Analyzer - Installation Script"
echo "=========================================="
echo

# Check if Python is installed
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "Error: Python is not installed. Please install Python 3.6 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "Found Python version: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 6 ]); then
    echo "Error: Python 3.6 or higher is required. Found Python $PYTHON_VERSION."
    exit 1
fi

# Create virtual environment (optional)
echo
echo "Would you like to create a virtual environment? (recommended) [Y/n]"
read -r CREATE_VENV

if [[ $CREATE_VENV != "n" && $CREATE_VENV != "N" ]]; then
    echo "Creating virtual environment..."
    
    # Check if venv module is available
    if ! $PYTHON -c "import venv" &>/dev/null; then
        echo "Error: The venv module is not available. Please install it or use pip directly."
        echo "Continuing with system Python..."
    else
        $PYTHON -m venv venv
        
        # Activate virtual environment
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
            echo "Virtual environment created and activated."
            PYTHON="venv/bin/python"
        else
            echo "Failed to create virtual environment. Continuing with system Python..."
        fi
    fi
fi

# Install dependencies
echo
echo "Installing required packages..."
$PYTHON -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo
    echo "Installation completed successfully!"
    echo
    echo "To run the Mouse Curve Analyzer:"
    if [[ $CREATE_VENV != "n" && $CREATE_VENV != "N" && -f "venv/bin/activate" ]]; then
        echo "1. Activate the virtual environment: source venv/bin/activate"
        echo "2. Run the application: python mouse_curve.py"
    else
        echo "Run the application: $PYTHON mouse_curve.py"
    fi
    echo
    echo "For a simpler command-line version, you can also run:"
    echo "$PYTHON example_basic_usage.py"
else
    echo
    echo "Error: Failed to install required packages."
    exit 1
fi