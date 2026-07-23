# Awake

A tiny macOS menu bar app that stops your Mac from sleeping when you **close the lid** and keeps phone hotspots from dropping an idle connection.

```
☕  ← in your menu bar
────────────────────────
Keep awake            ✓
   Status: On (won't sleep on lid close)
────────────────────────
Quit
```

- ☕ — **on**: lid close won't sleep the machine; hotspot keepalive is active
- 💤 — **off**: normal sleep behavior
- ❓ — current state couldn't be read

## How it works

macOS sleeps on lid close regardless of `caffeinate` or your Energy settings. The only switch that overrides it is pmset's `disablesleep` flag:

```sh
sudo pmset -a disablesleep 1   # stay awake with the lid closed
sudo pmset -a disablesleep 0   # back to normal
```

Awake uses that flag for lid-close sleep. While enabled, it also sends one tiny
DNS packet every 20 seconds so an iPhone or other phone hotspot continues to
see the Mac as an active client. It does not reconnect to a different network
or consume meaningful data.

## Install

```sh
git clone https://github.com/Koomook/awake.git
cd awake
./install.sh
```

`install.sh` builds a **self-contained** `Awake.app` with [py2app](https://py2app.readthedocs.io/) — it embeds its own Python interpreter and `rumps`, so at runtime it needs neither `uv` nor a network connection. The bundle is ad-hoc code-signed and installed to `~/Applications`, so you can:

- **Launch from Spotlight** — press `Cmd-Space`, type **Awake**, hit Return.
- It also **starts automatically at login** and shows in the menu bar (☕/💤).

It's a menu-bar-only agent (`LSUIElement`), so there's no Dock icon.

> **First launch:** the app is ad-hoc signed, not notarized by Apple, so the *first* time you open it from Finder macOS may say it's from an "unidentified developer." Right-click the app → **Open** once to approve it (Spotlight/login launches work normally after that).

Uninstall anytime:

```sh
./uninstall.sh
```

### Requirements

- macOS (Apple Silicon or Intel)
- [uv](https://docs.astral.sh/uv/) — **build-time only**, to provide a py2app-compatible Python. Not needed once the app is installed.

### Run without building

To try it straight from source without building the bundle:

```sh
uv run app.py
```

## Toggling & permissions

`pmset` needs root, so each toggle shows a Touch ID / password prompt. To make toggling instant and prompt-free, allow *only* these two exact commands without a password:

```sh
echo "$(whoami) ALL=(root) NOPASSWD: /usr/bin/pmset -a disablesleep 0, /usr/bin/pmset -a disablesleep 1" \
  | sudo tee /etc/sudoers.d/awake >/dev/null && sudo chmod 440 /etc/sudoers.d/awake
```

The app automatically prefers this passwordless path and falls back to the GUI prompt when it isn't set up. Remove it anytime with `sudo rm /etc/sudoers.d/awake`.

## Notes

- Keeping the lid closed while awake generates heat and drains the battery — keep it plugged in, keep it ventilated, and never put it in a bag while enabled.
- This controls only the lid-close (clamshell) sleep flag. Other sleep prevention (e.g. a running `caffeinate`) is independent and not reflected in the icon.

## License

MIT — see [LICENSE](LICENSE).
