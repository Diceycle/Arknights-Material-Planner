import json
import os.path
import re
import urllib.error
import urllib.request

from config import LOGGER
from database import *

CACHE_PATH = "data/upgradeCosts/"
CACHE_FILETYPE = ".costs"

userAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': userAgent, }

gamepressUrl = CONFIG.gamepressUrl

skillTableStart = "class=\"skill-material-cost17"
masteryTableStart = "class=\"skill-material-cost810"
eliteTableStart = "class=\"table-3"
moduleTableStart = "class=\"main-title\">Modules"
materialCell = "class=\"material-cell"
materialQuantityTag = "class=\"material-quantity"

def getFileName(operator):
    return CACHE_PATH + operator.externalName + CACHE_FILETYPE

def indexToMastery(index):
    return "S" + str(1 + index // 3) + "M" + str(index % 3 + 1)

def indexToSkillLevel(index):
    return "SK" + str(index + 2)

def indexToElite(index):
    return "E" + str(index+1)

def valuesToModuleUpgrade(moduleType, moduleLevel):
    return "MOD-{}-{}".format(moduleType, moduleLevel).upper()

def parseMaterial(line):
    return re.search(".*data-item=\"([^\"]*)\"", line).group(1)

def parseMaterialFileName(line):
    return re.search(".*item-image\".*(?=/[^/\.]*\.png)/(.+)\.png", line).group(1)

def parseQuantity(line):
    return re.search(".*material-quantity\">x(\d+)", line).group(1)

def parseModuleType(line):
    match = re.search(".*img src.*(?=/[^/\.]*\.png)/[\w\-]+([xyz])\.png", line)
    if match is not None:
        return match.group(1)

    return None

def parseModuleLevel(line):
    match = re.search(".*module-equip-level\">Lvl\. (\d)", line)
    if match is not None:
        return match.group(1)

    return None

def getMaterial(canonicalName):
    for m in MATERIALS.values():
        if m.canonicalName == canonicalName:
            return m
    LOGGER.warning("Unrecognized Material: %s", canonicalName)

def getMaterialFromFileName(fileName):
    for m in MATERIALS.values():
        if m.externalFileName == fileName:
            return m
    LOGGER.warning("Unrecognized Material: %s", fileName)

def getRequest(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, None, headers))
    except urllib.error.HTTPError as response:
        LOGGER.error("Error reading url: %s", response.code)
        for line in response.readlines():
            line = line.decode("utf-8")
            LOGGER.debug(line)

def hasCache(operator):
    return os.path.isfile(getFileName(operator))

def downloadCosts(operator):
    if hasCache(operator):
        data = json.load(open(getFileName(operator), "r"))
        return toUpgrades(data, recurse=toMaterials)

    skillTableRow = None
    masteryTableRow = None
    eliteTableRow = None
    moduleParsing = False
    currentModuleType = None
    currentModule = None
    currentMaterial = None

    costs = {}

    response = getRequest(gamepressUrl + operator.externalName)

    for line in response.readlines():
        line = line.decode("utf-8")

        if (masteryTableRow is not None or eliteTableRow is not None or skillTableRow is not None) and "</table>" in line:
            skillTableRow = None
            masteryTableRow = None
            eliteTableRow = None

        if skillTableStart in line:
            skillTableRow = -2

        if skillTableRow is not None:
            if "<tr>" in line:
                skillTableRow += 1
                if skillTableRow >= 0:
                    costs[UPGRADES[indexToSkillLevel(skillTableRow)]] = {}
            if materialCell in line:
                currentMaterial = parseMaterial(line)
            if materialQuantityTag in line:
                m = getMaterial(currentMaterial)
                costs[UPGRADES[indexToSkillLevel(skillTableRow)]][m] = int(parseQuantity(line))

        if masteryTableStart in line:
            masteryTableRow = -2

        if masteryTableRow is not None:
            if "<tr>" in line:
                masteryTableRow += 1
                if masteryTableRow >= 0:
                    costs[UPGRADES[indexToMastery(masteryTableRow)]] = {}
            if materialCell in line:
                currentMaterial = parseMaterial(line)
            if materialQuantityTag in line:
                costs[UPGRADES[indexToMastery(masteryTableRow)]][getMaterial(currentMaterial)] = int(parseQuantity(line))

        if eliteTableStart in line:
            eliteTableRow = -2

        if eliteTableRow is not None:
            if "<tr>" in line:
                eliteTableRow += 1
                if eliteTableRow >= 0:
                    costs[UPGRADES[indexToElite(eliteTableRow)]] = {}
            if materialCell in line:
                currentMaterial = parseMaterial(line)
            if materialQuantityTag in line:
                costs[UPGRADES[indexToElite(eliteTableRow)]][getMaterial(currentMaterial)] = int(parseQuantity(line))


        if moduleTableStart in line:
            moduleParsing = True

        if moduleParsing:
            if "module-type-image" in line:
                currentModuleType = "next"
            if "img src" in line and currentModuleType == "next":
                currentModuleType = parseModuleType(line)
            if "module-equip-level" in line:
                currentModuleLevel = parseModuleLevel(line)
                if currentModuleType is not None and currentModuleLevel is not None:
                    currentModule = valuesToModuleUpgrade(currentModuleType, currentModuleLevel)
                    costs[UPGRADES[currentModule]] = {}

            if currentModule is not None and "class=\"item-image" in line:
                currentMaterial = parseMaterialFileName(line)
            if currentModule is not None and materialQuantityTag in line:
                costs[UPGRADES[currentModule]][getMaterialFromFileName(currentMaterial)] = parseQuantity(line)

            if "</article>" in line:
                currentModule = None

    json.dump(toExternal(costs, recurse=toExternal), safeOpen(getFileName(operator)))
    return costs