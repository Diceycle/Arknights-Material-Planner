import json
import datetime
import os.path
import urllib.error
import urllib.request
import urllib.parse

from utilImport import *

MODULE_IMAGE_PATH = "data/moduleTypeImages/"
OPERATOR_IMAGE_PATH = "data/operatorImages/"

DATA_REPOSITORY = CONFIG.dataRepository
DATA_REPOSITORY_FOLDER = "json/gamedata/ArknightsGameData/zh_CN/gamedata/excel/"
OPERATOR_DATA_FILE = "character_table.json"
ADDITIONAL_OPERATOR_DATA_FILE = "char_patch_table.json"
MODULE_DATA_FILE = "uniequip_table.json"

IMAGE_REPOSITORY_BASE_URL = CONFIG.imageRepositoryBaseUrl
MODULE_IMAGE_SUB_URL = "equip/type/"
OPERATOR_IMAGE_SUB_URL = "avatars/"

userAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': userAgent, }

RAW_OPERATORS = None
RAW_MODULES = None

def getRequest(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, None, headers))
    except urllib.error.HTTPError as response:
        LOGGER.error("Error(%s) reading url: %s", response.code, url)
        for line in response.readlines()[:10]:
            line = line.decode("utf-8")
            LOGGER.debug(line.replace("\n", ""))

def getMostRecentCommitTimestamp(repo, remotePath):
    response = json.loads(getRequest(f"https://api.github.com/repos/{repo}/commits?path={remotePath}").read())
    return response[0]["commit"]["author"]["date"]

def tryDownloadNewerFileFromGithub(repo, remotePath, localPath):
    fullUrl = f"https://raw.githubusercontent.com/{repo}/refs/heads/main/{remotePath}"
    if not os.path.exists(localPath):
        downloadFileFromWeb(fullUrl, localPath)
    else:
        localTimestamp = os.path.getmtime(localPath)
        remoteTimestamp = datetime.datetime.fromisoformat(getMostRecentCommitTimestamp(repo, remotePath)).timestamp()

        if localTimestamp < remoteTimestamp:
            downloadFileFromWeb(fullUrl, localPath, replace=True)

def downloadFileFromWeb(url, localPath, replace=False):
    if replace or not os.path.exists(localPath):
        LOGGER.debug("Updating from Web: %s", localPath)
        f = safeOpen(localPath, mode="wb+")
        f.write(getRequest(url).read())
        f.close()

def getModuleImagePath(subclassId, moduleType):
    return MODULE_IMAGE_PATH + f"{subclassId}-{moduleType}.png"

def getOperatorImagePath(internalId):
    return OPERATOR_IMAGE_PATH + internalId + ".png"

def getMaterial(externalId):
    for m in MATERIALS.values():
        if m.externalId == externalId:
            return m
    LOGGER.warning("Unrecognized Material: %s", externalId)

def getOperator(internalId):
    for o in OPERATORS.values():
        if o.internalId == internalId:
            return o
    LOGGER.warning("Unrecognized Operator: %s", internalId)

def toModuleUpgradeKey(moduleType, stage):
    return f"MOD-{moduleType.upper()}-{stage}"

def addCosts(cost, upgradeKey, material, quantity):
    up = UPGRADES[upgradeKey]
    if not up in cost:
        cost[up] = {}

    cost[up][material] = quantity

def getOperatorCosts(internalId):
    data = RAW_OPERATORS[internalId]

    costs = {}
    subclassId = None

    downloadFileFromWeb(IMAGE_REPOSITORY_BASE_URL + OPERATOR_IMAGE_SUB_URL + internalId + ".png", getOperatorImagePath(internalId))

    for i, phase in enumerate(data["phases"]):
        if phase["evolveCost"] is not None:
            eliteKey = "E" + str(i)
            for mat in phase["evolveCost"]:
                addCosts(costs, eliteKey, getMaterial(mat["id"]), mat["count"])

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
            addCosts(costs, skillKey, getMaterial(mat["id"]), mat["count"])

    for i, skill in enumerate(data["skills"]):
        skillKeyPrefix = "S" + str(i + 1)
        for j, mastery in enumerate(skill["levelUpCostCond"]):
            skillKey = skillKeyPrefix + "M" + str(j + 1)
            for mat in mastery["levelUpCost"]:
                addCosts(costs, skillKey, getMaterial(mat["id"]), mat["count"])

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
                        addCosts(costs, moduleKey, getMaterial(mat["id"]), mat["count"])

    return costs, subclassId

def downloadOperatorData(progressCallback = None):
    global RAW_OPERATORS
    global RAW_MODULES

    files = [OPERATOR_DATA_FILE, ADDITIONAL_OPERATOR_DATA_FILE, MODULE_DATA_FILE]
    for i, f in enumerate(files):
        if progressCallback is not None:
            progressCallback(i, len(files))
        tryDownloadNewerFileFromGithub(DATA_REPOSITORY, DATA_REPOSITORY_FOLDER + f, "data/" + f)

    RAW_OPERATORS = json.load(open("data/" + OPERATOR_DATA_FILE, "r", encoding="utf-8"))
    RAW_MODULES = json.load(open("data/" + MODULE_DATA_FILE, "r", encoding="utf-8"))

    rawCharacterAdditions = json.load(open("data/" + ADDITIONAL_OPERATOR_DATA_FILE, "r", encoding="utf-8"))
    for k, v in rawCharacterAdditions["patchChars"].items():
        RAW_OPERATORS[k] = v

if __name__ == "__main__":
    knownOperatorIds = [op["internalId"] for op in json.load(open("operators.json", "r"))]
    downloadOperatorData()
    for operatorId, op in RAW_OPERATORS.items():
        if operatorId.startswith("char") and not op["isNotObtainable"] and not operatorId in knownOperatorIds:
            print(operatorId)



