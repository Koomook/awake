#!/usr/bin/env bash
# Stop Awake and remove its login item and app bundle. This does not change
# the current pmset setting — toggle it off in the app first if you want the
# machine to sleep normally again.
set -euo pipefail

NAME="Awake"
BUNDLE_ID="com.koomook.awake"
APP="$HOME/Applications/$NAME.app"
PLIST="$HOME/Library/LaunchAgents/$BUNDLE_ID.plist"

launchctl bootout "gui/$(id -u)/$BUNDLE_ID" 2>/dev/null || true
rm -f "$PLIST"
pkill -f "$NAME.app/Contents/MacOS/$NAME" 2>/dev/null || true
rm -rf "$APP"
rm -f "/tmp/awake-$(id -u).lock"
# Remove leftovers from older install methods, if present.
rm -rf "$HOME/Library/Application Support/$NAME"

echo "Uninstalled. Awake will no longer start at login."
