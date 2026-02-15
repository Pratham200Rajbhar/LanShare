# Project: LANShare

Build a complete, production-ready Python desktop application called **LANShare**.

The application must allow users to share files between two PCs over a Local Area Network (LAN) using HTTP.

The application must be simple, stable, and easy to run.

------------------------------------------------------------

## 🎯 Core Requirements

The app must have two modes:

1. Sender Mode (Host files)
2. Receiver Mode (Download files)

The app must be fully functional end-to-end.

------------------------------------------------------------

## 🖥️ Tech Stack

- Python 3.10+
- Tkinter for GUI (custom styled, modern dark theme)
- Built-in `http.server` for file hosting
- `requests` library for downloading files
- `threading` for background tasks
- No Flask
- No FastAPI
- No database
- No external web frameworks

Only lightweight dependencies allowed:
- requests

------------------------------------------------------------

## 🏗️ Application Architecture

Use clean OOP design.

Structure:

lan_share/
│
├── main.py
├── ui/
│   ├── main_window.py
│   ├── sender_ui.py
│   ├── receiver_ui.py
│
├── network/
│   ├── server.py
│   ├── client.py
│
└── utils/
    ├── ip_utils.py

Use classes for:
- HTTP server management
- Download client
- Each UI screen

Networking logic must be separated from UI logic.

------------------------------------------------------------

# 🟢 SENDER MODE REQUIREMENTS

## UI Features:
- Folder selection (file dialog)
- Port input (default: 8000)
- Start button
- Stop button
- Display:
  - Local IP
  - Full Share URL (http://IP:PORT)
- Copy URL button
- Status indicator (Running / Stopped)

## Backend Requirements:
- Detect local LAN IP automatically
- Start HTTP server serving selected folder
- Run server in background thread
- Allow clean shutdown
- Handle port already in use
- Must not freeze UI

------------------------------------------------------------

# 🔵 RECEIVER MODE REQUIREMENTS

## UI Features:
- Input field: Sender IP
- Input field: Port
- Connect button
- Listbox showing available files
- Download button
- Download progress bar
- Status label

## Backend Requirements:
- Connect to sender via HTTP
- Fetch file list from root directory
- Parse HTML page to extract file names
- Display file list
- Download selected file
- Stream file in chunks
- Show live progress bar
- Save to user-selected folder

Must handle:
- Invalid IP
- Timeout
- Server unreachable
- Empty directory
- Download interruption

------------------------------------------------------------

# 🧵 THREADING RULES

- All networking must run in background threads
- Tkinter mainloop must never block
- Use thread-safe UI updates
- Proper thread termination

------------------------------------------------------------

# 🎨 UI DESIGN REQUIREMENTS

- Modern dark theme
- Custom colors (dark gray background)
- Clean spacing
- Responsive layout
- Buttons styled
- Clear separation between sections
- Fixed minimum window size
- Proper window title and icon placeholder

Main screen must have:

-----------------------------------
|           LANShare              |
|                                 |
|   [ Start as Sender ]           |
|   [ Start as Receiver ]         |
-----------------------------------

Switch screens inside same window (do not open new app instances).

------------------------------------------------------------

# 🌐 NETWORKING DETAILS

Sender:
- Use `http.server.SimpleHTTPRequestHandler`
- Use `socketserver.ThreadingTCPServer`
- Serve selected directory only
- Change working directory safely

Receiver:
- Use `requests.get()`
- Use `stream=True` for downloads
- Chunk size: 8192 bytes
- Calculate download progress percentage

------------------------------------------------------------

# 🛡️ ERROR HANDLING

Must include:

- Try/except around networking
- Graceful server shutdown
- Popup messageboxes for errors
- Validate IP format
- Validate port range
- Prevent duplicate server start
- Handle keyboard interrupt safely

------------------------------------------------------------

# 📦 PACKAGING

App must be runnable via:

python main.py

Ensure:
- No hardcoded paths
- Cross-platform compatibility (Linux, Windows, Mac)

------------------------------------------------------------

# 🧪 TEST SCENARIOS (Must Work)

1. Start sender on PC1
2. Connect receiver on PC2
3. List files successfully
4. Download large file (1GB test)
5. Stop sender cleanly
6. Handle wrong IP
7. Handle port already used

------------------------------------------------------------

# 🚀 EXTRA 
- Auto-detect local IP
- File size display in list
- Basic logging to console
- Clean code comments

------------------------------------------------------------

# 📤 FINAL OUTPUT REQUIREMENTS

The final output must include:

1. Complete source code
2. All files separated clearly
3. Instructions to install dependencies
4. Instructions to run
5. No missing components
6. No pseudo code
7. Fully working application

The solution must be clean, readable, and production-level quality.

------------------------------------------------------------

Build the full working application now.
