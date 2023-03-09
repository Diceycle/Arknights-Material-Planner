import json
import os
import urllib.request
import urllib.error
import re

from config import CONFIG, LOGGER
from database import *

CACHE_PATH = "data/upgradeCosts/"
CACHE_FILETYPE = ".costs"

userAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': userAgent, }

gamepressUrl = CONFIG.gamepressUrl

skillTableStart = "class=\"skill-material-cost17"
masteryTableStart = "class=\"skill-material-cost810"
eliteTableStart = "class=\"table-3"
materialCell = "class=\"material-cell"
materialQuantityTag = "class=\"material-quantity"

def getFileName(operator):
    return CACHE_PATH + operator.externalName + CACHE_FILETYPE

def indexToMastery(index):
    return "S" + str(1 + index // 3) + "M" + str(index % 3 + 1)

def indexToElite(index):
    return "E" + str(index+1)

def parseMaterial(line):
    return re.search(".*data-item=\"([^\"]*)\"", line).group(1)

def parseQuantity(line):
    return re.search(".*material-quantity\">x(\d+)", line).group(1)

def getMaterial(canonicalName):
    for m in MATERIALS.values():
        if m.canonicalName == canonicalName:
            return m
    LOGGER.warning("Unrecognized Material: %s", canonicalName)

def getRequest(url):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, None, headers))
    except urllib.error.HTTPError as response:
        LOGGER.error("Error reading url: %s", response.code)
        for line in response.readlines():
            line = line.decode("utf-8")
            LOGGER.debug(line)

def downloadCosts(operator):
    if os.path.isfile(getFileName(operator)):
        data = json.load(open(getFileName(operator), "r"))
        return toUpgrades(data, recurse=toMaterials)

    skillTableRow = None
    masteryTableRow = None
    eliteTableRow = None
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
            costs[UPGRADES["SK7"]] = {}

        if skillTableRow is not None:
            if materialCell in line:
                currentMaterial = parseMaterial(line)
            if materialQuantityTag in line:
                m = getMaterial(currentMaterial)
                if m.tier >= 3 and m.name != "skill-2":
                    costs[UPGRADES["SK7"]][m] = int(parseQuantity(line))

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
                if not currentMaterial.startswith("LMD") and not "chip" in currentMaterial.lower():
                    costs[UPGRADES[indexToElite(eliteTableRow)]][getMaterial(currentMaterial)] = int(parseQuantity(line))

    json.dump(toExternal(costs, recurse=toExternal), open(getFileName(operator), "w"))
    return costs