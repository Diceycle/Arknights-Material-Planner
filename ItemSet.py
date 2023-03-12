import math
import threading
from tkinter import *

from utilImport import *
from GlobalOverlays import OVERLAYS, GlobalSelection
from ItemIndicator import ItemIndicator
from widgets import LockableCanvas, ImageCheckbutton


class ItemSet(LockableCanvas):
    def __init__(self, parent, operator, upgrade, materials, scale, updateCallback = None, maxItems = 4,
                 grabbable = False, editable = True, deletable = False, toggleable = True, enabled = True,
                 researchOnly = False, allowMultipleRows = False):

        self.maxItems = maxItems
        self.width = ItemSet.getWidth(maxItems, scale)
        super().__init__(parent, highlightthickness=0, bd=0, bg=CONFIG.color, width=self.width, height=scale)

        self.operator = operator
        self.upgrade = upgrade
        self.materials = {}

        self.itemIndicators = []

        self.scale = scale
        self.uiIconScale = scale // 2

        self.updateCallback = updateCallback
        self.editable = editable
        self.researchOnly = researchOnly
        self.allowMultipleRows = allowMultipleRows

        self.researching = False

        self.dragOffset = 0
        if grabbable:
            self.dragHandle = self.create_image(0, self.scale // 2, image=UI_ELEMENTS["drag"].getPhotoImage(self.uiIconScale), anchor=W)
            self.dragOffset = self.uiIconScale
        self.operatorImage = self.create_image(self.dragOffset, 0, anchor=NW)
        if editable:
            self.tag_bind(self.operatorImage, "<Button-1>", lambda e: self.changeOperator())
        self.upgradeImage = self.create_image(self.dragOffset + self.scale + self.scale // 2, self.scale // 2, anchor=CENTER)
        if editable:
            self.tag_bind(self.upgradeImage, "<Button-1>", lambda e: self.changeUpgrade())

        self.loadingImage = self.create_image(self.scale * 2 + self.scale // 2, 0, image=UI_ELEMENTS["loading"].getPhotoImage(self.scale, transparency=0.75), anchor = NW, state="hidden")
        if researchOnly:
            self.notAvailable = self.create_image(self.scale * 2 + self.scale // 2, 0, image=UI_ELEMENTS["n-a"].getPhotoImage(self.scale, transparency=0.75), anchor = NW, state="hidden")

        if editable and not researchOnly:
            self.addButton = self.create_image(0, 0, image=UI_ELEMENTS["add"].getPhotoImage(self.scale, transparency=0.75), anchor=NW)
            self.tag_bind(self.addButton, "<Button-1>", lambda e: self.addMaterialTrigger())
            self.researchButton = self.create_image(0, 0, image=UI_ELEMENTS["research"].getPhotoImage(self.scale, transparency=0.75), anchor=NW)
            self.tag_bind(self.researchButton, "<Button-1>", lambda e: self.researchMaterials())

        if toggleable:
            self.enabled = enabled
            self.enableButton = ImageCheckbutton(self, self.width, self.scale, anchor = SE, callback=self.toggle,
                images=(UI_ELEMENTS["check-off"].getPhotoImage(self.uiIconScale),
                        UI_ELEMENTS["check-on"].getPhotoImage(self.uiIconScale)))
            self.enableButton.setState(self.enabled)
        if deletable:
            self.deleteButton = self.create_image(self.width, 0, image=UI_ELEMENTS["close"].getPhotoImage(self.uiIconScale), anchor=NE)

        if not self.researchOnly:
            for m, a in materials.items():
                self.addMaterialInternal(m, a)
            self.draw()
        else:
            self.researchMaterials()

    def draw(self):
        for i in self.itemIndicators:
            i.delete()

        self.itemIndicators = []

        self.itemconfigure(self.operatorImage, image=self.operator.getPhotoImage(self.scale))
        operator = None
        if not self.researching:
            operator = self.operator
        self.itemconfigure(self.upgradeImage, image=self.upgrade.getPhotoImage(self.scale, operator=operator))

        c = 0
        for m in self.materials.keys():
            x, y = self.getMaterialCoords(c)
            self.itemIndicators.append(ItemIndicator(self, self.scale, m, x, y, self.scale // 5,
                                                     self.materials[m], editable=self.editable and not self.researchOnly))
            if self.editable and not self.researchOnly:
                self.itemIndicators[-1].bind("<Button-3>", lambda e, mat=m: self.removeMaterial(mat))
            c += 1

        if self.researchOnly:
            if len(self.materials) == 0 and not self.researching:
                self.itemconfigure(self.notAvailable, state="normal")
            else:
                self.itemconfigure(self.notAvailable, state="hidden")

        if self.researching:
            self.itemconfigure(self.loadingImage, state="normal")
        else:
            self.itemconfigure(self.loadingImage, state="hidden")

        if self.editable and not self.researchOnly:
            if len(self.materials) < self.maxItems or self.allowMultipleRows:
                self.coords(self.addButton, self.getMaterialCoords(c))
                self.itemconfigure(self.addButton, state="normal")
            else:
                self.itemconfigure(self.addButton, state="hidden")

            if len(self.materials) == 0:
                self.coords(self.researchButton, self.getMaterialCoords(0))
                self.itemconfigure(self.researchButton, state="normal")
            else:
                self.itemconfigure(self.researchButton, state="hidden")

        if self.allowMultipleRows:
            self.resize(height=self.getHeight())

    def addMaterialTrigger(self):
        x, y = self.getMaterialCoords(len(self.materials.keys()))
        OVERLAYS["MaterialSelection"].registerCallback(self, posX = x, posY = y + self.scale, callback = lambda mat: self.addMaterial(mat))

    def addMaterialInternal(self, material, amount):
        self.materials[material] = IntVar(value = amount)
        self.materials[material].trace("w", lambda *args: self.updateAmounts())

    def addMaterial(self, material):
        self.addMaterialInternal(material, 1)
        self.updateInternal()

    def removeMaterial(self, material):
        del self.materials[material]
        self.updateInternal()

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
        for m, a in materials.items():
            self.addMaterialInternal(m, a)
        self.updateInternal()

    def updateInternal(self):
        self.updateAmounts()
        self.draw()

    def changeOperator(self):
        OVERLAYS["OperatorSelection"].registerCallback(self, posX = + self.dragOffset, posY = self.scale, callback = lambda op : self.changeOperatorInternal(op))

    def changeOperatorInternal(self, operator):
        self.operator = operator
        if self.researchOnly:
            self.researchMaterials()
        self.draw()

    def changeUpgrade(self):
        OVERLAYS["UpgradeSelection"].registerCallback(self, posX = self.scale + self.dragOffset, posY = self.scale,
                                                      callback = lambda op : self.changeUpgradeInternal(op), operator = self.operator)

    def changeUpgradeInternal(self, upgrade):
        self.upgrade = upgrade
        if self.researchOnly:
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

    def getMaterialCoords(self, c):
        return (self.dragOffset + self.scale * 2 + (c % self.maxItems) * self.scale,
                (c // self.maxItems) * self.scale)

    def getHeight(self):
        if not self.allowMultipleRows:
            return self.scale

        amountBoxes = len(self.materials)

        if not self.researchOnly:
            amountBoxes += 1

        return max(int(math.ceil(amountBoxes / self.maxItems)) * self.scale, self.scale)

    @staticmethod
    def getWidth(maxItems, scale):
        return (3 + maxItems) * scale

class RecipeDisplay(GlobalSelection):
    def __init__(self, parent, scale, **kwargs):
        width = 5*scale
        super().__init__(parent, "RecipeDisplay", width=width, height=1*scale, **kwargs)

        self.scale = scale

        self.targetMaterial = None
        self.arrow = UI_ELEMENTS["craft-arrow"]

        self.itemSet = ItemSet(self, MATERIALS["rock-3"], self.arrow, MATERIALS["rock-3"].getIngredients(), self.scale,
                               editable=False, toggleable=False, maxItems=3)
        self.itemSet.bind("<Button-3>", lambda e: self.cancelCallback())
        self.itemSet.place(x = 2, y = 2, width = width)

    def callDisableCallback(self):
        self.disableCallback(self.cancelCallback)

    def displayRecipe(self, parent, targetMaterial, x, y):
        if targetMaterial.isCraftable():
            self.itemSet.changeOperatorInternal(targetMaterial)
            self.itemSet.replaceMaterials(targetMaterial.getIngredients())
            super().registerCallback(parent, x, y, None)