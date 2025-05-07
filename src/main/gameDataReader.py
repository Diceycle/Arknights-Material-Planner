import json
from collections import Counter

from utilImport import *
from downloadUtil import Repos, tryDownloadFiles, tryDownloadFile, loadDownloadedJson, getDownloadedFilePath

MATERIAL_LIST_FILE = "materials.json"
OPERATOR_LIST_FILE = "operators.json"

MATERIAL_DATA_FILE = "item_table.json"
RECIPE_DATA_FILE = "building_data.json"
OPERATOR_DATA_FILE = "character_table.json"
ADDITIONAL_OPERATOR_DATA_FILE = "char_patch_table.json"
MODULE_DATA_FILE = "uniequip_table.json"

RAW_MATERIALS = None
RAW_RECIPES = None
RAW_OPERATORS = None
RAW_MODULES = None

def getModuleImagePath(subclassId, moduleType):
    return getDownloadedFilePath(Repos.MODULE_IMAGES, f"{subclassId}-{moduleType}.png")

def getOperatorImagePath(internalId):
    return getDownloadedFilePath(Repos.OPERATOR_IMAGES, internalId + ".png")

def getMaterialImagePath(internalId):
    return getDownloadedFilePath(Repos.MATERIAL_IMAGES, internalId + ".png")

def toModuleUpgradeKey(moduleType, stage):
    return f"MOD-{moduleType.upper()}-{stage}"

def addCosts(cost, upgradeKey, material, quantity):
    up = UPGRADES[upgradeKey]
    if not up in cost:
        cost[up] = {}

    cost[up][material] = quantity

def readOperatorCosts(internalId):
    data = RAW_OPERATORS[internalId]

    costs = {}
    subclassId = None

    tryDownloadFile(Repos.OPERATOR_IMAGES, internalId + ".png", replaceFile=False)

    for i, phase in enumerate(data["phases"]):
        if phase["evolveCost"] is not None:
            eliteKey = "E" + str(i)
            for mat in phase["evolveCost"]:
                addCosts(costs, eliteKey, getMaterialByInternalId(mat["id"]), mat["count"])

            # For some reason, money isn't listed in that table
            if data["rarity"] == "TIER_3":
                addCosts(costs, eliteKey, MATERIALS["money"], 10000)
            elif data["rarity"] == "TIER_4":
                if i == 1:
                    addCosts(costs, eliteKey, MATERIALS["money"], 15000)
                elif i == 2:
                    addCosts(costs, eliteKey, MATERIALS["money"], 60000)
            elif data["rarity"] == "TIER_5":
                if i == 1:
                    addCosts(costs, eliteKey, MATERIALS["money"], 20000)
                elif i == 2:
                    addCosts(costs, eliteKey, MATERIALS["money"], 120000)
            elif data["rarity"] == "TIER_6":
                if i == 1:
                    addCosts(costs, eliteKey, MATERIALS["money"], 30000)
                elif i == 2:
                    addCosts(costs, eliteKey, MATERIALS["money"], 180000)

    for i, skillUpgrade in enumerate(data["allSkillLvlup"]):
        skillKey = "SK" + str(i + 2)
        for mat in skillUpgrade["lvlUpCost"]:
            addCosts(costs, skillKey, getMaterialByInternalId(mat["id"]), mat["count"])

    for i, skill in enumerate(data["skills"]):
        skillKeyPrefix = "S" + str(i + 1)
        for j, mastery in enumerate(skill["levelUpCostCond"]):
            skillKey = skillKeyPrefix + "M" + str(j + 1)
            for mat in mastery["levelUpCost"]:
                addCosts(costs, skillKey, getMaterialByInternalId(mat["id"]), mat["count"])

    if internalId in RAW_MODULES["charEquip"]:
        for assignment in RAW_MODULES["charEquip"][internalId]:
            if not "001" in assignment and not RAW_MODULES["equipDict"][assignment]["isSpecialEquip"]:
                module = RAW_MODULES["equipDict"][assignment]
                subclassId = module["typeName1"]
                moduleType = module["typeName2"]
                imageFileName = module["typeIcon"] + ".png"

                tryDownloadFile(Repos.MODULE_IMAGES, imageFileName, replaceFile=False)

                for stage in module["itemCost"]:
                    moduleKey = toModuleUpgradeKey(moduleType, stage)
                    for mat in module["itemCost"][stage]:
                        addCosts(costs, moduleKey, getMaterialByInternalId(mat["id"]), mat["count"])

    for up in UPGRADES.values():
        if up.cumulativeUpgrades is not None and all(u in costs for u in up.cumulativeUpgrades):
            result = Counter()
            for u in up.cumulativeUpgrades:
                result += Counter(costs[u])
            costs[up] = result

    return costs, subclassId

def readMaterialData(internalId):
    data = RAW_MATERIALS["items"][internalId]
    imageId = data["iconId"]
    tier = int(data["rarity"][-1])

    tryDownloadFile(Repos.MATERIAL_IMAGES, imageId + ".png", replaceFile=False)

    recipe = None
    for formulaReference in data["buildingProductList"]:
        if formulaReference["roomType"] == "WORKSHOP":
            formula = RAW_RECIPES["workshopFormulas"][formulaReference["formulaId"]]
        elif formulaReference["roomType"] == "MANUFACTURE":
            formula = RAW_RECIPES["manufactFormulas"][formulaReference["formulaId"]]
        else:
            continue

        # Exclude Chip crafting recipes since that leads to infinite loops
        if formula["count"] > 1:
            continue

        recipe = {}
        costs = formula["costs"]
        for cost in costs:
            recipe[cost["id"]] = cost["count"]

    return tier, recipe

def downloadMaterialData(progressCallback = None):
    global RAW_MATERIALS
    global RAW_RECIPES

    updates = [
        (Repos.CN, MATERIAL_DATA_FILE),
        (Repos.CN, RECIPE_DATA_FILE),
        (Repos.ENTITIES, MATERIAL_LIST_FILE)
    ]

    tryDownloadFiles(updates, progressCallback)

    RAW_MATERIALS = loadDownloadedJson(Repos.CN, MATERIAL_DATA_FILE)
    RAW_RECIPES = loadDownloadedJson(Repos.CN, RECIPE_DATA_FILE)

def downloadOperatorData(progressCallback = None):
    global RAW_OPERATORS
    global RAW_MODULES

    updates = [
        (Repos.CN, OPERATOR_DATA_FILE),
        (Repos.CN, ADDITIONAL_OPERATOR_DATA_FILE),
        (Repos.CN, MODULE_DATA_FILE),
        (Repos.ENTITIES, OPERATOR_LIST_FILE)
    ]

    tryDownloadFiles(updates, progressCallback)

    RAW_OPERATORS = loadDownloadedJson(Repos.CN, OPERATOR_DATA_FILE)
    RAW_MODULES = loadDownloadedJson(Repos.CN, MODULE_DATA_FILE)

    rawCharacterAdditions = loadDownloadedJson(Repos.CN, ADDITIONAL_OPERATOR_DATA_FILE)
    for k, v in rawCharacterAdditions["patchChars"].items():
        RAW_OPERATORS[k] = v

if __name__ == "__main__":
    knownOperatorIds = [op["internalId"] for op in json.load(open("../../entityLists/operators.json", "r"))]
    downloadOperatorData()
    for operatorId, op in RAW_OPERATORS.items():
        if operatorId.startswith("char") and not op["isNotObtainable"] and not operatorId in knownOperatorIds:
            internalName = None
            if "appellation" in op:
                internalName = op["appellation"]
            print(operatorId, internalName)



