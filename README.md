markdown
# 🎬 Smart Music and Video Downloader 🎵

A simple, powerful desktop app for downloading music and videos from YouTube and 1000+ other sites — built on top of [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [FFmpeg](https://ffmpeg.org/).

Paste one or more links, pick Audio or Video, choose a quality, and click Download. That's it.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- **🎧 Audio downloads** — Extract MP3 with embedded cover art and metadata (title, artist, album)
- **🎬 Video downloads** — Best quality MP4 up to 4K, with merged audio and embedded thumbnail
- **📋 Multi-link support** — Paste one or many links at once (one per line or space-separated)
- **🎚️ Quality control** — Choose from Original (best), 1080p, 720p, 480p, or 360p for video; Original, High, Medium, or Low for audio
- **📋 Paste & Clear buttons** — One-click clipboard paste, one-click reset
- **⏸ Stop / Resume** — Pause downloads mid-way and continue later
- **📊 Live progress** — Progress bar and per-file counter, showing downloaded / errors / current index
- **🔄 Auto-update** — Checks for new yt-dlp releases and updates in place (with admin fallback)
- **💾 Remembers settings** — Download folder, format choice, and quality persist between sessions
- **🖼️ Embedded metadata** — Cover art, title, and artist written into every MP3
- **🎨 Native icon** — Custom app icon on the window, taskbar, and file explorer
- **🌍 Cross-platform** — Available for Windows, macOS, and Linux
- **📦 No dependencies required** — Python, FFmpeg, and yt-dlp are bundled into the installer

---

## 📥 Installation

### 🪟 Windows

1. Download **`SmartMusicVideoDownloaderSetup.exe`** from the [Releases page](../../releases/latest).
2. Double-click the installer.
3. If Windows shows a SmartScreen warning, click **More info → Run anyway**.
4. Follow the wizard. The app installs to `Program Files\SmartMusicVideoDownloader\`.
5. Launch from the **Start Menu** or **Desktop shortcut**.

**Requirements:** Windows 10 or 11 (64-bit). No Python or FFmpeg installation needed.

### 🍎 macOS - Coming soon

1. Download **`SmartMusicVideoDownloader.dmg`** from the [Releases page](../../releases/latest).
2. Open the DMG.
3. Drag **Smart Music and Video Downloader** into your **Applications** folder.
4. On first launch, right-click the app and choose **Open** (macOS Gatekeeper).
5. Click **Open** in the confirmation dialog.

**Requirements:** macOS 11 (Big Sur) or later.

### 🐧 Linux

1. Download **`SmartMusicVideoDownloader.deb`** from the [Releases page](../../releases/latest).
2. Install via terminal:
   ```bash
   sudo dpkg -i SmartMusicVideoDownloader.deb
Or double-click the .deb file in your file manager.

Launch from your application menu (search for "Smart Music and Video Downloader").

Requirements: Ubuntu 22.04+, Debian 12+, or any distro with glibc 2.35+.

🚀 Quick Start
Launch the app.

Paste your link(s) in the big text box — one per line, or space-separated.

YouTube videos

YouTube playlists

YouTube Music

Vimeo, Dailymotion, SoundCloud, TikTok, Twitter/X, Instagram, and 1000+ more

Choose your format:

🎧 Audio (MP3) — For music

🎬 Video (MP4) — For videos

Choose your quality:

Video: Original (Best), 1080p, 720p, 480p, 360p

Audio: Original (Best), High (320 kbps), Medium (192 kbps), Low (128 kbps)

Click ⬇ DOWNLOAD.

Files save to ~/Downloads by default. Change the folder anytime with Change Folder.

🎛️ UI Overview
text
┌──────────────────────────────────────────────────────────────────────┐
│ 🎬 Smart Music and Video Downloader 🎵        [🔄 Check for Updates] │
│                                                                      │
│ Save to: [C:\Users\you\Downloads              ]  [Change Folder]    │
│                                                                      │
│ Paste one or more links...        [📋 Paste]  [🗑 Clear]            │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ https://youtu.be/...                                             │ │
│ │ https://youtu.be/...                                             │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ Download as:  ⦿ 🎧 Audio   ○ 🎬 Video    Quality: [Original (Best)] │
│                                                                      │
│ [████████████░░░░░░░░░░░░░░░░░░]  Downloaded: 3  Errors: 0  (3/5)   │
│                                                                      │
│      [⬇ DOWNLOAD]     [⏸ STOP]     [▶ CONTINUE]                     │
│                                                                      │
│ Status: [3/5] Downloading...                                         │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ [download] 45.2% of 12.34MiB at 3.2MiB/s ETA 00:03              │ │
│ └──────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
🔧 How It Works
yt-dlp does the actual downloading and format extraction

FFmpeg handles conversion (video → MP3), merging (separate video + audio streams → single MP4), and embedding thumbnails/metadata

The app itself is a Python GUI (Tkinter) that orchestrates the two binaries and displays progress

When you click Download, the app spawns yt-dlp.exe as a child process and streams its output to the log area

Task Manager during a download:

SmartMusicVideoDownloader.exe — the GUI

yt-dlp.exe — the active download

ffmpeg.exe — appears briefly during postprocessing (conversion/merging)

🔄 Updating
Click 🔄 Check for Updates in the top-right corner to download the latest yt-dlp. This matters because YouTube frequently changes how it serves videos, and older yt-dlp versions can break.

Update priority:

Try to overwrite yt-dlp.exe in the app folder (needs write permission).

If denied, request admin rights via UAC.

If still denied, save the new version to %LOCALAPPDATA%\SmartMusicVideoDownloader\bin\ and use it automatically next launch.

No need to re-download the full app for yt-dlp updates.

⚙️ Settings Storage
Your preferences are saved to:

OS	Location
Windows	%LOCALAPPDATA%\SmartMusicVideoDownloader\settings.json
macOS	~/Library/Application Support/SmartMusicVideoDownloader/settings.json
Linux	~/.local/share/SmartMusicVideoDownloader/settings.json
Saved values: download folder, Audio/Video choice, video quality, audio quality.

Delete the file to reset to defaults.

🛠️ Building from Source
Prerequisites
Python 3.8+ (with Tkinter)

yt-dlp binary for your platform

FFmpeg + FFprobe binaries for your platform

Setup
bash
git clone https://github.com/lakepee/smart-music-video-downloader.git
cd smart-music-video-downloader
Place these files in the project root:

Windows: yt-dlp.exe, ffmpeg.exe, ffprobe.exe

macOS: yt-dlp_macos, ffmpeg, ffprobe

Linux: yt-dlp, ffmpeg, ffprobe

Run as a script
bash
python app.py
Build a distributable
Windows:

powershell
.\build.ps1
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
Produces Output\SmartMusicVideoDownloaderSetup.exe.

macOS:

bash
chmod +x build_macos.sh
./build_macos.sh
Produces dist/SmartMusicVideoDownloader.dmg.

Linux:

bash
chmod +x build_linux.sh
./build_linux.sh
Produces dist/SmartMusicVideoDownloader.deb.

❓ Troubleshooting
"ERROR: Preprocessing: ffmpeg not found"
The FFmpeg binaries aren't next to the app. If you installed via the official installer, this shouldn't happen. If you're running from source, make sure ffmpeg.exe and ffprobe.exe are in the same folder as app.py.

"ERROR: unable to download video data: HTTP Error 403"
YouTube has changed something on their end. Click 🔄 Check for Updates to grab the latest yt-dlp, then try again.

Downloads complete but files aren't where I expect
Check the Save to: path at the top of the app. The default is ~/Downloads. If you changed the folder and forgot, close and reopen the app — it remembers your last choice.

Taskbar icon is the default Python feather
Windows caches taskbar icons. Right-click the icon in the taskbar → Unpin, then relaunch and pin again.

App opens then closes immediately
Try running from a terminal to see the error:

powershell
.\SmartMusicVideoDownloader.exe
If it crashes with a Python traceback, open an issue and paste it.

Download seems stuck
Check the log area at the bottom of the app. If yt-dlp is downloading slowly (YouTube throttles sometimes), the progress bar will still update. If it's frozen for more than a minute, click ⏸ STOP then ▶ CONTINUE.

🛡️ Legal Notice
This tool is intended for personal use only and for downloading content you have the right to download. Respect the terms of service of the sites you use it with. Do not use this tool to redistribute copyrighted material.

The developers of this app are not responsible for how you use it.

🙏 Credits
yt-dlp — The amazing downloader engine

FFmpeg — Audio/video conversion and merging

PyInstaller — Packaging Python apps into standalone binaries

Inno Setup — Windows installer

📄 License
MIT License — see LICENSE for details.

💬 Support
Bug reports / feature requests: Open an issue

Security concerns: Email peterokerinola@gmail.com or contact me https://www.linkedin.com/in/peter-okerinola/

Questions: Start a Discussion

🌟 Star History
If this app saves you time, consider giving it a ⭐ — it helps others find it.

Made with ❤️ by Peter Okerinola
