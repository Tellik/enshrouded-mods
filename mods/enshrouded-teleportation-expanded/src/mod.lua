-- Category-controlled map travel for Enshrouded build 26404966.
-- Client and dedicated-server map labels must use the same marker types.
assert(loader.features.patch, "Teleportation Expanded needs game.assets.write")
assert(type(loader.is_server) == "boolean", "Unknown game target")
local is_server = loader.is_server
local catalog = require("locations")
assert(catalog.build == 26404966, "Unexpected Teleportation Expanded catalog")

local function setting(key, fallback)
    local value = shroudforge.settings.get(key, fallback)
    assert(type(value) == "boolean", "Expected a boolean setting: " .. key)
    return value
end

local allow_into_shroud = setting("allowIntoShroud", false)
local category_enabled = {}
local category_count = 0
for key, category in pairs(catalog.categories) do
    category_enabled[key] = setting(key, category.default)
    category_count = category_count + 1
end
assert(category_count == 16, "POI category catalog changed")
local registry, markers, marker_map, filterable_count
if not is_server then
    local registry_type = assert(game.types.get("keen::MapMarkerRegistryResource"))
    local registries = game.assets.get_resources_by_type(registry_type)
    assert(#registries == 1, "Expected one map-marker registry")
    registry = registries[1]
    assert(registry.guid == "d165e819-f603-42a3-8f7d-827e9e8cb97a",
        "Map-marker registry identity changed")
    markers = registry.data
    marker_map = markers.mapMarkers
    assert(marker_map and #marker_map.entries == 64 and
        #marker_map.keys == 49 and #marker_map.values == 49,
        "Map-marker registry layout changed")
    filterable_count = 0
    for _, marker in ipairs(marker_map.values) do
        if marker.canBeFiltered then filterable_count = filterable_count + 1 end
    end
    assert(filterable_count == 36, "Map-marker filter capacity changed")
end

-- The registry is a 64-bucket keyed map. Keys, values, and bucket offsets
-- must all be updated together so the game can find the new marker types.
local function check_marker_map()
    local expected = 0
    for bucket, entry in ipairs(marker_map.entries) do
        assert(entry.start == expected, "Map-marker bucket offset changed")
        for i = entry.start + 1, entry.start + entry.count do
            local id = marker_map.keys[i].value
            assert(id == marker_map.values[i].markerId.value,
                "Map-marker key/value mismatch")
            assert(id % #marker_map.entries == bucket - 1,
                "Map-marker hash bucket changed")
        end
        expected = expected + entry.count
    end
    assert(expected == #marker_map.values, "Map-marker count mismatch")
end
if not is_server then check_marker_map() end

local scene_type = assert(game.types.get("keen::SceneEntityChunkResource"))
local scene = assert(game.assets.get_resource("509feadb-4c60-425f-9c7c-deeefd9b6920", scene_type, 1600),
    "Map-label scene chunk missing")
local chunk = scene.data
assert(#chunk.entities == 1300 and #chunk.templates == (is_server and 617 or 618) and
    #chunk.templatesDoNotSave == 10,
    "Map-label scene layout changed; catalog needs regeneration")

local collection_type = assert(game.types.get("keen::ecs::TemplateCollectionResource"))
local collections = game.assets.get_resources_by_type(collection_type)
assert(#collections == 1 and collections[1].guid == "377f61dc-c7b8-4e4f-830f-7d2c3e8b7fd8",
    "Template collection identity changed")
local collection = collections[1]
local all_templates = collection.data
assert(#all_templates.templates == (is_server and 12267 or 12269),
    "Template collection layout changed")

local template_type = assert(game.types.get("keen::ecs::TemplateResource"))
local enabled = {}
local seen_entities = {}
for _, location in ipairs(catalog.locations) do
    assert(not seen_entities[location.entity], "Duplicate catalog scene entity")
    seen_entities[location.entity] = true
    local entity = chunk.entities[location.entity + 1]
    assert(entity and chunk.templates[entity.templateIndex + 1] == location.template and
        entity.transform.positionX1 == location.x and
        entity.transform.positionY1 == location.y and
        entity.transform.positionZ1 == location.z,
        "Map-label scene changed at " .. location.key)
    local category = assert(catalog.categories[location.category],
        "Unknown POI category: " .. location.key)
    assert(type(location.inShroud) == "boolean", "Missing Shroud classification: " .. location.key)
    if category_enabled[location.category] and
        (allow_into_shroud or not location.inShroud) then
        local source = assert(game.assets.get_resource(location.template, template_type),
            "POI template missing: " .. location.key)
        local source_marker = false
        for _, component in ipairs(source.data.components) do
            if component.type == "keen::ecs::MapMarker" then
                assert(component.value.markerType == location.markerType,
                    "POI marker type changed: " .. location.key)
                source_marker = true
            end
        end
        assert(source_marker, "POI marker missing: " .. location.key)
        table.insert(enabled, { location = location, source = source })
    end
end
assert(#catalog.locations == 505, "Location catalog count changed")

local created_types = {}
local function create_travel_marker(source_type)
    if is_server then return end
    if created_types[source_type] then return end
    local info = assert(catalog.markerTypes[source_type], "Unknown source marker type")
    local source_marker, source_key
    for i, key in ipairs(marker_map.keys) do
        if key.value == info.sourceId then
            source_marker = marker_map.values[i]
            source_key = key
            break
        end
    end
    assert(source_marker and source_marker.isFastTravelDestination == false and
        source_marker.showAboveFogOfWar == true,
        "Source marker type changed")
    local bucket = info.travelId % #marker_map.entries + 1
    local entry = marker_map.entries[bucket]
    local position = entry.start + entry.count + 1
    table.insert(marker_map.keys, position, source_key)
    marker_map.keys[position].value = info.travelId
    table.insert(marker_map.values, position, source_marker)
    local travel_marker = marker_map.values[position]
    travel_marker.markerId.value = info.travelId
    travel_marker.isFastTravelDestination = true
    travel_marker.showAboveFogOfWar = false
    -- The game has a 40-entry SmallDynamicArray for filterable marker types.
    -- Its 36 original types leave room for only four; travel clones stay out.
    travel_marker.canBeFiltered = false
    entry.count = entry.count + 1
    for i = bucket + 1, #marker_map.entries do
        marker_map.entries[i].start = marker_map.entries[i].start + 1
    end
    created_types[source_type] = true
end

for _, item in ipairs(enabled) do
    local location = item.location
    create_travel_marker(location.markerType)
    local info = catalog.markerTypes[location.markerType]
    local clone = game.assets.create_resource(item.source.data, template_type, location.clone, 0)
    local cloned = clone.data
    cloned.name = "ETE_" .. location.key
    local found = false
    for _, component in ipairs(cloned.components) do
        if component.type == "keen::ecs::MapMarker" then
            assert(component.value.markerType == location.markerType)
            component.value.markerType = info.clone
            found = true
        end
    end
    assert(found, "Cloned POI marker missing")
    clone.data = cloned

    local position = 1
    while position <= #all_templates.templates and
        all_templates.templates[position] < location.clone do
        position = position + 1
    end
    assert(all_templates.templates[position] ~= location.clone,
        "Cloned POI template already exists")
    table.insert(all_templates.templates, position, location.clone)

    local entity = chunk.entities[location.entity + 1]
    entity.templateIndex = #chunk.templates
    table.insert(chunk.templates, location.clone)
end

if #enabled > 0 then
    if not is_server then
        check_marker_map()
        local final_filterable_count = 0
        for _, marker in ipairs(marker_map.values) do
            if marker.canBeFiltered then
                final_filterable_count = final_filterable_count + 1
            end
        end
        assert(final_filterable_count == filterable_count,
            "Travel markers exceeded the game's map-filter capacity")
        registry.data = markers
    end
    while #chunk.templatesDoNotSave < math.ceil(#chunk.templates / 64) do
        table.insert(chunk.templatesDoNotSave, 0)
    end
    collection.data = all_templates
    scene.data = chunk
end
shroudforge.log.info("Teleportation Expanded: enabled " .. #enabled ..
    " POIs across " .. #catalog.locations .. " eligible locations on " ..
    (is_server and "server" or "client"))
