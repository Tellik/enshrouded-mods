# Wand Durability Hotfix #5 test profile (2026-11-04)

## Superseded by ShroudForge 1.7.9 (2026-11-08)

The official [ShroudForge 1.7.9 release](https://github.com/bonsaibauer/shroudforge/releases/tag/v1.7.9-build.42095151546)
includes `enshrouded/client/26430625.json` and
`enshrouded/server/26430253.json` as read-validated runtime profiles. The
release ZIP was checksum-verified, and its profile SHA-256, image size, and PE
timestamp match the exact Hotfix #5 client and dedicated-server executables
used by Wand Durability 0.2.3. The native runtime retains ABI 12 and the world
context/session exports required by the mod. The 1.7.8 discovery and manual
review below are historical; do not install those draft profiles. Live profile
selection and wand gameplay were subsequently checked on 2026-11-08. The
local Proton client selected `enshrouded-client-26430625`, reported session 5
with `world_kind=1`, and a Cryptic Wand test showed one durability per attack.
Its mod log recorded seven normal charges and ten extra costs skipped. The
separate dedicated test server selected `enshrouded-server-26430253` and
reported session 5 with `world_kind=1`. On 2026-11-08, a connected player
observed one durability per Cryptic Wand Multishot attack. The server log
recorded four normal charges and six extra costs skipped; the local client
reported `world_kind=2` and stayed inactive.

This is offline evidence for the v0.2.3 test build, not a gameplay result.
The original client executable came from the installed Steam build 26430625.
The original dedicated-server executable and KFC files were copied read-only
from the Pterodactyl server while it remained running. Both KFC sets identify
game version 1287369 (Hotfix #5).

| Target | SHA-256 | PE timestamp | Image size | Hook RVA | Skip RVA |
| --- | --- | ---: | ---: | ---: | ---: |
| `enshrouded.exe` | `5d9ef2f140b8ed49e30dbee655841b89d08baec20f799a1817e171a18a850c77` | 1793791052 | 44298240 | `0x229210` | `0x229221` |
| `enshrouded_server.exe` | `f0d824be7fcd48ebfe2458ff5c28da26060c2074e3ec1fcac587e5a1d508aeb2` | 1793791038 | 31318016 | `0x465d0` | `0x465e1` |

The exact 20-byte hook signatures are unique in each executable:

```text
client: 41 B8 FF FF FF FF 48 8B CB 44 8B 08 E8 4F CB 18 00 48 8D 3D
server: 41 B8 FF FF FF FF 48 8B CB 44 8B 08 E8 BF A3 11 00 48 8D 3D
```

Both still displace `mov r8d, -1` before the same tracked durability helper
call. The helper begins at client RVA `0x3b5d70` and server RVA `0x1609a0`.
The surrounding binding retains the actor pointer at `[rbp+0x390]`, resolved
durability component in `rbx`, actor entity at `[rax]`, and the same per-event
loop and skip boundary as the previously gameplay-tested server build. The
helper's leading control flow and arguments match between the new targets.
These checks support the hook site and callback layout, but cannot prove the
gameplay outcome.

Original `ItemInfo` and `ActorSequenceResource` exports were read from both
Hotfix #5 KFC sets. Each contains 58 wand items referring to the same nine
primary attack sequence IDs as the previous mod. No other weapon type uses
those nine sequences. Client and server wand sequence references and projectile
event values match; their full `ItemInfo` values differ in `equipment` and
`impactValues`, which the mod does not use.

The installed official ShroudForge 1.7.8 stable `kfc-runtime.dll` matches the
release ZIP and exports `KfcRuntimeAbi`, `KfcRuntimeWorldSessionId`, and
`KfcRuntimeWorldContextKind`. Its ABI is 12 in the runtime log. The release
catalog stops at client build 26404966 and server build 26404334. A working
exact or proven beta runtime profile and live wand gameplay verification remain
required. The dedicated server was still using ShroudForge 1.7.7 at this
inspection and was not changed.

The older exact client executable and its 26082781 runtime capture were
available for an offline manual rebase attempt. ShroudForge's development tool
produced a candidate for build 26430625 but reported 171 unresolved target
checks, including owner, ECS read, resource, and authority/lifetime checks.
It explicitly did not transfer profile approval or verify semantics. This
candidate is held outside the production catalog and is not bundled with the
mod.

The exact Hotfix #4 client executable was subsequently recovered from a local
test copy: SHA-256
`ce6fdba63e27744943b695921383a29133285d359e07671f6ca33a47e2147618`
for build 26404966. The matching Hotfix #4 dedicated-server executable was
downloaded privately from Steam depot 2278521, manifest
`7782830484557676320`, selecting only `enshrouded_server.exe`: SHA-256
`c5c9fe50c6398d2adedd98923c2d04bf9d9b4af64c1447ac167cdf8f874ff84f`
for build 26404334. These game files are kept out of the repository and mod
package.

The client baseline was seeded into ShroudForge 1.7.8's local discovery cache,
then Enshrouded was launched to the main menu. Discovery accepted the exact
baseline but reported `image-equivalence-not-established`; the mapped PE
headers changed and its rebase could establish only 120 fields. Another 42
fields remain unresolved: 20 resource, 12 ECS write, three ECS read, three
system dependency, two resource write, one building-prop spawn, and one
service field. ShroudForge wrote a `.v2.unresolved.json` evidence report, did
not publish a beta profile, and reported `execution_profile=missing-or-ambiguous-profile`.
This is a runtime loader result, not a wand gameplay test. The dedicated-server
baseline is ready for a separate offline analysis, but no server profile has
been produced or installed. The running Pterodactyl instance was not altered.

Further offline review used exact Hotfix #4 and #5 client captures. A review
candidate outside the installed profile catalog applies only the 120 fields
proved by the native comparison; nine proved RVAs moved by `0xe0`. All 42
unresolved numeric values happen to equal their Hotfix #4 values, but value
equality alone is not layout proof. Eleven of those gaps now have separate
static evidence: eight ResourceService map offsets, strides, and the 24-byte
resource-key extent are used by a byte-identical 349-byte lookup helper reached
from the paired resource-ID callbacks; the map key count is read by a paired
original validator, and the chunk-table offset by the paired handle callbacks.
The original active-Scene iterator independently
confirms the 144-byte entry stride while reading the same entry-array, count,
UUID, and ready-state fields in both client builds. Eleven of the automatic gaps
therefore have separate static field evidence.
These checks do not read live game ownership or complete profile approval.

For the 15 unresolved code-contract checks, the captured witness graph contains
201 distinct old/new procedure pairs. A separate normalized-code comparison
matches 199 pairs, misses one capture pair, and finds one different normalized
body. These are triage results, not proof of call targets or ownership. Exact
Hotfix #4 and #5 server captures also retain all 11,184 reflected types and
their layouts; 17,536 static procedure anchors match reciprocally. No
version-matched Hotfix #4 server KFC was used in those captures, and no server
runtime profile was produced. The local review artifacts remain outside the
mod package and the installed ShroudForge profile catalog.

ShroudForge 1.7.8 selects execution and resource/read-owner profiles
separately. Wand Durability uses its world-kind and world-session APIs, which
can work without the legacy execution profile if the exact resource/read-owner
profile configures ECS ownership. That selection is still blocked: the
installed catalog has no Hotfix #5 read profile. A separate, intentionally
unloadable review draft retains only the client read sections. Removing optional
write, service, dependency, item-ID map, and entity-definition UUID contracts
reduces the relevant automatic field gaps from 42 to 16. Eleven have the static
evidence above; entity generation, three ItemRegistry pointer offsets, and the
ResourceService value count still need targeted proof. The server has an
additional original registered-Scene and thread-registry requirement. No
review draft has been marked read-validated or installed.

The full server rebase tool refused the offline captures because the exact
Hotfix #4 server KFC is missing. A filtered attempt to obtain that one file
from the historical Steam depot stopped at authentication; the earlier QR
session was not cached. The running dedicated server remains untouched.
