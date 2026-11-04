# Enshrouded Autorun v0.4.0 prerelease

Autorun is a standalone, client-only ShroudForge mod. ShroudForge loads this
mod's `bin/autorun.dll` through `native-plugin.ini`; the ZIP does not replace
any ShroudForge runtime file. Install it on the playing client for both
single-player and dedicated-server worlds. The server does not need Autorun.

The native plugin supports the exact Enshrouded Steam client builds `26082781`
and `26430625` and ShroudForge's ABI-12 native-plugin interface. It refuses
unknown game images or incompatible ABI versions. The 0.4.0 change adds the
newer game build, a local input-based world check for cases where ShroudForge
has no exact game profile, focused stop diagnostics, a timing-race fix, and
continuation while the game loses focus.

## Install or update

Download the named ZIP assets from the [v0.4.0 prerelease](https://github.com/Tellik/enshrouded-mods/releases/tag/v0.4.0)
and the separate [official ShroudForge 1.7.8 stable release](https://github.com/bonsaibauer/shroudforge/releases/tag/v1.7.8-build.41706360752).
GitHub's generated source archives are not installation ZIPs.

- **First install:** use `autorun-0.4.0-initial.zip`. Copy its inner `autorun/`
  folder to `./mods/` beside `enshrouded.exe`. It includes the default enabled
  state and F8/S hotkeys in `extended.mod.json`.
- **Upgrade from 0.3.2:** close the game, back up `./mods/autorun/`, then overlay
  the inner `autorun/` folder from
  `autorun-0.4.0-upgrade-from-0.3.2.zip` onto the existing mod folder. This
  ZIP contains only the changed DLL, manifest, and README. It does **not**
  contain `extended.mod.json`, so your enabled state and hotkeys remain.
- **Upgrade from another version:** use the initial ZIP through the
  [configuration-preserving installer](https://github.com/Tellik/enshrouded-mods/blob/main/docs/install-mods.md#update-a-mod-without-losing-settings),
  or back up and restore `extended.mod.json` yourself. Do not use the 0.3.2
  upgrade ZIP on a fresh or older installation.

The result must include `./mods/autorun/mod.json`,
`./mods/autorun/extended.mod.json`, `./mods/autorun/native-plugin.ini`, and
`./mods/autorun/bin/autorun.dll`, relative to `enshrouded.exe`. Keep the ZIP
outside `./mods/`. If your archive tool adds a wrapper folder named after the
ZIP, move the inner `autorun/` folder directly into `./mods/`.

### Windows

Extract ShroudForge's full ZIP beside `enshrouded.exe` before installing
Autorun. Follow the [shared Windows guide](https://github.com/Tellik/enshrouded-mods/blob/main/docs/install-mods.md#install-shroudforge-on-a-windows-client)
if the loader is not already installed. F9 opens the ShroudForge Modloader.
Native Windows gameplay remains unverified; the Windows x64 DLL and ZIPs pass
automated build and package checks.

### Linux / Proton

Use the same mod layout and set Steam's Enshrouded launch options to:

```text
WINEDLLOVERRIDES="dbghelp=n,b;winmm=n,b" %command%
```

The [shared Proton guide](https://github.com/Tellik/enshrouded-mods/blob/main/docs/install-mods.md#install-shroudforge-on-a-linuxproton-client)
covers WebView2 and the tested Hyprland cursor setting. If the Modloader
window is disabled, edit `extended.mod.json` with the game closed. With
WebView2 installed, F9 opened the stock ShroudForge 1.7.8 Modloader in the
tested Proton setup, and its pointer was visible and aligned.

## Controls and behavior

The default toggle is **F8**: press once to start normal forward movement and
again to stop. The default cancel key is **S**, matching backward movement.
Left/right steering continues to work. Autorun does not force sprint or the
game's slower Walk action. World Editor also uses F8; disable it or give
Autorun another toggle key.

The Modloader can record a different keyboard or mouse shortcut. The plugin
reads setting changes live and stops the current run when a binding changes.
For manual configuration, close the game and edit these keys in
`./mods/autorun/extended.mod.json`:

```json
"toggleAutorun": { "value": "SDL:64|Mouse:5" },
"cancelAutorun": { "value": "SDL:22" }
```

`SDL:64` is F7, `Mouse:5` is Mouse X2, and `SDL:22` is S. The default F8 is
`SDL:65`; F6 is `SDL:63`. A `|` allows one keyboard or mouse alternative.
Modifiers such as `Ctrl+SDL:64` are supported. An empty value disables that
shortcut. The plugin recognizes A–Z, 0–9, F1–F12, Enter, Escape, Backspace,
Tab, Space, Insert, Delete, Home, End, Page Up/Down, arrows, and mouse
buttons 1–5. Malformed or unsupported bindings fail closed and are logged.

Losing game focus does **not** stop an active run. Toggle and cancel hotkeys
are read only while the game is focused, so stop Autorun before switching away
if continued movement would be unsafe. Leaving a world or losing fresh input
stops it; it starts off after a world change until toggled again.

## Verify and troubleshoot

After launch, `./mods/autorun/autorun-plugin.log` should contain
`Exact-build input hook installed`. In a safe open area, toggle once to move,
toggle again to stop, then start and press S to cancel. The log records start
and stop reasons, input activity, and input-source replacement. If it reports
an unsupported image or ABI, the plugin stays inactive; check your exact game
and ShroudForge versions.

Single-player and dedicated-server client tests passed on Linux/Proton with
the official ShroudForge 1.7.8 stable ZIP. In the final transition test,
Autorun was active in single-player, then started off after joining a
dedicated server and worked there. F9 also opened the Modloader. Earlier tests
confirmed toggle and S stops, fast travel, respawn, and continuation through
a brief focus change. The one-hour stability test has been deferred, and
native Windows gameplay is still unverified.

ShroudForge 1.7.8 currently has no exact game profile for Enshrouded build
`26430625`, so some other ShroudForge features may remain unavailable. Autorun
uses its own exact-image input hook and a validated local in-world signal on
that build; this does not establish compatibility for other mods.

## Build and package

The [Windows package workflow](https://github.com/Tellik/enshrouded-mods/blob/autorun/.github/workflows/autorun-windows.yml)
builds the Windows x64 DLL, runs the input-observation test, and creates both
0.4.0 ZIPs and SHA-256 files. The packaging script compares the upgrade ZIP
against the published 0.3.2 archive recorded in
`dev/build/autorun-0.3.2-baseline.json`. It normalizes text line endings,
rejects file removals or changed default settings, and includes only changed
files in the upgrade ZIP.

The bundled `LICENSE` retains ShroudForge's MIT notice for reused hook
helpers. `LICENSE.nlohmann` covers the JSON parser compiled into the plugin.
