import time
from collections import Counter
from tkinter import *

from ItemSet import ItemSet
from database import *
from widgets import LockableCanvas


class ItemSetDisplay(LockableCanvas):
    def __init__(self, parent, scale, height, spacing, scrollFPS = 25, scrollSpeed = 20, maxItems = 4,
                 totalsUpdateCallback=None):
        self.scale = scale
        self.scrollbarWidth = scale // 4
        self.width = ItemSet.getWidth(maxItems, scale) + self.scrollbarWidth
        self.height = height
        super().__init__(parent, height=self.height, width=self.width, highlightthickness=0, bg=CONFIG.colorDark)

        self.maxItems = maxItems
        self.spacing = spacing
        self.scrollFPS = scrollFPS
        self.scrollSpeed = scrollSpeed
        self.totalsUpdateCallback = totalsUpdateCallback

        self.currentSet = None
        self.currentSetWidget = None

        self.addSetButton = self.create_image(0, 0, image=UI_ELEMENTS["add-set"].getPhotoImage(self.scale, transparency=0.75), anchor = NW)
        self.tag_bind(self.addSetButton, "<Button-1>", lambda e: self.addSet(OPERATORS["Amiya"], UPGRADES["E1"], {}))

        self.scrollbarCanvas = LockableCanvas(self, height = self.height, width=self.scrollbarWidth, highlightthickness=0, bg=CONFIG.colorDark)
        self.scrollbarCanvas.place(relx = 1, y = 0, anchor=NE)
        self.addChildCanvas(self.scrollbarCanvas)
        self.scrollbar = self.scrollbarCanvas.create_rectangle(0, 0, 0, 0, fill=CONFIG.color, outline=CONFIG.highlightColor, width=1)
        self.bind("<MouseWheel>", self.scrollWheel)
        self.scrollbarCanvas.tag_bind(self.scrollbar, "<Button-1>", self.startScroll)
        self.scrollbarCanvas.tag_bind(self.scrollbar, "<B1-Motion>", self.scrollDrag)
        self.scrollbarCanvas.tag_bind(self.scrollbar, "<ButtonRelease-1>", lambda e: self.stopScroll())
        self.scrolling = False

        self.itemSets = []
        self.itemSetWidgets = []

    def addSet(self, operator, upgrade, materials, enabled=True):
        itemSet = ItemSet(self, operator, upgrade, materials, self.scale, updateCallback=self.updateItemTotals,
                          maxItems=self.maxItems, grabbable=True, deletable=True, enabled=enabled)
        itemSetWidget = self.create_window(0, 0, window=itemSet, anchor=NW)

        self.itemSets.append(itemSet)
        self.itemSetWidgets.append(itemSetWidget)
        self.addChildCanvas(itemSet)

        itemSet.bind("<MouseWheel>", self.scrollWheel)
        itemSet.tag_bind(itemSet.dragHandle, "<Button-1>", lambda e: self.pickUpSet(e, itemSet, itemSetWidget))
        itemSet.tag_bind(itemSet.dragHandle, "<B1-Motion>", self.dragCurrentSet)
        itemSet.tag_bind(itemSet.dragHandle, "<ButtonRelease-1>", lambda e: self.release())
        itemSet.tag_bind(itemSet.deleteButton, "<Button-1>", lambda e: self.removeSet(itemSet, itemSetWidget))
        self.updateItemTotals()
        self.draw()

    def removeSet(self, itemSet, setWidget):
        itemSet.destroy()
        self.itemSets.remove(itemSet)
        self.removeChildCanvas(itemSet)

        self.delete(setWidget)
        self.itemSetWidgets.remove(setWidget)

        self.updateItemTotals()
        self.draw()

    def updateItemTotals(self):
        if self.totalsUpdateCallback is not None:
            self.totalsUpdateCallback(self.getItemTotals())

    def getItemTotals(self):
        return sum([Counter(s.getMaterials()) for s in self.itemSets if s.enabled], Counter())

### UI-Methods ###

    def draw(self):
        for c in range(len(self.itemSetWidgets)):
            s = self.itemSetWidgets[c]
            if s != self.currentSetWidget:
                self.coords(s, 0, (self.scale + self.spacing) * c)

        self.coords(self.addSetButton, 0, (self.scale + self.spacing) * len(self.itemSets))
        self.updateViewbox()

    def pickUpSet(self, e, itemSet, widget):
        self.currentSet = itemSet
        self.currentSetWidget = widget
        self.setTime = time.time()
        self.winfo_toplevel().call('raise', itemSet, None)
        self.initialX = e.x
        self.initialY = e.y

    def dragCurrentSet(self, e):
        if self.currentSetWidget is not None and time.time() - self.setTime > 1 / self.scrollFPS:
            self.coords(self.currentSetWidget,
                        e.x - self.initialX + self.coords(self.currentSetWidget)[0],
                        e.y - self.initialY + self.coords(self.currentSetWidget)[1])
            self.setTime = time.time()
            self.dropInPosition(e)

    def dropInPosition(self, e):
        row = (e.y + int(self.coords(self.currentSetWidget)[1])) // (self.scale + self.spacing)
        self.itemSets.remove(self.currentSet)
        self.itemSets.insert(row, self.currentSet)
        self.itemSetWidgets.remove(self.currentSetWidget)
        self.itemSetWidgets.insert(row, self.currentSetWidget)
        self.draw()

    def release(self):
        self.currentSetWidget = None
        self.draw()

### SCROLLING ###

    def startScroll(self, e):
        self.scrolling = True
        self.lastScrollY = e.y

    def scrollDrag(self, e):
        if self.scrolling and time.time():
            self.updateViewbox((e.y - self.lastScrollY) * (self.getTotalHeight() / self.height))
            self.lastScrollY = e.y

    def scrollWheel(self, e):
        pixelScroll = -self.scrollSpeed * e.delta / abs(e.delta)
        self.updateViewbox(pixelScroll)

    def updateViewbox(self, delta = 0):
        if self.height >= self.getTotalHeight():
            self.scrollPercentage = 0
            self.config(scrollregion=(0, 0, self.width, self.height))

        else:
            excessHeight = self.getTotalHeight() - self.height
            self.scrollPercentage += delta / excessHeight
            self.scrollPercentage = min(1, max(0, self.scrollPercentage))

            self.config(scrollregion=(0, self.scrollPercentage*excessHeight, self.width, self.scrollPercentage*excessHeight + self.height))

        self.updateScrollbar()

    def updateScrollbar(self):
        displayedPercentage = min(1, self.height / self.getTotalHeight())
        scrollbarWiggleRoom = self.height *  (1 - displayedPercentage)

        self.scrollbarCanvas.coords(self.scrollbar,
                                    0, int(scrollbarWiggleRoom * self.scrollPercentage),
                                    self.scrollbarWidth - 1, self.height - int(scrollbarWiggleRoom * (1 - self.scrollPercentage)) - 1)

    def stopScroll(self):
        self.scrolling = False

    def getTotalHeight(self):
        return len(self.itemSets) * (self.scale + self.spacing) + self.scale