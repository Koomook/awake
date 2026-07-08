#!/usr/bin/env bash
# Build a self-contained Awake.app with py2app, ad-hoc sign it, install it to
# ~/Applications (Spotlight-launchable), and start it at login.
#
# The bundle embeds its own Python + rumps, so it does not depend on uv or a
# network connection at runtime. uv is only used at build time to provide a
# py2app-compatible Python.
set -euo pipefail

NAME="Awake"
BUNDLE_ID="com.koomook.awake"
PYVER="3.12"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$HOME/Applications/$NAME.app"
AGENTS="$HOME/Library/LaunchAgents"
PLIST="$AGENTS/$BUNDLE_ID.plist"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: 'uv' not found on PATH. Install it: https://docs.astral.sh/uv/" >&2
  exit 1
fi

# --- Build the self-contained bundle ---------------------------------------
cd "$SRC"
rm -rf build dist
uv run --python "$PYVER" --with py2app --with rumps python setup.py py2app

# --- Stop any running/previous copy, then install --------------------------
launchctl bootout "gui/$(id -u)/$BUNDLE_ID" 2>/dev/null || true
pkill -f "$NAME.app/Contents/MacOS/$NAME" 2>/dev/null || true
mkdir -p "$HOME/Applications"
rm -rf "$APP"
ditto "dist/$NAME.app" "$APP"

# --- Ad-hoc sign the installed app -----------------------------------------
codesign --force --deep --sign - "$APP"
codesign --verify --deep --strict "$APP"

# Remove build artifacts so no duplicate copy lingers in Spotlight.
rm -rf build dist

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
launchctl bootout "gui/$(id -u)/$BUNDLE_ID" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "Installed $APP (self-contained, ad-hoc signed)"
echo "• Spotlight: press Cmd-Space, type \"$NAME\", hit Return."
echo "• It now runs and starts automatically at login (menu bar: ☕/💤)."
echo "• First Finder launch may need right-click → Open once (unsigned by Apple)."
echo "• Uninstall with: ./uninstall.sh"
