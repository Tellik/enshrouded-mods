# Enshrouded Autorun (standalone prerelease)

This is a separate, client-only ShroudForge mod. It does not replace
`kfc-runtime.dll`, `shroudforge-runtime.dll`, or any other ShroudForge file.
ShroudForge loads the mod's own `bin/autorun.dll` through
`native-plugin.ini`. The published v0.3.2 plugin is restricted to Enshrouded
Steam build `26082781` and ShroudForge's ABI-12 world API; it stays inactive if
either check fails. Single-player and dedicated-server Proton tests on stock
ShroudForge 1.7.6 passed with F7 as a custom hotkey. The mod owner also
confirmed Autorun works on the patched 1.7.7 client loader used by Free
Airborne Architect.

The unreleased development branch also recognizes game build `26430625`.
Installed ShroudForge 1.7.7 has no profile for that build, so Autorun's draft
fix uses its exact-build local movement callback to identify in-world input.
The read-only probe found valid W/S input in the world and no callbacks at the
main menu. Single-player and dedicated-server Proton gameplay checks confirmed
forward movement and toggle and S stops. Movement also continued through a
brief focus change. The requested one-hour stability check is still pending;
the v0.3.2 ZIP below does not contain this fix.

Download the `autorun-0.3.2.zip` asset from the
[Autorun v0.3.2 prerelease](https://github.com/Tellik/enshrouded-mods/releases/tag/v0.3.2)
and `shroudforge-1.7.6-40026840919.zip` from the separate
[ShroudForge 1.7.6 dev release](https://github.com/bonsaibauer/shroudforge/releases/tag/v1.7.6-dev.40026840919).
If you also use Free Airborne Architect, use its
[patched 1.7.7 loader ZIP](https://github.com/Tellik/enshrouded-mods/releases/tag/airborne-architect-free-v0.2.1)
on the same client instead.

## Install the files (Windows and Linux/Proton)

1. Close the game. Extract the selected ShroudForge ZIP into the folder
   containing `enshrouded.exe`. Its three proxy DLLs go
   beside the executable; its `shroudforge` and `mods` folders go beside it.
   Back up an existing `mods/autorun` folder, if present.
2. Treat the folder containing `enshrouded.exe` as `./`. Open the Autorun ZIP
   and copy its inner `autorun/` folder into `./mods/`. The result must be
   `./mods/autorun/mod.json`, `./mods/autorun/extended.mod.json`,
   `./mods/autorun/native-plugin.ini`, and `./mods/autorun/bin/autorun.dll`.
   Keep the ZIP outside `./mods/`. If **Extract Here** creates
   `./mods/autorun-0.3.2/autorun/`, move the inner `autorun/` folder up into
   `./mods/` and remove the empty wrapper. The native loader needs the exact
   `./mods/autorun/` location.

Version 0.3.2 starts enabled; the older v0.3.0 ZIP starts disabled. On upgrade,
extracting either ZIP directly over the existing mod can reset its enabled
state and keybind. Use the
[shared guide's configuration-preserving installer](https://github.com/Tellik/enshrouded-mods/blob/main/docs/install-mods.md#update-a-mod-without-losing-settings)
or save the old `extended.mod.json`, extract the new ZIP, and restore that file
before restarting. The installer also saves the previous mod folder for rollback.

The stock ShroudForge 1.7.6 ZIP can enable bundled mods. World Editor uses
F8, Autorun's default key. Disable World Editor or change Autorun's key;
for an isolated first test, disable all bundled mods. The patched 1.7.7
loader ships its bundled mods disabled by default, but review their states
after any loader update.

### Windows

1. Version 0.3.2 starts enabled, so launch Enshrouded and check Autorun as
   described below. Press F9 if you want to open the ShroudForge Modloader.
2. Disable World Editor if you want to keep F8 for Autorun, or change
   Autorun's toggle key. Restart after changing which native mods load.

Native Windows gameplay has not yet been tested. The Windows build and ZIP
layout passed automated checks.

### Linux / Proton

These steps reproduce the simplest tested Proton setup without WebView2.
Before the first launch, set Steam's Enshrouded **Launch Options** to:

```text
WINEDLLOVERRIDES="dbghelp=n,b;winmm=n,b" %command%
```

Then, while the game is closed:

1. Open `shroudforge/config/modloader-config.json`. Under `modules`, change
   the `enabled` values for `debugConsole` and `modloaderUi` to `false`.
   This prevents the two WebView2 windows from causing a startup error.
2. Version 0.3.2 starts enabled. On upgrade, preserve your existing
   `mods/autorun/extended.mod.json` so its enabled state and hotkeys remain.
3. For an isolated first test, set `"enabled": false` in each bundled mod's
   `extended.mod.json`, especially `mods/world-editor`. To hold ShroudForge
   at the tested version, also set `modules.updates.automatic.enabled` to
   `false` in its config file. The clean-install test also disabled the
   `worldEditor` module there.
4. Start the game. The Modloader window is intentionally disabled; configure
   Autorun by editing its `extended.mod.json` while the game is closed.

To configure the mod through ShroudForge on Proton, install the official
[Microsoft WebView2 x64 Evergreen Standalone Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)
in Enshrouded's Proton prefix. The [shared installation guide](https://github.com/Tellik/enshrouded-mods/blob/main/docs/install-mods.md#webview2-window-does-not-open)
has the Protontricks command and the Hyprland window setting that made the
cursor visible and clicks accurate in the tested setup. Then enable
`modules.modloaderUi.enabled` and press F9 in game. The runtime is not part of
either release ZIP.

### Check the installation

Check `mods/autorun/autorun-plugin.log` for `Exact-build input hook installed`.
If it says the game image or ABI is unsupported, leave the mod off and check
for an updated build.

No server installation or save changes are needed. This version moves the
local client at normal forward speed. A dedicated-server test passed without
installing Autorun on the server.

## Change the hotkey

The default toggle is **F8**. Press it once to start and again to stop. **S**
also cancels movement. In the Modloader, open **Autorun → Keyboard shortcuts**
or **Compatibility → Hotkeys**, record another shortcut, then release all keys.
The plugin reads setting changes live and stops movement if a binding changes.

On Linux/Proton with the Modloader window disabled, close the game and edit
`mods/autorun/extended.mod.json`. Change
`settings.toggleAutorun.value` from `"SDL:65"` (F8) to `"SDL:64"` (F7),
`"SDL:63"` (F6), or another supported key. `settings.cancelAutorun.value`
defaults to `"SDL:22"` (S); match it to your backward movement key. Keyboard
modifiers use strings such as `"Ctrl+SDL:64"`. The plugin also supports mouse
buttons 1–5 through `"Mouse:4"` and one keyboard-or-mouse alternative such as
`"SDL:64|Mouse:4"`. An empty string disables a shortcut. Unsupported keys or
malformed settings fail closed and are reported in `autorun-plugin.log`.

The current native plugin recognizes A–Z, 0–9, F1–F12, Enter, Escape,
Backspace, Tab, Space, Insert, Delete, Home, End, Page Up/Down, arrow keys,
and mouse buttons 1–5. It does not consume those keys, so avoid conflicting
game or mod bindings. Version 0.3.2 starts enabled; the
native hook still refuses an unsupported game build or ABI.

## Use and limits

Wait for the world to load in a safe open area, then tap the toggle. Forward
movement uses the game's ordinary input speed and preserves left/right
steering. Backward movement stops it. Losing game focus leaves Autorun on; the
toggle and cancel keys are only read while the game is focused. Turn Autorun
off before switching apps or opening menus. Menu, disconnect, and native
Windows gameplay still need
dedicated checks. Another player was online during a dedicated-server test,
but their view of the movement was not checked. The plugin does
not force sprint or the game's slower Walk action.

Version 0.3.0 revalidates a replacement input source after travel or death.
The same plugin code passed fast-travel and death checks without a world rejoin
in both single-player and a dedicated-server client on Proton; the log recorded
two input replacements in each session. The v0.2.0 ZIP predates this fix.

For a first check, tap F8 and release all movement keys: the character should
continue forward. Tap F8 again to stop. Tap F8 once more and press S to
cancel. If you configured a different toggle key, use that key instead.

## Verified test

With unmodified ShroudForge 1.7.6 and Enshrouded Steam build `26082781`,
single-player and dedicated-server Proton tests used `"SDL:64"` (F7) instead
of the default F8. F7 started normal forward movement, a second F7 stopped
it, and S canceled a later run in both worlds. The game stayed stable. The
loader reported one plugin and no load issues; the plugin log recorded 55
local input writes before toggle-off and 57 before S cancellation on the
dedicated server. This confirms that editing the installed keybind takes
effect on the next launch. A later Proton/Hyprland check installed Microsoft's
WebView2 runtime and enabled the stock Modloader UI. F9 opened the window;
click-to-record changed the toggle to F7 and Mouse X2 (`"SDL:64|Mouse:5"`),
and both bindings worked in game. The cursor was visible and aligned after
applying Wine's `windowmanagerdecorated=n` setting. Native Windows gameplay
remains untested.

A separate clean-install check removed the previous ShroudForge and mod files,
then extracted the stock ShroudForge 1.7.6 ZIP and v0.2.0 Autorun ZIP into the
paths above. After the Linux/Proton and bundled-mod settings above, the game
opened without a WebView2 error. The packaged default F8 binding moved
forward, F8 stopped it, and S canceled it in both single-player and a
dedicated-server world. The game remained stable. The plugin recorded 68
local writes before F8 stopped it and 58 before S canceled it in single-player;
the dedicated-server run recorded 53 and 54. The game executable, both KFC
data files, and both stock ShroudForge runtime DLLs retained their original
hashes.

The bundled `LICENSE` retains ShroudForge's MIT notice for reused hook helpers.
`LICENSE.nlohmann` covers the JSON parser compiled into the plugin.
