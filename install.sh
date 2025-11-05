#!/usr/bin/env bash
set -euo pipefail
echo "Running install.sh: download N_m3u8DL-RE and (optionally) ffmpeg static if needed..."

GITHUB_REPO="nilaoda/N_m3u8DL-RE"

API_JSON=$(curl -s "https://api.github.com/repos/${GITHUB_REPO}/releases/latest")
ASSET_URL=$(echo "$API_JSON" | grep -E "browser_download_url.*linux" | head -n1 | sed -E 's/.*"(https.*)".*/\1/')

if [ -z "$ASSET_URL" ]; then
  echo "لم أجد ملف N تلقائياً. ستحتاج لرفع N_m3u8DL-RE يدوياً إلى الريبو."
  exit 0
fi

echo "Found N asset: $ASSET_URL"
curl -L "$ASSET_URL" -o N_m3u8DL-RE.zip || true
if [ -f N_m3u8DL-RE.zip ]; then
  unzip -o N_m3u8DL-RE.zip -d n_tmp || true
  EXE=$(find n_tmp -type f -name "N_m3u8DL-RE" | head -n1 || true)
  if [ -n "$EXE" ]; then
    mv "$EXE" ./N_m3u8DL-RE
    chmod +x ./N_m3u8DL-RE
    echo "N_m3u8DL-RE installed."
  fi
fi

# Try to download a static ffmpeg if not present (so N can call ffmpeg if needed)
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg not found, attempting to download static ffmpeg build..."
  FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
  curl -L "$FFMPEG_URL" -o ffmpeg_static.tar.xz || true
  if [ -f ffmpeg_static.tar.xz ]; then
    tar -xJf ffmpeg_static.tar.xz || true
    DIR=$(find . -maxdepth 2 -type d -name "ffmpeg*" | head -n1 || true)
    if [ -n "$DIR" ]; then
      cp "$DIR/ffmpeg" ./ffmpeg || true
      cp "$DIR/ffprobe" ./ffprobe || true
      chmod +x ./ffmpeg ./ffprobe || true
      echo "ffmpeg static installed."
    fi
  fi
fi

echo "install.sh finished."
