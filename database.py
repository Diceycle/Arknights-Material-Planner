import os
import sys

from PIL import Image, ImageTk, ImageColor

from config import CONFIG

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
        if CONFIG.highlightColor == "#FFFFFF":
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
    def __init__(self, name, canonicalName, image, skill = None, **kwargs):
        super().__init__(name, UPGRADES, "img/misc", image, **kwargs)
        self.canonicalName = canonicalName
        self.skill = skill

    def getPhotoImage(self, size):
        return super().getPhotoImage(size * UPGRADE_SCALE)

    def renderImage(self):
        im = self.image.copy()
        if self.skill is not None:
            im.alpha_composite(loadImage("img/misc", "S" + str(self.skill) + ".png"))

        return im

class Operator(ScalableImage):
    def __init__(self, name, image, externalName = None):
        super().__init__(name, OPERATORS, "img/operator", image)

        self.externalName = externalName
        if self.externalName is None:
            self.externalName = name.lower().replace(" ", "-")

class Material(ScalableImage):
    def __init__(self, name, canonicalName, tier, image, recipe = None):
        super().__init__(name, MATERIALS, "img/material", image)
        self.canonicalName = canonicalName
        self.tier = tier

        self.recipe = recipe

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
        elif self.name.startswith("module"):
            return 5-int(self.name[self.name.find("-")+1:]), 13

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

Upgrade("E1", "Elite 1", "1.png", mainDimension=0)
Upgrade("E2", "Elite 2", "2.png", mainDimension=0)
Upgrade("SK7", "Skill rank 7", "7.png", mainDimension=0)
Upgrade("S1M1", "Skill 1 Mastery 1", "m-1.png", skill = 1, mainDimension=0)
Upgrade("S1M2", "Skill 1 Mastery 2", "m-2.png", skill = 1, mainDimension=0)
Upgrade("S1M3", "Skill 1 Mastery 3", "m-3.png", skill = 1, mainDimension=0)
Upgrade("S2M1", "Skill 2 Mastery 1", "m-1.png", skill = 2, mainDimension=0)
Upgrade("S2M2", "Skill 2 Mastery 2", "m-2.png", skill = 2, mainDimension=0)
Upgrade("S2M3", "Skill 2 Mastery 3", "m-3.png", skill = 2, mainDimension=0)
Upgrade("S3M1", "Skill 3 Mastery 1", "m-1.png", skill = 3, mainDimension=0)
Upgrade("S3M2", "Skill 3 Mastery 2", "m-2.png", skill = 3, mainDimension=0)
Upgrade("S3M3", "Skill 3 Mastery 3", "m-3.png", skill = 3, mainDimension=0)

Material("keton-1", "Diketon", 1, "keton-1.png")
Material("keton-2", "Polyketon", 2, "keton-2.png", recipe={"keton-1": 3})
Material("keton-3", "Aketon", 3, "keton-3.png", recipe={"keton-2": 4})
Material("keton-4", "Keton Colloid", 4, "keton-4.png", recipe={"keton-3": 2, "sugar-3": 1, "manganese-3": 1})

Material("rock-1", "Orirock", 1, "rock-1.png")
Material("rock-2", "Orirock Cube", 2, "rock-2.png", recipe={"rock-1": 3})
Material("rock-3", "Orirock Cluster", 3, "rock-3.png", recipe={"rock-2": 5})
Material("rock-4", "Orirock Concentration", 4, "rock-4.png", recipe={"rock-3": 4})

Material("sugar-1", "Sugar Substitute", 1, "sugar-1.png")
Material("sugar-2", "Sugar", 2, "sugar-2.png", recipe={"sugar-1": 3})
Material("sugar-3", "Sugar Pack", 3, "sugar-3.png", recipe={"sugar-2": 4})
Material("sugar-4", "Sugar Lump", 4, "sugar-4.png", recipe={"sugar-3": 2, "oriron-3": 1, "manganese-3": 1})

Material("plastic-1", "Ester", 1, "plastic-1.png")
Material("plastic-2", "Polyester", 2, "plastic-2.png", recipe={"plastic-1": 3})
Material("plastic-3", "Polyester Pack", 3, "plastic-3.png", recipe={"plastic-2": 4})
Material("plastic-4", "Polyester Lump", 4, "plastic-4.png", recipe={"plastic-3": 2, "keton-3": 1, "kohl-3": 1})

