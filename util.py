import json
import logging
import os.path
import sys

from PIL import Image

class Config:
    def __init__(self,
                 uiScale = 100,
                 scrollSpeed = 30,
                 saveFile = "default.materials",
                 backgroundImage = None,
                 backgroundImageOffset = 0,
                 backgroundColor = "#444444",
                 color = "#555555",
                 colorDark = "#444444",
                 highlightColor = "white",
                 highlightUpgrades = False,
                 amountColor = "black",
                 amountColorFont = "white",
                 depotColorSufficient = "gray",
                 depotColorSufficientFont = "black",
                 depotColorCraftable = "#00DD00",
                 depotColorCraftableFont = "black",
                 depotColorInsufficient = "red",
                 depotColorInsufficientFont ="white",
                 gamepressUrl ="https://gamepress.gg/arknights/operator/",
                 depotParsingEnabled = True,
                 arknightsContainer = "BlueStacks",
                 arknightsWindowName ="BlueStacks",
                 arknightsInputWindowClass = None,
                 arknightsWindowBorder = (1, 33, 33, 1),
                 colorLeniency = 3,
                 imageRecognitionThreshold = 0.95,
                 tesseractExeLocation = None,
                 **kwargs):

        self.uiScale = uiScale
        self.scrollSpeed = scrollSpeed
        self.saveFile = saveFile
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
        self.depotColorCraftable = depotColorCraftable
        self.depotColorCraftableFont = depotColorCraftableFont
        self.depotColorInsufficient = depotColorInsufficient
        self.depotColorInsufficientFont = depotColorInsufficientFont
        self.gamepressUrl = gamepressUrl
        self.depotParsingEnabled = depotParsingEnabled
        self.arknightsContainer = arknightsContainer
        self.arknightsWindowName = arknightsWindowName
        self.arknightsInputWindowClass = arknightsInputWindowClass
        self.arknightsWindowBorder = arknightsWindowBorder
        self.colorLeniency = colorLeniency
        self.imageRecognitionThreshold = imageRecognitionThreshold
        self.tesseractExeLocation = tesseractExeLocation

        if len(kwargs) > 0:
            LOGGER.warning("Unrecognized Config Parameters: %s", kwargs)

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

def hasExtension(filename, extensions):
    return filename.lower().endswith(extensions)

def loadImage(path, name):
    return Image.open(path + "/" + name).convert("RGBA")

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

def multiplyCounter(counter, factor):
    for k in counter.keys():
        counter[k] *= factor
    return counter


LOGGER = logging.getLogger("ArknightsMaterials")
LOGGER.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler("arknightsMaterials.log")
handler.setFormatter(formatter)
LOGGER.addHandler(handler)

LOGGER.addHandler(logging.StreamHandler(sys.stdout))

MATERIALS = {}
UI_ELEMENTS = {}
UPGRADES = {}
OPERATORS = {}

if not os.path.isfile("config.json"):
    json.dump({}, open("config.json", "w+"))
CONFIG = Config(**(json.load(open("config.json", "r"))))
