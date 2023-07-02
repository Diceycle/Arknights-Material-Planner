import time
from collections import Counter
from tkinter import *

from GlobalOverlays import OVERLAYS
from utilImport import *
from ItemSet import UpgradeSet
from widgets import LockableCanvas


class ItemSetDisplay(LockableCanvas):
    def __init__(self, parent, scale, height, spacing, scrollFPS = 25, scrollSpeed = 20, maxItems = 4,
                 totalsUpdateCallback=None):
        self.scale = scale
        self.scrollbarWidth = scale // 4
        self.width = UpgradeSet.getWidth(maxItems, scale) + self.scrollbarWidth
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
        self.tag_bind(self.addSetButton, "<Button-1>", lambda e: self.addSet())

        self.scrollbarCanvas = LockableCanvas(self, height = self.height, width=self.scrollbarWidth, highlightthickness=0, bg=CONFIG.colorDark)
        self.scrollbarCanvas.place(relx = 1, y = 0, anchor=NE)
        self.addChildCanvas(self.scrollbarCanvas)
        self.separatorRight = self.scrollbarCanvas.create_line(self.scrollbarWidth -1, 0, self.scrollbarWidth -1, self.height, fill=CONFIG.color)
        self.scrollbar = self.scrollbarCanvas.create_rectangle(0, 0, 0, 0, fill=CONFIG.color, outline=CONFIG.highlightColor, width=1)
        self.bind("<MouseWheel>", self.scrollWheel)
        self.scrollbarCanvas.bind("<MouseWheel>", self.scrollWheel)
        self.scrollbarCanvas.tag_bind(self.scrollbar, "<Button-1>", self.startScroll)
        self.scrollbarCanvas.tag_bind(self.scrollbar, "<B1-Motion>", self.scrollDrag)
        self.scrollbarCanvas.tag_bind(self.scrollbar, "<ButtonRelease-1>", lambda e: self.stopScroll())
        self.scrolling = False

        self.upgradeSets = []
        self.upgradeSetWidgets = []

        self.draw()

    def addSet(self):
        OVERLAYS["OperatorSelection"].registerCallback(self, posX = self.scale + self.scale // 2, posY = self.coords(self.addSetButton)[1],
                                                       callback = lambda op : self.addSetInternal(op, [{ "upgrade": UPGRADES["E1"], "enabled": True }]))

    def addSetInternal(self, operator, upgrades):
        upgradeSet = UpgradeSet(self, operator, upgrades, self.scale, updateCallback=self.updateItemTotals,
                             maxItems=self.maxItems, naturalOrder=CONFIG.maintainNaturalOrder,
                             bindFunction=lambda canvas: canvas.bind("<MouseWheel>", self.scrollWheel))
        upgradeSetWidget = self.create_window(0, 0, window=upgradeSet, anchor=NW)
        upgradeSet.setDeleteCallBack(lambda : self.removeSet(upgradeSet, upgradeSetWidget))

        self.upgradeSets.append(upgradeSet)
        self.upgradeSetWidgets.append(upgradeSetWidget)
        self.addChildCanvas(upgradeSet)

        upgradeSet.tag_bind(upgradeSet.dragHandle, "<Button-1>", lambda e: self.pickUpSet(e, upgradeSet, upgradeSetWidget))
        upgradeSet.tag_bind(upgradeSet.dragHandle, "<B1-Motion>", self.dragCurrentSet)
        upgradeSet.tag_bind(upgradeSet.dragHandle, "<ButtonRelease-1>", lambda e: self.release())

        self.updateItemTotals()

    def removeSet(self, upgradeSet, setWidget):
        upgradeSet.destroy()
        self.upgradeSets.remove(upgradeSet)
        self.removeChildCanvas(upgradeSet)

        self.delete(setWidget)
        self.upgradeSetWidgets.remove(setWidget)

        self.updateItemTotals()

    def updateItemTotals(self):
        if self.totalsUpdateCallback is not None:
            self.totalsUpdateCallback(self.getItemTotals())
        self.draw()

    def getItemTotals(self):
        return sum([Counter(s.getEnabledMaterials()) for s in self.upgradeSets], Counter())

### UI-Methods ###

    def draw(self):
        currentY = 0
        for c in range(len(self.upgradeSetWidgets)):
            widget = self.upgradeSetWidgets[c]
            set = self.upgradeSets[c]
            if widget != self.currentSetWidget:
                self.coords(widget, 0, currentY)
            currentY += set.getHeight() + self.spacing

        self.coords(self.addSetButton, 0, currentY)
        self.updateViewbox()

    def pickUpSet(self, e, upgradeSet, widget):
        self.currentSet = upgradeSet
        self.currentSetWidget = widget
        self.setTime = time.time()
        self.winfo_toplevel().call('raise', upgradeSet, None)
        self.initialY = e.y

    def dragCurrentSet(self, e):
        if self.currentSetWidget is not None and time.time() - self.setTime > 1 / self.scrollFPS:
            self.coords(self.currentSetWidget,
                        self.coords(self.currentSetWidget)[0],
                        min(self.getTotalHeight() - self.currentSet.getHeight() - self.scale - self.spacing * 2,
                            max(0, e.y - self.initialY + self.coords(self.currentSetWidget)[1])))
            self.setTime = time.time()
            self.dropInPosition()

    def dropInPosition(self):
        yPosition = self.coords(self.currentSetWidget)[1] + self.currentSet.getHeight() // 2
        row = 0
        while row + 1 < len(self.upgradeSets):
            # Midway line of myself relative to the bottom line of the current row
            yPosition -= self.upgradeSets[row].getHeight() + self.spacing

            if self.currentSet.getHeight() == self.upgradeSets[row].getHeight():
                # Likely moving down, i.e. self.currentSet == self.itemSets[row]
                # Take this position if my bottom line is not over the halfway line of the next row
                if yPosition + self.currentSet.getHeight() // 2 <= (self.upgradeSets[row + 1].getHeight()) // 2:
                    break
            else:
                # Take this position if my top line is not over the halfway line of the current row
                if yPosition - self.currentSet.getHeight() // 2 <= -self.upgradeSets[row].getHeight() // 2:
                    break

            row += 1

        self.upgradeSets.remove(self.currentSet)
        self.upgradeSetWidgets.remove(self.currentSetWidget)
        self.upgradeSets.insert(row, self.currentSet)
        self.upgradeSetWidgets.insert(row, self.currentSetWidget)
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
        return self.scale + (len(self.upgradeSets) + 1) * self.spacing + sum([s.getHeight() for s in self.upgradeSets])