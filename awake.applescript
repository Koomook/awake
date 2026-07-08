-- Spotlight-launchable stub for Awake.
-- Starts the menu bar app detached, then quits immediately. Uses $HOME so it
-- is portable across accounts; the app itself enforces a single instance.
do shell script "export PATH=\"$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH\"; nohup uv run \"$HOME/Library/Application Support/Awake/app.py\" > /dev/null 2>&1 &"
