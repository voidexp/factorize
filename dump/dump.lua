-- https://raw.githubusercontent.com/rxi/json.lua/cc9833592eb4d90cb5beb29982cf5ac9eedff027/json.lua
local json = require("json")

local FACTORIO_PATH = "D:\\Games\\steamapps\\common\\Factorio\\"

local aggregator = {}

data = {}
data["extend"] = function (data, list_of_things)
    for key, thing in ipairs(list_of_things) do
        table.insert(aggregator, thing)
    end
end

files = {
    "ammo",
    "capsule",
    "demo-furnace-recipe",
    "demo-recipe",
    "demo-turret",
    "equipment",
    "fluid-recipe",
    "inserter",
    "module",
    "recipe",
    "turret",
}

for i, f in ipairs(files) do
    dofile(FACTORIO_PATH .. "data\\base\\prototypes\\recipe\\" .. f .. ".lua")
end

local output = io.open("data.json", "w")
output:write(json.encode(aggregator))
output:close()
