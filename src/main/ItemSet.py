import math
from collections import Counter
from tkinter import *

from utilImport import *
from GlobalOverlays import OVERLAYS
from ItemIndicator import ItemIndicator
from widgets import LockableCanvas, ImageCheckbutton

class ItemSet(LockableCanvas):
    def __init__(self, parent, operator, upgrade, scale, maxItems, enabled, updateCallback, naturalOrder):

        self.maxItems = maxItems
        self.scale = scale
        self.uiIconScale = scale // 2
        self.width = (1 + self.maxItems) * self.scale + self.uiIconScale

        super().__init__(parent, highlightthickness=0, bd=0, bg=CONFIG.color, width=self.width, height=scale)

        self.operator = operator
        self.upgrade = upgrade
        self.itemIndicators = []

        self.updateCallback = updateCallback
        self.naturalOrder = naturalOrder

        self.upgradeImage = self.create_image(self.scale // 2, self.scale // 2, anchor=CENTER)

        self.notAvailable = self.create_image(self.scale + self.scale // 2, 0, image=UI_ELEMENTS["n-a"].getPhotoImage(self.scale, transparency=0.75), anchor = NW, state="hidden")

        self.initializing = True
        self.enabled = enabled
        self.enableButton = ImageCheckbutton(self, self.width, self.scale, anchor = SE, callback=self.toggle,
                                             images=(UI_ELEMENTS["check-off"].getPhotoImage(self.uiIconScale),
                                                     UI_ELEMENTS["check-on"].getPhotoImage(self.uiIconScale)))
        self.enableButton.setState(self.enabled)

        self.deleteButton = self.create_image(self.width, 0, image=UI_ELEMENTS["close"].getPhotoImage(self.uiIconScale), anchor=NE)
        self.initializing = False

    def draw(self):
        for i in self.itemIndicators:
            i.delete()

        self.itemIndicators = []
        self.itemconfigure(self.upgradeImage, image=self.upgrade.getPhotoImage(self.scale, operator=self.operator))

        materials = self.getMaterials()
        c = 0
        for m in materials.keys():
            x, y = self.getMaterialCoords(c)
            self.itemIndicators.append(ItemIndicator(self, self.scale, m, x, y, self.scale // 5,
                                                     IntVar(value=materials[m]), editable=False))
            c += 1

        if len(materials) == 0:
            self.itemconfigure(self.notAvailable, state="normal")
        else:
            self.itemconfigure(self.notAvailable, state="hidden")

        self.resize(height=self.getHeight())

    def toggle(self, state):
        self.enabled = state
        if not self.initializing:
            self.updateCallback()

    def getMaterials(self):
        mats = self.upgrade.calculateCosts(self.operator.costs)
        if not self.naturalOrder:
            matsSorted = {}
            order = list(mats.keys())
            order.sort(key = lambda m: m.getSortKey())
            for m in order:
                matsSorted[m] = mats[m]
            return matsSorted

        return mats

    def getMaterialCoords(self, c):
        return (self.scale + (c % self.maxItems) * self.scale,
                (c // self.maxItems) * self.scale)

    def getHeight(self):
        numMaterials = len(self.upgrade.calculateCosts(self.operator.costs))
        if numMaterials < self.maxItems:
            return self.scale

        return int(math.ceil(numMaterials / self.maxItems)) * self.scale

class UpgradeSet(LockableCanvas):
    def __init__(self, parent, operator, upgrades, scale, updateCallback = None, maxItems = 4,
                 naturalOrder = True, bindFunction = None):

        super().__init__(parent, highlightthickness=0, bd=0, bg=CONFIG.color, width=UpgradeSet.getWidth(maxItems, scale), height=scale)

        self.scale = scale
        self.uiIconScale = self.scale // 2

        self.researching = False

        self.updateCallback = updateCallback
        self.deleteCallback = None
        self.maxItems = maxItems
        self.naturalOrder = naturalOrder

        self.bindFunction = bindFunction
        self.bindFunction(self)

        self.operator = operator
        self.operatorImage = self.create_image(self.getLeftOffset(), 0, anchor=NW)
        self.tag_bind(self.operatorImage, "<Button-1>", lambda e: self.changeOperator())

        self.dragHandle = self.create_image(0, self.scale // 2, image=UI_ELEMENTS["drag"].getPhotoImage(self.uiIconScale), anchor=W)

        self.addUpgradeButton = self.create_image(0, 0, image=UI_ELEMENTS["add"].getPhotoImage(self.uiIconScale), anchor=S)
        self.tag_bind(self.addUpgradeButton, "<Button-1>", lambda e: self.addUpgrade())

        self.initializing = True
        self.itemSets = []
        for u in upgrades:
            self.addUpgradeInternal(u["upgrade"], u["enabled"])

        self.changeOperatorInternal(self.operator)
        self.initializing = False
        self.draw()

    def draw(self):
        if self.initializing:
            return

        self.itemconfigure(self.operatorImage, image=self.operator.getPhotoImage(self.scale))

        yPos = 0
        sets = self.itemSets.copy()
        if CONFIG.sortUpgrades:
            sets.sort(key=lambda s: s.upgrade.getSortKey())
        for itemSet in sets:
            itemSet.place_forget()
            itemSet.place(x = self.getLeftOffset() + self.scale, y = yPos)
            itemSet.draw()
            yPos += itemSet.getHeight()

        self.resize(height=self.getHeight())

        self.coords(self.addUpgradeButton, self.getLeftOffset() + self.scale + self.scale // 2, self.getHeight())

        self.updateCallback()

    def changeOperator(self):
        OVERLAYS["OperatorSelection"].registerCallback(self, posX = self.getLeftOffset(), posY = self.scale, callback = lambda op : self.changeOperatorInternal(op))

    def changeOperatorInternal(self, operator):
        self.operator = operator
        for s in self.itemSets:
            s.operator = operator
        self.draw()

    def changeUpgrade(self, upgradeSet):
        OVERLAYS["UpgradeSelection"].registerCallback(self, posX = self.getLeftOffset() + self.scale, posY = self.scale + upgradeSet.winfo_y(),
                                                      callback = lambda up : self.changeUpgradeInternal(up, upgradeSet), operator = self.operator)

    def changeUpgradeInternal(self, upgrade, itemSet):
        itemSet.upgrade = upgrade
        self.draw()

    def addUpgrade(self):
        OVERLAYS["UpgradeSelection"].registerCallback(self, posX = self.getLeftOffset() + self.scale, posY = self.getHeight(),
                                                      callback = lambda up : self.addUpgradeInternal(up, True), operator = self.operator)

    def addUpgradeInternal(self, upgrade, enabled):
        itemSet = ItemSet(self, self.operator, upgrade, self.scale, self.maxItems, enabled, self.updateCallback, self.naturalOrder)
        self.bindFunction(itemSet)
        itemSet.tag_bind(itemSet.deleteButton, "<Button-1>", lambda e: self.removeUpgrade(itemSet))
        itemSet.tag_bind(itemSet.upgradeImage, "<Button-1>", lambda e: self.changeUpgrade(itemSet))
        self.itemSets.append(itemSet)
        self.addChildCanvas(itemSet)

        self.draw()

    def removeUpgrade(self, itemSet):
        self.itemSets.remove(itemSet)
        self.removeChildCanvas(itemSet)
        itemSet.destroy()
        if len(self.itemSets) == 0:
            if self.deleteCallback is not None:
                self.deleteCallback()
        else:
            self.draw()

    def setDeleteCallBack(self, callback):
        self.deleteCallback = callback

    def getEnabledMaterials(self):
        return sum([Counter(s.getMaterials()) for s in self.itemSets if s.enabled], Counter())

    def getHeight(self):
        height = 0
        for u in self.itemSets:
            height += u.getHeight()
        return height + self.uiIconScale

    def getLeftOffset(self):
        return self.uiIconScale

    @staticmethod
    def getWidth(maxItems, scale):
        return (3 + maxItems) * scale