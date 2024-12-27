import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image, ImageTk, ImageColor

from utilImport import *
from gameDataReader import readOperatorCosts, getModuleImagePath, getOperatorImagePath, readMaterialData, getMaterialImagePath

UPGRADE_SCALE = 0.75
MAX_MODULE_IMAGE_DIMENSIONS = (70, 60)

class ScalableImage:
    def __init__(self, name, collection, imagePath, mainDimension = 1):
        self.name = name
        self.image = loadImage(imagePath)
        self.mainDimension = mainDimension

        self.imageReferences = {}

        collection[name] = self

    def getPhotoImage(self, size, transparency = 1, operator = None):
        key = str(size) + "+" + str(transparency)
        if operator is not None:
            key += "+" + operator.name
        if not key in self.imageReferences:
            im = self.renderImage(**{"operator": operator})
            if transparency < 1:
                im.putalpha(Image.eval(im.getchannel("A"), lambda v: min(v, int(255 * transparency))))

            factor = size / im.size[self.mainDimension]
            im = im.resize((int(im.width * factor), int(im.height * factor)))

            self.imageReferences[key] = ImageTk.PhotoImage(im)

        return self.imageReferences[key]

    def renderImage(self, **flags):
        return self.image.copy()

class UIElement(ScalableImage):
    def __init__(self, name, image, **kwargs):
        super().__init__(name, UI_ELEMENTS, "img/ui/" + image, **kwargs)

    def renderImage(self, **flags):
        return colorize(self.image.copy(), ImageColor.getcolor(CONFIG.highlightColor, "RGB"))