Material("oriron-1", "Oriron Shard", 1, "oriron-1.png")
Material("oriron-2", "Oriron", 2, "oriron-2.png", recipe={"oriron-1": 3})
Material("oriron-3", "Oriron Cluster", 3, "oriron-3.png", recipe={"oriron-2": 4})
Material("oriron-4", "Oriron Block", 4, "oriron-4.png", recipe={"oriron-3": 2, "device-3": 1, "plastic-3": 1})

Material("device-1", "Damaged Device", 1, "device-1.png")
Material("device-2", "Device", 2, "device-2.png", recipe={"device-1": 3})
Material("device-3", "Integrated Device", 3, "device-3.png", recipe={"device-2": 4})
Material("device-4", "Optimized Device", 4, "device-4.png", recipe={"device-3": 1, "rock-3": 2, "grindstone-3": 1})

Material("rma-3", "RMA70-12", 3, "rma-3.png")
Material("rma-4", "RMA70-24", 4, "rma-4.png", recipe={"rma-3": 1, "rock-3": 2, "keton-3": 1})

Material("grindstone-3", "Grindstone", 3, "grindstone-3.png")
Material("grindstone-4", "Grindstone Pentahydrate", 4, "grindstone-4.png", recipe={"grindstone-3": 1, "oriron-3": 1, "device-3": 1})

Material("manganese-3", "Manganese Ore", 3, "manganese-3.png")
Material("manganese-4", "Manganese Trihydrate", 4, "manganese-4.png", recipe={"manganese-3": 2, "plastic-3": 1, "kohl-3": 1})

Material("kohl-3", "Loxic Kohl", 3, "kohl-3.png")
Material("kohl-4", "White Horse Kohl", 4, "kohl-4.png", recipe={"kohl-3": 1, "sugar-3": 1, "rma-3": 1})

Material("incandescent-3", "Incandescent Alloy", 3, "incandescent-3.png")
Material("incandescent-4", "Incandescent Alloy Block", 4, "incandescent-4.png", recipe={"device-3": 1, "grindstone-3": 1,"incandescent-3": 1})

Material("gel-3", "Coagulating Gel", 3, "gel-3.png")
Material("gel-4", "Polymerized Gel", 4, "gel-4.png", recipe={"oriron-3": 1, "gel-3": 1, "incandescent-3": 1})

Material("crystal-3", "Crystalline Component", 3, "crystal-3.png")
Material("crystal-4", "Crystalline Circuit", 4, "crystal-4.png", recipe={"crystal-3": 2, "gel-3": 1, "incandescent-3": 1})
Material("crystal-5", "Crystalline Electronic Unit", 5, "crystal-5.png", recipe={"crystal-4": 1, "gel-4": 2, "incandescent-4": 1})

Material("solvent-3", "Semi-Synthetic Solvent", 3, "solvent-3.png")
Material("solvent-4", "Refined Solvent", 4, "solvent-4.png", recipe={"solvent-3": 1, "fluid-3": 1, "gel-3": 1})

Material("fluid-3", "Compound Cutting Fluid", 3, "fluid-3.png")
Material("fluid-4", "Cutting Fluid Solution", 4, "fluid-4.png", recipe={"fluid-3": 1, "crystal-3": 1, "rma-3": 1})

Material("salt-3", "转质盐组", 3, "salt-3.png")
Material("salt-4", "转质盐聚块", 4, "salt-4.png", recipe={"salt-3": 2, "solvent-3": 1, "sugar-3": 1})
Material("salt-5", "烧结核凝晶", 5, "salt-5.png", recipe={"salt-4": 1, "fluid-4": 1, "solvent-4": 2})

Material("steel-5", "D32 Steel", 5, "steel-5.png", recipe={"manganese-4": 1, "grindstone-4": 1, "rma-4": 1})
Material("nanoflake-5", "Bipolar Nanoflake", 5, "nanoflake-5.png", recipe={"device-4": 1, "kohl-4": 2})
Material("polymer-5", "Polymerization Preparation", 5, "polymer-5.png", recipe={"rock-4": 1, "oriron-4": 1, "keton-4": 1})

