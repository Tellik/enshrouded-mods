#!/usr/bin/env python3
"""Generate build-specific per-location travel data from exported client assets.

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

NAMESPACE = uuid.UUID("5b89fd28-2b08-44a7-9b2d-d298c9f263c4")
MOD = pathlib.Path(__file__).resolve().parents[1]
CATEGORIES = {
    "mapmarker_well_plant": "Shroud Roots and Elixir Wells",
    "mapmarker_shroudforge": "Gem Forges",
    "mapmarker_fognest": "Fog Nests",
    "mapmarker_mine": "Mines",
    "mapmarker_dungeon": "Dungeons",
    "mapmarker_bigDungeon": "Large Dungeons",
    "mapmarker_challenge_chamber": "Challenge Chambers and Vaults",
    "mapmarker_nighttemple": "Night Sanctums",
    "mapmarker_special_enemy_camp": "Enemy Camps",
    "mapmarker_village": "Villages",
    "mapmarker_survivorcamp": "Survivor Camps",
    "mapmarker_farm": "Farms",
    "mapmarker_cave": "Caves",
    "mapmarker_obelisk": "Obelisks",
    "mapmarker_tomb": "Tombs",
    "mapmarker_balefire": "Balefire Sites",
}
ORDER = ["Flame Shrines", "Flame Sanctums", *CATEGORIES.values()]
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
    parser.add_argument("--build", required=True, type=int)
    args = parser.parse_args()

    templates = {p["id"]: p["value"] for p in json.loads(args.pois.read_text())}
    placements = json.loads(args.placements.read_text())
    registry = json.loads(args.registry.read_text())[0]["value"]["mapMarkers"]["values"]
    names = {tag["id"]["value"]: tag["text"] for tag in json.loads(args.loca.read_text())["tags"]}
    icons = {icon["id"]: icon["value"].get("debugName") for icon in json.loads(args.icons.read_text())}
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
        if icon == "mapmarker_flame_essence":
            category = "Flame Sanctums" if "FlameTemple" in template["name"] else "Flame Shrines"
        else:
            category = CATEGORIES.get(icon)
        if not category:
            continue  # Stock travel, quest hints, area labels, and platform markers.
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
        loca = component(template, 3179)  # keen::ecs::MapMarkerLocaTag
        name = names.get(fnv_guid(loca["locaTag"])) if loca and loca.get("locaTag") else None
        if not name or name.startswith("Placeholder"):
            name = re.sub(r"^8[kK]MapLabel_|^MapLabel_", "", template["name"]).replace("_", " ")
        region = next((label for token, label in REGIONS.items() if token in template["name"].lower()), None)
        label = f"{name} — {region} ({x}, {z})" if region else f"{name} ({x}, {z})"
        locations.append(dict(key=key, category=category, label=label, template=placement["template"],
                              markerType=source_type, clone=clone, entity=placement["entityIndex"],
                              x=x, y=y, z=z, default=category in ("Flame Shrines", "Flame Sanctums")))
        if source_type not in marker_types:
            travel_type = str(uuid.uuid5(NAMESPACE, "marker:" + source_type))
            travel_id = fnv_guid(travel_type)
            assert travel_id not in used_marker_ids
            used_marker_ids.add(travel_id)
            marker_types[source_type] = dict(sourceId=source_marker_id, clone=travel_type, travelId=travel_id)

    assert len(locations) == 617, f"Expected 617 locations, found {len(locations)}"
    assert sum(p["default"] for p in locations) == 63
    locations.sort(key=lambda loc: (ORDER.index(loc["category"]), loc["label"].casefold(), loc["key"]))
    counts = collections.Counter(loc["category"] for loc in locations)
    lines = ["-- Generated for Enshrouded client build 26404966. Do not hand-edit.",
             "return {", f"    build = {args.build},", "    markerTypes = {"]
    for source, info in sorted(marker_types.items()):
        lines.append(f"        [{lua(source)}] = {{ sourceId = {info['sourceId']}, clone = {lua(info['clone'])}, travelId = {info['travelId']} }},")
    lines.extend(["    },", "    locations = {"])
    for loc in locations:
        lines.append("        { " + ", ".join(f"{field} = {lua(value)}" for field, value in loc.items()) + " },")
    lines.extend(["    },", "}"])
    (MOD / "src" / "locations.lua").write_text("\n".join(lines) + "\n")

    settings = {
        "allowIntoShroud": {
            "value": False, "label": "Allow additional POIs, including Shroud destinations",
            "description": "Required for all optional POIs. Their Shroud status cannot be reliably classified from map-label assets, so this switch conservatively gates them all.",
            "control": "toggle", "applyAt": "restart", "restartRequired": True, "assetPreparation": True,
        }
    }
    for loc in locations:
        setting = {
            "value": loc["default"], "label": loc["label"],
            "description": "Enable map travel to this discovered POI only. The marker remains subject to the game's visibility and travel rules.",
            "control": "toggle", "applyAt": "restart", "restartRequired": True, "assetPreparation": True,
        }
        if not loc["default"]:
            setting["enabledWhen"] = {"setting": "allowIntoShroud", "equals": True}
        settings[loc["key"]] = setting
    groups = [{"label": "Travel safety", "description": "Optional locations may be hazardous or within Shroud.", "settings": ["allowIntoShroud"]}]
    for category in ORDER:
        groups.append({"label": category, "description": f"{counts[category]} individual map locations.",
                       "settings": [loc["key"] for loc in locations if loc["category"] == category]})
    config = {"$schema": "https://bonsaibauer.github.io/shroudforge/schemas/extended.mod.schema.json",
              "schemaVersion": 1, "enabled": True, "targets": ["client"], "launcher": "SF",
              "settings": settings, "groups": groups}
    (MOD / "extended.mod.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    print(f"Generated {len(locations)} locations across {len(counts)} categories; {sum(p['default'] for p in locations)} enabled by default")


if __name__ == "__main__":
    main()
