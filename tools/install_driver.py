#!/usr/bin/env python3
"""Install driver to SteamVR."""

import argparse
import shutil
import subprocess
from pathlib import Path


def find_steamvr() -> Path | None:
    paths = [
        Path("~/.steam/steam/steamapps/common/SteamVR").expanduser(),
        Path("~/Steam/steamapps/common/SteamVR").expanduser(),
    ]
    for p in paths:
        if p.exists():
            return p
    return None


def install(driver_path: Path, steamvr_path: Path) -> bool:
    dest = steamvr_path / "drivers" / "budget_vr_tracker"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(driver_path, dest)
    
    vrpathreg = steamvr_path / "bin" / "vrpathreg.sh"
    if vrpathreg.exists():
        subprocess.run([str(vrpathreg), "adddriver", str(dest)], check=True)
    return True


def main():
    parser = argparse.ArgumentParser(description="Install Budget VR Tracker driver")
    parser.add_argument("--driver-path", type=Path, default=Path("driver/build"))
    args = parser.parse_args()
    
    steamvr = find_steamvr()
    if not steamvr:
        print("SteamVR not found!")
        return 1
    
    if install(args.driver_path, steamvr):
        print("✓ Driver installed successfully!")
        print(f"  Location: {steamvr}/drivers/budget_vr_tracker")
    return 0


if __name__ == "__main__":
    exit(main())
