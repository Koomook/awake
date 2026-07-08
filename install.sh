#!/usr/bin/env bash
# Install Keep Awake as a login-time menu bar app via a per-user LaunchAgent.
# The plist is generated here so no absolute paths are baked into the repo.
set -euo pipefail

LABEL="com.koomook.keepawake"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UV="$(command -v uv || true)"
AGENTS="$HOME/Library/LaunchAgents"
PLIST="$AGENTS/$LABEL.plist"

if [ -z "$UV" ]; then
  echo "error: 'uv' not found on PATH. Install it: https://docs.astral.sh/uv/" >&2
  exit 1
fi

mkdir -p "$AGENTS"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$UV</string>
        <string>run</string>
        <string>$DIR/app.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/keepawake.out.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/keepawake.err.log</string>
</dict>
</plist>
EOF

# Reload if already installed, then start in the GUI session.
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "Installed. The Keep Awake icon should now be in your menu bar,"
echo "and it will start automatically at login."
echo "Uninstall with: ./uninstall.sh"
