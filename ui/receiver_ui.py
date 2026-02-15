import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
import threading
import queue
import os
from pathlib import Path
from network.client import HTTPClient
from utils.performance import transfer_optimizer, memory_optimizer


# ─── Color Palette (Windows 11 inspired) ────────────────────────────────
C = {
    "bg":           "#1e1e2e",
    "card":         "#2b2b3d",
    "sidebar":      "#252536",
    "hover":        "#35354a",
    "accent":       "#0078d4",
    "accent_hover": "#1a8cff",
    "text":         "#e4e4e8",
    "text2":        "#9090a0",
    "text_dim":     "#6c6c80",
    "success":      "#2ecc71",
    "danger":       "#e74c3c",
    "border":       "#3a3a50",
    "white":        "#ffffff",
    "input_bg":     "#333348",
    "row_alt":      "#2f2f42",
    "row_hover":    "#383850",
    "selected":     "#1a3a5c",
}

FILE_ICONS = {
    ".txt": "📄", ".md": "📄", ".log": "📄",
    ".py": "🐍", ".js": "📜", ".ts": "📜", ".java": "☕", ".c": "⚙️", ".cpp": "⚙️",
    ".html": "🌐", ".css": "🎨", ".json": "📋", ".xml": "📋", ".yaml": "📋", ".yml": "📋",
    ".jpg": "🖼️", ".jpeg": "🖼️", ".png": "🖼️", ".gif": "🖼️", ".svg": "🖼️", ".bmp": "🖼️",
    ".mp4": "🎬", ".avi": "🎬", ".mkv": "🎬", ".mov": "🎬",
    ".mp3": "🎵", ".wav": "🎵", ".flac": "🎵", ".ogg": "🎵",
    ".zip": "📦", ".tar": "📦", ".gz": "📦", ".rar": "📦", ".7z": "📦",
    ".pdf": "📕", ".doc": "📘", ".docx": "📘", ".xls": "📊", ".xlsx": "📊",
    ".exe": "⚡", ".sh": "⚡", ".bat": "⚡",
}


def _icon_for(name, ftype):
    if ftype == "folder":
        return "📁"
    ext = os.path.splitext(name)[1].lower()
    return FILE_ICONS.get(ext, "📄")


def _human_size(size):
    if size == 0:
        return "—"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != 'B' else f"{size} B"
        size /= 1024
    return f"{size:.1f} TB"


class FolderRow(ctk.CTkFrame):
    """A folder row that represents an entire downloadable folder unit."""
    def __init__(self, master, folder_name, file_count, total_size, on_toggle=None, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, height=44, **kwargs)
        self.pack_propagate(False)
        self.folder_name = folder_name
        self.file_count = file_count
        self.total_size = total_size
        self.on_toggle = on_toggle
        self.selected = ctk.BooleanVar(value=False)

        # Checkbox
        self.chk = ctk.CTkCheckBox(
            self, text="", variable=self.selected,
            width=22, height=22, corner_radius=4,
            fg_color=C["accent"], hover_color=C["accent_hover"],
            border_color=C["border"], command=self._on_check)
        self.chk.pack(side="left", padx=(16, 6))

        # Folder icon
        ctk.CTkLabel(self, text="📁", font=("Segoe UI", 18), width=32).pack(side="left", padx=(0, 8))

        # Folder info
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=(0, 16))
        
        ctk.CTkLabel(info_frame, text=folder_name, font=("Segoe UI Semibold", 14),
                     text_color=C["accent"], anchor="w").pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"{file_count} files  •  {_human_size(total_size)}",
                     font=("Segoe UI", 11), text_color=C["text_dim"], anchor="w").pack(anchor="w")

        # Download size on right
        ctk.CTkLabel(self, text=_human_size(total_size), font=("Segoe UI", 12),
                     text_color=C["text2"], width=100, anchor="e").pack(side="right", padx=16)

    def _on_check(self):
        if self.on_toggle:
            self.on_toggle()


