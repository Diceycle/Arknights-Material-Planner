import math
import threading
from tkinter import *

from utilImport import *
from GlobalOverlays import OVERLAYS, GlobalSelection
from ItemIndicator import ItemIndicator
from widgets import LockableCanvas, ImageCheckbutton

class ItemSet(LockableCanvas):
    def __init__(self, parent, operator, upgrade, materials, scale, maxItems):

        self.maxItems = maxItems
        self.width = ItemSet.getWidth(maxItems, scale)
        super().__init__(parent, highlightthickness=0, bd=0, bg=CONFIG.color, width=self.width, height=scale)

        self.operator = operator
        self.upgrade = upgrade
        self.materials = {}
        for m in list(materials.keys()):
            self.addMaterialInternal(m, materials[m])

        self.itemIndicators = []

        self.scale = scale

        self.operatorImage = self.create_image(self.getLeftOffset(), 0, anchor=NW)
        self.upgradeImage = self.create_image(self.getLeftOffset() + self.scale + self.scale // 2, self.scale // 2, anchor=CENTER)

        self.init()

    def init(self):
        self.draw()

    def addMaterialInternal(self, material, amount):
        self.materials[material] = IntVar(value=amount)

    def draw(self):
        for i in self.itemIndicators:
            i.delete()

        self.itemIndicators = []

        self.itemconfigure(self.operatorImage, image=self.operator.getPhotoImage(self.scale))
        self.drawUpgrade()

        c = 0
        for m in self.materials.keys():
            x, y = self.getMaterialCoords(c)
            self.itemIndicators.append(ItemIndicator(self, self.scale, m, x, y, self.scale // 5,
                                                     self.materials[m], editable=False))
            c += 1

        self.resize(height=self.getHeight())

    def drawUpgrade(self):
        self.itemconfigure(self.upgradeImage, image=self.upgrade.getPhotoImage(self.scale, operator=self.operator))

    def getMaterialCoords(self, c):
        return (self.getLeftOffset() + self.scale * 2 + (c % self.maxItems) * self.scale,
                (c // self.maxItems) * self.scale)

    def getHeight(self):
        return max(int(math.ceil(len(self.materials) / self.maxItems)) * self.scale, self.scale)

    def getLeftOffset(self):
        return 0

    @staticmethod
    def getWidth(maxItems, scale):
        return (3 + maxItems) * scale

class ResearchItemSet(ItemSet):
    def __init__(self, parent, operator, upgrade, materials, scale, updateCallback = None, maxItems = 4, enabled = True,
                 naturalOrder = True):

        self.uiIconScale = scale // 2
        self.updateCallback = updateCallback
        self.naturalOrder = naturalOrder

        self.researching = False

        super().__init__(parent, operator, upgrade, materials, scale, maxItems)

        self.dragHandle = self.create_image(0, self.scale // 2, image=UI_ELEMENTS["drag"].getPhotoImage(self.uiIconScale), anchor=W)

        self.tag_bind(self.operatorImage, "<Button-1>", lambda e: self.changeOperator())
        self.tag_bind(self.upgradeImage, "<Button-1>", lambda e: self.changeUpgrade())

        self.loadingImage = self.create_image(self.scale * 2 + self.scale // 2, 0, image=UI_ELEMENTS["loading"].getPhotoImage(self.scale, transparency=0.75), anchor = NW, state="hidden")
        self.notAvailable = self.create_image(self.scale * 2 + self.scale // 2, 0, image=UI_ELEMENTS["n-a"].getPhotoImage(self.scale, transparency=0.75), anchor = NW, state="hidden")

        self.enabled = enabled
        self.enableButton = ImageCheckbutton(self, self.width, self.scale, anchor = SE, callback=self.toggle,
            images=(UI_ELEMENTS["check-off"].getPhotoImage(self.uiIconScale),
                    UI_ELEMENTS["check-on"].getPhotoImage(self.uiIconScale)))
        self.enableButton.setState(self.enabled)

        self.deleteButton = self.create_image(self.width, 0, image=UI_ELEMENTS["close"].getPhotoImage(self.uiIconScale), anchor=NE)

        self.researchMaterials()

    def init(self):
        pass

    def draw(self):
        super().draw()

        if len(self.materials) == 0 and not self.researching:
            self.itemconfigure(self.notAvailable, state="normal")
        else:
            self.itemconfigure(self.notAvailable, state="hidden")

        if self.researching:
            self.itemconfigure(self.loadingImage, state="normal")
        else:
            self.itemconfigure(self.loadingImage, state="hidden")

    def drawUpgrade(self):
        operator = None
        if not self.researching:
            operator = self.operator
        self.itemconfigure(self.upgradeImage, image=self.upgrade.getPhotoImage(self.scale, operator=operator))

    def addMaterialInternal(self, material, amount):
        super().addMaterialInternal(material, amount)
        self.materials[material].trace("w", lambda *args: self.updateAmounts())

    def researchMaterials(self):
        if self.operator.hasCache():
            self.researching = False
            self.replaceMaterials(self.upgrade.calculateCosts(self.operator.getCosts()))
        else:
            if not self.researching:
                self.researching = True
                self.replaceMaterials({})
                threading.Thread(target=self.operator.getCosts).start()
            self.after(1, self.researchMaterials)

    def replaceMaterials(self, materials):
        self.materials = {}
        order = list(materials.keys())
        if not self.naturalOrder:
            order.sort(key = lambda m: m.getSearchKey())
        for m in order:
            self.addMaterialInternal(m, materials[m])
        self.updateInternal()

    def updateInternal(self):
        self.updateAmounts()
        self.draw()

    def changeOperator(self):
        OVERLAYS["OperatorSelection"].registerCallback(self, posX = + self.getLeftOffset(), posY = self.scale, callback = lambda op : self.changeOperatorInternal(op))

    def changeOperatorInternal(self, operator):
        self.operator = operator
        self.researchMaterials()
        self.draw()

    def changeUpgrade(self):
        OVERLAYS["UpgradeSelection"].registerCallback(self, posX = self.scale + self.getLeftOffset(), posY = self.scale,
                                                      callback = lambda op : self.changeUpgradeInternal(op), operator = self.operator)

    def changeUpgradeInternal(self, upgrade):
        self.upgrade = upgrade
        self.researchMaterials()
        self.draw()

    def toggle(self, state):
        self.enabled = state
        self.updateAmounts()

    def updateAmounts(self):
        if self.updateCallback is not None:
            self.updateCallback()

    def getMaterials(self):
        return unpackVar(self.materials)

    def getLeftOffset(self):
        return self.uiIconScale

class RecipeDisplay(GlobalSelection):
    def __init__(self, parent, scale, **kwargs):
        width = 5*scale
        super().__init__(parent, "RecipeDisplay", width=width, height=1*scale, **kwargs)

        self.scale = scale
        self.width = width
        self.arrow = UI_ELEMENTS["craft-arrow"]

        self.itemSet = None

    def callDisableCallback(self):
        self.disableCallback(self.cancelCallback)

    def displayRecipe(self, parent, targetMaterial, x, y):
        if targetMaterial.isCraftable():
            if self.itemSet is not None:
                self.itemSet.destroy()
            self.itemSet = ItemSet(self, targetMaterial, self.arrow, targetMaterial.getIngredients(), self.scale, maxItems=3)
            self.itemSet.bind("<Button-3>", lambda e: self.cancelCallback())
            self.itemSet.place(x=2, y=2, width=self.width)
            super().registerCallback(parent, x, y, None)