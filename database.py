import json
import os

from PIL import Image, ImageTk, ImageColor

from config import CONFIG, Config

UPGRADE_SCALE = 0.75

def createDirsIfNeeded(filename):
    dirname = os.path.dirname(filename)
    if len(dirname) > 0:
        os.makedirs(dirname, exist_ok=True)

def safeOpen(filename):
    createDirsIfNeeded(filename)
    return open(filename, "w+")

def safeSave(image, filename):
    createDirsIfNeeded(filename)
    image.save(filename)

def hasExtension(filename, extensions):
    return filename.lower().endswith(extensions)

def loadImage(path, name):
    return Image.open(path + "/" + name).convert("RGBA")

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

MATERIALS = {}
UI_ELEMENTS = {}
UPGRADES = {}
OPERATORS = {}
class ScalableImage:
    def __init__(self, name, collection, imagePath, image, mainDimension = 1):
        self.name = name
        self.image = loadImage(imagePath, image)
        self.mainDimension = mainDimension

        self.imageReferences = {}

        collection[name] = self

    def getPhotoImage(self, size, transparency = 1):
        key = str(size) + "+" + str(transparency)
        if not key in self.imageReferences:
            im = self.renderImage()
            if transparency < 1:
                im.putalpha(Image.eval(im.getchannel("A"), lambda v: min(v, int(255 * transparency))))

            factor = size / im.size[self.mainDimension]
            im = im.resize((int(im.width * factor), int(im.height * factor)))

            self.imageReferences[key] = ImageTk.PhotoImage(im)

        return self.imageReferences[key]

    def renderImage(self):
        return self.image.copy()

class UIElement(ScalableImage):
    def __init__(self, name, image, **kwargs):
        super().__init__(name, UI_ELEMENTS, "img/ui", image, **kwargs)

    def renderImage(self):
        if CONFIG.highlightColor == Config().highlightColor:
            return self.image.copy()

        im = self.image.copy()
        highlightColor = [c / 255 for c in ImageColor.getcolor(CONFIG.highlightColor, "RGB")]
        for x in range(im.width):
            for y in range(im.height):
                pix = im.getpixel((x, y))
                im.putpixel((x, y),
                            (int(pix[0] * highlightColor[0]),
                             int(pix[1] * highlightColor[1]),
                             int(pix[2] * highlightColor[2]),
                             pix[3]))

        return im

class Upgrade(ScalableImage):
    def __init__(self, name, canonicalName, image, overlay = None, **kwargs):
        super().__init__(name, UPGRADES, "img/misc", image, **kwargs)
        self.canonicalName = canonicalName
        self.overlay = overlay

    def getPhotoImage(self, size):
        return super().getPhotoImage(size * UPGRADE_SCALE)

    def renderImage(self):
        im = self.image.copy()
        if self.overlay is not None:
            im.alpha_composite(loadImage("img/misc", self.overlay + ".png"))

        return im

    def __str__(self):
        return self.canonicalName

    def __repr__(self):
        return self.__str__()

class Operator(ScalableImage):
    def __init__(self, name, image, externalName = None):
        super().__init__(name, OPERATORS, "img/operator", image)

        self.externalName = externalName
        if self.externalName is None:
            self.externalName = name.lower().replace(" ", "-")

