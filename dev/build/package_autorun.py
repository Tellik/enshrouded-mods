#!/usr/bin/env python3
"""Build the full Autorun ZIP and a delta from the published 0.3.2 ZIP."""

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "standalone" / "autorun"
BASELINE = Path(__file__).with_name("autorun-0.3.2-baseline.json")
UPGRADE_COMMENT = b"enshrouded-mods:delta-upgrade:autorun:0.3.2:0.4.0"
FILES = (
    "mod.json",
    "extended.mod.json",
    "native-plugin.ini",
    "README.md",
    "LICENSE.nlohmann",
)


def check_dll(data: bytes) -> None:
    if data[:2] != b"MZ" or len(data) < 0x100:
        raise ValueError("the native plugin is not a PE DLL")
    offset = struct.unpack_from("<I", data, 0x3C)[0]
    if offset + 6 > len(data):
        raise ValueError("the native plugin has an invalid PE header offset")
    if data[offset : offset + 4] != b"PE\0\0":
        raise ValueError("the native plugin has no PE header")
    if struct.unpack_from("<H", data, offset + 4)[0] != 0x8664:
        raise ValueError("the native plugin is not Windows x64")


def comparable_sha256(name: str, content: bytes) -> str:
    # Windows checkout converts text files to CRLF. Compare their contents,
    # not their platform-specific line endings, with the published 0.3.2 ZIP.
    if not name.endswith(".dll"):
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def expected_members(dll: bytes) -> dict[str, bytes]:
    manifest = json.loads((PACKAGE / "mod.json").read_text())
    extension = json.loads((PACKAGE / "extended.mod.json").read_text())
    if manifest["id"] != "autorun" or manifest["version"] != "0.4.0":
        raise ValueError("unexpected mod identity or version")
    if extension["targets"] != ["client"] or extension["enabled"] is not True:
        raise ValueError("the full package must be an enabled client mod")
    if b"Dll=bin/autorun.dll" not in (PACKAGE / "native-plugin.ini").read_bytes():
        raise ValueError("native-plugin.ini does not reference the packaged DLL")
    check_dll(dll)
    members = {f"autorun/{name}": (PACKAGE / name).read_bytes() for name in FILES}
    members["autorun/bin/autorun.dll"] = dll
    members["autorun/LICENSE"] = (ROOT / "LICENSE").read_bytes()
    return members


def changed_members(full: dict[str, bytes]) -> dict[str, bytes]:
    baseline = json.loads(BASELINE.read_text())
    if baseline["baseVersion"] != "0.3.2":
        raise ValueError("unexpected upgrade baseline")
    old = baseline["membersSha256"]
    if set(old) != set(full):
        raise ValueError("full package added or removed a file; review the upgrade strategy")
    changed = {name: content for name, content in full.items()
               if comparable_sha256(name, content) != old[name]}
    if "autorun/extended.mod.json" in changed:
        raise ValueError("default configuration changed; review migration before omitting it")
    if not {"autorun/mod.json", "autorun/bin/autorun.dll"} <= set(changed):
        raise ValueError("upgrade must update the manifest and plugin")
    return changed


def write_zip(output: Path, members: dict[str, bytes], comment: bytes = b"") -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.comment = comment
        for name, content in sorted(members.items()):
            entry = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    verify(output, members)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_name(output.name + ".sha256").write_text(f"{digest}  {output.name}\n")
    print(f"{output} sha256={digest}")


def verify(path: Path, expected: dict[str, bytes] | None = None) -> None:
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP contains a corrupt member")
        names = archive.namelist()
        if len(names) != len(set(names)) or any(not name.startswith("autorun/") for name in names):
            raise ValueError("ZIP has duplicate or misplaced files")
        if "autorun/mod.json" not in names or "autorun/bin/autorun.dll" not in names:
            raise ValueError("ZIP has no manifest or native plugin")
        manifest = json.loads(archive.read("autorun/mod.json"))
        if (manifest.get("id"), manifest.get("version")) != ("autorun", "0.4.0"):
            raise ValueError("ZIP has an unexpected mod version")
        dll = archive.read("autorun/bin/autorun.dll")
        check_dll(dll)
        full = expected_members(dll)
        if "autorun/extended.mod.json" in names:
            selected = full
            if archive.comment:
                raise ValueError("initial-install ZIP must not have an upgrade marker")
        else:
            selected = changed_members(full)
            if archive.comment != UPGRADE_COMMENT:
                raise ValueError("upgrade ZIP lacks its version-specific marker")
        if expected is not None and expected != selected:
            raise ValueError("the selected package contents do not match its intended layout")
        if set(names) != set(selected):
            raise ValueError(f"unexpected ZIP layout: {sorted(set(names) ^ set(selected))}")
        for name, content in selected.items():
            if archive.read(name) != content:
                raise ValueError(f"packaged file differs from source: {name}")
    print(f"Verified Autorun ZIP: {path}")


def package(dll_path: Path, out_dir: Path) -> None:
    full = expected_members(dll_path.read_bytes())
    upgrade = changed_members(full)
    write_zip(out_dir / "autorun-0.4.0-initial.zip", full)
    write_zip(out_dir / "autorun-0.4.0-upgrade-from-0.3.2.zip", upgrade, UPGRADE_COMMENT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dll", type=Path)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    try:
        if args.verify:
            verify(args.verify)
        elif args.dll and args.out_dir:
            package(args.dll, args.out_dir)
        else:
            parser.error("use --verify ZIP or --dll DLL --out-dir DIRECTORY")
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        sys.exit(str(error))
