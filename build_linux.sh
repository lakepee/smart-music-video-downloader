#!/usr/bin/env bash
set -e

echo "Cleaning..."
rm -rf build dist package

echo "Installing build tools..."
pip3 install --upgrade pyinstaller pillow

echo "Building Linux binary..."
pyinstaller \
  --noconfirm --onefile \
  --name "SmartMusicVideoDownloader" \
  --icon "icon.png" \
  --add-binary "yt-dlp:." \
  --add-binary "ffmpeg:." \
  --add-binary "ffprobe:." \
  --add-data "icon.png:." \
  app.py

echo "Creating .deb package structure..."
mkdir -p package/DEBIAN
mkdir -p package/usr/local/bin
mkdir -p package/usr/share/applications
mkdir -p package/usr/share/icons/hicolor/256x256/apps

cp dist/SmartMusicVideoDownloader package/usr/local/bin/
cp icon.png package/usr/share/icons/hicolor/256x256/apps/smartmusicvideodownloader.png

cat > package/DEBIAN/control <<EOF
Package: smartmusicvideodownloader
Version: 1.0.0
Section: sound
Priority: optional
Architecture: amd64
Maintainer: Your Name <you@example.com>
Description: Smart Music and Video Downloader built on yt-dlp.
EOF

cat > package/usr/share/applications/smartmusicvideodownloader.desktop <<EOF
[Desktop Entry]
Name=Smart Music and Video Downloader
Exec=/usr/local/bin/SmartMusicVideoDownloader
Icon=smartmusicvideodownloader
Type=Application
Categories=AudioVideo;Audio;Video;
EOF

dpkg-deb --build package dist/SmartMusicVideoDownloader.deb

echo "Done: dist/SmartMusicVideoDownloader.deb"
