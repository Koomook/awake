# Keep Awake

A tiny macOS menu bar app that stops your Mac from sleeping when you **close the lid** — one click to toggle, nothing else.

```
●  ← in your menu bar
────────────────────────
Keep Awake            ✓
   Status: On (won't sleep on lid close)
────────────────────────
Quit
```

- `●` — **on**: lid close won't sleep the machine
- `○` — **off**: normal sleep behavior
- `◐` — current state couldn't be read

## How it works

macOS sleeps on lid close regardless of `caffeinate` or your Energy settings. The only switch that overrides it is pmset's `disablesleep` flag:

```sh
sudo pmset -a disablesleep 1   # stay awake with the lid closed
sudo pmset -a disablesleep 0   # back to normal
```

Keep Awake is just a menu bar switch for that flag. It reads the current state with `pmset -g` and flips it with `pmset -a disablesleep 0|1`.

## Requirements

- macOS (Apple Silicon or Intel)
- [uv](https://docs.astral.sh/uv/) — used to run the single-file script with its `rumps` dependency; no manual `pip install` needed.

## Quick start

```sh
git clone https://github.com/Koomook/keep-awake.git
cd keep-awake
uv run app.py
```

An icon appears in your menu bar. Click it → **Keep Awake** to toggle.

Because `pmset` needs root, each toggle shows a Touch ID / password prompt. To make toggling instant and prompt-free, see [Passwordless toggling](#passwordless-toggling-optional).

## Run at login (menu bar app)

Install a per-user LaunchAgent so it starts automatically and stays running:

```sh
./install.sh      # generates the LaunchAgent, starts it now
./uninstall.sh    # stops it and removes the LaunchAgent
```

The plist is generated at install time from your actual clone path and `uv` location, so nothing machine-specific is committed to the repo.

> **Quit note:** the LaunchAgent runs with `KeepAlive=true`, so clicking **Quit** relaunches it a moment later. To turn it off for good, run `./uninstall.sh`.

## Passwordless toggling (optional)

Allow *only* these two exact commands to run without a password, so the menu bar toggle never prompts:

```sh
echo "$(whoami) ALL=(root) NOPASSWD: /usr/bin/pmset -a disablesleep 0, /usr/bin/pmset -a disablesleep 1" \
  | sudo tee /etc/sudoers.d/keepawake >/dev/null && sudo chmod 440 /etc/sudoers.d/keepawake
```

The app automatically prefers this passwordless path and falls back to the GUI prompt when it isn't set up. Remove it anytime with `sudo rm /etc/sudoers.d/keepawake`.

## Notes

- Keeping the lid closed while awake generates heat and drains the battery — keep it plugged in.
- This controls only the lid-close (clamshell) sleep flag. Other sleep prevention (e.g. a running `caffeinate`) is independent and not reflected in the icon.

## License

MIT — see [LICENSE](LICENSE).
