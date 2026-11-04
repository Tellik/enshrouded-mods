#!/usr/bin/env python3
"""Install one ShroudForge mod ZIP while preserving its existing configuration.

The game or dedicated server must be stopped before this tool is run.
"""

import argparse
import csv
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile


MAX_FILES = 2000
MAX_UNCOMPRESSED_BYTES = 512 * 1024 * 1024


def require_stopped(game: Path) -> None:
    names = [name for name in ("enshrouded.exe", "enshrouded_server.exe")
             if (game / name).is_file()]
    if sys.platform.startswith("linux"):
        proc = Path("/proc")
        if not proc.is_dir():
            raise ValueError("cannot check whether Enshrouded is stopped")
        running = set()
        for process in proc.iterdir():
            if not process.name.isdigit():
                continue
            try:
                name = (process / "comm").read_text().strip().casefold()
            except (OSError, UnicodeError):
                continue
            for target in names:
                if name == target[:15].casefold():
                    running.add(target)
        if running:
            raise ValueError(f"game process is still running: {', '.join(sorted(running))}")
    elif os.name == "nt":
        result = subprocess.run(["tasklist", "/FO", "CSV", "/NH"],
                                capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise ValueError("cannot check whether Enshrouded is stopped")
        running = {row[0].casefold() for row in csv.reader(result.stdout.splitlines()) if row}
        if running.intersection(names):
            raise ValueError("game or server process is still running")
    else:
        raise ValueError("this platform cannot verify that Enshrouded is stopped")


def package_files(archive: zipfile.ZipFile):
    files = {}
    seen = set()
    total_bytes = 0
    for info in archive.infolist():
        name = info.filename
        if not name or name.startswith("/") or "\\" in name:
            raise ValueError(f"unsafe ZIP path: {name!r}")
        parts = name.rstrip("/").split("/")
        if any(part in ("", ".", "..") or ":" in part for part in parts):
            raise ValueError(f"unsafe ZIP path: {name!r}")
        if (info.external_attr >> 16) & 0o170000 == 0o120000:
            raise ValueError(f"ZIP contains a symbolic link: {name}")
        if info.is_dir():
            continue
        folded = name.casefold()
        if folded in seen:
            raise ValueError(f"ZIP contains duplicate path: {name}")
        seen.add(folded)
        files[name] = info
        total_bytes += info.file_size
        if len(files) > MAX_FILES or total_bytes > MAX_UNCOMPRESSED_BYTES:
            raise ValueError("ZIP exceeds the installer size limit")
    roots = {PurePosixPath(name).parts[0] for name in files}
    if len(roots) != 1:
        raise ValueError("ZIP must contain exactly one mod folder")
    folder = roots.pop()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", folder):
        raise ValueError("ZIP has an invalid mod folder name")
    manifest_path = f"{folder}/mod.json"
    if manifest_path not in files:
        raise ValueError("ZIP has no mod.json inside its mod folder")
    manifest = json.loads(archive.read(manifest_path))
    if manifest.get("id") != folder:
        raise ValueError("mod.json ID does not match the ZIP folder")
    extension_path = f"{folder}/extended.mod.json"
    if extension_path in files:
        extension = json.loads(archive.read(extension_path))
        if not isinstance(extension, dict):
            raise ValueError("extended.mod.json must be a JSON object")
    return folder, files


def install(archive_path: Path, game: Path, dry_run: bool) -> None:
    game = game.resolve()
    if not game.is_dir() or not any(
        (game / executable).is_file()
        for executable in ("enshrouded.exe", "enshrouded_server.exe")
    ):
        raise ValueError("game folder must contain enshrouded.exe or enshrouded_server.exe")
    with zipfile.ZipFile(archive_path) as archive:
        if archive.comment.startswith(b"enshrouded-mods:delta-upgrade:"):
            raise ValueError("delta upgrade ZIP: overlay it onto the existing mod folder as its guide describes; use the full initial ZIP with this installer")
        folder, files = package_files(archive)
        if archive.testzip() is not None:
            raise ValueError("ZIP failed its integrity check")
        mods = game / "mods"
        destination = mods / folder
        if destination.is_symlink():
            raise ValueError("installed mod folder is a symbolic link")
        existing = destination.is_dir()
        config = destination / "extended.mod.json"
        if existing:
            manifest_path = destination / "mod.json"
            if manifest_path.is_symlink() or config.is_symlink():
                raise ValueError("installed mod contains a symbolic-link manifest or configuration")
            if config.exists() and not config.is_file():
                raise ValueError("installed configuration is not a regular file")
            installed_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if installed_manifest.get("id") != folder:
                raise ValueError("installed mod ID does not match the update")
        elif destination.exists():
            raise ValueError("mod destination exists but is not a directory")
        keep_config = existing and config.is_file()
        action = "Update" if existing else "Install"
        print(f"{action} {folder} into {destination}")
        print("Preserve existing extended.mod.json" if keep_config else "Use packaged default configuration")
        if dry_run:
            print("Dry run: no files changed")
            return

        require_stopped(game)
        mods.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".mod-stage-", dir=mods) as temporary:
            staged = Path(temporary) / folder
            staged.mkdir()
            prefix = f"{folder}/"
            for name, info in files.items():
                relative = name.removeprefix(prefix)
                target = staged.joinpath(*PurePosixPath(relative).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
            if keep_config:
                shutil.copyfile(config, staged / "extended.mod.json")

            backup = None
            if existing:
                backup_parent = game / "shroudforge" / "backups" / "manual-mod-installs" / folder
                backup_parent.mkdir(parents=True, exist_ok=True)
                backup = backup_parent / str(time.time_ns())
                os.replace(destination, backup)
            try:
                os.replace(staged, destination)
            except OSError:
                if backup is not None:
                    os.replace(backup, destination)
                raise
        if backup is not None:
            print(f"Previous version saved at {backup}")
        print("Installed. Start the game or server when ready.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", type=Path, help="one mod release ZIP")
    parser.add_argument("game_folder", type=Path, help="folder containing the game or server EXE")
    parser.add_argument("--dry-run", action="store_true", help="check the ZIP and destination only")
    args = parser.parse_args()
    try:
        install(args.zip, args.game_folder, args.dry_run)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, json.JSONDecodeError) as error:
        sys.exit(f"Install stopped: {error}")


if __name__ == "__main__":
    main()
