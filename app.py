import os
import sys
import re
import json
import time
import shutil
import tempfile
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import urllib.request
import ctypes


# ------------------------------------------------------------
# Windows DPI awareness — MUST run before Tk() is created
# ------------------------------------------------------------
if sys.platform.startswith("win"):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


# ============================================================
# Paths & platform detection
# ============================================================

def _app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = _app_dir()
BUNDLE_DIR = APP_DIR

IS_WINDOWS = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

if IS_WINDOWS:
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "SmartMusicVideoDownloader.App"
        )
    except Exception:
        pass


def _user_data_dir():
    if IS_WINDOWS:
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    elif IS_MAC:
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME",
                              os.path.expanduser("~/.local/share"))
    path = os.path.join(base, "SmartMusicVideoDownloader")
    os.makedirs(path, exist_ok=True)
    return path


def _user_bin_dir():
    path = os.path.join(_user_data_dir(), "bin")
    os.makedirs(path, exist_ok=True)
    return path


SETTINGS_FILE = os.path.join(_user_data_dir(), "settings.json")
PREF_FILE = os.path.join(_user_data_dir(), "update_pref.json")


def _load_settings():
    defaults = {
        "download_dir": os.path.join(os.path.expanduser("~"), "Downloads"),
        "format": "audio",
        "video_quality": "Original (Best)",
        "audio_quality": "Original (Best)",
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
            defaults.update({k: v for k, v in data.items() if v})
        except Exception:
            pass
    return defaults


def _save_settings(download_dir, format_choice, video_quality, audio_quality):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump({
                "download_dir": download_dir,
                "format": format_choice,
                "video_quality": video_quality,
                "audio_quality": audio_quality,
            }, f, indent=2)
    except Exception:
        pass


def _binary_name(base):
    if IS_WINDOWS:
        return base + ".exe"
    if IS_MAC:
        return base + "_macos" if base == "yt-dlp" else base
    return base


def _resolve_binary(base):
    fallback = os.path.join(_user_bin_dir(), _binary_name(base))
    bundled = os.path.join(BUNDLE_DIR, _binary_name(base))

    if os.path.exists(PREF_FILE):
        try:
            with open(PREF_FILE) as f:
                pref = json.load(f).get(base)
            if pref and os.path.exists(pref):
                return pref
        except Exception:
            pass

    if os.path.exists(fallback):
        return fallback
    return bundled


YTDLP = _resolve_binary("yt-dlp")
FFMPEG = _resolve_binary("ffmpeg")
FFPROBE = _resolve_binary("ffprobe")

YTDLP_URLS = {
    "win":    "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
    "darwin": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos",
    "linux":  "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux",
}

APP_TITLE = "Smart Music and Video Downloader"

VIDEO_QUALITIES = ["Original (Best)", "1080p", "720p", "480p", "360p"]
AUDIO_QUALITIES = ["Original (Best)", "High (320 kbps)", "Medium (192 kbps)", "Low (128 kbps)"]


# ============================================================
# Font scale helper
# ============================================================

class UiScale:
    """Holds scaled sizes so every widget fits the current screen."""

    def __init__(self, root):
        self.root = root
        self.recalc()

    def recalc(self):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # Base scale for a 1920x1080 screen.  Smaller screens shrink.
        # Never go below 0.65 (already big enough to read) or above 1.25.
        scale_w = screen_w / 1920.0
        scale_h = screen_h / 1080.0
        self.factor = max(0.65, min(1.25, min(scale_w, scale_h)))

    def s(self, n):
        """Scale an integer."""
        return max(1, int(round(n * self.factor)))

    def font(self, size, weight="normal"):
        base = self.s(size)
        if weight == "normal":
            return ("Segoe UI", base)
        return ("Segoe UI", base, weight)


# ============================================================
# App
# ============================================================

class SmartDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)

        # Build the scale once, from screen size
        self.ui = UiScale(root)

        # --- Window sizing ---
        self._size_window()

        saved = _load_settings()

        self.download_dir = tk.StringVar(value=saved["download_dir"])
        self.format_choice = tk.StringVar(value=saved["format"])
        self.video_quality = tk.StringVar(value=saved.get("video_quality", VIDEO_QUALITIES[0]))
        self.audio_quality = tk.StringVar(value=saved.get("audio_quality", AUDIO_QUALITIES[0]))
        self.quality_var = tk.StringVar()

        self.status_text = tk.StringVar(value="Ready. Paste your links and click Download.")
        self.count_text = tk.StringVar(value="Downloaded: 0    Errors: 0")

        self.downloaded = 0
        self.errors = 0
        self.total = 0
        self.current_index = 0
        self.current_proc = None
        self.stop_requested = False
        self.pending_links = []
        self.current_url = None

        self._build_ui()
        self._sync_quality_dropdown()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self._save_current_settings()
        self.root.destroy()

    def _save_current_settings(self):
        _save_settings(
            self.download_dir.get(),
            self.format_choice.get(),
            self.video_quality.get(),
            self.audio_quality.get(),
        )

    def _size_window(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        # Base target: 1280x820 at 100% scale, never exceed 85% of screen
        target_w = min(1280, int(sw * 0.85))
        target_h = min(820, int(sh * 0.85))

        # Allow it to be smaller on tiny screens
        target_w = max(target_w, 800)
        target_h = max(target_h, 560)

        x = (sw - target_w) // 2
        y = max(0, (sh - target_h) // 2 - self.ui.s(20))

        self.root.geometry(f"{target_w}x{target_h}+{x}+{y}")
        self.root.minsize(self.ui.s(700), self.ui.s(500))
        self.root.resizable(True, True)

    # ---------- UI ----------
    def _build_ui(self):
        s = self.ui.s
        f = self.ui.font

        main = tk.Frame(self.root, padx=s(30), pady=s(20))
        main.pack(fill="both", expand=True)

        # ---- Top row ----
        top_row = tk.Frame(main)
        top_row.pack(fill="x")

        tk.Label(top_row, text=f"🎬 {APP_TITLE} 🎵",
                 font=f(22, "bold")).pack(side="left")

        tk.Button(
            top_row, text="🔄 Check for Updates", font=f(11),
            command=self.check_for_updates, padx=s(14), pady=s(6)
        ).pack(side="right")

        # ---- Folder row ----
        folder_frame = tk.Frame(main)
        folder_frame.pack(fill="x", pady=(s(14), s(6)))
        tk.Label(folder_frame, text="Save to:", font=f(11)).pack(side="left")
        self.folder_entry = tk.Entry(
            folder_frame, textvariable=self.download_dir,
            font=f(11), state="readonly"
        )
        self.folder_entry.pack(side="left", fill="x", expand=True,
                               padx=(s(10), s(10)))
        tk.Button(
            folder_frame, text="Change Folder", font=f(11),
            command=self.choose_folder, padx=s(14), pady=s(6)
        ).pack(side="right")

        # ---- Links header + Paste/Clear ----
        links_header = tk.Frame(main)
        links_header.pack(fill="x", pady=(s(12), s(6)))
        tk.Label(
            links_header,
            text="Paste one or more links (one per line or space-separated):",
            font=f(11)
        ).pack(side="left")
        tk.Button(
            links_header, text="🗑 Clear", font=f(11),
            command=self.clear_links, padx=s(14), pady=s(5)
        ).pack(side="right", padx=(s(8), 0))
        tk.Button(
            links_header, text="📋 Paste", font=f(11),
            command=self.paste_links, padx=s(14), pady=s(5)
        ).pack(side="right")

        self.links_box = tk.Text(
            main, font=f(11), height=6, wrap="word",
            relief="solid", borderwidth=2, padx=s(10), pady=s(10)
        )
        self.links_box.pack(fill="both", expand=True)

        # ---- Format + Quality row ----
        format_frame = tk.Frame(main)
        format_frame.pack(fill="x", pady=(s(12), s(6)))

        tk.Label(format_frame, text="Download as:", font=f(11)).pack(side="left")
        tk.Radiobutton(
            format_frame, text="🎧 Audio (MP3)", font=f(11),
            variable=self.format_choice, value="audio",
            command=self._on_format_change
        ).pack(side="left", padx=(s(12), s(6)))
        tk.Radiobutton(
            format_frame, text="🎬 Video (MP4)", font=f(11),
            variable=self.format_choice, value="video",
            command=self._on_format_change
        ).pack(side="left")

        tk.Label(format_frame, text="Quality:", font=f(11)).pack(
            side="left", padx=(s(20), s(6)))
        self.quality_combo = ttk.Combobox(
            format_frame, textvariable=self.quality_var,
            font=f(11), state="readonly", width=18
        )
        self.quality_combo.pack(side="left")
        self.quality_combo.bind("<<ComboboxSelected>>", self._on_quality_change)

        # ---- Progress + counter ----
        progress_frame = tk.Frame(main)
        progress_frame.pack(fill="x", pady=(s(14), s(6)))
        self.progress = ttk.Progressbar(
            progress_frame, orient="horizontal", mode="determinate"
        )
        self.progress.pack(side="left", fill="x", expand=True)
        tk.Label(
            progress_frame, textvariable=self.count_text,
            font=f(11), width=28, anchor="e"
        ).pack(side="right", padx=(s(14), 0))

        # ---- Action buttons ----
        btn_row = tk.Frame(main)
        btn_row.pack(pady=(s(12), s(6)))
        self.download_btn = tk.Button(
            btn_row, text="⬇  DOWNLOAD", font=f(16, "bold"),
            bg="#2e7d32", fg="white", activebackground="#1b5e20",
            activeforeground="white", padx=s(28), pady=s(12),
            command=self.start_download
        )
        self.download_btn.pack(side="left", padx=s(6))

        self.stop_btn = tk.Button(
            btn_row, text="⏸  STOP", font=f(16, "bold"),
            bg="#c62828", fg="white", activebackground="#8e0000",
            activeforeground="white", padx=s(28), pady=s(12),
            state="disabled", command=self.stop_download
        )
        self.stop_btn.pack(side="left", padx=s(6))

        self.resume_btn = tk.Button(
            btn_row, text="▶  CONTINUE", font=f(16, "bold"),
            bg="#1565c0", fg="white", activebackground="#0d47a1",
            activeforeground="white", padx=s(28), pady=s(12),
            state="disabled", command=self.resume_download
        )
        self.resume_btn.pack(side="left", padx=s(6))

        # ---- Status ----
        tk.Label(
            main, textvariable=self.status_text, font=f(11),
            fg="#555", wraplength=1000, justify="left"
        ).pack(anchor="w", pady=(s(4), 0))

        # ---- Log ----
        self.log_box = tk.Text(
            main, font=("Consolas", self.ui.s(10)), height=5, wrap="word",
            state="disabled", bg="#f5f5f5", relief="solid", borderwidth=1
        )
        self.log_box.pack(fill="both", expand=True, pady=(s(8), 0))

    # ---------- quality dropdown ----------
    def _sync_quality_dropdown(self):
        if self.format_choice.get() == "audio":
            options = AUDIO_QUALITIES
            current = self.audio_quality.get()
        else:
            options = VIDEO_QUALITIES
            current = self.video_quality.get()
        self.quality_combo["values"] = options
        if current not in options:
            current = options[0]
        self.quality_var.set(current)

    def _on_format_change(self):
        self._sync_quality_dropdown()

    def _on_quality_change(self, event=None):
        if self.format_choice.get() == "audio":
            self.audio_quality.set(self.quality_var.get())
        else:
            self.video_quality.set(self.quality_var.get())
        self._save_current_settings()

    # ---------- helpers ----------
    def choose_folder(self):
        chosen = filedialog.askdirectory(initialdir=self.download_dir.get())
        if chosen:
            self.download_dir.set(chosen)
            self._save_current_settings()

    def paste_links(self):
        try:
            clipboard = self.root.clipboard_get()
        except tk.TclError:
            return
        if not clipboard:
            return
        existing = self.links_box.get("1.0", "end").strip()
        self.links_box.insert("end", ("\n" if existing else "") + clipboard.strip())
        self.links_box.see("end")

    def clear_links(self):
        self.links_box.delete("1.0", "end")

    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def set_status(self, message):
        self.status_text.set(message)
        self.root.update_idletasks()

    def update_counts(self):
        self.count_text.set(
            f"Downloaded: {self.downloaded}  Errors: {self.errors}  "
            f"({self.current_index}/{self.total})"
        )
        self.root.update_idletasks()

    def set_progress(self, value):
        self.progress["value"] = max(0, min(100, value))
        self.root.update_idletasks()

    def _overall_progress(self, per_file_pct):
        if self.total == 0:
            return 0
        completed = self.current_index - 1
        return ((completed + per_file_pct / 100) / self.total) * 100

    # ---------- download flow ----------
    def start_download(self):
        raw = self.links_box.get("1.0", "end").strip()
        if not raw:
            messagebox.showwarning("No links", "Please paste at least one link.")
            return
        links = [l for l in raw.split() if l.strip()]
        if not links:
            messagebox.showwarning("No links", "Please paste at least one link.")
            return

        os.makedirs(self.download_dir.get(), exist_ok=True)
        self._save_current_settings()

        self.downloaded = 0
        self.errors = 0
        self.total = len(links)
        self.current_index = 0
        self.pending_links = links
        self.stop_requested = False

        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

        self.download_btn.config(state="disabled", text="⏳ Downloading...")
        self.stop_btn.config(state="normal")
        self.resume_btn.config(state="disabled")
        self.set_progress(0)
        self.update_counts()

        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while self.pending_links:
            if self.stop_requested:
                break
            url = self.pending_links.pop(0)
            self.current_url = url
            self.current_index += 1
            self.update_counts()
            self.set_status(f"[{self.current_index}/{self.total}] {url}")
            self.log(f"\n=== [{self.current_index}/{self.total}] {url} ===")

            ok = self._download_one(url)
            if ok:
                self.downloaded += 1
            elif not self.stop_requested:
                self.errors += 1

            self.set_progress((self.current_index / self.total) * 100)
            self.update_counts()

            if self.stop_requested:
                break

        self.current_proc = None
        if self.stop_requested:
            self.set_status("⏸ Stopped. Click Continue to resume.")
            self.root.after(0, lambda: (
                self.stop_btn.config(state="disabled"),
                self.resume_btn.config(state="normal"),
                self.download_btn.config(state="normal", text="⬇  DOWNLOAD"),
            ))
        else:
            self.set_status("✅ All done.")
            self.root.after(0, lambda: (
                self.stop_btn.config(state="disabled"),
                self.resume_btn.config(state="disabled"),
                self.download_btn.config(state="normal", text="⬇  DOWNLOAD"),
            ))

    def _video_format_string(self):
        q = self.video_quality.get()
        if q == "Original (Best)":
            return "bv*+ba/b"
        m = re.match(r"(\d+)p", q)
        if not m:
            return "bv*+ba/b"
        h = m.group(1)
        return f"bv*[height<={h}]+ba/b[height<={h}]"

    def _audio_quality_number(self):
        q = self.audio_quality.get()
        if q == "Original (Best)":
            return "0"
        if q.startswith("High"):
            return "2"
        if q.startswith("Medium"):
            return "5"
        if q.startswith("Low"):
            return "9"
        return "0"

    def _build_args(self, url):
        common = [
            "--embed-thumbnail",
            "--embed-metadata",
            "--ffmpeg-location", BUNDLE_DIR,
            "--newline", "--no-warnings",
            "-o", os.path.join(self.download_dir.get(), "%(title)s.%(ext)s"),
            url,
        ]
        if self.format_choice.get() == "audio":
            return [
                YTDLP, "-x", "--audio-format", "mp3",
                "--audio-quality", self._audio_quality_number(),
                "--convert-thumbnails", "jpg",
                *common,
            ]
        return [
            YTDLP,
            "-f", self._video_format_string(),
            "--merge-output-format", "mp4",
            *common,
        ]

    def _download_one(self, url):
        args = self._build_args(url)
        self.log("CMD: " + " ".join(args))
        popen_kwargs = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
        }
        if IS_WINDOWS:
            popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        try:
            self.current_proc = subprocess.Popen(args, **popen_kwargs)
        except FileNotFoundError:
            self.log(f"❌ yt-dlp not found at {YTDLP}")
            return False

        if self.current_proc.stdout is None:
            self.log("❌ Could not read yt-dlp output.")
            return False

        pct_re = re.compile(r"\[download\]\s+([\d.]+)%")

        for line in self.current_proc.stdout:
            if self.stop_requested:
                self.current_proc.terminate()
                break
            line = line.rstrip()
            if not line:
                continue
            m = pct_re.search(line)
            if m:
                try:
                    per_file = float(m.group(1))
                    self.set_progress(self._overall_progress(per_file))
                except ValueError:
                    pass
                self.set_status(f"[{self.current_index}/{self.total}] {line}")
            elif "ERROR" in line.upper():
                self.log(f"❌ {line}")
            elif (line.startswith("[download] Destination")
                  or "has already been downloaded" in line):
                self.log(line)

        self.current_proc.wait()
        rc = self.current_proc.returncode
        self.current_proc = None

        if self.stop_requested:
            return False
        if rc == 0:
            self.log("✅ Success")
            return True
        self.log(f"❌ Failed (exit code {rc})")
        return False

    def stop_download(self):
        self.stop_requested = True
        if self.current_proc is not None:
            try:
                self.current_proc.terminate()
            except Exception:
                pass
        self.set_status("⏸ Stopping...")
        self.stop_btn.config(state="disabled")

    def resume_download(self):
        if self.current_url:
            self.pending_links.insert(0, self.current_url)
        self.stop_requested = False
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.download_btn.config(state="disabled", text="⏳ Downloading...")
        self.set_status("▶ Resuming...")
        threading.Thread(target=self._worker, daemon=True).start()

    # ---------- update ----------
    def check_for_updates(self):
        self.set_status("🔄 Checking for updates...")
        threading.Thread(target=self._do_update, daemon=True).start()

    def _platform_url(self):
        if IS_WINDOWS:
            return YTDLP_URLS["win"]
        if IS_MAC:
            return YTDLP_URLS["darwin"]
        return YTDLP_URLS["linux"]

    def _is_writable(self, path):
        try:
            if os.path.exists(path):
                return os.access(path, os.W_OK)
            return os.access(os.path.dirname(path), os.W_OK)
        except Exception:
            return False

    def _do_update(self):
        try:
            url = self._platform_url()
            tmp = os.path.join(tempfile.gettempdir(), _binary_name("yt-dlp"))
            self.log(f"⬇ Downloading latest yt-dlp to {tmp} ...")
            urllib.request.urlretrieve(url, tmp)

            if self._is_writable(YTDLP):
                try:
                    shutil.move(tmp, YTDLP)
                    self.log("✅ yt-dlp updated in app folder.")
                    self.set_status("✅ Update installed.")
                    return
                except PermissionError:
                    pass

            if IS_WINDOWS:
                self.log("🔒 Requesting admin rights to update in place...")
                helper = os.path.join(tempfile.gettempdir(), "ytdlp_update.bat")
                with open(helper, "w", encoding="utf-8") as f:
                    f.write(f'@echo off\nmove /Y "{tmp}" "{YTDLP}"\n')
                try:
                    rc = ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", "cmd.exe", f'/c "{helper}"', None, 0
                    )
                    if rc > 32:
                        time.sleep(2)
                        if os.path.exists(YTDLP) and os.path.getsize(YTDLP) > 5_000_000:
                            self.log("✅ yt-dlp updated (elevated).")
                            self.set_status("✅ Update installed.")
                            return
                except Exception as e:
                    self.log(f"⚠ Elevation failed: {e}")

            self.log("⚠ Falling back to user folder update.")
            fallback = os.path.join(_user_bin_dir(), _binary_name("yt-dlp"))
            try:
                if os.path.exists(fallback):
                    os.remove(fallback)
                shutil.move(tmp, fallback)
                if not IS_WINDOWS:
                    os.chmod(fallback, 0o755)
                self.log(f"✅ yt-dlp saved to {fallback}")
                self.log("   The app will use this copy on next launch.")
                try:
                    with open(PREF_FILE, "w") as f:
                        json.dump({"yt-dlp": fallback}, f)
                except Exception:
                    pass
                self.set_status("✅ Update installed (user folder).")
            except Exception as e:
                self.log(f"❌ Fallback update failed: {e}")
                self.set_status("❌ Update failed. See log.")
        except Exception as e:
            self.log(f"❌ Update failed: {e}")
            self.set_status("❌ Update failed. See log.")


# ============================================================
# Entry
# ============================================================

def _resource_path(name):
    candidates = [
        os.path.join(APP_DIR, name),
        os.path.join(APP_DIR, "_internal", name),
    ]
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(os.path.join(meipass, name))
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartDownloaderApp(root)

    _icon_ref = None

    def _set_icon():
        global _icon_ref
        ico = _resource_path("icon.ico")
        png = _resource_path("icon.png")
        if ico and IS_WINDOWS:
            try:
                root.iconbitmap(ico)
                return
            except Exception:
                pass
        if png:
            try:
                img = tk.PhotoImage(file=png)
                root.iconphoto(True, img)
                _icon_ref = img
                return
            except Exception:
                pass
        if ico:
            try:
                img = tk.PhotoImage(file=ico)
                root.iconphoto(True, img)
                _icon_ref = img
            except Exception:
                pass

    _set_icon()
    root.mainloop()
