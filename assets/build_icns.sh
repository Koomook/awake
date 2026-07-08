#!/usr/bin/env bash
# Build AppIcon.icns from master.png (run render_icon.py first).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

SET="Awake.iconset"
rm -rf "$SET"
mkdir -p "$SET"
for s in 16 32 128 256 512; do
  sips -z "$s" "$s"       master.png --out "$SET/icon_${s}x${s}.png"      >/dev/null
  sips -z $((s*2)) $((s*2)) master.png --out "$SET/icon_${s}x${s}@2x.png" >/dev/null
done
iconutil -c icns "$SET" -o AppIcon.icns
rm -rf "$SET"
echo "wrote $(pwd)/AppIcon.icns"
