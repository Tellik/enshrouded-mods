-- Client map-marker registry patch checked on builds 26082781 and 26320373.
-- This does not create teleport events or change the server's travel rules.
assert(loader.features.patch, "Teleportation Expanded needs game.assets.write")

local registry_type = assert(game.types.get("keen::MapMarkerRegistryResource"),
    "MapMarkerRegistryResource is unavailable")
local resources = game.assets.get_resources_by_type(registry_type)
assert(#resources == 1, "Expected one map-marker registry")
local resource = resources[1]
assert(resource.guid == "d165e819-f603-42a3-8f7d-827e9e8cb97a",
    "Map-marker registry identity changed")

local data = resource.data
assert(data and data.mapMarkers and data.mapMarkers.values and
    #data.mapMarkers.values == 49, "Map-marker registry layout changed")

local function setting(key, fallback)
    local value = shroudforge.settings.get(key, fallback)
    assert(type(value) == "boolean", "Expected a boolean setting: " .. key)
    return value
end

local destinations = {
    -- Both Flame Shrines and Flame Sanctums use mapmarker_flame_essence.
    [2068618774] = {
        enabled = setting("flameShrinesAndSanctums", true),
        name = "Flame Shrines and Sanctums",
    },
    -- The game labels the Gem Forge map-marker texture mapmarker_shroudforge.
    [4099254117] = {
        enabled = setting("allowIntoShroud", false) and setting("gemForges", false),
        name = "Gem Forges",
    },
}

local found = {}
for _, marker in ipairs(data.mapMarkers.values) do
    local id = marker.markerId and marker.markerId.value
    local selected = destinations[id]
    if selected then
        assert(not found[id], "Duplicate map-marker type " .. tostring(id))
        assert(marker.isFastTravelDestination == false or marker.isFastTravelDestination == true,
            "Unexpected fast-travel field")
        assert(marker.showAboveFogOfWar == false or marker.showAboveFogOfWar == true,
            "Unexpected fog field")
        found[id] = marker
    end
end
for id in pairs(destinations) do
    assert(found[id], "Missing map-marker type " .. tostring(id))
end

local count = 0
for id, selected in pairs(destinations) do
    local marker = found[id]
    marker.isFastTravelDestination = selected.enabled
    -- The stock type advertises these POIs above the fog. Hide the selected
    -- destinations there so an unrevealed icon cannot become a travel button.
    marker.showAboveFogOfWar = not selected.enabled
    if selected.enabled then count = count + 1 end
end

resource.data = data
shroudforge.log.info("Teleportation Expanded: enabled " .. count ..
    " additional map-marker categories")
