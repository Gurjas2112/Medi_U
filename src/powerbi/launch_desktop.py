"""Launch Power BI Desktop against the hospital dashboard on this Windows PC."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from src.config import POWER_BI_EXE_CANDIDATES, POWER_BI_START_MENU, POWERBI_FILE


def find_power_bi_desktop() -> Path | None:
    for candidate in POWER_BI_EXE_CANDIDATES:
        if candidate.exists():
            return candidate
    if POWER_BI_START_MENU.exists():
        exe_hits = list(POWER_BI_START_MENU.rglob("*.exe"))
        if exe_hits:
            return exe_hits[0]
        lnk_hits = list(POWER_BI_START_MENU.rglob("*.lnk"))
        if lnk_hits:
            return lnk_hits[0]
    return None


def launch_power_bi(pbix_path: Path | None = None) -> None:
    pbix = pbix_path or POWERBI_FILE
    if not pbix.exists():
        raise FileNotFoundError(f"Power BI file not found: {pbix}")

    desktop = find_power_bi_desktop()
    if desktop is not None and desktop.suffix.lower() == ".exe":
        subprocess.Popen([str(desktop), str(pbix)], shell=False)
        print(f"Launched Power BI Desktop: {desktop}")
        print(f"Opened: {pbix}")
        return

    if os.name == "nt":
        target = str(desktop) if desktop is not None else str(pbix)
        os.startfile(target)  # noqa: S606 - local Windows file association
        print(f"Opened with Windows file association: {target}")
        if desktop is not None:
            print(f"Dashboard file: {pbix}")
        return

    raise RuntimeError("Power BI Desktop launching is only automated on Windows.")


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    launch_power_bi(path)