class Upgrade(ScalableImage):
    def __init__(self, name, canonicalName, image, overlay = None, cumulativeUpgrades = None, moduleType = None, **kwargs):
        self.canonicalName = canonicalName
        self.overlay = overlay
        self.moduleType = moduleType
        self.cumulativeUpgrades = [UPGRADES[up] for up in cumulativeUpgrades] if cumulativeUpgrades is not None else None

        super().__init__(name, UPGRADES, "img/misc/" + image, **kwargs)

    def calculateCosts(self, costs):
        if self.cumulativeUpgrades is None:
            if self in costs:
                return costs[self]
            else:
                return {}
        else:
            result = Counter()
            for up in self.cumulativeUpgrades:
                if up in costs:
                    result += Counter(costs[up])
                else:
                    return {}
            return result

    def getPhotoImage(self, size, **renderFlags):
        return super().getPhotoImage(size * UPGRADE_SCALE, **renderFlags)

    def renderImage(self, operator = None, **flags):
        im = self.image.copy()

        if (operator is not None and
            self.moduleType is not None and
            (self in operator.costs or self.cumulativeUpgrades is not None and self.cumulativeUpgrades[0] in operator.costs)):

            orig = im
            moduleImage = self.centerModuleImage(Image.open(operator.getModuleImagePath(self.moduleType), "r").convert("RGBA"))

            im = Image.new("RGBA", (100, 100), (0,0,0,0))

            orig.thumbnail(size = ((im.height - MAX_MODULE_IMAGE_DIMENSIONS[1]) * 2,
                                   (im.height - MAX_MODULE_IMAGE_DIMENSIONS[1]) * 2))
            typeImage = loadImage("img/misc/" + self.overlay + "-small.png")
            typeImage.thumbnail(size = (moduleImage.height // 2, moduleImage.height // 2))

            im.alpha_composite(orig, dest=(im.width - orig.width, 0))
            im.alpha_composite(moduleImage, dest=(0, im.height - moduleImage.height))
            im.alpha_composite(typeImage, dest=(moduleImage.width - typeImage.width // 2, im.height - typeImage.height))

        elif self.overlay is not None:
            im.alpha_composite(loadImage("img/misc/" + self.overlay + ".png"))

        if CONFIG.highlightUpgrades:
            im = colorize(im, ImageColor.getcolor(CONFIG.highlightColor, "RGB"))
        return im

    def centerModuleImage(self, module):
        i = Image.new("RGBA", MAX_MODULE_IMAGE_DIMENSIONS, (0,0,0,0))
        i.alpha_composite(module, dest=(MAX_MODULE_IMAGE_DIMENSIONS[0] // 2 - module.width // 2,
                                        MAX_MODULE_IMAGE_DIMENSIONS[1] // 2 - module.height // 2))
        return i

    def getSortKey(self):
        return (str(not int(self.name.startswith("SK1")) and not int(self.name == "SK2") and not int(self.name == "SK3") and not int(self.name == "SK4")) +
                str(not int(self.name == "E1")) +
                str(not int(self.name.startswith("SK"))) +
                str(not int(self.name == "E2") and not int(self.name == "Base E2")) +
                str(not int(self.name.startswith("S"))) +
                str(int(self.name.startswith("MOD-D"))) +
                str(not int(self.name.startswith("MOD"))) +
                self.name)

    def __str__(self):
        return self.canonicalName

    def __repr__(self):
        return self.__str__()

class Operator(ScalableImage):
    def __init__(self, name, internalId):
        self.internalId = internalId
        self.costs, self.subclassId = readOperatorCosts(internalId)

        super().__init__(name, OPERATORS, getOperatorImagePath(internalId))

    def getModuleImagePath(self, moduleType):
        return getModuleImagePath(self.subclassId, moduleType)

class Material(ScalableImage):
    def __init__(self, name, canonicalName, internalId, position):
        self.tier, self.recipe = readMaterialData(internalId)

        self.internalId = internalId
        self.canonicalName = canonicalName
        self.position = position

        super().__init__(name, MATERIALS, getMaterialImagePath(internalId))

    def isCraftable(self):
        return self.recipe is not None

    def getIngredients(self):
        if self.isCraftable():
            return { getMaterialByInternalId(k): v for k, v in self.recipe.items() }

    def getPosition(self):
        return tuple(self.position)

    def renderImage(self, **flags):
        border = loadImage("img/border/T" + str(self.tier) + ".png")
        border.alpha_composite(self.image, ((border.width - self.image.width) // 2, (border.height - self.image.height) // 2))
        return border

    def getSortKey(self):
        return (str(int(self.canonicalName != "LMD")) +
                str(int(not self.name.startswith("chip") and not self.name.startswith("exp"))) +
                str(int(not self.name.startswith("module") and not self.name.startswith("skill"))) +
                str(5 - self.tier) +
                self.name)

    def __str__(self):
        return self.canonicalName

    def __repr__(self):
        return self.__str__()

UIElement("confirm", "confirm.png")
UIElement("close", "close.png")
UIElement("check-off", "check-off.png")
UIElement("check-on", "check-on.png")
UIElement("visibility-full", "visibility-full.png")
UIElement("visibility-partial", "visibility-partial.png")
UIElement("visibility-low", "visibility-low.png")
UIElement("missing", "missing.png")
UIElement("total", "total.png")
UIElement("arrow-up", "arrow-up.png")
UIElement("arrow-down", "arrow-down.png")
UIElement("drag", "drag.png")
UIElement("add", "add.png")
UIElement("resetCache", "resetCache.png")
UIElement("research-button", "research-button.png")
UIElement("export", "export.png")
UIElement("craft-arrow", "craft-arrow.png")
UIElement("add-set", "add-set.png")
UIElement("n-a", "na.png")
UIElement("loading", "loading.png")

Upgrade("E1", "Elite 1", "E1.png", mainDimension=0)
Upgrade("E2", "Elite 2", "E2.png", mainDimension=0)
Upgrade("SK2", "Skill rank 2", "2.png", mainDimension=0)
Upgrade("SK3", "Skill rank 3", "3.png", mainDimension=0)
Upgrade("SK4", "Skill rank 4", "4.png", mainDimension=0)
Upgrade("SK1-4", "Skill rank 1-4", "1-4.png", mainDimension=0, cumulativeUpgrades=["SK2", "SK3", "SK4"])
Upgrade("SK5", "Skill rank 5", "5.png", mainDimension=0)
Upgrade("SK6", "Skill rank 6", "6.png", mainDimension=0)
Upgrade("SK7", "Skill rank 7", "7.png", mainDimension=0)
Upgrade("SK4-7", "Skill rank 4-7", "4-7.png", mainDimension=0, cumulativeUpgrades=["SK5", "SK6", "SK7"])
Upgrade("Base E2", "E2 and Skills Maxed", "E2-7.png", mainDimension=0, cumulativeUpgrades=["SK2", "SK3", "SK4", "SK5", "SK6", "SK7", "E1", "E2"])
Upgrade("S1M1", "Skill 1 Mastery 1", "m-1.png", overlay = "S1", mainDimension=0)
Upgrade("S1M2", "Skill 1 Mastery 2", "m-2.png", overlay = "S1", mainDimension=0)
Upgrade("S1M3", "Skill 1 Mastery 3", "m-3.png", overlay = "S1", mainDimension=0)
Upgrade("S1MX", "Skill 1 Full Mastery", "m-x.png", overlay = "S1", mainDimension=0, cumulativeUpgrades=["S1M1", "S1M2", "S1M3"])
Upgrade("S2M1", "Skill 2 Mastery 1", "m-1.png", overlay = "S2", mainDimension=0)
Upgrade("S2M2", "Skill 2 Mastery 2", "m-2.png", overlay = "S2", mainDimension=0)
Upgrade("S2M3", "Skill 2 Mastery 3", "m-3.png", overlay = "S2", mainDimension=0)
Upgrade("S2MX", "Skill 2 Full Mastery", "m-x.png", overlay = "S2", mainDimension=0, cumulativeUpgrades=["S2M1", "S2M2", "S2M3"])
Upgrade("S3M1", "Skill 3 Mastery 1", "m-1.png", overlay = "S3", mainDimension=0)
Upgrade("S3M2", "Skill 3 Mastery 2", "m-2.png", overlay = "S3", mainDimension=0)
Upgrade("S3M3", "Skill 3 Mastery 3", "m-3.png", overlay = "S3", mainDimension=0)
Upgrade("S3MX", "Skill 3 Full Mastery", "m-x.png", overlay = "S3", mainDimension=0, cumulativeUpgrades=["S3M1", "S3M2", "S3M3"])

Upgrade("MOD-X-1", "Module X Stage 1", "img_stg1.png", overlay = "mod-x", mainDimension=1, moduleType="X")
Upgrade("MOD-X-2", "Module X Stage 2", "img_stg2.png", overlay = "mod-x", mainDimension=1, moduleType="X")
Upgrade("MOD-X-3", "Module X Stage 3", "img_stg3.png", overlay = "mod-x", mainDimension=1, moduleType="X")
Upgrade("MOD-X-X", "Module X Full", "img_stgX.png", overlay = "mod-x", mainDimension=1, moduleType="X", cumulativeUpgrades=["MOD-X-1", "MOD-X-2", "MOD-X-3"])
Upgrade("MOD-Y-1", "Module Y Stage 1", "img_stg1.png", overlay = "mod-y", mainDimension=1, moduleType="Y")
Upgrade("MOD-Y-2", "Module Y Stage 2", "img_stg2.png", overlay = "mod-y", mainDimension=1, moduleType="Y")
Upgrade("MOD-Y-3", "Module Y Stage 3", "img_stg3.png", overlay = "mod-y", mainDimension=1, moduleType="Y")
Upgrade("MOD-Y-X", "Module Y Full", "img_stgX.png", overlay = "mod-y", mainDimension=1, moduleType="Y", cumulativeUpgrades=["MOD-Y-1", "MOD-Y-2", "MOD-Y-3"])
Upgrade("MOD-D-1", "Module D Stage 1", "img_stg1.png", overlay = "mod-d", mainDimension=1, moduleType="D")
Upgrade("MOD-D-2", "Module D Stage 2", "img_stg2.png", overlay = "mod-d", mainDimension=1, moduleType="D")
Upgrade("MOD-D-3", "Module D Stage 3", "img_stg3.png", overlay = "mod-d", mainDimension=1, moduleType="D")
Upgrade("MOD-D-X", "Module D Full", "img_stgX.png", overlay = "mod-d", mainDimension=1, moduleType="D", cumulativeUpgrades=["MOD-D-1", "MOD-D-2", "MOD-D-3"])


DEPOT_ORDER = None
def loadMaterials(progressCallback):
    global DEPOT_ORDER
    rawMaterials = json.load(open("data/materials.json", "r"))
    
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [ pool.submit(lambda args: Material(**args), m) for m in rawMaterials["materials"] ]

        for i, future in enumerate(as_completed(futures)):
            progressCallback(i, len(rawMaterials["materials"]))

    DEPOT_ORDER = rawMaterials["depotOrder"]

    return rawMaterials["pageSize"]

def loadOperators(progressCallback):
    rawOperators = json.load(open("data/operators.json", "r"))

    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [ pool.submit(lambda args: Operator(**args), m) for m in rawOperators ]

        for i, future in enumerate(as_completed(futures)):
            progressCallback(i, len(rawOperators))
