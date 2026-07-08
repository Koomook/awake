"""py2app build script for Awake — produces a fully self-contained
menu-bar .app bundle (embedded Python interpreter + rumps + deps).

Build with a py2app-compatible pinned Python via uv, e.g.:

    cd /Users/bong/awake
    uv run --python 3.12 --with py2app --with rumps python setup.py py2app

Output: dist/Awake.app
"""

import os

from setuptools import setup

# --- Workaround: py2app unconditionally does `self.copy_file(zlib.__file__, ...)`
# assuming zlib is always a separate extension module. uv's managed Pythons
# (python-build-standalone) statically link zlib into the interpreter itself,
# so it has no __file__ and nothing needs to be copied (it's already embedded
# in the executable). Give it a harmless dummy __file__ pointing at an empty
# stub so py2app's copy_file call succeeds instead of raising AttributeError.
import zlib  # noqa: E402

if not hasattr(zlib, "__file__"):
    _stub = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "_zlib_stub.txt")
    os.makedirs(os.path.dirname(_stub), exist_ok=True)
    if not os.path.exists(_stub):
        open(_stub, "w").close()
    zlib.__file__ = _stub

APP_NAME = "Awake"
BUNDLE_ID = "com.koomook.awake"
VERSION = "0.2.0"

APP = ["app.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "iconfile": "assets/AppIcon.icns",
    "packages": ["rumps"],
    "includes": ["rumps", "objc", "Foundation", "AppKit"],
    "plist": {
        "CFBundleName": APP_NAME,
        "CFBundleDisplayName": APP_NAME,
        "CFBundleIdentifier": BUNDLE_ID,
        "CFBundleShortVersionString": VERSION,
        "CFBundleVersion": VERSION,
        "LSUIElement": True,
        "NSHumanReadableCopyright": "",
    },
}

setup(
    app=APP,
    name=APP_NAME,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
