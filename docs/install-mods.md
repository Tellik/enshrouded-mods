# Install ShroudForge and mods for Enshrouded

This guide covers ShroudForge itself and a generic ShroudForge mod. A mod's own
guide decides its required game build, loader version, install targets, and
settings. Use that guide when it gives more specific instructions. Installing
files on a client does not make a server run the mod.

## Before you download

1. Identify the machine that needs the mod: your client for local controls,
   the world host or dedicated server for authoritative gameplay, or both for
   changes to assets that the client displays and the server enforces.
2. Read the mod's supported Enshrouded and ShroudForge versions. Native mods
   may deliberately stay inactive when either version is unsupported. Do not
   assume that the newest loader is compatible with every mod.
3. Download the **named ZIP asset** from the mod's release page and the full
   ShroudForge ZIP specified by its guide. GitHub's “Source code” ZIPs are not
   install packages. If the mod offers separate initial-install and upgrade
   ZIPs, use the initial ZIP for a new installation and follow its guide's
   stated source version before using the upgrade ZIP. If the release provides
   a `.sha256` file, verify the ZIP before installation.

On Linux, put the ZIP and matching `.sha256` file in one folder and run
`sha256sum -c NAME.zip.sha256` there. On Windows, run
`Get-FileHash .\NAME.zip -Algorithm SHA256` in PowerShell and compare its hash
with the `.sha256` file. Replace `NAME` with the actual asset name.

## Install ShroudForge on a Windows client

1. Exit Enshrouded. In Steam, right-click **Enshrouded → Manage → Browse local
   files**. This opens the folder containing `enshrouded.exe`.
2. If ShroudForge is already installed, save
   `shroudforge/config/modloader-config.json` and every changed
   `mods/<mod-id>/extended.mod.json` outside the game folder. The ShroudForge
   ZIP may contain bundled mods and default settings.
3. Open the **full ShroudForge release ZIP** and copy its contents into the
   folder from step 1. The ZIP's top level belongs beside `enshrouded.exe`:
   `dbghelp.dll`, `dinput8.dll`, `winmm.dll`, `shroudforge/`, and `mods/`. Do not
   create an extra `shroudforge-<version>` directory around them.
4. If this was an update, restore your saved loader configuration and changed
   mod configurations. Check the release notes for new settings before
   restoring an older file over a newer default.
