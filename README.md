# LANShare

Complete production-ready Python desktop application to share files between two PCs over a Local Area Network (LAN) using HTTP.

## Features

- **Sender Mode**:
    - Select a folder to share.
    - Start a threaded HTTP server.
    - Auto-detect local IP address.
    - Prevents UI freezing.
    
- **Receiver Mode**:
    - Connect to sender via IP and Port.
    - List available files.
    - Download files with progress bar.
    - Handle large files and connection errors.

## Tech Stack

- Python 3.10+
- Tkinter (GUI)
- requests (HTTP Client)
- http.server (HTTP Server)
- threading (Concurrency)

## Installation Guide

### 1. Install System Dependencies

Before running the application, you must install Python and Tkinter. Tkinter is a system-level dependency and cannot be installed via `pip` on Linux/macOS.

#### **🐧 Linux**

**Debian / Ubuntu / Kali / Mint:**
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**Arch Linux:**
```bash
sudo pacman -S tk
```

#### **🍎 macOS**
If you installed Python via Homebrew, Tkinter should be included. If not:
```bash
brew install python-tk
```

#### **🪟 Windows**
Tkinter is included with the standard Python installer. Ensure you checked "tcl/tk and IDLE" during installation.

---

### 2. Install Project Dependencies

1. **Clone or Download** this repository.
2. Open a terminal in the project directory.
3. Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## Usage

> **Note:** Ensure your firewall allows Python to accept incoming connections on the specified port (8000 by default).

1. Run the application:
   ```bash
   python main.py
   ```
   
   Or if you are in the `lan_share` directory:
   ```bash
   python main.py
   ```

2. **Sender**: 
   - Click "Start as Sender".
   - Select a folder to share.
   - Click "Start Server".
   - Note the IP and Port.

3. **Receiver**:
   - On the other PC, run the app.
   - Click "Start as Receiver".
   - Enter the Sender's IP and Port.
   - Click "Connect".
   - Select a file and click "Download Selected".

## Troubleshooting

- **ModuleNotFoundError: No module named 'tkinter'**: 
  Follow the "Install System Dependencies" section above for your OS.
  
- **Connection Refused / Timeout**:
  - Check that both PCs are on the same Wi-Fi/LAN.
  - Disable Firewall temporarily on the Sender PC.
  - Verify the IP address is correct.

## License

MIT
