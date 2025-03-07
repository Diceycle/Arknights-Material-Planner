
from tkinter import *
from PIL import Image, ImageTk

from utilImport import *
from widgets import LockableCanvas
from ItemSetDisplay import ItemSetDisplay
from GlobalOverlays import MaterialSelection, OperatorSelection, UpgradeSelection, RecipeDisplay
from Depot import Depot, ParseDepotOverlay

class GUI:
    def __init__(self, window, materialPageSize):

        self.materialPageSize = materialPageSize
        self.scale = CONFIG.uiScale
        self.width = 16 * self.scale
        self.height = self.materialPageSize * self.scale
        self.setSpacing = self.scale // 10

        self.window = window
        self.window.geometry(str(self.width) + "x" + str(self.height))
        self.window.title("Arknights Materials")
        self.window.protocol("WM_DELETE_WINDOW", self.destroy)
        self.window.configure(background=CONFIG.backgroundColor)
        self.window.resizable(width=False, height=False)

        MaterialSelection(self.window, self.scale, disableCallback = self.disable, enableCallback = self.enable)
        OperatorSelection(self.window, self.scale, disableCallback = self.disable, enableCallback = self.enable)
        UpgradeSelection(self.window, self.scale, disableCallback = self.disable, enableCallback = self.enable)
        RecipeDisplay(self.window, self.scale, disableCallback = self.disable, enableCallback = self.enable)
        ParseDepotOverlay(self.window, self.scale, self.materialPageSize, disableCallback = self.disable, enableCallback = self.enable)

        self.setCanvas = ItemSetDisplay(self.window, self.scale, self.height, self.scale // 10,
                                        scrollSpeed=int(CONFIG.scrollSpeed / 100 * self.scale),
                                        totalsUpdateCallback=None) # Don't set callback yet, only activate when initializing is done
        self.setCanvas.pack(side=LEFT)

        saveData = load()

        self.background = LockableCanvas(self.window, bg=CONFIG.backgroundColor, highlightthickness=0, width=self.height, height=self.height)

        if CONFIG.backgroundImage is not None:
            image = Image.open(CONFIG.backgroundImage)
            image.thumbnail((self.height, self.height))
            self.backgroundImage = ImageTk.PhotoImage(image)
            self.background.create_image(CONFIG.backgroundImageOffset, self.height // 2, anchor=CENTER, image=self.backgroundImage)

        self.depot = Depot(self.window, self.materialPageSize, self.scale, initialContents=saveData["depot"], controlCanvasParent=self.background)
        self.depot.pack(side=RIGHT)
        self.background.pack(side=RIGHT)
        self.depot.controlCanvas.place(relx=1, y=0, anchor=NE)

        for savedSet in saveData["sets"]:
            self.setCanvas.addSetInternal(savedSet["operator"], savedSet["upgrades"])
        self.setCanvas.totalsUpdateCallback = self.updateItemTotals
        self.setCanvas.updateItemTotals()

    def updateItemTotals(self, totals):
        self.depot.updateItemRequirements(totals)

    def disable(self, notifyCallback = None):
        self.depot.disable(notifyCallback)
        self.background.disable(notifyCallback)
        self.setCanvas.disable(notifyCallback)

    def enable(self):
        self.depot.enable()
        self.background.enable()
        self.setCanvas.enable()

    def destroy(self):
        save(self.setCanvas.upgradeSets, self.depot.getContents())
        self.window.destroy()