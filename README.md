# Autorun v0.4.0 prerelease

Autorun toggles ordinary forward movement for the local Enshrouded character.
It is a **client-only** ShroudForge mod: install it on the PC where you play,
including when you join a dedicated server. The server does not need Autorun.

The native plugin supports the exact Enshrouded Steam client builds `26082781`
and `26430625`. It stays inactive on an unknown executable or incompatible
ShroudForge ABI. Version 0.4.0 was tested on Linux/Proton in single-player and
as a dedicated-server client with the [official ShroudForge 1.7.8 stable ZIP](https://github.com/bonsaibauer/shroudforge/releases/tag/v1.7.8-build.41706360752).
Native Windows gameplay and a longer stability test remain outstanding, so
this release is a prerelease.

## Download the right ZIP

Get the named assets from the [Autorun v0.4.0 prerelease](https://github.com/Tellik/enshrouded-mods/releases/tag/v0.4.0),
not GitHub's generated source archives. ShroudForge is a separate download.

| ZIP | Use it when | Contents |
| --- | --- | --- |
| `autorun-0.4.0-initial.zip` | First install, or updating from a version other than 0.3.2 | Complete `autorun/` folder, including default `extended.mod.json` |
| `autorun-0.4.0-upgrade-from-0.3.2.zip` | Updating an existing 0.3.2 installation | Only files changed since the published 0.3.2 ZIP; no default settings file |

The upgrade ZIP is **not** a standalone installation. It relies on the
unchanged files already present in `./mods/autorun/`. Both ZIPs place their
files under an inner `autorun/` folder; neither includes ShroudForge.

## Windows

1. Close Enshrouded. If needed, install the full [ShroudForge 1.7.8 stable ZIP](https://github.com/bonsaibauer/shroudforge/releases/tag/v1.7.8-build.41706360752)
   beside `enshrouded.exe` using the [shared Windows guide](https://github.com/Tellik/enshrouded-mods/blob/main/docs/install-mods.md#install-shroudforge-on-a-windows-client).
2. For a first install, open `autorun-0.4.0-initial.zip` and copy its inner
   `autorun/` folder to `./mods/`, relative to `enshrouded.exe`.
3. For an update **from 0.3.2**, first back up `./mods/autorun/`. Open
   `autorun-0.4.0-upgrade-from-0.3.2.zip` and copy its inner `autorun/`
   contents over the existing `./mods/autorun/`, replacing the three files in
   the ZIP. Do not remove the existing folder or its `extended.mod.json`.
4. For an update from another version, use the initial ZIP with the
   [configuration-preserving installer](https://github.com/Tellik/enshrouded-mods/blob/main/docs/install-mods.md#update-a-mod-without-losing-settings),
   or save `extended.mod.json`, replace the mod folder, then restore the
   settings file before starting the game.

The final path must be `./mods/autorun/mod.json`, with
`./mods/autorun/bin/autorun.dll` beside the other mod files. If your extractor
creates `./mods/autorun-0.4.0-initial/autorun/`, move the inner `autorun/`
folder up one level. Keep ZIP files outside `./mods/`.

Native Windows gameplay has not yet been tested; the Windows x64 build and ZIP
layouts are checked by the package workflow.

## Linux / Proton

Use the same ZIP choice and file layout as above, with the game fully closed.
Set Steam's Enshrouded **Launch Options** to:

```text
WINEDLLOVERRIDES="dbghelp=n,b;winmm=n,b" %command%
```

The [shared Proton guide](https://github.com/Tellik/enshrouded-mods/blob/main/docs/install-mods.md#install-shroudforge-on-a-linuxproton-client)
explains the loader placement, WebView2 setup, and the Hyprland cursor fix.
With WebView2 installed, F9 opens ShroudForge's Modloader and lets you record
a new hotkey. Without that window, edit `./mods/autorun/extended.mod.json`
while the game is closed. The upgrade ZIP leaves that file untouched.

## Check and configure

Autorun starts enabled. Its default toggle is **F8**; press it once to move
forward and again to stop. **S** cancels a run. World Editor also uses F8, so
disable World Editor or choose another Autorun key. In ShroudForge's Modloader,
open Autorun and record a shortcut. The tested custom setting combined F7 and
Mouse X2. The detailed guide explains the JSON setting for manual changes.

After launching, `./mods/autorun/autorun-plugin.log` should show
`Exact-build input hook installed`. The updated plugin also logs why movement
stops. An unsupported-image or ABI message means it did not activate. ShroudForge
1.7.8 currently lacks an exact profile for Enshrouded build `26430625`, which
may limit other ShroudForge features; Autorun has its own exact-build movement
check and was verified on that build.

For behavior, hotkeys, build details, and test limits, see the
[detailed Autorun guide](standalone/autorun/README.md).