Material("exp-1", "Drill Battle Record", 2, "exp-1.png")
Material("exp-2", "Frontline Battle Record", 3, "exp-2.png")
Material("exp-3", "Tactical Battle Record", 4, "exp-3.png")
Material("exp-4", "Strategic Battle Record", 5, "exp-4.png")

Material("skill-1", "Skill Summary - 1", 2, "skill-1.png")
Material("skill-2", "Skill Summary - 2", 3, "skill-2.png", recipe={"skill-1": 3})
Material("skill-3", "Skill Summary - 3", 4, "skill-3.png", recipe={"skill-2": 3})

Material("module-1", "Module Data Block", 5, "module-1.png")
Material("module-2", "Data Supplement Stick", 4, "module-2.png")
Material("module-3", "Data Supplement Instrument", 5, "module-3.png")

DEPOT_ORDER = ["exp-4", "exp-3", "exp-2", "exp-1", "skill-3", "skill-2", "skill-1", "module-1", "module-3", "module-2",
               "steel-5", "nanoflake-5", "polymer-5",
               "kohl-4", "kohl-3", "manganese-4", "manganese-3", "grindstone-4", "grindstone-3", "rma-4", "rma-3",
               "rock-4", "rock-3", "rock-2", "rock-1", "device-4", "device-3", "device-2", "device-1",
               "plastic-4", "plastic-3", "plastic-2", "plastic-1", "sugar-4", "sugar-3", "sugar-2", "sugar-1",
               "oriron-4", "oriron-3", "oriron-2", "oriron-1", "keton-4", "keton-3", "keton-2", "keton-1",
               "gel-4", "gel-3", "incandescent-4", "incandescent-3", "crystal-5", "crystal-4", "crystal-3",
               "solvent-4", "solvent-3", "fluid-4", "fluid-3"]