5. Start Enshrouded. Press **F9** to open the Modloader. If its window cannot
   start, use [WebView2 troubleshooting](#webview2-window-does-not-open) below.

The [official ShroudForge releases](https://github.com/bonsaibauer/shroudforge/releases)
provide the standard loader. Use the version specified by the mod's guide;
the tested Autorun 0.4.0 client used the
[official stable 1.7.8 ZIP](https://github.com/bonsaibauer/shroudforge/releases/tag/v1.7.8-build.41706360752).

## Install ShroudForge on a Linux/Proton client

Use the same file layout as the Windows client. In Steam's Enshrouded
**Properties → General → Launch Options**, add:

```text
WINEDLLOVERRIDES="dbghelp=n,b;winmm=n,b" %command%
```

This asks Proton to load ShroudForge's local proxy DLLs. Keep the setting when
updating the loader. The in-game Modloader and Debug Console use Microsoft
WebView2; if they fail to open under Proton, install the runtime or disable
those two windows as described below. The loader and mods can still work with
those windows disabled.

## Install ShroudForge on a dedicated server

1. Stop the server through its normal control panel and back up its world.
   Leave restart under the server owner's control.
2. Find the folder containing `enshrouded_server.exe`. Save any changed
   `shroudforge/config/modloader-config.json` and
   `mods/<mod-id>/extended.mod.json` files.
3. Extract the full ShroudForge ZIP into that folder, with its proxy DLLs,
   `shroudforge/`, and `mods/` beside `enshrouded_server.exe`. Restore saved
   settings, then check for new defaults in the release.
4. For a Wine/Proton server, add
   `WINEDLLOVERRIDES=dbghelp=native,builtin;winmm=native,builtin` to the
   existing game-process environment. A native Windows server does not need
   this setting. The server does not need the WebView2 windows.
5. Start the server when you choose. Check ShroudForge and mod logs, then test
   the mod from a connected client. A loaded mod or a changed client display
   alone does not prove that the server accepted the gameplay change.

## Add a generic ShroudForge mod

1. Close the game or stop the server. Read the mod author's guide for its
   targets, supported versions, dependencies, and default enabled state.
2. Treat the folder containing `enshrouded.exe` or `enshrouded_server.exe` as
   `./`. The destination is **`./mods/<mod-id>/mod.json`**, relative to that
   executable. Keep the downloaded ZIP in Downloads. Open it and copy only
   the inner `<mod-id>` folder (the folder containing `mod.json`) into
   `./mods/`. Some archive tools make an extra folder named after the ZIP when
   you choose **Extract Here**. If you see
   `./mods/MOD-VERSION/<mod-id>/mod.json`, move the inner `<mod-id>` folder up
   one level. Do not leave the ZIP or that extra folder in `./mods/`.
   Follow the author's instructions for any files outside the mod folder.
3. If the mod is disabled, enable it in the Modloader or set `"enabled": true`
   in its `extended.mod.json` while the process is stopped. Native DLL mods
   generally need a restart to load. Review hotkeys and any bundled ShroudForge
   mods for conflicts.
4. Check the mod's own log or on-screen behavior. For a server mod, check the
   authoritative server log and perform the author's gameplay check.

### Update a mod without losing settings

`extended.mod.json` contains the enabled state and user settings. Many mod ZIPs
also contain their own default copy, so extracting an update directly over an
installed mod can reset your choices.

**For a release with separate initial and upgrade ZIPs:** the initial ZIP is a
complete mod folder and includes default settings. The upgrade ZIP may contain
only changed files and omit `extended.mod.json`; it must be copied **over an
existing installation of the version named by the author**, never used for a
first install or as a replacement folder. Close the game or stop the server,
back up the existing mod folder, then copy the upgrade ZIP's inner mod folder
over it and allow replacement of the included files. Confirm `mod.json` shows
the new version afterward. Autorun 0.4.0's upgrade ZIP is specifically for
0.3.2 and preserves the existing hotkey and enabled state. If you are on an
older version, use the full initial ZIP with the installer below.

For a **full** one-folder ZIP whose folder name matches the mod ID, use the optional
[configuration-preserving installer](../tools/install_mod.py) from this
repository. Open that link, use GitHub's **Download raw file** action, and
save `install_mod.py` next to the downloaded mod ZIP. Python 3.9 or newer is
required. This installer reads the ZIP directly, so an archive tool cannot
create an extra enclosing folder. It works for first installs and updates.
Do not pass a delta upgrade ZIP to this installer: it replaces the whole mod
folder and therefore needs the full ZIP. The installer rejects Autorun's
marked upgrade ZIP with an explanation.
Run it while the game or server is stopped:

```text
python3 install_mod.py MOD.zip /path/to/folder-containing-enshrouded.exe --dry-run
python3 install_mod.py MOD.zip /path/to/folder-containing-enshrouded.exe
```

On Windows, use the Python launcher in PowerShell, with the actual ZIP and
game-folder paths:

```text
py -3 .\install_mod.py .\MOD.zip "C:\path\to\Enshrouded" --dry-run
py -3 .\install_mod.py .\MOD.zip "C:\path\to\Enshrouded"
```

The tool checks the ZIP and mod identity, refuses a detected running game or
server process, keeps the installed `extended.mod.json` byte for byte, and
saves the previous mod folder
under `shroudforge/backups/manual-mod-installs/`. On a first install it uses the
packaged defaults. It does not stop or restart the game or server. If a new
release adds configuration fields, compare its packaged defaults with your
preserved file before relying on those new options.

To update manually, first copy the installed `extended.mod.json` somewhere
safe. Extract the new mod folder, then restore that saved file into the new
folder **before** starting the game. Keep a copy of the old mod folder for
rollback. If the author changed the configuration format, use the new default
file and transfer your changed values into it instead of blindly restoring the
old file. To remove a mod, stop the process, remove only its own
`mods/<mod-id>/` folder, and follow the author's advice about save effects.

## WebView2 window does not open

ShroudForge's Modloader and Debug Console windows use the Microsoft Edge
WebView2 Runtime. A missing runtime can produce a “WebView2” or “File not
found” error even when the game and mods load. Check `shroudforge/logs/` for
the exact error.

**Install the runtime:** On Windows, download and run Microsoft's official
[WebView2 Evergreen Standalone Installer, x64](https://developer.microsoft.com/en-us/microsoft-edge/webview2/),
then restart the game. On Linux/Proton, download that same x64 installer and
run it **inside Enshrouded's Proton prefix**, not with the host's ordinary
Wine setup. [Protontricks](https://github.com/Matoking/protontricks) can do
that; after installing Protontricks, run:

```text
protontricks-launch --appid 1203620 "$HOME/Downloads/MicrosoftEdgeWebView2RuntimeInstallerX64.exe"
```

Adjust the downloaded file path if necessary. Close Enshrouded before running
the installer, and then try F9 again. If the window opens but its cursor is
missing or clicks are offset under a Wayland compositor such as Hyprland,
this Wine setting fixed the tested setup:

```text
protontricks 1203620 windowmanagerdecorated=n
```

**Run without the windows:** While the game is closed, open
`shroudforge/config/modloader-config.json` and set both
`modules.modloaderUi.enabled` and `modules.debugConsole.enabled` to `false`.
Then edit each mod's `extended.mod.json` directly for its enabled state and
settings. Keep valid JSON and restart the game. F9 and the Debug Console will
not open in this mode, but the loader can still run the mods. A dedicated
server can use this mode without installing WebView2.

If neither path works, confirm the release ZIP was fully extracted, the proxy
DLLs are beside the executable, the Proton launch option is set, and the logs
show whether ShroudForge started at all.
