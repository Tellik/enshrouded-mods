# Wand Durability v0.2.3

Apply the normal single-shot durability cost once per primary wand attack,
including attacks with built-in Multishot or skill-generated bonus projectiles.
This is normally one durability per attack. The game still controls projectile
count, damage, durability-saving effects, and the world's durability setting.

This experimental native mod requires ShroudForge's **ABI-12 world identity
API**. Its supported executable identities are the original client build
26082781 and dedicated-server build 26083076, plus the exact Hotfix #5
(game version 1287369) client build 26430625 and dedicated-server build
26430253 inspected on 2026-11-04. It stays inactive if the executable or
ShroudForge ABI does not match. ShroudForge 1.7.9 stable exports the required
ABI-12 functions and bundles exact Hotfix #5 client and dedicated-server
runtime profiles. Both packaged profile identities match the inspected
executables above. A selected profile and an authoritative world session are
still required at runtime; package inspection alone does not prove gameplay.

The mod ZIP does not include ShroudForge runtime profiles. Install ShroudForge
1.7.9, which supplies the Hotfix #5 profiles under
`shroudforge/runtime/profiles/enshrouded/`. The earlier 1.7.8 automatic profile
discovery attempt did not produce a usable Hotfix #5 profile.

## Download

- Download the [v0.2.3 release ZIP](https://github.com/Tellik/enshrouded-mods/releases/tag/wand-durability-v0.2.3). Do not use the older [v0.2.2 prerelease](https://github.com/Tellik/enshrouded-mods/releases/tag/wand-durability-v0.2.2) on Hotfix #5; its exact-build guard rejects the new executables.
- [ShroudForge 1.7.9 stable](https://github.com/bonsaibauer/shroudforge/releases/tag/v1.7.9-build.42095151546) provides ABI-12 and the exact Hotfix #5 profiles. Use its release ZIP rather than 1.7.8 for Hotfix #5.

Use the ZIP assets, not GitHub's generated source archives. The Wand Durability
ZIP contains one `wand-durability` folder and no game files or ShroudForge
runtime. Version 0.2.3 defaults to **enabled**; the older v0.2.0 ZIP defaults
to disabled.

## Which machine needs the mod?

| World | Install and enable on | Connecting players |
| --- | --- | --- |
| Single-player | Your local Enshrouded client | None |
| Player-hosted co-op | The host's Enshrouded client | Guests do not need it; hosted co-op gameplay is not yet verified |
| Dedicated server | The dedicated server | No client install needed; tested with and without the client mod |
| A remote world without the mod on its host/server | Install on that host/server to gain the correction | A client-only copy stays inactive and cannot change remote durability |

Use the **same ZIP** for client and server. If you play single-player and also
join a dedicated server, you may leave it installed and enabled on your client:
it works in your local world and automatically stays inactive in the remote
world. If that server has the mod, its installation applies to every player.
No per-player handshake or manual switching is required.

## Install on a client

1. Close Enshrouded. In Steam, choose **Manage → Browse local files** and find
   the folder containing `enshrouded.exe`.
2. Install ShroudForge 1.7.9 into that folder. On Proton, set
   Steam Launch Options to
   `WINEDLLOVERRIDES="dbghelp=n,b;winmm=n,b" %command%`.
3. Treat the folder containing `enshrouded.exe` as `./`. Open
   `wand-durability-0.2.3.zip` and copy its inner `wand-durability/` folder
   into `./mods/`. Check `./mods/wand-durability/mod.json` and
   `./mods/wand-durability/bin/wand-durability.dll`. If your archive tool
   creates `./mods/wand-durability-0.2.3/wand-durability/`, move the inner
   `wand-durability/` folder up one level. Version 0.2.3 starts enabled. If
   updating an existing install, retain your changed `extended.mod.json`.
4. Start the game and perform the [operation check](#check-operation) in a
   single-player world. A local client copy stays inactive in a remote world.

## Install on a dedicated server

1. Stop the server using its control panel and back up its world. Use the
   server's folder containing `enshrouded_server.exe`.
2. Treat the folder containing `enshrouded_server.exe` as `./`. Install the
   ShroudForge 1.7.9 ZIP there and copy the mod ZIP's inner `wand-durability/`
   folder into `./mods/`, yielding `./mods/wand-durability/mod.json`. Avoid
   an extra folder named after the ZIP. For a Wine or
   Proton server, set its game-process environment to
   `WINEDLLOVERRIDES=dbghelp=native,builtin;winmm=native,builtin`.
3. Version 0.2.3 starts enabled. If updating an existing installation, retain
   its changed `extended.mod.json` while the server is stopped. Check bundled
   ShroudForge mods so only intended gameplay changes run.
4. Start the server when you choose. Check the server log as described below,
   then test from a connected client. Guests do not need a client copy.

For full ShroudForge installation steps and WebView2 troubleshooting, see the
[shared guide](https://github.com/Tellik/enshrouded-mods/blob/main/docs/install-mods.md).
Before any update, keep the installed `extended.mod.json`: extracting a ZIP
directly over this mod can reset the enabled state. The shared guide provides
a configuration-preserving installer and manual update steps.

## Check operation

In `mods/wand-durability/wand-durability.log` on the machine that owns the
world, look for `Exact-build client durability hook installed` or
`Exact-build dedicated-server durability hook installed`, followed by a
nonzero `session` and `world_kind=1`. A client connected to a remote world
instead reports `session=0 world_kind=2`; its copy makes no durability changes.
`wand_charges` counts allowed wand charge calls and `bonus_costs_skipped`
counts extra calls suppressed. The original game may still waive a charge for
a durability-saving effect.

Without a saving effect, a Cryptic Wand attack should cost one durability
whether or not Multishot adds a projectile. Bonus projectiles should still
hit and deal damage. Other weapons retain the game's normal behavior. If the
log says the image or ABI is unsupported, check the game and ShroudForge
versions; the mod deliberately leaves costs unchanged on unknown builds.
On Hotfix #5, also check that ShroudForge has a selected runtime profile and
that the mod reports `world_kind=1` with a nonzero session. Loading the DLL
alone is insufficient.

To disable the correction, set `"enabled": false` in the mod's
`extended.mod.json`; it stops applying within one second. To remove the mod,
stop the game or server first and remove `mods/wand-durability`. No permanent
game executable patch or save edit is made.

## Tested behavior and remaining limits

The 0.1.0 client passed a single-player Proton test with the Cryptic Wand's
built-in Multishot +1. Version 0.2.0 passed on a Pterodactyl-hosted Wine
dedicated server: two connected players each observed one durability lost per
Cryptic Wand Multishot attack, including a player without the client mod.
The server's recognized wand counters reached six allowed charges and six
extra costs skipped. The first player's installed client copy reported a
remote world and stayed inactive.

Hotfix #5 single-player Proton gameplay passed with ShroudForge 1.7.9 and the
Cryptic Wand's built-in Multishot +1 on 2026-11-08. ShroudForge selected its
exact client profile, and the mod reported an authoritative world session.
During the test it recorded seven normal charges and ten extra costs skipped;
the player observed one durability lost per attack. The separate dedicated
test server selected its exact Hotfix #5 profile and reported an authoritative
world session. A connected player observed one durability lost per Cryptic Wand
Multishot attack on 2026-11-08. Its server log recorded four normal charges
and six extra costs skipped; the player's client copy reported a remote world
and stayed inactive. Native Windows gameplay, player-hosted co-op, other wands,
skill-generated Multishot, and travel/death or world-rejoin cases remain
unverified.

## Implementation and limits

The current game calls its durability subtraction once for each successful
`SpawnEntityEvent`, outside that event's own projectile-count loop. Wands can
contain multiple such events in one attack. This mod intercepts just that call
site, recognizes nine primary wand sequence IDs from the original `ItemInfo`
resources, and suppresses repeated charges with the same engine attack identity.

The identity includes world session, actor, sequence, trigger time, engine call
index, weapon entity, and resolved durability component. There is no wall-clock
debounce. The first charge uses the original tracked engine operation, and later
charges skip that operation. Unknown sequences (including other weapon types),
unsupported images, unreadable state, and cache contention retain original costs.
Special skill attacks outside these nine primary sequences retain original costs.

The plugin checks the complete executable SHA-256, PE identity, unique instruction
signature, and original bytes before installing its hook. It reads settings and
world identity on a worker thread, not inside the game's callback. The callback
uses a bounded 128-entry journal and never dereferences stored pointers later.
The DLL and tiny hook allocation remain loaded until process exit so disabling
does not leave an executable jump into freed memory.

Source-derived inspection and unit tests cannot establish live gameplay behavior.
The 0.1.0 single-player Proton and two-player 0.2.0 dedicated-server tests
above are the live gameplay validation so far. Native Windows gameplay,
hosted co-op, other wand/skill cases, and lifecycle cases remain unverified.

Completed locally for Hotfix #5: original resource audit (58 wand items, the
same nine primary attack sequences and projectile events, no other weapon
types sharing them), exact client and server image hashes, unique hook
signatures, original-byte and durability-helper checks,
per-attack policy tests, and instruction emulation of both hook branches.
Emulation verifies Windows x64 callback stack alignment, shadow space, flags,
general-purpose registers, and all sixteen XMM registers.