class Material(ScalableImage):
    def __init__(self, name, canonicalName, tier, image, externalFileName = None, recipe = None):
        super().__init__(name, MATERIALS, "img/material", image)
        self.canonicalName = canonicalName
        self.tier = tier

        self.recipe = recipe
        self.externalFileName = externalFileName

    def isCraftable(self):
        return self.recipe is not None

    def getIngredients(self):
        if self.isCraftable():
            return toMaterials(self.recipe)

    def getPosition(self):

        x = 5 - self.tier
        if self.name.startswith("fluid") or self.name.startswith("gel") or \
            self.name.startswith("solvent") or self.name.startswith("manganese") or \
            self.name.startswith("grindstone"):
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
        elif self.name.startswith("exp"):
            return x+1, 11
        elif self.name.startswith("skill"):
            return x+1, 12
        elif self.name.startswith("money"):
            return 1, 12
        elif self.name.startswith("module"):
            return 5-int(self.name[self.name.find("-")+1:]), 13
        elif self.name.startswith("chip-catalyst"):
            return 1, 13
        elif self.name.startswith("chip-vanguard"):
            return x+2, 14
        elif self.name.startswith("chip-guard"):
            return x+2, 15
        elif self.name.startswith("chip-defender"):
            return x+2, 16
        elif self.name.startswith("chip-sniper"):
            return x+2, 17
        elif self.name.startswith("chip-caster"):
            return x+2, 18
        elif self.name.startswith("chip-healer"):
            return x+2, 19
        elif self.name.startswith("chip-supporter"):
            return x+2, 20
        elif self.name.startswith("chip-specialist"):
            return x+2, 21

    def renderImage(self):
        border = loadImage("img/border", "T" + str(self.tier) + ".png")
        border.alpha_composite(self.image, ((border.width - self.image.width) // 2, (border.height - self.image.height) // 2))
        return border

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
UIElement("arrow-up", "arrow-up.png")
UIElement("arrow-down", "arrow-down.png")
UIElement("drag", "drag.png")
UIElement("add", "add.png")
UIElement("research", "research.png")
UIElement("research-button", "research-button.png")
UIElement("craft-arrow", "craft-arrow.png")
UIElement("add-set", "add-set.png")
UIElement("n-a", "na.png")
UIElement("loading", "loading.png")

Upgrade("E1", "Elite 1", "E1.png", mainDimension=0)
Upgrade("E2", "Elite 2", "E2.png", mainDimension=0)
Upgrade("SK1", "Skill rank 1", "1.png", mainDimension=0)
Upgrade("SK2", "Skill rank 2", "2.png", mainDimension=0)
Upgrade("SK3", "Skill rank 3", "3.png", mainDimension=0)
Upgrade("SK4", "Skill rank 4", "4.png", mainDimension=0)
Upgrade("SK5", "Skill rank 5", "5.png", mainDimension=0)
Upgrade("SK6", "Skill rank 6", "6.png", mainDimension=0)
Upgrade("SK7", "Skill rank 7", "7.png", mainDimension=0)
Upgrade("S1M1", "Skill 1 Mastery 1", "m-1.png", overlay = "S1", mainDimension=0)
Upgrade("S1M2", "Skill 1 Mastery 2", "m-2.png", overlay = "S1", mainDimension=0)
Upgrade("S1M3", "Skill 1 Mastery 3", "m-3.png", overlay = "S1", mainDimension=0)
Upgrade("S2M1", "Skill 2 Mastery 1", "m-1.png", overlay = "S2", mainDimension=0)
Upgrade("S2M2", "Skill 2 Mastery 2", "m-2.png", overlay = "S2", mainDimension=0)
Upgrade("S2M3", "Skill 2 Mastery 3", "m-3.png", overlay = "S2", mainDimension=0)
Upgrade("S3M1", "Skill 3 Mastery 1", "m-1.png", overlay = "S3", mainDimension=0)
Upgrade("S3M2", "Skill 3 Mastery 2", "m-2.png", overlay = "S3", mainDimension=0)
Upgrade("S3M3", "Skill 3 Mastery 3", "m-3.png", overlay = "S3", mainDimension=0)

Upgrade("MOD-X-1", "Module X Stage 1", "img_stg1.png", overlay = "mod-x", mainDimension=1)
Upgrade("MOD-X-2", "Module X Stage 2", "img_stg2.png", overlay = "mod-x", mainDimension=1)
Upgrade("MOD-X-3", "Module X Stage 3", "img_stg3.png", overlay = "mod-x", mainDimension=1)
Upgrade("MOD-Y-1", "Module Y Stage 1", "img_stg1.png", overlay = "mod-y", mainDimension=1)
Upgrade("MOD-Y-2", "Module Y Stage 2", "img_stg2.png", overlay = "mod-y", mainDimension=1)
Upgrade("MOD-Y-3", "Module Y Stage 3", "img_stg3.png", overlay = "mod-y", mainDimension=1)

Material("money", "LMD", 4, "lmd.png", externalFileName="GOLD")

Material("keton-1", "Diketon", 1, "keton-1.png")
Material("keton-2", "Polyketon", 2, "keton-2.png", recipe={"keton-1": 3})
Material("keton-3", "Aketon", 3, "keton-3.png", externalFileName="MTL_SL_KETONE3", recipe={"keton-2": 4})
Material("keton-4", "Keton Colloid", 4, "keton-4.png", externalFileName="MTL_SL_KETONE4", recipe={"keton-3": 2, "sugar-3": 1, "manganese-3": 1})

Material("rock-1", "Orirock", 1, "rock-1.png")
Material("rock-2", "Orirock Cube", 2, "rock-2.png", recipe={"rock-1": 3})
Material("rock-3", "Orirock Cluster", 3, "rock-3.png", externalFileName="MTL_SL_G3", recipe={"rock-2": 5})
Material("rock-4", "Orirock Concentration", 4, "rock-4.png", externalFileName="MTL_SL_G4", recipe={"rock-3": 4})

Material("sugar-1", "Sugar Substitute", 1, "sugar-1.png")
Material("sugar-2", "Sugar", 2, "sugar-2.png", recipe={"sugar-1": 3})
Material("sugar-3", "Sugar Pack", 3, "sugar-3.png", externalFileName="MTL_SL_STRG3", recipe={"sugar-2": 4})
Material("sugar-4", "Sugar Lump", 4, "sugar-4.png", externalFileName="MTL_SL_STRG4", recipe={"sugar-3": 2, "oriron-3": 1, "manganese-3": 1})

Material("plastic-1", "Ester", 1, "plastic-1.png")
Material("plastic-2", "Polyester", 2, "plastic-2.png", recipe={"plastic-1": 3})
Material("plastic-3", "Polyester Pack", 3, "plastic-3.png", externalFileName="MTL_SL_RUSH3", recipe={"plastic-2": 4})
Material("plastic-4", "Polyester Lump", 4, "plastic-4.png", externalFileName="MTL_SL_RUSH4", recipe={"plastic-3": 2, "keton-3": 1, "kohl-3": 1})

Material("oriron-1", "Oriron Shard", 1, "oriron-1.png")
Material("oriron-2", "Oriron", 2, "oriron-2.png", recipe={"oriron-1": 3})
Material("oriron-3", "Oriron Cluster", 3, "oriron-3.png", externalFileName="MTL_SL_IRON3", recipe={"oriron-2": 4})
Material("oriron-4", "Oriron Block", 4, "oriron-4.png", externalFileName="MTL_SL_IRON4", recipe={"oriron-3": 2, "device-3": 1, "plastic-3": 1})

Material("device-1", "Damaged Device", 1, "device-1.png")
Material("device-2", "Device", 2, "device-2.png", recipe={"device-1": 3})
Material("device-3", "Integrated Device", 3, "device-3.png", externalFileName="MTL_SL_BOSS3", recipe={"device-2": 4})
Material("device-4", "Optimized Device", 4, "device-4.png", externalFileName="MTL_SL_BOSS4", recipe={"device-3": 1, "rock-3": 2, "grindstone-3": 1})

Material("rma-3", "RMA70-12", 3, "rma-3.png", externalFileName="MTL_SL_RMA7012")
Material("rma-4", "RMA70-24", 4, "rma-4.png", externalFileName="MTL_SL_RMA7024", recipe={"rma-3": 1, "rock-3": 2, "keton-3": 1})

Material("grindstone-3", "Grindstone", 3, "grindstone-3.png", externalFileName="MTL_SL_PG1")
Material("grindstone-4", "Grindstone Pentahydrate", 4, "grindstone-4.png", externalFileName="MTL_SL_PG2", recipe={"grindstone-3": 1, "oriron-3": 1, "device-3": 1})

Material("manganese-3", "Manganese Ore", 3, "manganese-3.png", externalFileName="MTL_SL_MANGANESE1")
Material("manganese-4", "Manganese Trihydrate", 4, "manganese-4.png", externalFileName="MTL_SL_MANGANESE2", recipe={"manganese-3": 2, "plastic-3": 1, "kohl-3": 1})

Material("kohl-3", "Loxic Kohl", 3, "kohl-3.png", externalFileName="MTL_SL_ALCOHOL1")
Material("kohl-4", "White Horse Kohl", 4, "kohl-4.png", externalFileName="MTL_SL_ALCOHOL2", recipe={"kohl-3": 1, "sugar-3": 1, "rma-3": 1})

Material("incandescent-3", "Incandescent Alloy", 3, "incandescent-3.png", externalFileName="MTL_SL_IAM3")
Material("incandescent-4", "Incandescent Alloy Block", 4, "incandescent-4.png", externalFileName="MTL_SL_IAM4", recipe={"device-3": 1, "grindstone-3": 1,"incandescent-3": 1})

Material("gel-3", "Coagulating Gel", 3, "gel-3.png", externalFileName="MTL_SL_PGEL3")
Material("gel-4", "Polymerized Gel", 4, "gel-4.png", externalFileName="MTL_SL_PGEL4", recipe={"oriron-3": 1, "gel-3": 1, "incandescent-3": 1})

Material("crystal-3", "Crystalline Component", 3, "crystal-3.png", externalFileName="MTL_SL_OC3")
Material("crystal-4", "Crystalline Circuit", 4, "crystal-4.png", externalFileName="MTL_SL_OC4", recipe={"crystal-3": 2, "gel-3": 1, "incandescent-3": 1})
Material("crystal-5", "Crystalline Electronic Unit", 5, "crystal-5.png", externalFileName="MTL_SL_OEU", recipe={"crystal-4": 1, "gel-4": 2, "incandescent-4": 1})

Material("solvent-3", "Semi-Synthetic Solvent", 3, "solvent-3.png", externalFileName="MTL_SL_SS")
Material("solvent-4", "Refined Solvent", 4, "solvent-4.png", externalFileName="MTL_SL_RS", recipe={"solvent-3": 1, "fluid-3": 1, "gel-3": 1})

Material("fluid-3", "Compound Cutting Fluid", 3, "fluid-3.png", externalFileName="MTL_SL_CCF")
Material("fluid-4", "Cutting Fluid Solution", 4, "fluid-4.png", externalFileName="MTL_SL_PLCF", recipe={"fluid-3": 1, "crystal-3": 1, "rma-3": 1})

Material("salt-3", "转质盐组", 3, "salt-3.png", externalFileName="MTL_SL_ZY")
Material("salt-4", "转质盐聚块", 4, "salt-4.png", externalFileName="MTL_SL_ZYK", recipe={"salt-3": 2, "solvent-3": 1, "sugar-3": 1})
Material("salt-5", "烧结核凝晶", 5, "salt-5.png", externalFileName="MTL_SL_SHJ", recipe={"salt-4": 1, "fluid-4": 1, "solvent-4": 2})

Material("steel-5", "D32 Steel", 5, "steel-5.png", externalFileName="MTL_SL_DS", recipe={"manganese-4": 1, "grindstone-4": 1, "rma-4": 1})
Material("nanoflake-5", "Bipolar Nanoflake", 5, "nanoflake-5.png", externalFileName="MTL_SL_BN", recipe={"device-4": 1, "kohl-4": 2})
Material("polymer-5", "Polymerization Preparation", 5, "polymer-5.png", externalFileName="MTL_SL_PP", recipe={"rock-4": 1, "oriron-4": 1, "keton-4": 1})

Material("exp-1", "Drill Battle Record", 2, "exp-1.png")
Material("exp-2", "Frontline Battle Record", 3, "exp-2.png")
Material("exp-3", "Tactical Battle Record", 4, "exp-3.png")
Material("exp-4", "Strategic Battle Record", 5, "exp-4.png")

Material("skill-1", "Skill Summary - 1", 2, "skill-1.png")
Material("skill-2", "Skill Summary - 2", 3, "skill-2.png", recipe={"skill-1": 3})
Material("skill-3", "Skill Summary - 3", 4, "skill-3.png", recipe={"skill-2": 3})

Material("module-1", "Module Data Block", 5, "module-1.png",
         externalFileName="%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%A8%A1%E7%BB%84%E6%95%B0%E6%8D%AE%E5%9D%97")
Material("module-2", "Data Supplement Stick", 4, "module-2.png",
         externalFileName="%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%95%B0%E6%8D%AE%E5%A2%9E%E8%A1%A5%E6%9D%A1")
Material("module-3", "Data Supplement Instrument", 5, "module-3.png",
         externalFileName="%E9%81%93%E5%85%B7_%E5%B8%A6%E6%A1%86_%E6%95%B0%E6%8D%AE%E5%A2%9E%E8%A1%A5%E4%BB%AA")

Material("chip-catalyst", "Chip Catalyst", 4, "chip-catalyst.png")

Material("chip-vanguard-1", "Vanguard Chip", 3, "chip-vanguard-1.png")
Material("chip-vanguard-2", "Vanguard Chip Pack", 4, "chip-vanguard-2.png")
Material("chip-vanguard-3", "Vanguard Dualchip", 5, "chip-vanguard-3.png", recipe={"chip-vanguard-2": 2, "chip-catalyst": 1})

Material("chip-guard-1", "Guard Chip", 3, "chip-guard-1.png")
Material("chip-guard-2", "Guard Chip Pack", 4, "chip-guard-2.png")
Material("chip-guard-3", "Guard Dualchip", 5, "chip-guard-3.png", recipe={"chip-guard-2": 2, "chip-catalyst": 1})

Material("chip-caster-1", "Caster Chip", 3, "chip-caster-1.png")
Material("chip-caster-2", "Caster Chip Pack", 4, "chip-caster-2.png")
Material("chip-caster-3", "Caster Dualchip", 5, "chip-caster-3.png", recipe={"chip-caster-2": 2, "chip-catalyst": 1})

Material("chip-sniper-1", "Sniper Chip", 3, "chip-sniper-1.png")
Material("chip-sniper-2", "Sniper Chip Pack", 4, "chip-sniper-2.png")
Material("chip-sniper-3", "Sniper Dualchip", 5, "chip-sniper-3.png", recipe={"chip-sniper-2": 2, "chip-catalyst": 1})

Material("chip-defender-1", "Defender Chip", 3, "chip-defender-1.png")
Material("chip-defender-2", "Defender Chip Pack", 4, "chip-defender-2.png")
Material("chip-defender-3", "Defender Dualchip", 5, "chip-defender-3.png", recipe={"chip-defender-2": 2, "chip-catalyst": 1})

Material("chip-healer-1", "Medic Chip", 3, "chip-healer-1.png")
Material("chip-healer-2", "Medic Chip Pack", 4, "chip-healer-2.png")
Material("chip-healer-3", "Medic Dualchip", 5, "chip-healer-3.png", recipe={"chip-healer-2": 2, "chip-catalyst": 1})

Material("chip-supporter-1", "Supporter Chip", 3, "chip-supporter-1.png")
Material("chip-supporter-2", "Supporter Chip Pack", 4, "chip-supporter-2.png")
Material("chip-supporter-3", "Supporter Dualchip", 5, "chip-supporter-3.png", recipe={"chip-supporter-2": 2, "chip-catalyst": 1})

Material("chip-specialist-1", "Specialist Chip", 3, "chip-specialist-1.png")
Material("chip-specialist-2", "Specialist Chip Pack", 4, "chip-specialist-2.png")
Material("chip-specialist-3", "Specialist Dualchip", 5, "chip-specialist-3.png", recipe={"chip-specialist-2": 2, "chip-catalyst": 1})


DEPOT_ORDER = ["exp-4", "exp-3", "exp-2", "exp-1", "skill-3", "skill-2", "skill-1", "module-1", "module-3", "module-2",
               "steel-5", "nanoflake-5", "polymer-5",
               "kohl-4", "kohl-3", "manganese-4", "manganese-3", "grindstone-4", "grindstone-3", "rma-4", "rma-3",
               "rock-4", "rock-3", "rock-2", "rock-1", "device-4", "device-3", "device-2", "device-1",
               "plastic-4", "plastic-3", "plastic-2", "plastic-1", "sugar-4", "sugar-3", "sugar-2", "sugar-1",
               "oriron-4", "oriron-3", "oriron-2", "oriron-1", "keton-4", "keton-3", "keton-2", "keton-1",
               "gel-4", "gel-3", "incandescent-4", "incandescent-3", "crystal-5", "crystal-4", "crystal-3",
               "solvent-4", "solvent-3", "fluid-4", "fluid-3",
               "chip-catalyst",
               "chip-vanguard-3", "chip-guard-3", "chip-defender-3", "chip-sniper-3", "chip-caster-3", "chip-healer-3", "chip-supporter-3", "chip-specialist-3",
               "chip-vanguard-2", "chip-guard-2", "chip-defender-2", "chip-sniper-2", "chip-caster-2", "chip-healer-2", "chip-supporter-2", "chip-specialist-2",
               "chip-vanguard-1", "chip-guard-1", "chip-defender-1", "chip-sniper-1", "chip-caster-1", "chip-healer-1", "chip-supporter-1", "chip-specialist-1",
]

rawOperators = json.load(open("operators.json", "r"))
for o in rawOperators:
    Operator(**o)