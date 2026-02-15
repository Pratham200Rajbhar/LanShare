# LanShare Packaging Guide

This guide explains how to create standalone executables for LanShare on Windows and Linux.

## For Users (Non-Developers)
To use LanShare without installing Python or any libraries, simply download the pre-built executable for your operating system from the 'releases' section (if available) or follow the build instructions below.

## Build Instructions

### 🪟 Windows
1. Make sure [Python](https://www.python.org/downloads/) is installed.
2. Double-click the `build_windows.bat` file in the project folder.
3. Wait for the process to finish.
4. Your standalone executable will be in the `dist` folder named `LanShare.exe`.

### 🐧 Linux
1. Open a terminal in the project folder.
2. Run `./build_linux.sh`.
3. Your standalone executable will be in the `dist` folder named `LanShare`.

## Technical Details
The build process uses `PyInstaller` to bundle the Python interpreter, dependencies (like `customtkinter`, `requests`, and `psutil`), and the application code into a single file. 

Special care is taken to include `customtkinter` assets which are required for the modern UI to function correctly.
