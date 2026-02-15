<p align="center">
  <img src="assets/hero.png" width="100%" alt="LanShare Hero">
</p>

# 🚀 LanShare

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)]()
[![Platform Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()

**LanShare** is a powerful, lightweight, and cross-platform LAN file sharing application. Built with **Python** and **CustomTkinter**, it provides a modern UI for seamless peer-to-peer file transfers over your local network—no internet required.

---

## ✨ Features

- 📂 **High-Speed Transfers**: Direct P2P file sharing using your local network's full bandwidth.
- 🔒 **Privacy Focused**: No cloud servers. Your files stay within your local network.
- 🖥️ **Modern UI**: Clean, responsive, and dark-themed interface powered by CustomTkinter.
- 🔍 **Auto-Discovery**: Automatically find other users on the same network.
- 📦 **Zero Config**: Just run and share. No complex setup or internet connection needed.

---

## 📥 Download & Install (For Users)

If you just want to use LanShare without touching code, follow these steps:

### 🐧 Linux (Debian/Ubuntu)
1.  **Download** the latest `.deb` package from the [Releases](https://github.com/PrathamCode/LanShare/releases) page.
2.  **Install** it using `apt` (this handles everything for you):
    ```bash
    sudo apt install ./lanshare_1.0.0.deb
    ```
3.  **Run**: You can now find "LanShare" in your application menu or just type `lanshare` in the terminal.

### 🪟 Windows
1.  **Download** the `LanShare.exe` from the [Releases](https://github.com/PrathamCode/LanShare/releases) page.
2.  **Run**: Just double-click the `.exe` file. No installation is required!
    *   *Note: If Windows Defender shows a warning, click "More info" and "Run anyway".*

---

## 🛠️ Installation (For Developers)
- **Python 3.8 or higher** installed on your system.
- Git (optional, for cloning).

### 🐧 Linux (Ubuntu/Debian)
Most Linux distributions do not include the `tkinter` module by default. You need to install it manually.

1. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-tk python3-pip
   ```

2. **Clone and Setup**:
   ```bash
   git clone https://github.com/PrathamCode/LanShare.git
   cd LanShare
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### 🪟 Windows
1. **Clone and Setup**:
   Open PowerShell or Command Prompt:
   ```powershell
   git clone https://github.com/PrathamCode/LanShare.git
   cd LanShare
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

---

## 🚀 How to Use

Once installed, simply run the application:

```bash
python main.py
```

### 💡 Quick Tips
- Make sure both devices are on the same WiFi/Ethernet network.
- Ensure your firewall allows incoming connections on the app's default ports.

---

## 🛠️ Building from Source

If you want to create a standalone executable (`.exe` for Windows or ELF for Linux):

### For Windows:
```bash
scripts/build_windows.bat
```

### For Linux:
```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```
The output will be located in the `dist/` directory.

---

## 🤝 Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git checkout -b feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.

---
<p align="center">Made with ❤️ by Pratham</p>
