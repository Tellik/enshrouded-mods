# Free Airborne Architect 0.1.1

This ShroudForge mod makes **Airborne Architect** cost **0 skill points**. It
also adds a direct link from the nearest free Root node so the skill is
reachable without buying a path through the tree. No other skill is changed.

The mod uses ShroudForge's pregame asset patch. The same folder targets client
and dedicated server. It was checked against Enshrouded client build
**26082781**, dedicated-server build **26083076**, and a locally patched
ShroudForge **1.7.7 dev (40603042431)**. On Linux/Proton, stock ShroudForge
1.7.6 and 1.7.7 dev report `Access denied (os error 5)` when committing the
changed asset, leaving the skill at 3 points. The patched loader closes its
game asset reader before committing. Native Windows gameplay remains untested.
On a different game build, the patch refuses to change the tree if the expected
node or its original cost has changed.

## Install

1. Close the client or stop the dedicated server using its normal controls.
2. On Linux/Proton, install the patched ShroudForge 1.7.7 dev package from this
   project's `releases` folder. Preserve your existing mod settings when
   updating. On native Windows, the stock 1.7.7 dev loader has not been tested
   with this mod.
3. Copy the `airborne-architect-free` folder into that installation's `mods`
   folder. The script must be at
   `mods/airborne-architect-free/src/mod.lua`.
4. The mod is enabled by default. Start the client or server normally.

For single-player, install it on the client; unlocking at zero points has been
verified there. For a dedicated-server world, install it on the server **and
each client that should see the zero-point price and Root link in its Skills
screen**. Client and server each load their own skill-tree asset. With only the
client modded, the UI shows zero points but clicking the skill leaves it locked
on an unmodded dedicated server. A server installation alone has not been shown
to update an unmodded client's UI. With both sides modded, unlocking, refunding,
and unlocking again worked on a private dedicated test server. Hosted co-op
needs a separate host-and-guest check.

On Linux/Proton, ShroudForge's DLLs may need the Steam launch option:

```text
WINEDLLOVERRIDES="dbghelp=n,b;winmm=n,b" %command%
```

## Check

In the ShroudForge log, find `Free Airborne Architect: cost 0; free Root link
ready`. Then open Skills (H): Airborne Architect should show **0** points,
be reachable from a Root node, and unlock without reducing the available
points. For a dedicated server, check the same result with a connected client
and confirm it remains after reconnecting. The private dedicated-server test
verified unlock, refund, and repeat unlock; reconnect persistence and the exact
skill-point count after each action were not recorded.

To disable, set `"enabled": false` in `extended.mod.json` and restart the
process. To remove it, close the game or stop the server and delete the mod
folder. Existing unlocked skills and character saves are not edited by this
mod; the game controls the result of a later respec.

## Implementation

The script checks the skill node ID, English localization ID, original cost,
Root node, and proposed link ID before writing. It adds one directed link to
the skill-tree link list and the two nodes' link references, then changes only
the skill's `costs` field. Re-running the patch is idempotent. The source is an
independent implementation of the behavior described on the [Zero Cost Build
Camera Nexus page](https://www.nexusmods.com/enshrouded/mods/177); it does not
include any files or assets from that mod.

Version 0.1.1 fixes startup failure on ShroudForge's userdata-backed game
arrays. Version 0.1.0 did not apply the patch. The loader commit fix is separate
from the mod and must be present for the patch to persist under Proton.
