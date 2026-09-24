$ErrorActionPreference = "Stop"

Write-Host "Cleaning old build..."
Remove-Item -Recurse -Force .\build, .\dist -ErrorAction SilentlyContinue

Write-Host "Installing build tools..."
pip install --upgrade pyinstaller pillow setuptools

Write-Host "Building Windows app (folder mode)..."
pyinstaller --noconfirm --onedir --windowed --name "SmartMusicVideoDownloader" --icon "icon.ico" --add-data "icon.png;." --add-data "icon.ico;." app.py

Write-Host "Copying binaries next to the exe..."
$out = "dist\SmartMusicVideoDownloader"
Copy-Item "yt-dlp.exe"  $out
Copy-Item "ffmpeg.exe"  $out
Copy-Item "ffprobe.exe" $out

Write-Host "Done: $out\SmartMusicVideoDownloader.exe"
