#!/usr/bin/env python3
"""Package the standalone Free Airborne Architect mod for a release."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "mods" / "airborne-architect-free"
FILES = ("LICENSE", "README.md", "extended.mod.json", "mod.json", "src/mod.lua")
PREFIX = "airborne-architect-free/"


def verify(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        expected = {PREFIX + name for name in FILES}
        if set(archive.namelist()) != expected or len(archive.namelist()) != len(expected):
            raise ValueError("unexpected files or folder layout in mod ZIP")
        if archive.testzip() is not None:
            raise ValueError("corrupt mod ZIP")
        manifest = json.loads(archive.read(PREFIX + "mod.json"))
        settings = json.loads(archive.read(PREFIX + "extended.mod.json"))
        if manifest.get("id") != "airborne-architect-free" or manifest.get("version") != "0.2.1":
            raise ValueError("unexpected mod ID or version")
        if settings.get("enabled") is not True or settings.get("targets") != ["client", "server"]:
            raise ValueError("mod must default to enabled for client and server")
    print(f"Verified {path.name}: one mod folder, enabled by default")


def package(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in FILES:
            entry = zipfile.ZipInfo(PREFIX + name, (2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, (MOD / name).read_bytes(), compress_type=zipfile.ZIP_DEFLATED,
                             compresslevel=9)
    verify(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_name(path.name + ".sha256").write_text(f"{digest}  {path.name}\n")
    print(f"{path} sha256={digest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    try:
        if arguments.verify:
            verify(arguments.verify)
        elif arguments.out:
            package(arguments.out)
        else:
            parser.error("use --out ZIP or --verify ZIP")
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        sys.exit(str(error))