Operator("Amiya", "char_002_amiya.png")
Operator("Kal'tsit", "char_003_kalts.png", externalName="kaltsit")
Operator("12F", "char_009_12fce.png")
Operator("Ch'en", "char_010_chen.png", externalName="chen")
Operator("Huang", "char_017_huang.png")
Operator("Amiya (Guard)", "char_1001_amiya2.png", externalName="amiya-guard")
Operator("Lava Purgatory Alter", "char_1011_lava2.png", externalName="lava-purgatory")
Operator("Skadi Corrupting Heart Alter", "char_1012_skadi2.png", externalName="skadi-corrupting-heart")
Operator("Ch'en Holungday Alter", "char_1013_chen2.png", externalName="chen-holungday")
Operator("Nearl Radiant Knight Alter", "char_1014_nearl2.png", externalName="nearl-radiant-knight")
Operator("Sora", "char_101_sora.png")
Operator("Reed Flame Shadow Alter", "char_1020_reed2.png", externalName="reed-flame-shadow")
Operator("Kroos Keen Glint Alter", "char_1021_kroos2.png", externalName="kroos-keen-glint")
Operator("Specter Unchained Alter", "char_1023_ghost2.png", externalName="specter-unchained")
Operator("Hibiscus Purifier Alter", "char_1024_hbisc2.png", externalName="hibiscus-purifier")
Operator("Gavial Invincible Alter", "char_1026_gvial2.png", externalName="gavial-invincible")
Operator("Greyy Lightningbearer Alter", "char_1027_greyy2.png", externalName="greyy-lightningbearer")
Operator("Texas Omertosa Alter", "char_1028_texas2.png", externalName="texas-omertosa")
Operator("Texas", "char_102_texas.png")
Operator("Exusiai", "char_103_angel.png")
Operator("Franka", "char_106_franka.png")
Operator("Liskarm", "char_107_liskam.png")
Operator("Silence", "char_108_silent.png")
Operator("Gitano", "char_109_fmout.png")
Operator("Deepcolor", "char_110_deepcl.png")
Operator("Siege", "char_112_siege.png")
Operator("W", "char_113_cqbw.png")
Operator("Zima", "char_115_headbr.png")
Operator("Myrrh", "char_117_myrrh.png")
Operator("Shirayuki", "char_118_yuki.png")
Operator("Hibiscus", "char_120_hibisc.png")
Operator("Lava", "char_121_lava.png")
Operator("Beagle", "char_122_beagle.png")
Operator("Fang", "char_123_fang.png")
Operator("Kroos", "char_124_kroos.png")
Operator("Meteor", "char_126_shotst.png")
Operator("Estelle", "char_127_estell.png")
Operator("Ptilopsis", "char_128_plosis.png")
Operator("Blue Poison", "char_129_bluep.png")
Operator("Doberman", "char_130_doberm.png")
Operator("Flamebringer", "char_131_flameb.png")
Operator("May", "char_133_mm.png")
Operator("Ifrit", "char_134_ifrit.png")
Operator("Astgenne", "char_135_halo.png")
Operator("Hoshiguma", "char_136_hsguma.png")
Operator("Beehunter", "char_137_brownb.png")
Operator("Lappland", "char_140_whitew.png")
Operator("Haze", "char_141_nights.png")
Operator("Specter", "char_143_ghost.png")
Operator("Projekt Red", "char_144_red.png")
Operator("Provence", "char_145_prove.png")
Operator("Shining", "char_147_shining.png")
Operator("Nearl", "char_148_nearl.png")
Operator("Scavenger", "char_149_scave.png")
Operator("Cuora", "char_150_snakek.png")
Operator("Myrtle", "char_151_myrtle.png")
Operator("Indra", "char_155_tiger.png")
Operator("Dagda", "char_157_dagda.png")
Operator("Firewatch", "char_158_milu.png")
Operator("Conviction", "char_159_peacok.png")
Operator("Vulcan", "char_163_hpsts.png")
Operator("Nightmare", "char_164_nightm.png")
Operator("Skyfire", "char_166_skfire.png")
Operator("Warfarin", "char_171_bldsk.png")
Operator("Silverash", "char_172_svrash.png")
Operator("Cliffheart", "char_173_slchan.png")
Operator("Pramanix", "char_174_slbell.png")
Operator("Nightingale", "char_179_cgbird.png")
Operator("Eyjafjalla", "char_180_amgoat.png")
Operator("Perfumer", "char_181_flower.png")
Operator("Earthspirit", "char_183_skgoat.png")
Operator("Mousse", "char_185_frncat.png")
Operator("Gavial", "char_187_ccheal.png")
Operator("Helagur", "char_188_helage.png")
Operator("Vermeil", "char_190_clour.png")
Operator("Plume", "char_192_falco.png")
Operator("Frostleaf", "char_193_frostl.png")
Operator("Istina", "char_195_glassb.png")
Operator("Gummy", "char_196_sunbr.png")
Operator("Rosa", "char_197_poca.png", externalName="rosa-poca")
Operator("Courier", "char_198_blackd.png")
Operator("Matterhorn", "char_199_yak.png")
Operator("Ceobe", "char_2013_cerber.png")
Operator("Nian", "char_2014_nian.png")
Operator("Dusk", "char_2015_dusk.png")
Operator("Croissant", "char_201_moeshd.png")
Operator("Ling", "char_2023_ling.png")
Operator("Chyue", "char_2024_chyue.png")
Operator("Saria", "char_202_demkni.png")
Operator("Platinum", "char_204_platnm.png")
Operator("Gnosis", "char_206_gnosis.png")
Operator("Melantha", "char_208_melan.png")
Operator("Cardigan", "char_209_ardign.png")
Operator("Steward", "char_210_stward.png")
Operator("Adnachiel", "char_211_adnach.png")
Operator("Ansel", "char_212_ansel.png")
Operator("Mostima", "char_213_mostma.png")
Operator("Kafka", "char_214_kafka.png")
Operator("Manticore", "char_215_mantic.png")
Operator("Andreana", "char_218_cuttle.png")
Operator("Meteorite", "char_219_meteo.png")
Operator("Grani", "char_220_grani.png")
Operator("Bagpipe", "char_222_bpipe.png")
Operator("Aak", "char_225_haak.png")
Operator("Hung", "char_226_hmau.png")
Operator("Savage", "char_230_savage.png")
Operator("Jessica", "char_235_jesica.png")
Operator("Rope", "char_236_rope.png")
Operator("Gravel", "char_237_gravel.png")
Operator("Vanilla", "char_240_wyvern.png")
Operator("Feater", "char_241_panda.png")
Operator("Mayer", "char_242_otter.png")
Operator("Waai Fu", "char_243_waaifu.png")
Operator("Magellan", "char_248_mgllan.png")
Operator("Phantom", "char_250_phatom.png")
Operator("Bibeak", "char_252_bibeak.png")
Operator("Greyy", "char_253_greyy.png")
Operator("Shamare", "char_254_vodfox.png")
Operator("Podenco", "char_258_podego.png")
Operator("Dur-Nar", "char_260_durnar.png")
Operator("Reed", "char_261_sddrag.png")
Operator("Skadi", "char_263_skadi.png")
Operator("Mountain", "char_264_f12yin.png")
Operator("Whislash", "char_265_sophia.png")
Operator("Arene", "char_271_spikes.png")
Operator("Jaye", "char_272_strong.png")
Operator("Astesia", "char_274_astesi.png")
Operator("Breeze", "char_275_breeze.png")
Operator("Shaw", "char_277_sqrrel.png")
Operator("Orchid", "char_278_orchid.png")
Operator("Executor", "char_279_excu.png")
Operator("Popucar", "char_281_popka.png")
Operator("Catapult", "char_282_catap.png")
Operator("Midnight", "char_283_midn.png")
Operator("Spot", "char_284_spot.png")
Operator("Lancet-2", "char_285_medic2.png")
Operator("Castle-3", "char_286_cast3.png")
Operator("Matoimaru", "char_289_gyuki.png")
Operator("Vigna", "char_290_vigna.png")
Operator("Angelina", "char_291_aglina.png")
Operator("Thorns", "char_293_thorns.png")
Operator("Ayerscarpe", "char_294_ayer.png")
Operator("Harmonie", "char_297_hamoni.png")
Operator("Sussurro", "char_298_susuro.png")
Operator("Fiametta", "char_300_phenxi.png")
Operator("Cutter", "char_301_cutter.png")
Operator("Ambriel", "char_302_glaze.png")
Operator("Heavyrain", "char_304_zebra.png")
Operator("Leizi", "char_306_leizi.png")
Operator("Swire", "char_308_swire.png")
Operator("Mudrock", "char_311_mudrok.png")
Operator("Lee", "char_322_lmlee.png")
Operator("Bison", "char_325_bison.png")
Operator("Glaucus", "char_326_glacus.png")
Operator("Click", "char_328_cammou.png")
Operator("Archetto", "char_332_archet.png")
Operator("Sideroca", "char_333_sidero.png")
Operator("Scene", "char_336_folivo.png")
Operator("Utage", "char_337_utage.png")
Operator("Iris", "char_338_iris.png")
Operator("Schwarz", "char_340_shwaz.png")
Operator("Tsukinogi", "char_343_tknogi.png")
Operator("Beeswax", "char_344_beewax.png")
Operator("Folinic", "char_345_folnic.png")
Operator("Aosta", "char_346_aosta.png")
Operator("Jackie", "char_347_jaksel.png")
Operator("Ceylon", "char_348_ceylon.png")
Operator("Chiave", "char_349_chiave.png")
Operator("Surtr", "char_350_surtr.png")
Operator("Ethan", "char_355_ethan.png")
Operator("Broca", "char_356_broca.png")
Operator("Suzuran", "char_358_lisa.png")
Operator("Saga", "char_362_saga.png")
Operator("Toddifoons", "char_363_toddi.png")
Operator("April", "char_365_aprl.png")
Operator("Aciddrop", "char_366_acdrop.png")
Operator("Greythroat", "char_367_swllow.png")
Operator("Bena", "char_369_bena.png")
Operator("Leonhart", "char_373_lionhd.png")
Operator("Therm-Ex", "char_376_therex.png")
Operator("Goldenglow", "char_377_gdglow.png")
Operator("Asbestos", "char_378_asbest.png")
Operator("Sesa", "char_379_sesa.png")
Operator("Bubble", "char_381_bubble.png")
Operator("Snowsant", "char_383_snsant.png")
Operator("Purestream", "char_385_finlpp.png")
Operator("Mint", "char_388_mint.png")
Operator("Rosmontis", "char_391_rosmon.png")
Operator("Justiceknight", "char_4000_jnight.png")
Operator("Pudding", "char_4004_pudd.png")
Operator("Irene", "char_4009_irene.png")
Operator("Weedy", "char_400_weedy.png")
Operator("Kjera", "char_4013_kjera.png")
Operator("Lunacub", "char_4014_lunacu.png")
Operator("Kazemaru", "char_4016_kazema.png")
Operator("Puzzle", "char_4017_puzzle.png")
Operator("Nine Colored Deer", "char_4019_ncdeer.png")
Operator("Elysium", "char_401_elysm.png")
Operator("Tuye", "char_402_tuye.png")
Operator("Proviso", "char_4032_provs.png")
Operator("Enforcer", "char_4036_forcer.png")
Operator("Horn", "char_4039_horn.png")
Operator("Rockrock", "char_4040_rockr.png")
Operator("Chestnut", "char_4041_chnut.png")
Operator("Lumen", "char_4042_lumen.png")
Operator("Erato", "char_4043_erato.png")
Operator("Heidi", "char_4045_heidi.png")
Operator("Ebenholz", "char_4046_ebnhlz.png")
Operator("Czerny", "char_4047_pianst.png")
Operator("Dorothy", "char_4048_doroth.png")
Operator("Minimalist", "char_4054_malist.png")
Operator("Pozyomka", "char_4055_bgsnow.png", externalName="pozemka")
Operator("Absinthe", "char_405_absin.png")
Operator("Totter", "char_4062_totter.png")
Operator("Quartz", "char_4063_quartz.png")
Operator("Mlynar", "char_4064_mlynar.png")
Operator("Penance", "char_4065_judge.png")
Operator("Highmore", "char_4066_highmo.png")
Operator("Luo Xiaohei", "char_4067_lolxh.png")
Operator("Paprika", "char_4071_peper.png")
Operator("Stainless", "char_4072_ironmn.png")
Operator("Jieyun", "char_4078_bdhkgt.png")
Operator("Lin", "char_4080_lin.png")
Operator("Qiubai", "char_4082_qiubai.png")
Operator("Chimes", "char_4083_chimes.png")
Operator("Tomimi", "char_411_tomimi.png")
Operator("Flint", "char_415_flint.png")
Operator("Eunectes", "char_416_zumama.png")
Operator("Flametail", "char_420_flamtl.png")
Operator("La Pluma", "char_421_crow.png")
Operator("Aurora", "char_422_aurora.png")
Operator("Blemishine", "char_423_blemsh.png")
Operator("Carnelian", "char_426_billro.png")
Operator("Vigil", "char_427_vigil.png")
Operator("Fartooth", "char_430_fartth.png")
Operator("Ashlock", "char_431_ashlok.png")
Operator("Windflit", "char_433_windft.png")
Operator("Whisperain", "char_436_whispr.png")
Operator("Mizuki", "char_437_mizuki.png")
Operator("Pinecone", "char_440_pinecn.png")
Operator("Honeyberry", "char_449_glider.png")
Operator("Robin", "char_451_robin.png")
Operator("Beanstalk", "char_452_bstalk.png")
Operator("Mr. Nothing", "char_455_nothin.png")
Operator("Ash", "char_456_ash.png")
Operator("Blitz", "char_457_blitz.png")
Operator("Frost", "char_458_rfrost.png")
Operator("Tachanka", "char_459_tachak.png")
Operator("Qanipalaat", "char_466_qanik.png")
Operator("Indigo", "char_469_indigo.png")
Operator("Passenger", "char_472_pasngr.png")
Operator("Mulberry", "char_473_mberry.png")
Operator("Gladiia", "char_474_glady.png")
Operator("Akafuyu", "char_475_akafyu.png")
Operator("Blacknight", "char_476_blkngt.png")
Operator("Kirara", "char_478_kirara.png")
Operator("Saileach", "char_479_sleach.png")
Operator("Roberta", "char_484_robrta.png")
Operator("Pallas", "char_485_pallas.png")
Operator("Tequila", "char_486_takila.png")
Operator("Corroserum", "char_489_serum.png")
Operator("Quercus", "char_492_quercu.png")
Operator("Firewhistle", "char_493_firwhl.png")
Operator("Wildmane", "char_496_wildmn.png")
Operator("Cantabile", "char_497_ctable.png")
Operator("Noir Corne", "char_500_noirc.png")
Operator("Durin", "char_501_durin.png")
Operator("Yato", "char_502_nblade.png")
Operator("Ranger", "char_503_rang.png")
Operator("Shalem", "char_512_aprot.png")