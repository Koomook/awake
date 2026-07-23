# /// script
# requires-python = ">=3.11"
# dependencies = ["rumps"]
# ///
"""Awake — a tiny macOS menu bar toggle that stops your Mac from sleeping
when the lid is closed, by flipping pmset's ``disablesleep`` flag.
"""

from __future__ import annotations

import fcntl
import os
import socket
import subprocess
import sys
import threading
from typing import Final

import rumps

__version__: Final = "0.3.0"

APP_NAME: Final = "Awake"

# Absolute paths so the app works under launchd's minimal PATH.
PMSET: Final = "/usr/bin/pmset"
SUDO: Final = "/usr/bin/sudo"
OSASCRIPT: Final = "/usr/bin/osascript"

SLEEP_DISABLED_KEY: Final = "SleepDisabled"
REFRESH_INTERVAL_SECONDS: Final = 5
KEEPALIVE_INTERVAL_SECONDS: Final = 20
KEEPALIVE_TARGET: Final = ("1.1.1.1", 53)

ICON_ENABLED: Final = "☕"    # on  — lid close won't sleep
ICON_DISABLED: Final = "💤"   # off — normal sleep behavior
ICON_UNKNOWN: Final = "❓"    # current state couldn't be read

TOGGLE_LABEL: Final = "Keep awake"
STATUS_ENABLED: Final = "Status: On (lid + hotspot keepalive)"
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


def send_network_keepalive() -> None:
    """Send one tiny DNS packet so phone hotspots do not see an idle client."""
    # Standard recursive A query for one.one.one.one. A reply is unnecessary:
    # putting the packet on the Wi-Fi link is enough to refresh hotspot idle
    # activity, and avoiding recv keeps this worker short and resilient.
    query = (
        b"\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
        b"\x03one\x03one\x03one\x03one\x00\x00\x01\x00\x01"
    )
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(query, KEEPALIVE_TARGET)
    except OSError:
        # Networks come and go. The next interval retries without surfacing a
        # noisy alert or affecting the sleep-prevention toggle.
        pass


def network_keepalive_loop(stop: threading.Event) -> None:
    """Keep network activity alive until ``stop`` is signalled."""
    while not stop.is_set():
        send_network_keepalive()
        stop.wait(KEEPALIVE_INTERVAL_SECONDS)


class AwakeApp(rumps.App):
    """Menu bar app that toggles pmset's disablesleep setting."""

    def __init__(self) -> None:
        super().__init__(APP_NAME, title=ICON_DISABLED, quit_button="Quit")
        self.status_item = rumps.MenuItem("")
        self.menu = [TOGGLE_LABEL, self.status_item, None]
        self._keepalive_stop: threading.Event | None = None
        self._keepalive_thread: threading.Thread | None = None
        state = query_enabled()
        self._sync_keepalive(state is True)
        self._render(state)

    @rumps.timer(REFRESH_INTERVAL_SECONDS)
    def refresh(self, _sender: rumps.Timer | None = None) -> None:
        """Keep the UI in sync with the real system state."""
        state = query_enabled()
        self._sync_keepalive(state is True)
        self._render(state)

    @rumps.clicked(TOGGLE_LABEL)
    def toggle(self, _sender: rumps.MenuItem) -> None:
        """Flip the keep-awake state (an unknown state is treated as off)."""
        target = query_enabled() is not True
        if set_enabled(target):
            self._sync_keepalive(target)
            self._render(target)
        else:
            self._report_failure()
            state = query_enabled()
            self._sync_keepalive(state is True)
            self._render(state)

    def _sync_keepalive(self, enabled: bool) -> None:
        """Start or stop the hotspot keepalive worker with the Awake toggle."""
        running = (
            self._keepalive_thread is not None
            and self._keepalive_thread.is_alive()
        )
        if enabled and not running:
            stop = threading.Event()
            thread = threading.Thread(
                target=network_keepalive_loop,
                args=(stop,),
                name="awake-network-keepalive",
                daemon=True,
            )
            self._keepalive_stop = stop
            self._keepalive_thread = thread
            thread.start()
        elif not enabled and running:
            assert self._keepalive_stop is not None
            self._keepalive_stop.set()
            self._keepalive_stop = None
            self._keepalive_thread = None

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


_lock_fd: int | None = None  # kept open for the process lifetime


def ensure_single_instance() -> None:
    """Exit silently if another Awake instance already holds the lock."""
    global _lock_fd
    fd = os.open(f"/tmp/awake-{os.getuid()}.lock", os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        sys.exit(0)
    _lock_fd = fd


def main() -> None:
    ensure_single_instance()
    AwakeApp().run()


if __name__ == "__main__":
    main()
