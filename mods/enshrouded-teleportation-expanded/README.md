# Enshrouded Teleportation Expanded 0.2.0

This ShroudForge client mod adds individual map-travel switches for **617 placed
points of interest** in Enshrouded build **26404966**. They are grouped into 18
categories in `extended.mod.json`. The 63 Flame Shrines and Flame Sanctums are
on by default. All other locations and **Allow additional POIs, including
Shroud destinations** are off by default. Existing Ancient Spires and placed
Flame Altars keep the game's normal behavior.

The map label at each selected location gets a travel-enabled marker type. The
mod keeps the original label identity and coordinates, and sets its marker not
to appear above unexplored fog. It does not uncover the map, bypass the game's
discovery and travel checks, move the player directly, or edit world saves.

## Settings

Open `mods/enshrouded-teleportation-expanded/extended.mod.json` beside
`enshrouded.exe`. Each location has one `poi_...` setting with a name, category,
and world coordinates. Set its `value` to `true` or `false`. Coordinates
disambiguate locations with the same map name. A restart and ShroudForge asset
preparation are required for changes to take effect.

When upgrading from 0.1.x, `tools/migrate_config.py` carries the old Shrine,
Gem Forge, Shroud, and mod-enabled values into the new per-location config.
The ordinary mod installer preserves the old file as-is, so run the migration
before replacing that configuration. The previous mod folder is saved by the
installer under `shroudforge/backups/manual-mod-installs/`.

The global `allowIntoShroud` switch is required for **all optional locations**.
The client map-label assets do not reliably say which optional locations are
inside Shroud, so gating the whole optional set prevents those destinations
from being enabled inadvertently. To enable a Gem Forge, set both
`allowIntoShroud` and that Gem Forge's individual `poi_...` value to `true`.
Turning on the global switch alone enables no optional locations.

Some optional map-label positions may be hazardous arrival points, including
Shroud Roots, caves, and dungeons. Test only locations you intend to use. The
client's default discovery, fog, travel, and multiplayer rules still determine
whether an enabled map label appears and can be used.

## Build and test status

This location catalog is tied to client build **26404966**. The mod checks the
registry, map-label scene, template collection, and every location's original
template and position before changing assets. If the game data changes, it
fails during preparation and needs a regenerated catalog.

In a disposable client copy, ShroudForge successfully prepared the default 63
locations, one additional Gem Forge, and all 617 locations. Asset readback
confirmed that only the selected scene entities changed, their new templates
were added to the collection, original templates and marker types stayed
unchanged, and the new travel marker IDs were valid in the registry. This is
asset validation, not proof of arrival or server acceptance.

The earlier 0.1.0 prototype was tested in game: a player reached a Flame Shrine
and Flame Sanctum safely in single player and with one modded client on an
unmodded dedicated server. Version 0.2.0 changes how individual map labels are
selected. Its in-game arrival behavior, fog discovery, Shroud travel,
per-player discovery, and two-client multiplayer behavior still need testing.

## Install and first test

1. Close Enshrouded. Keep the same path:
   `mods/enshrouded-teleportation-expanded/src/mod.lua` beside `enshrouded.exe`.
2. Start the game with the ShroudForge loader. Its log should say
   `Teleportation Expanded: enabled 63 individual POIs across 617 configured locations`
   for the packaged defaults.
3. In a disposable world, try an uncovered Flame Shrine and Flame Sanctum.
   Confirm each offers travel and that the player arrives safely.
4. If possible, check that a Shrine or Sanctum under unexplored fog cannot be
   used. Compare two players with different discovery states on a test server.
5. Only after the default path works, enable the global Shroud switch and one
   specific Gem Forge. Test arrival, Shroud timer, and return travel.

The dedicated server's resource container does not contain the client map
marker registry. Each player who wants the expanded destinations should
install the mod on their client. The server need not run this asset patch for
the earlier Shrine and Sanctum prototype; version 0.2.0 still needs the
multiplayer test described above.

## Regenerating after a game update

`tools/generate_locations.py` rebuilds `src/locations.lua` and
`extended.mod.json` from exports of the client's POI templates, placed map
labels, marker registry, English localization, and icon resources. Review the
generated catalog and repeat isolated preparation and in-game tests before
installing it for a new build. Existing `poi_...` keys are based on map-label
coordinates; review user settings when game placements change.
