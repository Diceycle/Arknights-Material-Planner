import json

class Config:
    def __init__(self,
                 uiScale = 100,
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
            print("Unrecognized Config Parameters:", kwargs)

jsonConfig = json.load(open("config.json", "r"))
CONFIG = Config(**jsonConfig)
