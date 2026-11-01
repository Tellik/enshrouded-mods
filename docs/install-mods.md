# Install a mod from this repository

Each mod's README names the **supported game build**, required **ShroudForge
version**, download ZIP, and which machines must run it. Read that page first:
the machine that handles a gameplay action may differ from the one showing
the interface. A client copy alone may display a change that a server rejects.

## Download

1. Open the release linked by the mod's README. Download the ZIP asset named
   for that mod. GitHub's automatically generated source archives are not
   install packages. A `.sha256` asset is an optional checksum.
2. Download the ShroudForge ZIP version linked by that README. Some mods need
   a patched ShroudForge build; use the exact package they specify. A mod ZIP
   does not include ShroudForge unless its README explicitly says so.

## Install on a Windows client or Linux/Proton client

1. Close Enshrouded. In Steam, choose **Manage → Browse local files** to open
   the folder containing `enshrouded.exe`.
2. Back up `mods/*/extended.mod.json` files whose settings you have changed.
   Extract the full ShroudForge ZIP into the game folder. Its DLLs, `shroudforge`
   folder, and `mods` folder belong beside `enshrouded.exe`.
3. Extract the mod ZIP inside the game's `mods` folder. The result should be
   `mods/<mod-id>/mod.json`, with no extra enclosing folder and no ZIP left in
   `mods`. Restore your saved settings if the package replaced them. Check the
   mod README for its default enabled state and any required settings.
4. On Linux/Proton, set these Steam **Launch Options** so the game loads the
   local ShroudForge DLLs:

   ```text
   WINEDLLOVERRIDES="dbghelp=n,b;winmm=n,b" %command%
   ```

5. Start the game. On Windows, the ShroudForge Modloader usually opens with
   **F9**. If you change a native mod's enabled state, restart the game. On
   Proton, if the UI cannot start without WebView2, edit the mod's
   `extended.mod.json` while the game is closed. You can disable the UI and
   debug console in `shroudforge/config/modloader-config.json` by setting
   `modules.modloaderUi.enabled` and `modules.debugConsole.enabled` to `false`.

## Install on a dedicated server

1. Follow the mod README to determine whether the server needs the mod and
   whether connecting clients need it too. Stop the server using its normal
   control panel and back up its world before changing files.
2. In the server folder containing `enshrouded_server.exe`, save any changed
   `mods/*/extended.mod.json` files. Extract the specified ShroudForge ZIP
   there, then extract the mod ZIP inside `mods`. Confirm
   `mods/<mod-id>/mod.json` exists and restore any settings you saved.
3. Enable the mod according to its README. Review bundled ShroudForge mods and
   disable gameplay features you do not intend to run.
4. For a Wine/Proton server, ensure its game process uses
   `WINEDLLOVERRIDES=dbghelp=native,builtin;winmm=native,builtin`. Set this in
   the server's existing launch configuration. Native Windows servers do not
   need that override.
5. Start the server and check the loader and mod logs for a successful load.
   Perform the gameplay check described by the mod README from a connected
   client. For an asset patch, confirm the server committed the changed asset
   before relying on what the client interface displays.

## Update or remove

Close the client or stop the server before replacing files. Save changed mod
settings, install the new ZIPs, then restore settings and restart. Keep client
and server versions aligned where the mod README requires both. To remove a
mod, stop the relevant process, delete only its `mods/<mod-id>` folder, and
restart. The mod README describes any save or gameplay effects of removal.
