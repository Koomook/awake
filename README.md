# Awake

A tiny macOS menu bar app that stops your Mac from sleeping when you **close the lid** — one click to toggle, nothing else.

```
☕  ← in your menu bar
────────────────────────
Keep awake            ✓
   Status: On (won't sleep on lid close)
────────────────────────
Quit
```

- ☕ — **on**: lid close won't sleep the machine
- 💤 — **off**: normal sleep behavior
- ❓ — current state couldn't be read

## How it works

macOS sleeps on lid close regardless of `caffeinate` or your Energy settings. The only switch that overrides it is pmset's `disablesleep` flag:

```sh
sudo pmset -a disablesleep 1   # stay awake with the lid closed
sudo pmset -a disablesleep 0   # back to normal
```

Awake is just a menu bar switch for that flag. It reads the current state with `pmset -g` and flips it with `pmset -a disablesleep 0|1`.

## Requirements

- macOS (Apple Silicon or Intel)
- [uv](https://docs.astral.sh/uv/) — runs the single-file script with its `rumps` dependency; no manual `pip install` needed.

## Install

```sh
git clone https://github.com/Koomook/awake.git
cd awake
./install.sh
```

This builds `~/Applications/Awake.app`, so you can:

- **Launch from Spotlight** — press `Cmd-Space`, type **Awake**, hit Return.
- It also **starts automatically at login** and appears in the menu bar (☕/💤).

Uninstall anytime:

```sh
./uninstall.sh
```

The app is a menu-bar-only agent (`LSUIElement`), so it has no Dock icon — just the ☕/💤 in the menu bar.

### Run without installing

To try it without creating the app bundle:

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

- Keeping the lid closed while awake generates heat and drains the battery — keep it plugged in.
- This controls only the lid-close (clamshell) sleep flag. Other sleep prevention (e.g. a running `caffeinate`) is independent and not reflected in the icon.

## License

MIT — see [LICENSE](LICENSE).
