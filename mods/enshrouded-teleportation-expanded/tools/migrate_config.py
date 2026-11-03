#!/usr/bin/env python3
"""Carry user toggle values from an installed 0.1.x or 0.2.x config into 0.2.0."""

import argparse
import json
from pathlib import Path


def boolean(config, key):
    item = config.get("settings", {}).get(key)
    if item is None:
        return None
    value = item.get("value")
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def migrate(old, packaged):
    if not isinstance(old.get("enabled", True), bool):
        raise ValueError("enabled must be a boolean")
    packaged["enabled"] = old.get("enabled", True)
    locations = packaged["settings"]
    groups = {group["label"]: group["settings"] for group in packaged["groups"]}
    for key in locations:
        previous = boolean(old, key)
        if previous is not None:
            locations[key]["value"] = previous
    old_flame = boolean(old, "flameShrinesAndSanctums")
    if old_flame is not None:
        for category in ("Flame Shrines", "Flame Sanctums"):
            for key in groups[category]:
                if key not in old.get("settings", {}):
                    locations[key]["value"] = old_flame
    old_forges = boolean(old, "gemForges")
    if old_forges is not None:
        for key in groups["Gem Forges"]:
            if key not in old.get("settings", {}):
                locations[key]["value"] = old_forges
    return packaged


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("existing", type=Path)
    parser.add_argument("packaged", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    old = json.loads(args.existing.read_text(encoding="utf-8"))
    packaged = json.loads(args.packaged.read_text(encoding="utf-8"))
    merged = migrate(old, packaged)
    args.output.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Migrated {len(merged['settings'])} settings; mod enabled={merged['enabled']}")


if __name__ == "__main__":
    main()
