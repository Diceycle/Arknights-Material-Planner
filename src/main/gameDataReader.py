import json
import datetime
import os.path
import urllib.error
import urllib.request
import urllib.parse

from utilImport import *

MATERIAL_IMAGE_PATH = "data/materialImages/"
OPERATOR_IMAGE_PATH = "data/operatorImages/"
MODULE_IMAGE_PATH = "data/moduleTypeImages/"

DOWNLOAD_METADATA_FILE = "data/downloadMetadata.json"
DOWNLOAD_METADATA = None

ENTITY_LIST_REPOSITORY = CONFIG.entityListRepository
ENTITY_LIST_REPOSITORY_FOLDER = "entityLists/"
MATERIAL_LIST_FILE = "materials.json"
OPERATOR_LIST_FILE = "operators.json"

DATA_REPOSITORY = CONFIG.dataRepository
DATA_REPOSITORY_FOLDER = CONFIG.dataRepositoryGameDataPath
MATERIAL_DATA_FILE = "item_table.json"
RECIPE_DATA_FILE = "building_data.json"
OPERATOR_DATA_FILE = "character_table.json"
ADDITIONAL_OPERATOR_DATA_FILE = "char_patch_table.json"
MODULE_DATA_FILE = "uniequip_table.json"

IMAGE_REPOSITORY_BASE_URL = CONFIG.imageRepositoryBaseUrl
MATERIAL_IMAGE_SUB_URL = "items/"
OPERATOR_IMAGE_SUB_URL = "avatars/"
MODULE_IMAGE_SUB_URL = "equip/type/"

userAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': userAgent, }

RAW_MATERIALS = None
RAW_RECIPES = None
RAW_OPERATORS = None
RAW_MODULES = None

LAST_COMMIT_TIMESTAMPS = {}

def getRequest(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, None, headers))
    except urllib.error.HTTPError as response:
        LOGGER.error("Error(%s) reading url: %s", response.code, url)
        for line in response.readlines()[:10]:
            line = line.decode("utf-8")
            LOGGER.debug(line.replace("\n", ""))

def getMostRecentCommitTimestamp(repo, remotePath=None):
    url = f"https://api.github.com/repos/{repo}/commits"
    if remotePath is not None:
        url += "?path=" + remotePath

    response = json.loads(getRequest(url).read())
    return datetime.datetime.fromisoformat(response[0]["commit"]["author"]["date"]).timestamp()

def tryDownloadNewerFileFromGithub(repo, remotePath, localPath):
    global DOWNLOAD_METADATA

    if not repo in LAST_COMMIT_TIMESTAMPS:
        LAST_COMMIT_TIMESTAMPS[repo] = getMostRecentCommitTimestamp(repo)

    fullUrl = f"https://raw.githubusercontent.com/{repo}/HEAD/{remotePath}"
    if not os.path.exists(localPath) or not localPath in DOWNLOAD_METADATA:
        downloadFileFromWeb(fullUrl, localPath, replace=True)
    else:
        lastDownloadAttempt = DOWNLOAD_METADATA[localPath]
        if lastDownloadAttempt < LAST_COMMIT_TIMESTAMPS[repo]:
            remoteTimestamp = getMostRecentCommitTimestamp(repo, remotePath)
            if lastDownloadAttempt < remoteTimestamp:
                downloadFileFromWeb(fullUrl, localPath, replace=True)

    DOWNLOAD_METADATA[localPath] = LAST_COMMIT_TIMESTAMPS[repo]
    writeDownloadMetadata(DOWNLOAD_METADATA)

def downloadFileFromWeb(url, localPath, replace=False):
    if replace or not os.path.exists(localPath):
        LOGGER.debug("Updating from Web: %s", localPath)
        file = getRequest(url).read()
        if file is not None:
            f = safeOpen(localPath, mode="wb+")
            f.write(file)
            f.close()

def writeDownloadMetadata(metadata):
    f = safeOpen(DOWNLOAD_METADATA_FILE, "w+")
    json.dump(metadata, f, indent=4)
    f.close()

