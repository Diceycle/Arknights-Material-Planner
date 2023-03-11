
from tkinter import *
import json

from widgets import LockableCanvas
from ItemSetDisplay import ItemSetDisplay
from database import *
from GlobalOverlays import MaterialSelection, OperatorSelection, UpgradeSelection
from ItemSet import RecipeDisplay
from Depot import Depot, ParseDepotOverlay

class GUI:
    def __init__(self):

        self.scale = CONFIG.uiScale
        self.width = 16 * self.scale
        self.height = 11 * self.scale
        self.setSpacing = self.scale // 10

        self.window = Tk()
        self.window.geometry(str(self.width) + "x" + str(self.height))
        self.window.title("Arknights Materials")
        self.window.protocol("WM_DELETE_WINDOW", self.destroy)
        self.window.configure(background="light blue")
        self.window.resizable(width=False, height=False)

        MaterialSelection(self.window, self.scale, disableCallback = self.disable, enableCallback = self.enable)
        OperatorSelection(self.window, self.scale, disableCallback = self.disable, enableCallback = self.enable)
        UpgradeSelection(self.window, self.scale, disableCallback = self.disable, enableCallback = self.enable)
        RecipeDisplay(self.window, self.scale, disableCallback = self.disable, enableCallback = self.enable)
        ParseDepotOverlay(self.window, self.scale, disableCallback = self.disable, enableCallback = self.enable)

        self.setCanvas = ItemSetDisplay(self.window, self.scale, self.height, self.scale // 10,
                                        scrollSpeed=int(CONFIG.scrollSpeed / 100 * self.scale),
                                        totalsUpdateCallback=self.updateItemTotals)
        self.setCanvas.pack(side=LEFT)

        saveData = self.load()

        self.background = LockableCanvas(self.window, bg=CONFIG.backgroundColor, highlightthickness=0, width=self.height, height=self.height)

        if CONFIG.backgroundImage is not None:
            image = Image.open(CONFIG.backgroundImage)
            image.thumbnail((self.height, self.height))
            self.backgroundImage = ImageTk.PhotoImage(image)
            self.background.create_image(CONFIG.backgroundImageOffset, self.height // 2, anchor=CENTER, image=self.backgroundImage)

        self.depot = Depot(self.window, self.scale, initialContents=saveData["depot"], controlCanvasParent=self.background)
        self.depot.pack(side=RIGHT)
        self.background.pack(side=RIGHT)
        self.depot.controlCanvas.place(relx=1, y=0, anchor=NE)

        for savedSet in saveData["sets"]:
            self.setCanvas.addSet(savedSet["operator"], savedSet["upgrade"], savedSet["materials"], savedSet["enabled"])

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

    def save(self):
        data = {}
        sets = []
        for s in self.setCanvas.itemSets:
            sets.append({
                "operator": s.operator.name,
                "upgrade": s.upgrade.name,
                "materials": toExternal(s.materials, lambda v: v.get()),
                "enabled": s.enabled
            })

        data["sets"] = sets
        data["depot"] = toExternal(self.depot.getContents())

        if data != {}:
            json.dump(data, safeOpen(CONFIG.saveFile))

    def load(self):
        data = {"sets": [], "depot": {}}

        if os.path.isfile(CONFIG.saveFile):
            rawData = json.load(open(CONFIG.saveFile, "r"))

            for rawSet in rawData["sets"]:
                data["sets"].append({
                    "operator": OPERATORS[rawSet["operator"]],
                    "upgrade": UPGRADES[rawSet["upgrade"]],
                    "materials": toMaterials(rawSet["materials"]),
                    "enabled": bool(rawSet["enabled"])
                })

                data["depot"] = toMaterials(rawData["depot"])

        return data

    def destroy(self):
        self.save()
        self.window.destroy()