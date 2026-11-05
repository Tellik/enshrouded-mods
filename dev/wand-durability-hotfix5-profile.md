# Wand Durability Hotfix #5 test profile (2026-11-04)

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
