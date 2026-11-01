-- The same asset patch runs during ShroudForge's pregame pass on a client or server.
assert(loader.features.patch, "Free Airborne Architect needs game.assets.write")

local tree_type = assert(game.types.get("keen::SkillTreeResource"),
    "SkillTreeResource is unavailable")
local resources = game.assets.get_resources_by_type(tree_type)
assert(#resources == 1, "Expected exactly one SkillTreeResource")

-- IDs and the original price were checked in the October 20, 2026 client and
-- dedicated-server game assets. The name ID resolves to Airborne Architect in
-- English and Flying Architect in the developer localization.
local skill_id = 1148578013
local skill_name_id = 3936526025
local root_id = 1707226914
local root_name_id = 2259947478
local link_id = 2687780846

local resource = resources[1]
local tree = resource.data
assert(tree and type(tree.nodes) == "table" and type(tree.links) == "table",
    "Unexpected skill-tree layout")

local skill, root
for _, node in ipairs(tree.nodes) do
    if node.id and node.id.value == skill_id then
        assert(not skill, "Duplicate Airborne Architect node")
        skill = node
    elseif node.id and node.id.value == root_id then
        assert(not root, "Duplicate Root node")
        root = node
    end
end
assert(skill and skill.name and skill.name.value == skill_name_id and
    (skill.type == "ActiveSkill" or skill.type == 2) and
    (skill.costs == 3 or skill.costs == 0) and
    type(skill.incomingLinks) == "table", "Airborne Architect asset changed")
assert(root and root.name and root.name.value == root_name_id and
    (root.type == "Root" or root.type == 0) and root.costs == 0 and
    type(root.outgoingLinks) == "table", "Expected free Root node changed")

local edge, reserved_id
for _, link in ipairs(tree.links) do
    if link.id and link.id.value == link_id then
        assert(not reserved_id, "Duplicate link ID")
        reserved_id = link
    end
    if link.sourceNode and link.targetNode and
        link.sourceNode.value == root_id and link.targetNode.value == skill_id then
        assert(not edge, "Duplicate Root-to-Airborne Architect link")
        edge = link
    end
end
assert(not reserved_id or reserved_id == edge, "Reserved link ID is in use")

local function contains_link(list, id)
    local found = false
    for _, ref in ipairs(list) do
        if ref.value == id then
            assert(not found, "Duplicate node link reference")
            found = true
        end
    end
    return found
end

if edge then
    assert(edge.id and edge.isBidirectional == false and
        contains_link(root.outgoingLinks, edge.id.value) and
        contains_link(skill.incomingLinks, edge.id.value),
        "Existing Root-to-Airborne Architect link is inconsistent")
else
    assert(not contains_link(root.outgoingLinks, link_id) and
        not contains_link(skill.incomingLinks, link_id),
        "Reserved link ID is already referenced")
    tree.links[#tree.links + 1] = {
        id = {value = link_id},
        sourceNode = {value = root_id},
        targetNode = {value = skill_id},
        isBidirectional = false,
    }
    root.outgoingLinks[#root.outgoingLinks + 1] = {value = link_id}
    skill.incomingLinks[#skill.incomingLinks + 1] = {value = link_id}
end

skill.costs = 0
resource.data = tree
shroudforge.log.info("Free Airborne Architect: cost 0; free Root link ready")
