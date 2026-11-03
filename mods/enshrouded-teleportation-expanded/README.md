# Enshrouded Teleportation Expanded 0.3.1

This ShroudForge client mod adds map travel to **505 placed points of interest**
in Enshrouded build **26404966**. It has 16 category switches and one separate
**Allow travel into Shroud** switch. It leaves Ancient Spires and placed Flame
Altars with their normal behavior. Elixir Wells, Fog Nests, Shroud Roots, and
related sites are excluded from the catalog.

The packaged configuration enables Flame Sites, Ruins, Settlements, and
Exploration, and leaves Gem Forges, Night Sanctums, and travel into Shroud off.
For the first gameplay test, use the all-enabled test configuration: all 16
categories and Shroud travel are on. The Shroud rule takes precedence over
*every* category when turned off, so a Gem Forge or a cave classified inside
Shroud cannot be selected for expanded travel even if its category is on.

## Settings

Edit `mods/enshrouded-teleportation-expanded/extended.mod.json` beside
`enshrouded.exe`, or use the ShroudForge mod settings UI. Each category has one
true/false switch. The 16 categories are Flame Shrines, Flame Sanctums, Gem
Forges, Night Sanctums, Dungeons, Hollow Halls, Ancient Vaults, Obelisks,
Tombs, Balefire Sites, Mines, Caves, Enemy Camps, Villages/Towns, Survivor
Camps, and Farms. The 17th switch is the Shroud rule. Restart and run
ShroudForge's asset preparation after a setting change.

`LOCATIONS.txt` lists every eligible location and marks destinations blocked
when Shroud travel is off. The build-specific classification samples the
game's gameplay Shroud volume near each map label. ShroudForge does not expose
the game's live destination fog query to this mod. The static rule errs toward
blocking sites near Shroud, and it does not update when a world event clears
Shroud. Confirm the arrival point and Shroud timer in game before treating a
site as safe. The all-enabled test config deliberately bypasses that guard.

The selected map labels get travel-enabled marker types that do not appear
above unexplored fog. These added marker types stay outside the game's fixed
map-filter list. The mod does not uncover the map, move players directly,
or edit world saves. The game still handles discovery, travel, arrival, and
server acceptance.

## Build and test status

The catalog is tied to client build **26404966**. It checks the registry,
map-label scene, template collection, and source POI positions before changing
assets. If those change, preparation fails and the catalog needs regeneration.

In a disposable game copy, ShroudForge prepared **250** destinations with the
packaged defaults and **505** with every switch on. Readback of the all-enabled
build confirmed 505 selected scene changes and cloned templates, 15 new travel
marker types, and unchanged source marker types. Version 0.3.0 crashed when
loading a world because its 15 new marker types raised the game's 40-entry
map-filter list from 36 entries to 51. Version 0.3.1 leaves the 15 travel
types out of that list; readback confirms 36 filterable types and 21 travel
types. These are asset checks, not gameplay or multiplayer proof.

The earlier Shrine/Sanctum prototype worked in single player and with one
modded client on an unmodded dedicated server. In a 0.3.1 single-player test,
the world loaded and the player reported successful travel to multiple enabled
locations, including a Hollow Hall and a Gem Forge. The game log records six
travel events and a normal shutdown. The player also confirmed that an
undiscovered destination could not be selected. The Shroud-off rule,
two-client behavior, and per-player discovery still need gameplay testing.
The dedicated server has no client map-marker registry, so each player wanting
expanded markers installs the mod on their own client.

## Install and first test

1. Close Enshrouded. Keep the mod at
   `mods/enshrouded-teleportation-expanded` beside `enshrouded.exe`.
2. For this first test, set every category and `allowIntoShroud` to `true`.
   Launch with ShroudForge to prepare the client assets. The log should report
   `enabled 505 POIs across 505 eligible locations`.
3. In a disposable world, try a discovered Shrine/Sanctum, Gem Forge, and one
   destination from a broad category. Confirm each travel option and arrival.
4. Check a destination still under unexplored fog with a different player if
   possible. After initial travel testing, turn Shroud travel off, prepare
   again, and verify a known Shroud destination is no longer offered while a
   clear destination in its category still is.
5. Repeat on a test dedicated server with two modded clients before treating
   multiplayer behavior as established.

When upgrading from 0.1.x or 0.2.x, `tools/migrate_config.py` carries the mod
enabled state and compatible settings into the category configuration. It
replaces old per-location defaults with the new category defaults. If a group
contains mixed custom location values, migration stops so you can choose a
category value manually. The installer saves the previous mod folder under
`shroudforge/backups/manual-mod-installs/`.

## Regenerating after a game update

`tools/generate_locations.py` rebuilds `src/locations.lua`,
`extended.mod.json`, and `LOCATIONS.txt` from client POI templates, scene
placements, marker registry, English localization, icon resources, and the
Shroud volume model and tile content. Review the catalog and repeat isolated
preparation and in-game tests for every supported game build.
