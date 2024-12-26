import json
import logging
import os.path
import sys
from collections import Counter

from PIL import Image

class Config:
    def __init__(self,
                 uiScale = 100,
                 scrollSpeed = 30,
                 saveFile = "default.materials",
                 maintainNaturalOrder = False,
                 sortUpgrades = True,
                 backgroundImage = None,
                 backgroundImageOffset = 0,
                 backgroundColor = "#444444",
                 color = "#555555",
                 colorDark = "#444444",
                 highlightColor = "white",
                 highlightUpgrades = False,
                 amountColor = "black",
                 amountColorFont = "white",
                 depotColorSufficient = "#00CC00",
                 depotColorSufficientFont = "black",
                 depotColorInsufficient = "red",
                 depotColorInsufficientFont ="white",
                 dataRepository ="Kengxxiao/ArknightsGameData",
                 dataRepositoryExcelPath ="zh_CN/gamedata/excel/",
                 imageRepositoryBaseUrl ="https://raw.githubusercontent.com/PuppiizSunniiz/Arknight-Images/refs/heads/main/",
                 depotParsingEnabled = True,
                 arknightsContainer = "BlueStacks",
                 arknightsWindowName = None,
                 arknightsInputWindowClass = None,
                 arknightsWindowBorder = None,
                 depotScanScrollDelay = 2,
                 depotScanScrollOffset = 25,
                 displayScale = 1,
                 colorLeniency = 3,
                 imageRecognitionThreshold = 0.8,
                 tesseractExeLocation = None,
                 debug = True,
                 **kwargs):

        self.uiScale = uiScale
        self.scrollSpeed = scrollSpeed
        self.saveFile = saveFile
        self.maintainNaturalOrder = maintainNaturalOrder
        self.sortUpgrades = sortUpgrades
        self.backgroundImage = backgroundImage
        self.backgroundImageOffset = backgroundImageOffset
        self.backgroundColor = backgroundColor
        self.color = color
        self.colorDark = colorDark
        self.amountColor = amountColor
        self.amountColorFont = amountColorFont
        self.highlightColor = highlightColor
        self.highlightUpgrades = highlightUpgrades
        self.depotColorSufficient = depotColorSufficient
        self.depotColorSufficientFont = depotColorSufficientFont
        self.depotColorInsufficient = depotColorInsufficient
        self.depotColorInsufficientFont = depotColorInsufficientFont
        self.dataRepository = dataRepository
        self.dataRepositoryExcelPath = dataRepositoryExcelPath
        self.imageRepositoryBaseUrl = imageRepositoryBaseUrl
        self.depotParsingEnabled = depotParsingEnabled
        self.arknightsContainer = arknightsContainer
        self.arknightsWindowName = arknightsWindowName
        self.arknightsInputWindowClass = arknightsInputWindowClass
        self.arknightsWindowBorder = arknightsWindowBorder
        self.depotScanScrollOffset = depotScanScrollOffset
        self.depotScanScrollDelay = depotScanScrollDelay
        self.displayScale = displayScale
        self.colorLeniency = colorLeniency
        self.imageRecognitionThreshold = imageRecognitionThreshold
        self.tesseractExeLocation = tesseractExeLocation
        self.debug = debug

        if self.usesBlueStacks():
            if self.arknightsWindowName is None:
                self.arknightsWindowName = "BlueStacks"
            if self.arknightsWindowBorder is None:
                self.arknightsWindowBorder = (1, 33, 33, 1)
        elif self.usesLDPlayer():
            if self.arknightsWindowName is None:
                self.arknightsWindowName = "LDPlayer"
            if self.arknightsWindowBorder is None:
                self.arknightsWindowBorder = (1, 34, 41, 2)
        else:
            if self.arknightsWindowBorder is None:
                self.arknightsWindowBorder = (0, 0, 0, 0)

        if len(kwargs) > 0:
            LOGGER.warning("Unrecognized Config Parameters: %s", kwargs)

    def usesBlueStacks(self):
        return self.arknightsContainer.lower() == "BlueStacks".lower()

    def usesLDPlayer(self):
        return self.arknightsContainer.lower() == "LDPlayer".lower()

def createDirsIfNeeded(filename):
    dirname = os.path.dirname(filename)
    if len(dirname) > 0:
        os.makedirs(dirname, exist_ok=True)

def safeOpen(filename, mode = "w+"):
    createDirsIfNeeded(filename)
    return open(filename, mode)

def safeSave(image, filename):
    createDirsIfNeeded(filename)
    image.save(filename)

def loadImage(path):
    return Image.open(path).convert("RGBA")

def colorize(image, color):
    floatColor = [c / 255 for c in color]
    r, g, b, a = image.split()
    r = Image.eval(r, lambda v: int(v * floatColor[0]))
    g = Image.eval(g, lambda v: int(v * floatColor[1]))
    b = Image.eval(b, lambda v: int(v * floatColor[2]))

    return Image.merge("RGBA", (r, g, b, a))

