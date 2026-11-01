# Autorun v0.3.0 installation guide

Autorun is a **client-only** mod for Enshrouded Steam build `26082781`.
Install it on the PC where you play, whether you use single-player or join a
dedicated server. Do not install it on the server. The mod stays inactive on an
unsupported game executable or ShroudForge ABI.

## Download

- [Autorun v0.3.0 prerelease](https://github.com/Tellik/enshrouded-mods/releases/tag/v0.3.0): download `autorun-0.3.0.zip`.
- If Autorun is your only mod, use the [official ShroudForge 1.7.6 dev ZIP](https://github.com/bonsaibauer/shroudforge/releases/tag/v1.7.6-dev.40026840919), the loader used in the verified Autorun tests.
- If you also use Free Airborne Architect, use its [patched ShroudForge 1.7.7 dev ZIP](https://github.com/Tellik/enshrouded-mods/releases/tag/airborne-architect-free-v0.2.0) on the same client. Autorun 0.3.0 has not had a separate gameplay check with that loader.

Download the named ZIP assets, not GitHub's generated source archives. The
Autorun ZIP does not include ShroudForge.

## Install and enable

Follow the [shared installation guide](https://github.com/Tellik/enshrouded-mods/blob/main/docs/install-mods.md)
for ShroudForge placement, Proton launch options, and updates. Extract the
Autorun ZIP inside the client's `mods` folder. Confirm
`mods/autorun/mod.json` and `mods/autorun/bin/autorun.dll` exist.

The package is **disabled by default**. While the game is closed, set
`"enabled": true` in `mods/autorun/extended.mod.json`, or enable Autorun in
the ShroudForge Modloader and restart the game so its native DLL loads. The
package defaults to **F8** for toggle and **S** for cancel. World Editor also
uses F8; disable World Editor or change Autorun's toggle key. You can edit
`settings.toggleAutorun.value` in `extended.mod.json` while the game is
closed. For example, `"SDL:63"` selects F6. Preserve this file before an
update so your enabled state and custom keybind are not reset.

On Proton, if the Modloader UI cannot start without WebView2, enable Autorun
through `extended.mod.json` while the game is closed. The shared guide gives
the loader settings for running without that UI.

## Check the installation

After launch, `mods/autorun/autorun-plugin.log` should contain
`Exact-build input hook installed`. Press the configured toggle key once to
move forward, again to stop, and press the backward key to cancel. A log
message about an unsupported game image or ABI means the mod stayed inactive.

Single-player and dedicated-server client gameplay were verified with Proton
Experimental and the stock ShroudForge 1.7.6 dev package. Native Windows
and the patched 1.7.7 loader combination still need a separate Autorun
check. For controls, behavior limits, and development details, see the
[detailed mod guide](standalone/autorun/README.md).
