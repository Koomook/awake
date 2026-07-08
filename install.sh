#!/usr/bin/env bash
# Install Awake so Spotlight can launch it and it starts at login.
#
# Builds an AppleScript applet (~/Applications/Awake.app) as the launcher.
# An applet's runtime stub is Apple-signed, so Gatekeeper/LaunchServices let
# it launch — unlike a hand-rolled unsigned .app. The applet just starts the
# real menu bar app (installed to Application Support) and quits.
set -euo pipefail

NAME="Awake"
BUNDLE_ID="com.koomook.awake"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUPPORT="$HOME/Library/Application Support/$NAME"
APP="$HOME/Applications/$NAME.app"
AGENTS="$HOME/Library/LaunchAgents"
PLIST="$AGENTS/$BUNDLE_ID.plist"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: 'uv' not found on PATH. Install it: https://docs.astral.sh/uv/" >&2
  exit 1
fi

# --- Install the app itself ------------------------------------------------
mkdir -p "$SUPPORT"
cp "$SRC/app.py" "$SUPPORT/app.py"

# --- Build the Spotlight launcher (AppleScript applet) ---------------------
rm -rf "$APP"
osacompile -o "$APP" "$SRC/awake.applescript"

# --- Start at login (and now) ----------------------------------------------
mkdir -p "$AGENTS"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>$BUNDLE_ID</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/open</string>
        <string>$APP</string>
    </array>
    <key>RunAtLoad</key><true/>
</dict>
</plist>
EOF

# Reload (RunAtLoad also launches it now).
launchctl bootout "gui/$(id -u)/$BUNDLE_ID" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "Installed $APP"
echo "• Spotlight: press Cmd-Space, type \"$NAME\", hit Return."
echo "• It now runs and starts automatically at login (menu bar: ☕/💤)."
echo "• Uninstall with: ./uninstall.sh"