def toUpgrades(d, recurse=lambda v: v):
    return { UPGRADES[k]: recurse(v) for k, v in d.items() }

def toOperators(d, recurse=lambda v: v):
    return { OPERATORS[k]: recurse(v) for k, v in d.items() }

def toMaterials(d, recurse=lambda v: v):
    return { MATERIALS[k]: recurse(v) for k, v in d.items() }

def toExternal(d, recurse=lambda v: v):
    return { k.name: recurse(v) for k, v in d.items() }

def unpackVar(d):
    return { k: v.get() for k, v in d.items() }

def getMaterialByInternalId(internalId):
    for m in MATERIALS.values():
        if m.internalId == internalId:
            return m
    LOGGER.warning("Unrecognized Material: %s", internalId)

def multiplyCounter(counter, factor):
    for k in counter.keys():
        counter[k] *= factor
    return counter

def craftPossible(missing, available):
    for tier in range(5, 0, -1):
        for m in list(missing.keys()):
            if m.tier != tier:
                continue
            if m.canonicalName == "LMD":
                missing[m] -= min(missing[m], available[m])
                continue

            while missing[m] > 0:
                path = findCraftingPath(m, available)
                if path is None:
                    break
                else:
                    missing[m] -= 1
                    available -= path

            if m.isCraftable():
                missing += Counter(multiplyCounter(m.getIngredients(), missing[m]))

def findCraftingPath(material, available):
    if available[material] > 0:
        return Counter({ material: 1 })
    if not material.isCraftable():
        return None

    path = Counter(material.getIngredients())
    while True:
        if path <= available:
            return path
        else:
            for m in list(path.keys()):
                if available[m] >= path[m]:
                    continue
                if not m.isCraftable():
                    return None

                need = max(0, path[m] - available[m])
                path += multiplyCounter(Counter(m.getIngredients()), need)
                path[m] -= need

def save(upgradeSets, depotContents):
    data = {}
    sets = []
    for s in upgradeSets:
        sets.append({
            "operator": s.operator.name,
            "upgrades": [{ "name": itemSet.upgrade.name, "enabled": itemSet.enabled } for itemSet in s.itemSets]
        })

    data["version"] = "1.4"
    data["sets"] = sets
    data["depot"] = toExternal(depotContents)

    json.dump(data, safeOpen(CONFIG.saveFile), indent=2)

def load():
    data = {"sets": [], "depot": {}}

    if os.path.isfile(CONFIG.saveFile):
        rawData = json.load(open(CONFIG.saveFile, "r"))

        version = None
        if "version" in rawData:
            version = rawData["version"]

        if version is None:
            rawData = migrateToVersion_1_1(rawData)

        if version == "1.1":
            rawData = migrateToVersion_1_4(rawData)

        for rawSet in rawData["sets"]:
            data["sets"].append({
                "operator": OPERATORS[rawSet["operator"]],
                "upgrades": [{ "upgrade": UPGRADES[up["name"]], "enabled": bool(up["enabled"]) } for up in rawSet["upgrades"]]
            })

        data["depot"] = toMaterials(rawData["depot"])

    return data

def migrateToVersion_1_1(rawData):
    operators = {}
    for rawSet in rawData["sets"]:
        operator = rawSet["operator"]
        if not operator in operators:
            operators[operator] = []

        operators[operator].append({"name": rawSet["upgrade"], "enabled": rawSet["enabled"]})

    return { "sets": [{ "operator": op, "upgrades": operators[op] } for op in operators.keys()],
             "depot": rawData["depot"],
             "version": "1.1" }

def migrateToVersion_1_4(rawData):
    return { "sets": [{ "operator": s["operator"], "upgrades": [{ "name": up["name"].replace("Z", "D"), "enabled": up["enabled"]} for up in s["upgrades"]] } for s in rawData["sets"]],
             "depot": rawData["depot"],
             "version": "1.4" }

LOGGER = logging.getLogger("ArknightsMaterials")
LOGGER.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler("arknightsMaterials.log")
handler.setFormatter(formatter)
LOGGER.addHandler(handler)

LOGGER.addHandler(logging.StreamHandler(sys.stdout))

ERROR_LOGGER = logging.getLogger("ArknightsMaterialsErrors")
ERROR_LOGGER.addHandler(handler)
ERROR_LOGGER.addHandler(logging.StreamHandler(sys.stderr))

def exceptHook(type, value, traceback):
    ERROR_LOGGER.error("Unhandled exception occurred", exc_info=(type,value,traceback))

sys.excepthook = exceptHook

MATERIALS = {}
UI_ELEMENTS = {}
UPGRADES = {}
OPERATORS = {}

if not os.path.isfile("config.json"):
    json.dump({}, open("config.json", "w+"))
CONFIG = Config(**(json.load(open("config.json", "r"))))
