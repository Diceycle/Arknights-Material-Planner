import json
import logging
import os.path
import sys

LOGGER = logging.getLogger("ArknightsMaterials")
LOGGER.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler("arknightsMaterials.log")
handler.setFormatter(formatter)
LOGGER.addHandler(handler)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))

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
                 highlightColor = "#FFFFFF",
                 gamepressUrl ="https://gamepress.gg/arknights/operator/",
                 depotParsingEnabled = True,
                 arknightsWindowName ="BlueStacks",
                 arknightsInputWindowClass ="plrNativeInputWindowClass",
                 arknightsWindowBorder = (1, 33, 33, 1),
                 colorLeniency = 3,
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
        self.highlightColor = highlightColor
        self.gamepressUrl = gamepressUrl
        self.depotParsingEnabled = depotParsingEnabled
        self.arknightsWindowName = arknightsWindowName
        self.arknightsInputWindowClass = arknightsInputWindowClass
        self.arknightsWindowBorder = arknightsWindowBorder
        self.colorLeniency = colorLeniency
        self.tesseractExeLocation = tesseractExeLocation

        if len(kwargs) > 0:
            LOGGER.warning("Unrecognized Config Parameters: %s", kwargs)


if not os.path.isfile("config.json"):
    json.dump({}, open("config.json", "w+"))
CONFIG = Config(**(json.load(open("config.json", "r"))))
