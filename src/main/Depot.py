import json
from queue import Queue

import pyperclip
from collections import Counter
from tkinter import *

from utilImport import *
from DepotParser import DepotParser
from GlobalOverlays import OVERLAYS, GlobalSelection
from ItemIndicator import ItemIndicator
from widgets import CanvasLabel, LockableCanvas, ImageCheckbutton


class Depot(LockableCanvas):
    def __init__(self, parent, materialPageSize, scale, initialContents = {}, controlCanvasParent = None):
        self.materialPageSize = materialPageSize
        self.pageHeight = materialPageSize * scale
        self.totalHeight = self.pageHeight * 2
        self.width = 7 * scale

        self.controlCanvasParent = controlCanvasParent
        if self.controlCanvasParent is None:
            self.controlCanvasParent = parent
        super().__init__(parent, highlightthickness=0, bg=CONFIG.color, width=self.width, height=self.totalHeight)

        self.updatesEnabled = True

        self.scale = scale
        self.amountLabelHeight = self.scale // 5
        self.contents = {}
        self.trueRequirements = {}
        self.craftingRequirements = {}
        self.missingMaterials = {}
        self.missingLabels = {}
        self.craftable = []
        self.requirementLabels = {}

        self.indicators = {}

        controlCanvasHeight = self.scale // 2 * 4
        if CONFIG.depotParsingEnabled:
            controlCanvasHeight += self.scale // 2
        self.controlCanvas = LockableCanvas(self.controlCanvasParent, highlightthickness=0, bg=CONFIG.backgroundColor, width=scale // 2, height=controlCanvasHeight)
        self.contentCanvas = LockableCanvas(self, highlightthickness=0, bg=CONFIG.color, width=self.width, height=self.totalHeight)
        self.contentCanvas.place(x = 0, y = 0)
        self.addChildCanvas(self.contentCanvas)
        self.addChildCanvas(self.controlCanvas)

        for m in MATERIALS.values():
            x, y =  m.getPosition()
            if m in initialContents:
                self.placeItemIndicator(m, x, y, initialAmount=initialContents[m])
            else:
                self.placeItemIndicator(m, x, y)

        self.indicatorToggleButton = ImageCheckbutton(self.controlCanvas, 0, 0, callback=lambda state: self.draw(),
            images=(UI_ELEMENTS["visibility-full"].getPhotoImage(self.scale // 2),
                    UI_ELEMENTS["visibility-partial"].getPhotoImage(self.scale // 2),
                    UI_ELEMENTS["visibility-low"].getPhotoImage(self.scale // 2)))

        self.labelToggleButton = ImageCheckbutton(self.controlCanvas, 0, self.scale // 2, callback=lambda state : self.draw(),
            images=(UI_ELEMENTS["total"].getPhotoImage(self.scale // 2),
                    UI_ELEMENTS["missing"].getPhotoImage(self.scale // 2)))

        self.pageToggleButton = ImageCheckbutton(self.controlCanvas, 0, self.scale // 2 * 2, callback=self.togglePage,
            images= (UI_ELEMENTS["arrow-down"].getPhotoImage(self.scale // 2),
                     UI_ELEMENTS["arrow-up"].getPhotoImage(self.scale // 2)))

        self.exportButton = self.controlCanvas.create_image(0 , self.scale // 4 * 7,
                                                            image=UI_ELEMENTS["export"].getPhotoImage(self.scale // 2), anchor=W)
        self.controlCanvas.tag_bind(self.exportButton, "<Button-1>", lambda e: self.exportContentsForPenguinStats())

        if CONFIG.depotParsingEnabled:
            self.researchButton = self.controlCanvas.create_image(0, self.scale // 4 * 9,
                                                                  image=UI_ELEMENTS["research-button"].getPhotoImage(self.scale // 2), anchor=W)
            self.controlCanvas.tag_bind(self.researchButton, "<Button-1>", lambda e: self.parseDepot())

        self.separator = self.contentCanvas.create_line(0, 0, 0, self.totalHeight, fill=CONFIG.highlightColor, width=1)

        self.draw()

    def placeItemIndicator(self, material, x, y, initialAmount = 0):
        self.contents[material] = IntVar(value = initialAmount)
        self.contents[material].trace("w", lambda *args: self.updateItemRequirementsInternal())

        labelArgs = { "x": (x + 1) * self.scale - self.scale // 20,
                      "y": (y + 1) * self.scale - self.scale // 4 - self.scale // 20,
                      "height": self.scale // 5,
                      "anchor": SE }

        self.craftingRequirements[material] = IntVar()
        self.requirementLabels[material] = CanvasLabel(self.contentCanvas, var=self.craftingRequirements[material], **labelArgs)
        self.missingMaterials[material] = IntVar()
        self.missingLabels[material] = CanvasLabel(self.contentCanvas, var=self.missingMaterials[material], **labelArgs)

        multiplier = 1
        if material.name == "money":
            multiplier = 10000

        i = ItemIndicator(self.contentCanvas, self.scale, material, x * self.scale, y * self.scale, self.amountLabelHeight,
                          self.contents[material], scrollable=True, incrementMultiplier=multiplier,
                          additionalLabels=[self.requirementLabels[material], self.missingLabels[material]])
        i.bind("<Button-1>", lambda e: self.displayRecipe(material, x, y), incrementors=False)

        self.requirementLabels[material].raiseWidgets()
        self.missingLabels[material].raiseWidgets()
        self.indicators[material] = i

    def updateItemRequirements(self, requirements):
        self.trueRequirements = Counter(requirements)
        self.updateItemRequirementsInternal()

    def updateItemRequirementsInternal(self):
        if not self.updatesEnabled:
            return

        requirements = self.trueRequirements.copy()

        for tier in range(5, 0, -1):
            for m in list(requirements.keys()):
                if m.tier == tier and m.isCraftable():
                    c = Counter(m.getIngredients())
                    requirements += multiplyCounter(c, (max(0, requirements[m] - self.contents[m].get())))
        for m in self.craftingRequirements.keys():
            self.craftingRequirements[m].set(requirements[m])

        missing = self.trueRequirements.copy()
        craftPossible(missing, Counter(unpackVar(self.contents)))
        for m in self.missingMaterials.keys():
            self.missingMaterials[m].set(missing[m])

        self.craftable = []
        for i in range(5):
            tier = i + 1
            for m, a in self.craftingRequirements.items():
                if m.tier == tier and m.isCraftable():
                    craftable = True
                    for ing in m.getIngredients().keys():
                        if ing not in self.craftable and missing[ing] > 0:
                            craftable = False
                            break
                    if craftable:
                        self.craftable.append(m)
                elif m.tier == tier and not m.isCraftable():
                    if self.craftingRequirements[m].get() <= self.contents[m].get():
                        self.craftable.append(m)

        self.draw()

    def draw(self):
        for m in self.craftingRequirements.keys():
            self.drawRequirementLabel(m, self.labelToggleButton.state)
        self.renderIndicatorVisibility(self.indicatorToggleButton.state)

    def togglePage(self, state):
        if state:
            offset = self.pageHeight
        else:
            offset = 0

        self.contentCanvas.config(scrollregion=(0, offset, self.width, offset + self.totalHeight))

    def drawRequirementLabel(self, material, showMissingAmount):
        if self.craftingRequirements[material].get() > 0:
            self.missingLabels[material].setHidden(not showMissingAmount)
            self.requirementLabels[material].setHidden(showMissingAmount)
        else:
            self.missingLabels[material].hide()
            self.requirementLabels[material].hide()

        if self.missingMaterials[material].get() > 0:
            self.missingLabels[material].changeColor(color=CONFIG.depotColorInsufficient, fontColor=CONFIG.depotColorInsufficientFont)
        else:
            self.missingLabels[material].changeColor(color=CONFIG.depotColorSufficient, fontColor=CONFIG.depotColorSufficientFont)

        if self.craftingRequirements[material].get() > self.contents[material].get() and (not material.isCraftable or not material in self.craftable):
            self.requirementLabels[material].changeColor(color=CONFIG.depotColorInsufficient, fontColor=CONFIG.depotColorInsufficientFont)
        else:
            self.requirementLabels[material].changeColor(color=CONFIG.depotColorSufficient, fontColor=CONFIG.depotColorSufficientFont)

    def renderIndicatorVisibility(self, state):
        for m in self.indicators.keys():
            if self.craftingRequirements[m].get() == 0 and state > 0:
                self.indicators[m].hide()
                self.missingLabels[m].hide()
                self.requirementLabels[m].hide()
            elif self.missingMaterials[m].get() == 0 and state > 1:
                self.indicators[m].hide()
                self.missingLabels[m].hide()
                self.requirementLabels[m].hide()
            else:
                self.indicators[m].show()

    def parseDepot(self):
        OVERLAYS["ParsedDepotContents"].registerCallback(self.updateDepot)

    def updateDepot(self, materials):
        self.updatesEnabled = False
        for m, v in materials.items():
            self.contents[m].set(v)
        self.updatesEnabled = True
        self.updateItemRequirementsInternal()

    def displayRecipe(self, material, x, y):
        OVERLAYS["RecipeDisplay"].displayRecipe(self, material, (x-1)*self.scale, ((y+1)*self.scale - 1) % self.pageHeight)

    def getContents(self):
        return unpackVar(self.contents)

    def exportContentsForPenguinStats(self):
        result = {}
        items = []
        for m in MATERIALS.values():
            if m.internalId is not None:
                items.append({ "id": m.internalId, "have": self.contents[m].get(), "need": self.trueRequirements[m] })
        result["items"] = items
        result["@type"] = "@penguin-statistics/planner/config"

        pyperclip.copy(json.dumps(result))

class ParseDepotOverlay(GlobalSelection):
    def __init__(self, parent, scale, materialPageSize, **kwargs):
        self.materialPageSize = materialPageSize
        width = 15 * scale
        height = 8 * scale
        super().__init__(parent, "ParsedDepotContents", width=width, height=height, **kwargs)

        self.parent = parent
        self.scale = scale
        self.vars = {}
        self.currentMaterials = {}
        self.parser = None
        self.parsing = False
        self.indicators = {}

        self.confirmButton = self.create_image(width, 0,
                                               image=UI_ELEMENTS["confirm"].getPhotoImage(self.scale // 2), anchor=NE)
        self.tag_bind(self.confirmButton, "<Button-1>", lambda e: self.confirmContents(True))
        self.closeButton = self.create_image(width, self.scale // 2,
                                             image=UI_ELEMENTS["close"].getPhotoImage(self.scale // 2), anchor=NE)
        self.tag_bind(self.closeButton, "<Button-1>", lambda e: self.confirmContents(False))

        self.statusLabel = self.create_text(width // 2, self.scale // 4, fill=CONFIG.highlightColor, anchor=N, font = ("Arial", self.scale // 6), width=width - self.scale)

        for m in MATERIALS.values():
            self.placeIndicator(m)

    def placeIndicator(self, material):
        y, x = material.getPosition()
        y += 1
        self.vars[material] = IntVar(value=0)
        i = ItemIndicator(self, self.scale, material, x * self.scale, y * self.scale, self.scale // 5, self.vars[material], editable=False)
        i.hide()

        self.indicators[material] = i

    def registerCallback(self, callback):
        super().registerCallback(self.parent, 0, 0, callback, centered=True)
        self.changeStatus("Setting up...")
        self.parsing = True
        self.interrupted = False
        self.error = False
        self.currentMaterials = {}
        self.workQueue = Queue()

        self.update()
        self.after(0, self.startParsing)

    def displayMaterial(self, material, amount):
        self.workQueue.put(["Material", material, amount])

    def displayText(self, text, error = False):
        if self.error:
            return
        if error:
            self.error = True
        self.workQueue.put(["Text", text])

    def notifyFinish(self, success):
        self.workQueue.put(["Finish", success])

    def handleQueue(self):
        queueItem = self.workQueue.get()
        if queueItem[0] == "Finish":
            self.finishParsing(queueItem[1])
            return
        elif queueItem[0] == "Text":
            self.changeStatus(queueItem[1])
        elif queueItem[0] == "Material":
            self.setMaterial(queueItem[1], queueItem[2])

        self.update()
        self.after(0, self.handleQueue)

    def startParsing(self):
        self.parser = DepotParser(confidenceThreshold=CONFIG.imageRecognitionThreshold)
        self.parser.startParsing(self.displayText, self.displayMaterial, self.notifyFinish)
        self.handleQueue()

    def setMaterial(self, material, amount):
        i = self.indicators[material]
        if amount is None:
            self.vars[material].set(0)
            i.amountLabel.changeColor(color=CONFIG.depotColorInsufficient, fontColor=CONFIG.depotColorInsufficientFont)

        if amount is not None:
            self.vars[material].set(amount)
            self.currentMaterials[material] = amount

        i.show()

    def confirmContents(self, confirmed):
        if self.parsing and confirmed:
            return
        elif not self.parsing and confirmed:
            self.notifyObserver(self.currentMaterials)
        elif self.parsing and not confirmed:
            self.finishParsing(False)
        else:
            self.cancelCallback()

    def finishParsing(self, success):
        if not self.error:
            if success:
                self.changeStatus("Done scanning, either confirm or discard the new materials with the buttons on the right")
            else:
                self.changeStatus("Interrupted, either confirm or discard the new materials with the buttons on the right")
        self.parsing = False
        self.parser.stop()
        self.parser.destroy()

    def cleanup(self):
        super().cleanup()
        for i in self.indicators.values():
            i.hide()
            i.amountLabel.changeColor(color=CONFIG.amountColor, fontColor=CONFIG.amountColorFont)

    def changeStatus(self, text):
        self.itemconfigure(self.statusLabel,text=text)

