#!/usr/bin/env python3
"""Generate the build-specific POI catalog and category-switch configuration.

Inputs are JSON exports of TemplateResource, scene map-label placements,
MapMarkerRegistryResource, English localization, and marker icon resources.
The outputs are reviewed and committed; this is not run at game startup.
"""

import argparse
import collections
import json
import pathlib
import re
import uuid
from shroud_volume import ShroudVolume

NAMESPACE = uuid.UUID("5b89fd28-2b08-44a7-9b2d-d298c9f263c4")
MOD = pathlib.Path(__file__).resolve().parents[1]
CATEGORY_SPECS = [
    ("flameShrines", "Flame Shrines", "Flame Sites", True, 48),
    ("flameSanctums", "Flame Sanctums", "Flame Sites", True, 15),
    ("gemForges", "Gem Forges", "Shroud Sites", False, 21),
    ("nightSanctums", "Night Sanctums", "Shroud Sites", False, 30),
    ("dungeons", "Dungeons", "Ruins", True, 37),
    ("hollowHalls", "Hollow Halls", "Ruins", True, 6),
    ("ancientVaults", "Ancient Vaults", "Ruins", True, 5),
    ("obelisks", "Obelisks", "Ruins", True, 14),
    ("tombs", "Tombs", "Ruins", True, 4),
    ("balefireSites", "Balefire Sites", "Ruins", True, 9),
    ("mines", "Mines", "Exploration", True, 21),
    ("caves", "Caves", "Exploration", True, 55),
    ("enemyCamps", "Enemy Camps", "Settlements", True, 92),
    ("villagesTowns", "Villages/Towns", "Settlements", True, 67),
    ("survivorCamps", "Survivor Camps", "Settlements", True, 44),
    ("farms", "Farms", "Settlements", True, 37),
]
ICON_CATEGORIES = {
    "mapmarker_shroudforge": "gemForges",
    "mapmarker_nighttemple": "nightSanctums",
    "mapmarker_dungeon": "dungeons",
    "mapmarker_bigDungeon": "hollowHalls",
    "mapmarker_obelisk": "obelisks",
    "mapmarker_tomb": "tombs",
    "mapmarker_balefire": "balefireSites",
    "mapmarker_mine": "mines",
    "mapmarker_cave": "caves",
    "mapmarker_special_enemy_camp": "enemyCamps",
    "mapmarker_village": "villagesTowns",
    "mapmarker_survivorcamp": "survivorCamps",
    "mapmarker_farm": "farms",
}
ORDER = [spec[0] for spec in CATEGORY_SPECS]
REGIONS = {
    "grassland": "Springlands", "deepforest": "Revelwood",
    "steppes": "Nomad Highlands", "coldheights": "Albaneve Summits",
    "desert": "Kindlewastes", "wetland": "Blackmire",
    "ancientlands": "Ancient Lands",
}


def fnv_guid(guid):
    result = 2166136261
    for byte in uuid.UUID(guid).bytes_le:
        result = ((result ^ byte) * 16777619) & 0xFFFFFFFF
    return result


