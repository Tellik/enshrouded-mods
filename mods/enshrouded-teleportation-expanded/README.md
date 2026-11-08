# Enshrouded Teleportation Expanded

Add map fast travel to discovered points of interest while keeping the game's
normal discovery and travel rules. The mod supports 505 placed locations in 16
independently controlled categories. A separate **Allow travel into Shroud**
switch applies to every category.

Ancient Spires and placed Flame Altars retain their normal behavior. Elixir
Wells, Fog Nests, Shroud Roots, and related sites are excluded.

## Configuration

Set the switches in `mods/enshrouded-teleportation-expanded/extended.mod.json`
beside each game executable, or in ShroudForge's mod settings UI. Install and
configure the mod on every participating client and the dedicated server.
Restart and prepare game assets after changing a switch.

| Group | Switches | Packaged default |
| --- | --- | --- |
| Flame Sites | Flame Shrines, Flame Sanctums | On |
| Shroud Sites | Gem Forges, Night Sanctums | Off |
| Ruins | Dungeons, Hollow Halls, Ancient Vaults, Obelisks, Tombs, Balefire Sites | On |
| Exploration | Mines, Caves | On |
| Settlements | Enemy Camps, Villages/Towns, Survivor Camps, Farms | On |
| Shroud rule | Allow travel into Shroud | Off |

When Shroud travel is off, a location classified inside Shroud is excluded even
if its category is on. `LOCATIONS.txt` lists every eligible location and its
Shroud classification. The classification samples the game's Shroud volume
near each map label. It errs toward blocking sites near Shroud and does not
update when a world event clears Shroud. Check the arrival point and Shroud
timer before relying on an enabled Shroud destination.

The mod gives selected map labels travel-enabled marker types that remain
hidden under unexplored fog. The game still decides whether a player has
discovered a destination, performs the travel, and accepts it on the server.
The mod does not uncover the map, move players directly, or edit saves.

## Install

1. Close the game and stop the dedicated server before installing or changing
   settings.
2. Put the packaged `enshrouded-teleportation-expanded` folder at
   `mods/enshrouded-teleportation-expanded` beside the client and server
   executables. Do not add a second enclosing folder.
3. Keep the client and server category and Shroud switches aligned. Prepare
   assets with ShroudForge, then start the game and server. Check the
   ShroudForge log for `Teleportation Expanded: enabled ... POIs` and a
   successful asset commit.

The packaged defaults enable 14 categories and exclude Shroud locations,
selecting 250 destinations on the current builds. With all 16 categories on
and Shroud travel off, the catalog selects 268 clear destinations. Turning
Shroud travel on selects all 505. These counts
describe asset preparation; verify travel in game.

## Compatibility and test status

The catalog was generated from client build **26404966**. Its map-marker,
scene, template, and placement checks also pass on client build **26430625**
and dedicated-server build **26430253**. On those newer builds, isolated
Shroud-off preparation selected 268 locations on both sides; Shroud-on
preparation selected 505 on both sides. Both preparations committed using the
patched ShroudForge 1.7.7 asset loader.

Single-player travel to several enabled POIs and rejection of an undiscovered
POI were confirmed on the earlier client build. A modded client also joined
the remote dedicated test server on build **26404334**, traveled to multiple
POIs, and arrived safely. On the current client and dedicated-server builds,
the player reported that clear POI travel works and Shroud POIs are unavailable
with Shroud travel off in both worlds. With Shroud travel on, the player
reported safe travel to discovered Shroud and clear POIs in both worlds.
Two-client discovery behavior has not yet been tested.

On this Linux/Wine test setup, stock ShroudForge **1.7.9** has exact profiles
for the newer game builds but fails a fresh asset publish with `Access denied
(os error 5)`, even when this is the only asset mod. The previously patched
1.7.7 loader completes the same publish. An already applied asset patch can
remain usable after upgrading ShroudForge; its applied status alone does not
prove new settings were published. Check for a successful commit after every
configuration change. See the upstream [Wine asset publishing issue](https://github.com/bonsaibauer/shroudforge/issues/75)
and [proposed fix](https://github.com/bonsaibauer/shroudforge/pull/73).

The source checks expected map-marker, scene, template, and location data
before changing assets. It stops preparation if those assumptions change in
a future game build.

## Upgrading older configurations

When upgrading from 0.1.x or 0.2.x, `tools/migrate_config.py` carries the mod
enabled state and compatible settings into the category configuration. It
stops when a category contains mixed custom location values so you can choose
its category value yourself. The config-preserving installer saves the old
mod folder under `shroudforge/backups/manual-mod-installs/`.

`tools/generate_locations.py` rebuilds the catalog and configuration from the
game data after a future incompatible update. Review the result and repeat
asset and gameplay tests before distributing it.
