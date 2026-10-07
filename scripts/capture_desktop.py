"""Save a full-desktop PNG for system-test evidence."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import ImageGrab


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/capture_desktop.py <output.png>")
    path = Path(sys.argv[1])
    path.parent.mkdir(parents=True, exist_ok=True)
    image = ImageGrab.grab()
    image.save(path)
    print(f"Saved {path} ({image.size[0]}x{image.size[1]})")


if __name__ == "__main__":
    main()
