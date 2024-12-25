import json
from collections import Counter

from PIL import Image, ImageTk, ImageColor

from utilImport import *
from gameDataReader import getOperatorCosts, getModuleImagePath, getOperatorImagePath, downloadMaterialImage, getMaterialImagePath

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
        super().__init__(name, UPGRADES, "img/misc/" + image, **kwargs)
        self.canonicalName = canonicalName
        self.overlay = overlay
        self.moduleType = moduleType
        self.cumulativeUpgrades = [UPGRADES[up] for up in cumulativeUpgrades] if cumulativeUpgrades is not None else None

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
        self.costs, self.subclassId = getOperatorCosts(internalId)

        super().__init__(name, OPERATORS, getOperatorImagePath(internalId))

    def getModuleImagePath(self, moduleType):
        return getModuleImagePath(self.subclassId, moduleType)

class Material(ScalableImage):
    def __init__(self, name, canonicalName, tier, internalId, recipe = None):
        downloadMaterialImage(internalId)

        self.internalId = internalId
        self.canonicalName = canonicalName
        self.tier = tier
        self.recipe = recipe

        super().__init__(name, MATERIALS, getMaterialImagePath(internalId))

    def isCraftable(self):
        return self.recipe is not None

    def getIngredients(self):
        if self.isCraftable():
            return toMaterials(self.recipe)

    def getPosition(self):
        page2 = 12
        x = 5 - self.tier
        if self.name.startswith("fluid") or self.name.startswith("gel") or \
            self.name.startswith("solvent") or self.name.startswith("manganese") or \
            self.name.startswith("grindstone") or self.name.startswith("carbon"):
            x += 2

        if self.name.startswith("keton") or self.name.startswith("polymer"):
            return x, 0
        elif self.name.startswith("oriron"):
            return x, 1
        elif self.name.startswith("rock"):
            return x, 2
        elif self.name.startswith("plastic"):
            return x, 3
        elif self.name.startswith("sugar"):
            return x, 4
        elif self.name.startswith("device") or self.name.startswith("nanoflake"):
            return x, 5
        elif self.name.startswith("kohl") or self.name.startswith("grindstone"):
            return x, 6
        elif self.name.startswith("rma") or self.name.startswith("manganese") or self.name.startswith("steel"):
            return x, 7
        elif self.name.startswith("crystal") or self.name.startswith("gel"):
            return x, 8
        elif self.name.startswith("incandescent") or self.name.startswith("solvent"):
            return x, 9
        elif self.name.startswith("salt") or self.name.startswith("fluid"):
            return x, 10
        elif self.name.startswith("fiber") or self.name.startswith("carbon"):
            return x, 11

        elif self.name.startswith("exp"):
            return x+1, page2
        elif self.name.startswith("skill"):
            return x+1, page2 + 1
        elif self.name.startswith("money"):
            return 1, page2 + 1
        elif self.name.startswith("module"):
            return 5-int(self.name[self.name.find("-")+1:]), page2 + 2
        elif self.name.startswith("chip-catalyst"):
            return 1, page2 + 2
        elif self.name.startswith("chip-vanguard"):
            return x+2, page2 + 3
        elif self.name.startswith("chip-guard"):
            return x+2, page2 + 4
        elif self.name.startswith("chip-defender"):
            return x+2, page2 + 5
        elif self.name.startswith("chip-sniper"):
            return x+2, page2 + 6
        elif self.name.startswith("chip-caster"):
            return x+2, page2 + 7
        elif self.name.startswith("chip-healer"):
            return x+2, page2 + 8
        elif self.name.startswith("chip-supporter"):
            return x+2, page2 + 9
        elif self.name.startswith("chip-specialist"):
            return x+2, page2 + 10

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


DEPOT_ORDER = ["exp-4", "exp-3", "exp-2", "exp-1", "skill-3", "skill-2", "skill-1", "module-1", "module-3", "module-2",
               "salt-5", "crystal-5", "steel-5", "nanoflake-5", "polymer-5",
               "carbon-4", "carbon-3", "fiber-4", "fiber-3", "salt-4", "salt-3", "fluid-4", "fluid-3", "solvent-4", "solvent-3", "crystal-4", "crystal-3",
               "incandescent-4", "incandescent-3", "gel-4", "gel-3",
               "kohl-4", "kohl-3", "manganese-4", "manganese-3", "grindstone-4", "grindstone-3", "rma-4", "rma-3",
               "rock-4", "rock-3", "rock-2", "rock-1", "device-4", "device-3", "device-2", "device-1",
               "plastic-4", "plastic-3", "plastic-2", "plastic-1", "sugar-4", "sugar-3", "sugar-2", "sugar-1",
               "oriron-4", "oriron-3", "oriron-2", "oriron-1", "keton-4", "keton-3", "keton-2", "keton-1",
               "chip-catalyst",
               "chip-vanguard-3", "chip-guard-3", "chip-defender-3", "chip-sniper-3", "chip-caster-3", "chip-healer-3", "chip-supporter-3", "chip-specialist-3",
               "chip-vanguard-2", "chip-guard-2", "chip-defender-2", "chip-sniper-2", "chip-caster-2", "chip-healer-2", "chip-supporter-2", "chip-specialist-2",
               "chip-vanguard-1", "chip-guard-1", "chip-defender-1", "chip-sniper-1", "chip-caster-1", "chip-healer-1", "chip-supporter-1", "chip-specialist-1",
]

def loadMaterials(progressCallback):
    rawMaterials = json.load(open("materials.json", "r"))
    for i, m in enumerate(rawMaterials["materials"]):
        progressCallback(i, len(rawMaterials["materials"]))
        Material(**m)

def loadOperators(progressCallback):
    rawOperators = json.load(open("operators.json", "r"))
    for i, o in enumerate(rawOperators):
        progressCallback(i, len(rawOperators))
        Operator(**o)
