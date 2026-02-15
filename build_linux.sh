#!/bin/bash
echo "=================================================="
echo "LanShare Build Script for Linux"
echo "=================================================="

# Check for python3
if ! command -v python3 &> /dev/null
then
    echo "Error: python3 could not be found."
    exit 1
fi

echo "Installing dependencies..."
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller
python3 -m pip uninstall -y pathlib

echo "Starting build process..."
python3 scripts/build.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Build successful! Check the 'dist' folder for the LanShare executable."
else
    echo ""
    echo "BUILD FAILED!"
    exit 1
fi
