# /// script
# requires-python = ">=3.11"
# dependencies = ["rumps"]
# ///
"""Keep Awake — a tiny macOS menu bar toggle that stops your Mac from
sleeping when the lid is closed, by flipping pmset's ``disablesleep`` flag.
"""

from __future__ import annotations

import subprocess
from typing import Final

import rumps

__version__: Final = "0.1.0"

APP_NAME: Final = "Keep Awake"

# Absolute paths so the app works under launchd's minimal PATH.
PMSET: Final = "/usr/bin/pmset"
SUDO: Final = "/usr/bin/sudo"
OSASCRIPT: Final = "/usr/bin/osascript"

SLEEP_DISABLED_KEY: Final = "SleepDisabled"
REFRESH_INTERVAL_SECONDS: Final = 5

ICON_ENABLED: Final = "●"    # on  — lid close won't sleep
ICON_DISABLED: Final = "○"   # off — normal sleep behavior
ICON_UNKNOWN: Final = "◐"    # current state couldn't be read

TOGGLE_LABEL: Final = "Keep Awake"
STATUS_ENABLED: Final = "Status: On (won't sleep on lid close)"
STATUS_DISABLED: Final = "Status: Off (normal)"
STATUS_UNKNOWN: Final = "Status: unavailable"


def query_enabled() -> bool | None:
    """Return whether pmset's SleepDisabled flag is set.

    Returns ``True``/``False`` when known, or ``None`` if pmset could not
    be read (so callers can distinguish "off" from "unknown").
    """
    try:
        result = subprocess.run(
            [PMSET, "-g"], capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return None
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if SLEEP_DISABLED_KEY in line:
            return line.split()[-1] == "1"
    return False  # flag absent => disabled


def set_enabled(enabled: bool) -> bool:
    """Set pmset's disablesleep flag, returning whether it succeeded.

    Tries passwordless sudo first; if that isn't configured, falls back to
    a GUI admin authorization prompt (Touch ID capable).
    """
    value = "1" if enabled else "0"
    try:
        passwordless = subprocess.run(
            [SUDO, "-n", PMSET, "-a", "disablesleep", value],
            capture_output=True, text=True, timeout=10, check=False,
        )
        if passwordless.returncode == 0:
            return True

        # No passwordless sudo: fall back to a GUI admin prompt (Touch ID).
        script = (
            f'do shell script "{PMSET} -a disablesleep {value}" '
            "with administrator privileges"
        )
        prompt = subprocess.run(
            [OSASCRIPT, "-e", script],
            capture_output=True, text=True, timeout=120, check=False,
        )
        return prompt.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


class KeepAwakeApp(rumps.App):
    """Menu bar app that toggles pmset's disablesleep setting."""

    def __init__(self) -> None:
        super().__init__(APP_NAME, title=ICON_DISABLED, quit_button="Quit")
        self.status_item = rumps.MenuItem("")
        self.menu = [TOGGLE_LABEL, self.status_item, None]
        self._render(query_enabled())

    @rumps.timer(REFRESH_INTERVAL_SECONDS)
    def refresh(self, _sender: rumps.Timer | None = None) -> None:
        """Keep the UI in sync with the real system state."""
        self._render(query_enabled())

    @rumps.clicked(TOGGLE_LABEL)
    def toggle(self, _sender: rumps.MenuItem) -> None:
        """Flip the keep-awake state (an unknown state is treated as off)."""
        target = query_enabled() is not True
        if set_enabled(target):
            self._render(target)
        else:
            self._report_failure()
            self._render(query_enabled())

    def _render(self, state: bool | None) -> None:
        """Reflect ``state`` (True/False/None) in the icon and menu."""
        if state is None:
            self.title = ICON_UNKNOWN
            self.menu[TOGGLE_LABEL].state = False
            self.status_item.title = STATUS_UNKNOWN
        else:
            self.title = ICON_ENABLED if state else ICON_DISABLED
            self.menu[TOGGLE_LABEL].state = state
            self.status_item.title = STATUS_ENABLED if state else STATUS_DISABLED

    def _report_failure(self) -> None:
        """Tell the user a toggle failed, resiliently across run modes."""
        message = "Authorization was cancelled or denied."
        try:
            rumps.notification(APP_NAME, "Change failed", message)
        except Exception:
            # Bare-script runs have no bundle id, so Notification Center may
            # be unavailable — fall back to a modal alert.
            rumps.alert(title=f"{APP_NAME}: change failed", message=message, ok="OK")


def main() -> None:
    KeepAwakeApp().run()


if __name__ == "__main__":
    main()
