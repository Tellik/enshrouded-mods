# Enshrouded Teleportation Expanded 0.1.0 prototype

This experimental ShroudForge asset mod marks Flame Shrine and Flame Sanctum
map markers as fast-travel destinations. The two POIs use the same marker type in the
current game data, so they share one switch. Gem Forge travel is optional and
requires both **Allow destinations in the Shroud** and **Gem Forges** to be on.
The packaged defaults enable Flame Shrines and Sanctums, and leave Shroud
destinations and Gem Forges off.

The mod changes the game's map-marker registry before the client starts. For
enabled categories, it hides their markers above unexplored fog. The game
also has a separate marker-visibility state, which starts hidden on the
inspected Shrine and Gem Forge templates. Whether uncovering fog alone makes
the marker visible still needs a live check. The mod does not uncover the map,
add POIs, move a player directly, or change the game's travel animation. It
does not alter any world or character save.

## Status

The mod source and configuration have been checked against Enshrouded client
builds **26082781** and **26320373** and their matching game resources. The
exact registry GUID, entry count, and two marker IDs are checked before any
asset is changed. In an isolated copy, the patched ShroudForge loader completed
its pregame pass and
committed one changed resource. Reading that resource back showed only the
two intended fields changed on the enabled marker types, both with defaults
and with Gem Forges enabled.

On November 1, 2026, the default configuration was installed in the live
client. ShroudForge prepared the assets successfully, and readback showed
exactly the two intended field changes on the Shrine/Sanctum marker type.
The tester then traveled to an uncovered Flame Shrine and Flame Sanctum in a
local single-player world and reported safe arrival at both. The game log
records two player teleports and normal session shutdown; POI identification
comes from the tester because the log does not name the destinations.

On November 2, 2026, the tester joined an unmodded dedicated server with the
modded client and reported safe arrival after map travel to both a Flame Shrine
and a Flame Sanctum. The client log confirms an online session and map use but
does not name the destinations or record the server's travel decision; the
arrival results come from the tester. This supports client-only installation
for these two destinations in the tested dedicated-server setup. On the
updated client build 26320373, comparing the clean and prepared marker registry
again showed exactly the two intended Shrine/Sanctum field changes.

Fog-only discovery, per-player discovery behavior, Shroud entry, Gem Forge
travel, hosted co-op, and a two-client dedicated-server session **have not yet
been tested**. This is a development prototype, not a release.

## Staged installation for a controlled test

1. Close Enshrouded and back up the local world to be used for testing.
2. Use a ShroudForge build that can commit pregame asset patches under your
   platform. The patched 1.7.7 development loader in this repository includes
   the Proton/Wine asset-reader fix.
3. Copy this folder into `mods/` beside `enshrouded.exe`, so the path ends in
   `mods/enshrouded-teleportation-expanded/src/mod.lua`.
4. Start a disposable single-player world. Confirm the ShroudForge log says
   `Teleportation Expanded: enabled 1 additional map-marker categories`.
5. Compare a Shrine or Sanctum still under fog with one whose area is
   uncovered. Check both whether the uncovered marker appears immediately and
   whether it offers map travel. Travel to it and record the arrival position
   and whether movement, combat, and saving continue normally.
6. For broader multiplayer coverage, test a player-hosted world and a
   disposable dedicated world with two clients. Install the mod on each client
   that should have additional destinations. Check that each player can travel
   only to POIs uncovered on that player's map, and record both arrivals.
7. Only after the default path works, enable both Shroud switches and try a
   Gem Forge in a disposable world. Check arrival, Shroud timer, and return
   travel separately.

The dedicated server's resource container has no map-marker registry resource;
this prototype therefore runs on clients. Travel to the two default
destination types succeeded during the initial test with an unmodded dedicated
server. Other multiplayer cases still need the controlled checks above.

To disable the prototype, set `"enabled": false` in `extended.mod.json` and
restart the client. Changes to any travel setting also need a restart.

## Source evidence

The client `MapMarkerRegistryResource` has GUID
`d165e819-f603-42a3-8f7d-827e9e8cb97a` and 49 marker types in build
26082781 and 26320373. In the clean game data, `isFastTravelDestination` is
false for `mapmarker_flame_essence` (type ID `2068618774`) and
`mapmarker_shroudforge` (type ID `4099254117`). The first type is used by
`8kMapLabel_general_FlameShrine` and `8kMapLabel_*_FlameTemple_*` templates.
The second is used by `8kMapLabel_generic_gemForgeStation*` templates. The
game's existing fast-travel types have the flag set. These are static asset
observations, not gameplay proof.
