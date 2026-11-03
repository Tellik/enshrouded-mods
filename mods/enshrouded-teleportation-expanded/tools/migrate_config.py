#!/usr/bin/env python3
"""Migrate a 0.1.x/0.2.x configuration to the 0.3 category settings."""

import argparse
import json
from pathlib import Path

OLD_GROUPS = {
    "Flame Shrines": "flameShrines", "Flame Sanctums": "flameSanctums",
    "Gem Forges": "gemForges", "Night Sanctums": "nightSanctums",
    "Dungeons": "dungeons", "Large Dungeons": "hollowHalls",
    "Obelisks": "obelisks", "Tombs": "tombs",
    "Balefire Sites": "balefireSites", "Mines": "mines", "Caves": "caves",
    "Enemy Camps": "enemyCamps", "Villages": "villagesTowns",
    "Survivor Camps": "survivorCamps", "Farms": "farms",
}


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
    settings = packaged["settings"]
    for key in settings:
        previous = boolean(old, key)
        if previous is not None:
            settings[key]["value"] = previous

    if any(key.startswith("poi_") for key in old.get("settings", {})):
        # Replace old per-location defaults with the new category defaults.
        # A mixed custom group cannot be represented by one switch.
        for group in old.get("groups", []):
            label = group.get("label")
            category = OLD_GROUPS.get(label)
            if not category:
                continue
            values = [boolean(old, key) for key in group["settings"]]
            expected = label in ("Flame Shrines", "Flame Sanctums")
            if len(set(values)) > 1:
                if any(value != expected for value in values):
                    raise ValueError(f"{label} has mixed custom location values; choose a category value manually")
            elif values and values[0] != expected:
                settings[category]["value"] = values[0]
        vault_group = next((group for group in old.get("groups", [])
                            if group.get("label") == "Challenge Chambers and Vaults"), None)
        if vault_group:
            vault_keys = [key for key in vault_group["settings"]
                          if old["settings"][key]["label"].startswith("Ancient Vault —")]
            vault_values = [boolean(old, key) for key in vault_keys]
            if len(set(vault_values)) > 1:
                raise ValueError("Ancient Vaults has mixed custom location values; choose a category value manually")
            if vault_values and vault_values[0]:
                settings["ancientVaults"]["value"] = True
    else:
        old_flame = boolean(old, "flameShrinesAndSanctums")
        if old_flame is not None:
            settings["flameShrines"]["value"] = old_flame
            settings["flameSanctums"]["value"] = old_flame
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