class ReceiverUI(ctk.CTkFrame):
    def __init__(self, master, switch_callback):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.switch_callback = switch_callback
        self.client = HTTPClient()
        self.msg_queue = queue.Queue()
        self.file_entries = []
        self.folder_rows = []
        self._build()
        self._poll_queue()

    def _build(self):
        # ── Top bar ──
        topbar = ctk.CTkFrame(self, fg_color=C["sidebar"], corner_radius=0, height=58)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkButton(topbar, text="←  Back",
                      command=lambda: self.switch_callback("main"),
                      fg_color="transparent", hover_color=C["hover"],
                      font=("Segoe UI", 13), width=80, anchor="w",
                      text_color=C["text2"]).pack(side="left", padx=16, pady=12)

        ctk.CTkLabel(topbar, text="📥  Receiver Mode",
                     font=("Segoe UI Semibold", 18),
                     text_color=C["white"]).pack(side="left", padx=8)

        # ── Connection bar ──
        conn_card = ctk.CTkFrame(self, fg_color=C["card"], corner_radius=12,
                                  border_width=1, border_color=C["border"])
        conn_card.pack(fill="x", padx=24, pady=(16, 12))

        conn_inner = ctk.CTkFrame(conn_card, fg_color="transparent")
        conn_inner.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(conn_inner, text="Connect to Sender",
                     font=("Segoe UI Semibold", 14),
                     text_color=C["text"]).pack(anchor="w", pady=(0, 8))

        row = ctk.CTkFrame(conn_inner, fg_color="transparent")
        row.pack(fill="x")

        ctk.CTkLabel(row, text="IP:", font=("Segoe UI", 12),
                     text_color=C["text2"]).pack(side="left")
        self.ip_var = ctk.StringVar()
        ctk.CTkEntry(row, textvariable=self.ip_var, width=160,
                     font=("Segoe UI", 12), fg_color=C["input_bg"],
                     border_color=C["border"], corner_radius=8,
                     height=36, placeholder_text="192.168.x.x").pack(side="left", padx=(6, 14))

        ctk.CTkLabel(row, text="Port:", font=("Segoe UI", 12),
                     text_color=C["text2"]).pack(side="left")
        self.port_var = ctk.StringVar(value="8000")
        ctk.CTkEntry(row, textvariable=self.port_var, width=80,
                     font=("Segoe UI", 12), fg_color=C["input_bg"],
                     border_color=C["border"], corner_radius=8,
                     height=36).pack(side="left", padx=(6, 14))

        self.connect_btn = ctk.CTkButton(
            row, text="Connect", command=self._connect,
            font=("Segoe UI Semibold", 12), fg_color=C["accent"],
            hover_color=C["accent_hover"], corner_radius=8,
            width=110, height=36)
        self.connect_btn.pack(side="left")

        # ── Toolbar ──
        toolbar = ctk.CTkFrame(self, fg_color="transparent", height=36)
        toolbar.pack(fill="x", padx=24, pady=(8, 4))

        self.file_count_label = ctk.CTkLabel(
            toolbar, text="Connect to see shared folders",
            font=("Segoe UI", 12), text_color=C["text_dim"])
        self.file_count_label.pack(side="left")

        self.deselect_btn = ctk.CTkButton(
            toolbar, text="Deselect All", command=self._deselect_all,
            font=("Segoe UI", 11), fg_color="transparent",
            hover_color=C["hover"], text_color=C["text2"],
            width=90, height=28, corner_radius=6, state="disabled")
        self.deselect_btn.pack(side="right", padx=4)

        self.select_all_btn = ctk.CTkButton(
            toolbar, text="Select All", command=self._select_all,
            font=("Segoe UI", 11), fg_color="transparent",
            hover_color=C["hover"], text_color=C["text2"],
            width=80, height=28, corner_radius=6, state="disabled")
        self.select_all_btn.pack(side="right", padx=4)

        # ── Folder browser ──
        browser_card = ctk.CTkFrame(self, fg_color=C["card"], corner_radius=12,
                                     border_width=1, border_color=C["border"])
        browser_card.pack(fill="both", expand=True, padx=24, pady=(4, 8))

        # Header row
        header = ctk.CTkFrame(browser_card, fg_color=C["sidebar"], corner_radius=0, height=38)
        header.pack(fill="x", padx=2, pady=(2, 0))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="      Shared Folders", font=("Segoe UI Semibold", 12),
                     text_color=C["text_dim"], anchor="w").pack(side="left", padx=16, fill="x", expand=True)
        ctk.CTkLabel(header, text="Size", font=("Segoe UI Semibold", 12),
                     text_color=C["text_dim"], width=100, anchor="e").pack(side="right", padx=(4, 16))

        self.folder_scroll = ctk.CTkScrollableFrame(browser_card, fg_color="transparent",
                                                     corner_radius=0)
        self.folder_scroll.pack(fill="both", expand=True, padx=2, pady=(0, 2))

        # Placeholder
        self.placeholder = ctk.CTkLabel(
            self.folder_scroll, text="Connect to a sender to browse shared folders",
            font=("Segoe UI", 13), text_color=C["text_dim"])
        self.placeholder.pack(pady=60)

        # ── Bottom bar ──
        bottom = ctk.CTkFrame(self, fg_color=C["sidebar"], corner_radius=0, height=92)
        bottom.pack(fill="x", side="bottom")
        bottom.pack_propagate(False)

        # Progress section
        prog_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        prog_frame.pack(fill="x", padx=24, pady=(12, 0))

        self.status_label = ctk.CTkLabel(prog_frame, text="Ready",
                                          font=("Segoe UI", 12),
                                          text_color=C["text_dim"])
        self.status_label.pack(side="left")

        self.progress_pct = ctk.CTkLabel(prog_frame, text="",
                                          font=("Segoe UI", 12),
                                          text_color=C["accent"])
        self.progress_pct.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(bottom, height=6, corner_radius=3,
                                                fg_color=C["input_bg"],
                                                progress_color=C["accent"])
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=24, pady=(8, 14))

        # Buttons
        btn_container = ctk.CTkFrame(bottom, fg_color="transparent")
        btn_container.pack(fill="x", pady=(0, 16))
        
        btn_frame = ctk.CTkFrame(btn_container, fg_color="transparent")
        btn_frame.pack()

        self.dl_selected_btn = ctk.CTkButton(
            btn_frame, text="📥  Download Selected", command=self._download_selected,
            font=("Segoe UI Semibold", 13), fg_color=C["accent"],
            hover_color=C["accent_hover"], corner_radius=8,
            width=200, height=40, state="disabled")
        self.dl_selected_btn.pack(side="left", padx=10)

        self.dl_all_btn = ctk.CTkButton(
            btn_frame, text="📦  Download All (ZIP)", command=self._download_all,
            font=("Segoe UI Semibold", 13), fg_color="#6b46c1",
            hover_color="#7c3aed", corner_radius=8,
            width=200, height=40, state="disabled")
        self.dl_all_btn.pack(side="left", padx=10)

    # ── Queue polling ──
    def _poll_queue(self):
        try:
            if not self.winfo_exists():
                return
            while True:
                msg = self.msg_queue.get_nowait()
                self._handle_msg(msg)
        except queue.Empty:
            pass
        except Exception:
            return
        if self.winfo_exists():
            self.after(80, self._poll_queue)

    def _handle_msg(self, msg):
        t = msg.get("type")

        if t == "list_result":
            self.connect_btn.configure(state="normal", text="Connect")
            if msg["success"]:
                self._populate_folders(msg["data"])
            else:
                self.status_label.configure(text="Connection failed")
                messagebox.showerror("Error", msg["data"])

        elif t == "progress":
            cur, total = msg["current"], msg["total"]
            if total > 0:
                pct = cur / total
                self.progress_bar.set(pct)
                self.progress_pct.configure(text=f"{int(pct * 100)}%")
                self.status_label.configure(text=f"Downloading... {_human_size(cur)} / {_human_size(total)}")

        elif t == "file_progress":
            cur, total = msg["current"], msg["total"]
            self.status_label.configure(text=f"Folder {cur}/{total}: {msg.get('name', '')}")
            self.progress_bar.set(cur / total if total else 0)
            self.progress_pct.configure(text=f"{cur}/{total}")

        elif t == "download_result":
            self.dl_selected_btn.configure(state="normal")
            self.dl_all_btn.configure(state="normal")
            if msg["success"]:
                self.progress_bar.set(1)
                self.progress_pct.configure(text="100%")
                self.status_label.configure(text="Download complete!")
                messagebox.showinfo("Success", msg["message"])
            else:
                self.progress_bar.set(0)
                self.progress_pct.configure(text="")
                self.status_label.configure(text="Download failed")
                messagebox.showerror("Error", msg["message"])

    # ── Connection ──
    def _connect(self):
        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()
        if not ip or not port:
            messagebox.showwarning("Input Error", "Enter both IP and Port.")
            return
        self.status_label.configure(text="Connecting...")
        self.connect_btn.configure(state="disabled", text="Connecting...")
        threading.Thread(target=self._list_thread, args=(ip, port), daemon=True).start()

    def _list_thread(self, ip, port):
        ok, data = self.client.list_files(ip, port)
        self.msg_queue.put({"type": "list_result", "success": ok, "data": data})

    # ── Folder list population ──
    def _populate_folders(self, entries):
        # Clear old rows
        for w in self.folder_scroll.winfo_children():
            w.destroy()
        self.folder_rows.clear()
        self.file_entries = entries

        if not entries:
            ctk.CTkLabel(self.folder_scroll, text="No shared folders found",
                         font=("Segoe UI", 13), text_color=C["text_dim"]).pack(pady=40)
            return

        # Group files by their top-level folder
        folders = {}  # folder_name -> {"files": [files], "total_size": 0}

        for entry in entries:
            if entry["type"] == "file":
                path_parts = entry["path"].split("/")
                if len(path_parts) > 1:
                    # File in a folder
                    top_folder = path_parts[0]
                    if top_folder not in folders:
                        folders[top_folder] = {"files": [], "total_size": 0}
                    folders[top_folder]["files"].append(entry)
                    folders[top_folder]["total_size"] += entry["size"]

        if not folders:
            ctk.CTkLabel(self.folder_scroll, text="No folders shared (only individual files)",
                         font=("Segoe UI", 13), text_color=C["text_dim"]).pack(pady=40)
            return

        # Show folders
        row_idx = 0
        for folder_name, folder_data in sorted(folders.items()):
            file_count = len(folder_data["files"])
            total_size = folder_data["total_size"]
            
            fr = FolderRow(self.folder_scroll, folder_name, file_count, total_size,
                           on_toggle=self._update_selection_count)
            bg = C["card"] if row_idx % 2 == 0 else C["row_alt"]
            fr.configure(fg_color=bg)
            fr.pack(fill="x", pady=2, padx=4)
            self.folder_rows.append(fr)
            row_idx += 1

        # Update stats
        total_files = len([e for e in entries if e["type"] == "file"])
        total_folders = len(folders)
        total_size = sum(e["size"] for e in entries if e["type"] == "file")
        
        self.file_count_label.configure(
            text=f"{total_folders} shared folder(s)  •  {total_files} total files  •  {_human_size(total_size)}")

        self.dl_selected_btn.configure(state="normal")
        self.dl_all_btn.configure(state="normal")
        self.select_all_btn.configure(state="normal")
        self.deselect_btn.configure(state="normal")
        self.status_label.configure(text=f"Ready — {total_folders} folders available")

    # ── Selection helpers ──
    def _get_selected_files(self):
        # Return all files from selected folders
        selected_files = []
        for folder_row in self.folder_rows:
            if folder_row.selected.get():
                # Get all files in this folder
                folder_name = folder_row.folder_name
                folder_files = [e for e in self.file_entries 
                               if e["type"] == "file" and e["path"].startswith(folder_name + "/")]
                selected_files.extend(folder_files)
        return selected_files

    def _select_all(self):
        for fr in self.folder_rows:
            fr.selected.set(True)
        self._update_selection_count()

    def _deselect_all(self):
        for fr in self.folder_rows:
            fr.selected.set(False)
        self._update_selection_count()

    def _update_selection_count(self):
        sel = self._get_selected_files()
        if sel:
            total = sum(f["size"] for f in sel)
            folder_count = sum(1 for fr in self.folder_rows if fr.selected.get())
            self.status_label.configure(
                text=f"{folder_count} folder(s) selected  •  {len(sel)} files  •  {_human_size(total)}")
        else:
            folder_count = len(self.folder_rows)
            self.status_label.configure(text=f"Ready — {folder_count} folders available")

    # ── Downloads ──
    def _download_selected(self):
        selected = self._get_selected_files()
        if not selected:
            messagebox.showwarning("No Selection", "Select at least one folder to download.")
            return

        save_dir = filedialog.askdirectory(title="Choose Download Location")
        if not save_dir:
            return

        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()

        self.dl_selected_btn.configure(state="disabled")
        self.dl_all_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_pct.configure(text="0%")

        threading.Thread(target=self._batch_download_thread,
                         args=(ip, port, selected, save_dir), daemon=True).start()

    def _batch_download_thread(self, ip, port, files, save_dir):
        total = len(files)
        ok_count = 0

        for i, entry in enumerate(files):
            rel_path = entry["path"]
            save_path = os.path.join(save_dir, rel_path)

            self.msg_queue.put({
                "type": "file_progress", "current": i + 1,
                "total": total, "name": entry["name"]})

            def progress_cb(cur, tot):
                self.msg_queue.put({"type": "progress", "current": cur, "total": tot})

            ok, _ = self.client.download_file(ip, port, rel_path, save_path, progress_cb)
            if ok:
                ok_count += 1

        self.msg_queue.put({
            "type": "download_result", "success": ok_count > 0,
            "message": f"Downloaded {ok_count}/{total} files to:\n{save_dir}"})

    def _download_all(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("Zip Archive", "*.zip")],
            initialfile="shared_files.zip",
            title="Save ZIP As")
        if not save_path:
            return

        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()

        self.dl_selected_btn.configure(state="disabled")
        self.dl_all_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_pct.configure(text="0%")
        self.status_label.configure(text="Downloading ZIP...")

        threading.Thread(target=self._zip_download_thread,
                         args=(ip, port, save_path), daemon=True).start()

    def _zip_download_thread(self, ip, port, save_path):
        def progress_cb(cur, tot):
            self.msg_queue.put({"type": "progress", "current": cur, "total": tot})

        ok, msg = self.client.download_all(ip, port, save_path, progress_cb)
        self.msg_queue.put({"type": "download_result", "success": ok, "message": msg})
