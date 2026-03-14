#!/usr/bin/env python3
"""
install.py — Install the Frankie language.

Installs the frankiec command into frankie/bin/ (alongside this script),
so the whole frankie/ folder stays self-contained.

Usage:
    python3 install.py            Install to frankie/bin/
    python3 install.py --uninstall

After installing, add frankie/bin to your PATH:
    export PATH="/path/to/frankie/bin:$PATH"

Or run directly without installing:
    python3 frankiec.py run examples/hello.fk
"""

import sys
import os
import stat

FRANKIE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR     = os.path.join(FRANKIE_DIR, "bin")
SCRIPT_NAME = "frankiec"


def install():
    os.makedirs(BIN_DIR, exist_ok=True)
    target = os.path.join(BIN_DIR, SCRIPT_NAME)

    launcher = f"""#!/usr/bin/env python3
import sys, os
sys.path.insert(0, {FRANKIE_DIR!r})
from frankiec import main
main()
"""
    with open(target, 'w') as f:
        f.write(launcher)

    # Make executable
    st = os.stat(target)
    os.chmod(target, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    print(f"Installed: {target}")
    print()

    # Check if bin/ is already on PATH
    path_dirs = os.environ.get('PATH', '').split(':')
    if BIN_DIR in path_dirs:
        print("  frankiec is ready -- bin/ is already on your PATH.")
    else:
        print("  To use frankiec from anywhere, add this to your ~/.bashrc or ~/.zshrc:")
        print(f'    export PATH="{BIN_DIR}:$PATH"')
        print()
        print("  Or run directly from the frankie directory:")
        print(f"    ./bin/frankiec run examples/hello.fk")


def uninstall():
    target = os.path.join(BIN_DIR, SCRIPT_NAME)
    if os.path.exists(target):
        os.remove(target)
        print(f"Removed: {target}")
        if not os.listdir(BIN_DIR):
            os.rmdir(BIN_DIR)
            print(f"Removed empty dir: {BIN_DIR}")
    else:
        print(f"frankiec not found at {target}")


if __name__ == '__main__':
    if '--uninstall' in sys.argv:
        uninstall()
    else:
        install()
