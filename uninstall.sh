#!/usr/bin/env bash
# Stop Awake and remove its launcher, login item, and installed files. This
# does not change the current pmset setting — toggle it off in the app first
# if you want the machine to sleep normally again.
set -euo pipefail

NAME="Awake"
BUNDLE_ID="com.koomook.awake"
SUPPORT="$HOME/Library/Application Support/$NAME"
APP="$HOME/Applications/$NAME.app"
PLIST="$HOME/Library/LaunchAgents/$BUNDLE_ID.plist"

launchctl bootout "gui/$(id -u)/$BUNDLE_ID" 2>/dev/null || true
rm -f "$PLIST"
pkill -f "$SUPPORT/app.py" 2>/dev/null || true
rm -rf "$APP" "$SUPPORT"

echo "Uninstalled. Awake will no longer start at login."
