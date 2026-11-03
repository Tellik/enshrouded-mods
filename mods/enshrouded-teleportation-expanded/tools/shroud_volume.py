"""Read the gameplay Shroud volume from the current client's exported fog tiles.

The model has 16-voxel tiles. Each tile is a 16x16x16 BC5 texture; the first
BC4 channel holds gameplay fog coverage. The second channel is not used here.
This is a conservative build-specific asset check, not a live engine query.
"""

import json
import math
from pathlib import Path

WORLD = "509feadb-4c60-425f-9c7c-deeefd9b6920"
ACTIVE_PARTS = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 15}


class ShroudVolume:
    def __init__(self, model_path: Path, content_dir: Path):
        model = json.loads(model_path.read_text())
        self.parts = {}
        for entry in model:
            if entry["guid"] != WORLD or entry["part"] not in ACTIVE_PARTS:
                continue
            part = entry["part"]
            value = entry["value"]
            tile_count = value["tileCount"]
            size = value["sizeInTiles"]
            assert tile_count > 0
            assert len(value["tileIndirectionData"]) == size["x"] * size["y"] * size["z"]
            data = (content_dir / f"fog-part-{part}.bin").read_bytes()
            assert len(data) == tile_count * 4096
            self.parts[part] = (value, data)
        assert set(self.parts) == ACTIVE_PARTS, "Expected all gameplay Shroud layers"

    @staticmethod
    def _bc4_value(block: bytes, pixel: int) -> int:
        low, high = block[:2]
        index = (int.from_bytes(block[2:8], "little") >> (pixel * 3)) & 7
        if index == 0:
            return low
        if index == 1:
            return high
        if low > high:
            return ((8 - index) * low + (index - 1) * high) // 7
        if index < 6:
            return ((6 - index) * low + (index - 1) * high) // 5
        return 0 if index == 6 else 255

    @staticmethod
    def _sample_part(value, data, position):
        origin = value["originInVoxels"]
        size = value["sizeInTiles"]
        voxel = {axis: math.floor(position[axis] / 16) - origin[axis] for axis in "xyz"}
        tile = {axis: voxel[axis] // 16 for axis in "xyz"}
        if any(tile[axis] < 0 or tile[axis] >= size[axis] for axis in "xyz"):
            return 0
        index = (tile["z"] * size["y"] + tile["y"]) * size["x"] + tile["x"]
        indirect = value["tileIndirectionData"][index]
        if indirect == 0:
            return 0
        if indirect < 32768:
            return 255  # Uniform occupied tile; fail closed for other sentinels.
        tile_index = indirect - 32768
        assert tile_index < value["tileCount"]
        local = {axis: voxel[axis] % 16 for axis in "xyz"}
        block = (local["z"] * 4 + local["y"] // 4) * 4 + local["x"] // 4
        pixel = (local["y"] % 4) * 4 + local["x"] % 4
        offset = tile_index * 4096 + block * 16
        return ShroudVolume._bc4_value(data[offset:offset + 8], pixel)

    def coverage(self, x, y, z):
        position = {"x": x, "y": y, "z": z}
        return max(self._sample_part(value, data, position)
                   for value, data in self.parts.values())

    def near_shroud(self, x, y, z):
        # Allow one voxel of landing uncertainty on each axis. Any covered
        # sample blocks travel while the Shroud switch is off.
        return any(self.coverage(x + dx, y + dy, z + dz) > 0
                   for dx in (-16, 0, 16)
                   for dy in (-16, 0, 16)
                   for dz in (-16, 0, 16))
