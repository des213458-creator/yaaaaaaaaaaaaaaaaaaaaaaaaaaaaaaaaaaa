#!/usr/bin/env bash
set -euo pipefail

echo "Running install.sh: downloading N_m3u8DL-RE and ffmpeg if needed..."

GITHUB_REPO="nilaoda/N_m3u8DL-RE"

API_JSON=$(curl -s "https://api.github.com/repos/${GITHUB_REPO}/releases/latest") || true
ASSET_URL=$(echo "$API_JSON" | grep -Eo "https[^\"]*linux[^\"]*zip" | head -n1 || true)

if [ -z "${ASSET_URL:-}" ]; then
  echo "⚠️ لم أجد ملف N_m3u8DL-RE تلقائياً، يمكنك رفعه يدوياً."
else
  echo "✅ Found N asset: $ASSET_URL"
  curl -L "$ASSET_URL" -o N_m3u8DL-RE.zip || true
  unzip -o N_m3u8DL-RE.zip -d n_tmp || true
  EXE=$(find n_tmp -type f -name "N_m3u8DL-RE" | head -n1 || true)
  if [ -n "${EXE:-}" ]; then
    mv "$EXE" ./N_m3u8DL-RE
    chmod +x ./N_m3u8DL-RE
    echo "✅ N_m3u8DL-RE installed."
  fi
fi

# Install ffmpeg if not already present
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "⚙️ Downloading static ffmpeg build..."
  FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
  curl -L "$FFMPEG_URL" -o ffmpeg_static.tar.xz || true
  tar -xJf ffmpeg_static.tar.xz || true
  DIR=$(find . -maxdepth 2 -type d -name "ffmpeg*" | head -n1 || true)
  if [ -n "${DIR:-}" ]; then
    cp "$DIR/ffmpeg" ./ffmpeg || true
    cp "$DIR/ffprobe" ./ffprobe || true
    chmod +x ./ffmpeg ./ffprobe || true
    echo "✅ ffmpeg static installed."
  fi
else
  echo "ffmpeg already present."
fi

echo "🎉 install.sh finished successfully."
