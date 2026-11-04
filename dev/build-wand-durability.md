# Build Wand Durability from source

The release ZIP already contains the Windows x64 plugin. These steps are for
developers building from source. Use the repository's Wand Durability Windows
Package workflow, or Visual Studio with CMake on Windows x64. Initialize the
pinned JSON submodule first.

```text
cmake -S mods/wand-durability/native -B build/wand-durability -A x64
cmake --build build/wand-durability --config Release
ctest --test-dir build/wand-durability -C Release --output-on-failure
python dev/build/package_wand_durability.py --dll build/wand-durability/Release/wand-durability.dll --out build/wand-durability-0.2.3.zip
```

On Linux the same CMake project builds the portable policy tests and the hook
byte exporter. Hook helpers are unchanged from the Autorun branch at `b174ac9`.
They originate in ShroudForge under the MIT license. The JSON dependency retains
its separate MIT license.
