# LanShare

LanShare is a simple, cross-platform LAN file sharing application built with Python and CustomTkinter. It allows users to easily send and receive files over the local network without needing internet access.

## Features

- **Cross-Platform**: Works on Windows, Linux, and potentially macOS (setup required).
- **Simple UI**: Clean and intuitive interface powered by CustomTkinter.
- **Fast Transfer**: Direct peer-to-peer file transfer over your local network.
- **No Internet Required**: Completely offline, ensuring privacy and speed.
- **Auto-Discovery**: Automatically finds other LanShare instances on the network (if supported by network configuration).

## Installation

### Prerequisites

- Python 3.8+
- pip

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/PrathamCode/LanShare.git
   cd LanShare
   ```

2. **Create a virtual environment (Optional but recommended)**:
   ```bash
   python -m venv venv
   # Windows
   bg venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```
Or use the pre-built executables if available.

## Building from Source

To create a standalone executable:

### Windows
Run the `scripts/build_windows.bat` script.
```cmd
scripts\build_windows.bat
```
The executable will be in the `dist/` folder.

### Linux
Run the `scripts/build_linux.sh` script.
```bash
./scripts/build_linux.sh
```
The executable will be in the `dist/` folder.

## Project Structure

- `main.py`: Entry point for the application.
- `ui/`: User interface components (CustomTkinter windows and widgets).
- `network/`: Networking logic (p2p communication).
- `utils/`: Helper functions and configuration.
- `assets/`: Icons and static resources.
- `scripts/`: Build and utility scripts.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.
