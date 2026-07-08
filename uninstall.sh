#!/usr/bin/env bash
# Stop and remove the Keep Awake LaunchAgent. This does not change the
# current pmset setting — flip it off in the app first if you want the
# machine to sleep normally again.
set -euo pipefail

LABEL="com.koomook.keepawake"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$PLIST"

echo "Uninstalled. Keep Awake will no longer start at login."