def getModuleImagePath(subclassId, moduleType):
    return MODULE_IMAGE_PATH + f"{subclassId}-{moduleType}.png"

def getOperatorImagePath(internalId):
    return OPERATOR_IMAGE_PATH + internalId + ".png"

def getMaterialImagePath(internalId):
    return MATERIAL_IMAGE_PATH + internalId + ".png"

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

    downloadFileFromWeb(IMAGE_REPOSITORY_BASE_URL + OPERATOR_IMAGE_SUB_URL + internalId + ".png", getOperatorImagePath(internalId))

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
            if not "001" in assignment and not RAW_MODULES["equipDict"][assignment]["typeName1"].lower() == "ISW".lower():
                module = RAW_MODULES["equipDict"][assignment]
                subclassId = module["typeName1"]
                moduleType = module["typeName2"]
                imageFileName = module["typeIcon"] + ".png"

                downloadFileFromWeb(IMAGE_REPOSITORY_BASE_URL + MODULE_IMAGE_SUB_URL + imageFileName.lower(), getModuleImagePath(subclassId, moduleType))

                for stage in module["itemCost"]:
                    moduleKey = toModuleUpgradeKey(moduleType, stage)
                    for mat in module["itemCost"][stage]:
                        addCosts(costs, moduleKey, getMaterialByInternalId(mat["id"]), mat["count"])

    return costs, subclassId

def readMaterialData(internalId):
    data = RAW_MATERIALS["items"][internalId]
    imageId = data["iconId"]
    tier = int(data["rarity"][-1])

    downloadFileFromWeb(IMAGE_REPOSITORY_BASE_URL + MATERIAL_IMAGE_SUB_URL + imageId + ".png", getMaterialImagePath(internalId))

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

def downloadGamedata(progressCallback = None):
    global RAW_MATERIALS
    global RAW_RECIPES
    global RAW_OPERATORS
    global RAW_MODULES

    files = [MATERIAL_DATA_FILE, RECIPE_DATA_FILE, OPERATOR_DATA_FILE, ADDITIONAL_OPERATOR_DATA_FILE, MODULE_DATA_FILE]
    for i, f in enumerate(files):
        if progressCallback is not None:
            progressCallback(i, len(files))
        tryDownloadNewerFileFromGithub(DATA_REPOSITORY, DATA_REPOSITORY_FOLDER + f, "data/" + f)

    RAW_MATERIALS = json.load(open("data/" + MATERIAL_DATA_FILE, "r", encoding="utf-8"))
    RAW_RECIPES = json.load(open("data/" + RECIPE_DATA_FILE, "r", encoding="utf-8"))
    RAW_OPERATORS = json.load(open("data/" + OPERATOR_DATA_FILE, "r", encoding="utf-8"))
    RAW_MODULES = json.load(open("data/" + MODULE_DATA_FILE, "r", encoding="utf-8"))

    rawCharacterAdditions = json.load(open("data/" + ADDITIONAL_OPERATOR_DATA_FILE, "r", encoding="utf-8"))
    for k, v in rawCharacterAdditions["patchChars"].items():
        RAW_OPERATORS[k] = v

def downloadEntityLists(progressCallback):
    files = [MATERIAL_LIST_FILE, OPERATOR_LIST_FILE]
    for i, f in enumerate(files):
        if progressCallback is not None:
            progressCallback(i, len(files))
        tryDownloadNewerFileFromGithub(ENTITY_LIST_REPOSITORY, ENTITY_LIST_REPOSITORY_FOLDER + f, "data/" + f)


if not os.path.isfile(DOWNLOAD_METADATA_FILE):
    writeDownloadMetadata({})
DOWNLOAD_METADATA = json.load(open(DOWNLOAD_METADATA_FILE, "r"))

if __name__ == "__main__":
    knownOperatorIds = [op["internalId"] for op in json.load(open("../../entityLists/operators.json", "r"))]
    downloadGamedata()
    for operatorId, op in RAW_OPERATORS.items():
        if operatorId.startswith("char") and not op["isNotObtainable"] and not operatorId in knownOperatorIds:
            print(operatorId)