def lua(value):
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def component(template, type_id):
    return next((c["$value"] for c in template["components"] if c["$type"] == type_id), None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("pois", "placements", "registry", "loca", "icons"):
        parser.add_argument("--" + name, required=True, type=pathlib.Path)
    parser.add_argument("--fog-model", required=True, type=pathlib.Path)
    parser.add_argument("--fog-content-dir", required=True, type=pathlib.Path)
    parser.add_argument("--build", required=True, type=int)
    args = parser.parse_args()

    templates = {p["id"]: p["value"] for p in json.loads(args.pois.read_text())}
    placements = json.loads(args.placements.read_text())
    registry = json.loads(args.registry.read_text())[0]["value"]["mapMarkers"]["values"]
    names = {tag["id"]["value"]: tag["text"] for tag in json.loads(args.loca.read_text())["tags"]}
    icons = {icon["id"]: icon["value"].get("debugName") for icon in json.loads(args.icons.read_text())}
    shroud = ShroudVolume(args.fog_model, args.fog_content_dir)
    marker_by_id = {marker["markerId"]["value"]: marker for marker in registry}
    marker_icons = {mid: icons.get(marker["icon"]["image"]) for mid, marker in marker_by_id.items()}
    locations = []
    marker_types = {}
    seen_keys = set()
    seen_clones = set()
    used_marker_ids = set(marker_by_id)

    for placement in placements:
        template = templates[placement["template"]]
        marker = component(template, 3184)  # keen::ecs::MapMarker on build 26404966
        if not marker or not marker.get("markerType"):
            continue
        source_type = marker["markerType"]
        icon = marker_icons.get(fnv_guid(source_type))
        loca = component(template, 3179)  # keen::ecs::MapMarkerLocaTag
        name = names.get(fnv_guid(loca["locaTag"])) if loca and loca.get("locaTag") else None
        if icon == "mapmarker_flame_essence":
            category = "flameSanctums" if "FlameTemple" in template["name"] else "flameShrines"
        elif icon == "mapmarker_challenge_chamber" and name and name.startswith("Ancient Vault —"):
            category = "ancientVaults"
        else:
            category = ICON_CATEGORIES.get(icon)
        if not category:
            continue  # Excluded Shroud POIs, stock travel, quest hints, and other challenge chambers.
        source_marker_id = fnv_guid(source_type)
        assert source_marker_id in marker_by_id
        assert not marker_by_id[source_marker_id]["isFastTravelDestination"]
        transform = placement["transform"]
        x, y, z = (transform["position" + axis + "1"] for axis in "XYZ")
        key = f"poi_{x:05d}_{z:05d}"
        if key in seen_keys:
            key += f"_{placement['entityIndex']}"
        assert key not in seen_keys, key
        seen_keys.add(key)
        clone = str(uuid.uuid5(NAMESPACE, f"template:{placement['template']}:{placement['entityIndex']}:{x}:{z}"))
        assert clone not in seen_clones and clone not in templates
        seen_clones.add(clone)
        if not name or name.startswith("Placeholder"):
            name = re.sub(r"^8[kK]MapLabel_|^MapLabel_", "", template["name"]).replace("_", " ")
        region = next((label for token, label in REGIONS.items() if token in template["name"].lower()), None)
        label = f"{name} — {region} ({x}, {z})" if region else f"{name} ({x}, {z})"
        locations.append(dict(key=key, category=category, label=label, template=placement["template"],
                              markerType=source_type, clone=clone, entity=placement["entityIndex"],
                              x=x, y=y, z=z, inShroud=shroud.near_shroud(x, y, z)))
        if source_type not in marker_types:
            travel_type = str(uuid.uuid5(NAMESPACE, "marker:" + source_type))
            travel_id = fnv_guid(travel_type)
            assert travel_id not in used_marker_ids
            used_marker_ids.add(travel_id)
            marker_types[source_type] = dict(sourceId=source_marker_id, clone=travel_type, travelId=travel_id)

    assert len(locations) == 505, f"Expected 505 eligible locations, found {len(locations)}"
    locations.sort(key=lambda loc: (ORDER.index(loc["category"]), loc["label"].casefold(), loc["key"]))
    counts = collections.Counter(loc["category"] for loc in locations)
    shroud_counts = collections.Counter(loc["category"] for loc in locations if loc["inShroud"])
    assert all(counts[key] == expected for key, _, _, _, expected in CATEGORY_SPECS)
    lines = ["-- Generated for Enshrouded client build 26404966. Do not hand-edit.",
             "return {", f"    build = {args.build},", "    categories = {"]
    for key, label, group, default, _ in CATEGORY_SPECS:
        lines.append(f"        {key} = {{ label = {lua(label)}, group = {lua(group)}, default = {lua(default)} }},")
    lines.append("    },")
    lines.append("    markerTypes = {")
    for source, info in sorted(marker_types.items()):
        lines.append(f"        [{lua(source)}] = {{ sourceId = {info['sourceId']}, clone = {lua(info['clone'])}, travelId = {info['travelId']} }},")
    lines.extend(["    },", "    locations = {"])
    for loc in locations:
        lines.append("        { " + ", ".join(f"{field} = {lua(value)}" for field, value in loc.items()) + " },")
    lines.extend(["    },", "}"])
    (MOD / "src" / "locations.lua").write_text("\n".join(lines) + "\n")

    settings = {}
    for key, label, group, default, _ in CATEGORY_SPECS:
        setting = {
            "value": default, "label": label,
            "description": f"Enable travel to all {counts[key]} discovered locations in this category. Shroud travel remains a separate rule.",
            "control": "toggle", "applyAt": "restart", "restartRequired": True, "assetPreparation": True,
        }
        settings[key] = setting
    settings["allowIntoShroud"] = {
        "value": False, "label": "Allow travel into Shroud",
        "description": "Allow selected destinations inside Shroud. When off, the Shroud rule blocks those locations regardless of their category switch.",
        "control": "toggle", "applyAt": "restart", "restartRequired": True, "assetPreparation": True,
    }
    groups = []
    groups.append({"label": "Travel Rules", "description": "This rule applies to every enabled category.",
                   "settings": ["allowIntoShroud"]})
    for group in ("Flame Sites", "Shroud Sites", "Ruins", "Settlements", "Exploration"):
        keys = [key for key, _, heading, _, _ in CATEGORY_SPECS if heading == group]
        groups.append({"label": group, "description": "Category switches apply to every listed map location.",
                       "settings": keys})
    config = {"$schema": "https://bonsaibauer.github.io/shroudforge/schemas/extended.mod.schema.json",
              "schemaVersion": 1, "enabled": True, "targets": ["client"], "launcher": "SF",
              "settings": settings, "groups": groups}
    (MOD / "extended.mod.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    inventory = [f"Enshrouded Teleportation Expanded location catalog — build {args.build}",
                 "One category switch controls every location listed beneath it.", ""]
    for key, label, _, default, _ in CATEGORY_SPECS:
        inventory.extend([f"{label} ({counts[key]}; default {'on' if default else 'off'}; {shroud_counts[key]} Shroud blocked when rule is off)", "-" * len(label)])
        inventory.extend(f"  {loc['key']}  {'[Shroud] ' if loc['inShroud'] else ''}{loc['label']}" for loc in locations if loc["category"] == key)
        inventory.append("")
    (MOD / "LOCATIONS.txt").write_text("\n".join(inventory), encoding="utf-8")
    print(f"Generated {len(locations)} locations across {len(counts)} category switches; {sum(counts[key] for key, _, _, default, _ in CATEGORY_SPECS if default)} enabled by default")


if __name__ == "__main__":
    main()
