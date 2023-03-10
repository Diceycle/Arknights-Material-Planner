import random
from collections import Counter
from tkinter import *

from widgets import CanvasLabel, LockableCanvas, ImageCheckbutton
from GlobalOverlays import OVERLAYS, GlobalSelection
from WindowHandler import WindowHandler
from config import CONFIG, LOGGER
from database import *
from ItemIndicator import ItemIndicator
from DepotParser import DepotParser


class Depot(LockableCanvas):
    def __init__(self, parent, scale, initialContents = {}, controlCanvasParent = None):
        self.pageHeight = 11 * scale
        self.totalHeight = self.pageHeight * 2
        self.width = 5 * scale

        self.controlCanvasParent = controlCanvasParent
        if self.controlCanvasParent is None:
            self.controlCanvasParent = parent
        super().__init__(parent, highlightthickness=0, bg=CONFIG.color, width=self.width, height=self.totalHeight)


        self.scale = scale
        self.amountLabelHeight = self.scale // 5
        self.contents = {}
        self.trueRequirements = {}
        self.craftingRequirements = {}
        self.requirementLabels = {}

        self.indicators = {}

        controlCanvasHeight = self.scale // 2 * 2
        if CONFIG.depotParsingEnabled:
            controlCanvasHeight += self.scale // 2
        self.controlCanvas = LockableCanvas(self.controlCanvasParent, highlightthickness=0, bg=CONFIG.backgroundColor, width=scale // 2, height=controlCanvasHeight)
        self.contentCanvas = LockableCanvas(self, highlightthickness=0, bg=CONFIG.color, width=self.width, height=self.pageHeight)
        self.contentCanvas.place(x = 0, y = 0)
        self.addChildCanvas(self.contentCanvas)
        self.addChildCanvas(self.controlCanvas)

        for m in MATERIALS.values():
            x, y =  m.getPosition()
            if m in initialContents:
                self.placeItemIndicator(m, x, y, initialAmount=initialContents[m])
            else:
                self.placeItemIndicator(m, x, y)

        self.indicatorToggleButton = ImageCheckbutton(self.controlCanvas, 0, 0, callback=self.toggleVisibility,
            images=(UI_ELEMENTS["visibility-full"].getPhotoImage(self.scale // 2),
                    UI_ELEMENTS["visibility-partial"].getPhotoImage(self.scale // 2),
                    UI_ELEMENTS["visibility-low"].getPhotoImage(self.scale // 2)))

        self.pageToggleButton = ImageCheckbutton(self.controlCanvas, 0, self.scale // 2, callback=self.togglePage,
            images= (UI_ELEMENTS["arrow-down"].getPhotoImage(self.scale // 2),
                     UI_ELEMENTS["arrow-up"].getPhotoImage(self.scale // 2)))

        if CONFIG.depotParsingEnabled:
            self.researchButton = self.controlCanvas.create_image(self.scale // 2, self.scale // 4 * 5,
                                                                  image=UI_ELEMENTS["research-button"].getPhotoImage(self.scale // 2), anchor=E)
            self.controlCanvas.tag_bind(self.researchButton, "<Button-1>", lambda e: self.parseDepot())

        self.separator = self.contentCanvas.create_line(0, 0, 0, self.totalHeight, fill=CONFIG.highlightColor, width=1)

        self.draw()

    def placeItemIndicator(self, material, x, y, initialAmount = 0):
        self.contents[material] = IntVar(value = initialAmount)
        self.contents[material].trace("w", lambda *args: self.updateItemRequirementsInternal())
        self.craftingRequirements[material] = IntVar()
        i = ItemIndicator(self.contentCanvas, self.scale, material, x * self.scale, y * self.scale, self.amountLabelHeight, self.contents[material], scrollable=True)
        i.bind("<Button-1>", lambda e: self.displayRecipe(material, x, y), incrementors=False)

        self.indicators[material] = i

        self.requirementLabels[material] = CanvasLabel(self.contentCanvas,
                                                       (x+1)*self.scale - self.scale // 20,
                                                       (y+1)*self.scale - self.scale // 4 - self.scale // 20, backgroundColor="gray",
                                                       var=self.craftingRequirements[material], textColor="white",
                                                       height=self.scale // 5, anchor=SE)

    def updateItemRequirements(self, requirements):
        self.trueRequirements = Counter(requirements)
        self.updateItemRequirementsInternal()

    def updateItemRequirementsInternal(self):
        requirements = self.trueRequirements.copy()

        tier = 5
        while tier > 0:
            for m in list(requirements.keys()):
                if m.tier == tier and m.isCraftable():
                    c = Counter(m.getIngredients())
                    requirements += multiplyCounter(c, (max(0, requirements[m] - self.contents[m].get())))
            tier -= 1

        for m in self.craftingRequirements.keys():
            if m in requirements:
                self.craftingRequirements[m].set(requirements[m])
            else:
                self.craftingRequirements[m].set(0)

        self.draw()

    def draw(self):
        for m in self.craftingRequirements.keys():
            self.drawRequirementLabel(m)
        self.renderIndicatorVisibility(self.indicatorToggleButton.state)

    def togglePage(self, state):
        if state:
            offset = self.pageHeight
        else:
            offset = 0

        self.contentCanvas.config(scrollregion=(0, offset, self.width, offset + self.pageHeight))

    def toggleVisibility(self, state):
        self.renderIndicatorVisibility(state)

    def renderIndicatorVisibility(self, state):
        for m in self.indicators.keys():
            if self.craftingRequirements[m].get() == 0 and state > 0:
                self.indicators[m].hide()
            elif self.craftingRequirements[m].get() <= self.contents[m].get() and state > 1:
                self.indicators[m].hide()
            else:
                self.indicators[m].show()

    def drawRequirementLabel(self, material):
        x, y = material.getPosition()

        if self.craftingRequirements[material].get() > 0:
            self.requirementLabels[material].show()
        else:
            self.requirementLabels[material].hide()

        if self.craftingRequirements[material].get() > self.contents[material].get():
            self.requirementLabels[material].updateBackgroundColor("red")
        else:
            self.requirementLabels[material].updateBackgroundColor("gray")

    def parseDepot(self):
        OVERLAYS["ParsedDepotContents"].registerCallback(self.updateDepot)

    def updateDepot(self, materials):
        for m, v in materials.items():
            self.contents[m].set(v)

    def displayRecipe(self, material, x, y):
        OVERLAYS["RecipeDisplay"].displayRecipe(self, material, (x-1)*self.scale, ((y+1)*self.scale - 1) % self.pageHeight)

    def getContents(self):
        return unpackVar(self.contents)

class ParseDepotOverlay(GlobalSelection):
    def __init__(self, parent, scale, **kwargs):
        width = 14 * scale
        height = 5 * scale + scale // 2
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

        self.statusLabel = self.create_text(width // 2, self.scale // 4, fill=CONFIG.highlightColor, anchor=CENTER, font = ("Arial", self.scale // 6))

        for m in MATERIALS.values():
            self.placeIndicator(m)

    def placeIndicator(self, material):
        y, x = material.getPosition()
        self.vars[material] = IntVar(value=0)
        i = ItemIndicator(self, self.scale, material, x * self.scale, y * self.scale + self.scale // 2, self.scale // 5, self.vars[material], editable=False)
        i.hide()

        self.indicators[material] = i

    def registerCallback(self, callback):
        super().registerCallback(self.parent, 0, 0, callback, centered=True)
        self.changeStatus("Setting up...")
        self.parsing = True
        self.currentMaterials = {}

        self.update()
        self.after(0, self.startParsing)

    def startParsing(self):
        self.parser = DepotParser()
        valid = self.parser.startParsing()
        if valid is not None:
            self.changeStatus(valid)
            self.finishParsing()
            return

        try:
            nextMaterial = self.parser.parseNext()
            while nextMaterial is not None and self.parsing:
                if isinstance(nextMaterial, str):
                    self.changeStatus(nextMaterial)
                    self.update()
                    nextMaterial = self.parser.parseNext()
                    continue
                else:
                    self.changeStatus("Scanning...")

                self.setMaterial(nextMaterial[0], nextMaterial[1])
                self.update()
                nextMaterial = self.parser.parseNext()

            self.changeStatus("Done scanning, either confirm or discard the new materials with the buttons on the right")
        except Exception as e:
            self.changeStatus("Error encountered during scanning of depot: " + str(e))
            LOGGER.exception("Scanning Error: %s", e)

        self.finishParsing()

    def setMaterial(self, material, amount):
        i = self.indicators[material]
        if amount is None:
            self.vars[material].set(0)
            i.amountLabel.updateBackgroundColor("red")

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
            self.changeStatus("Interrupted, either confirm or discard the new materials with the buttons on the right")
            self.finishParsing()
        else:
            self.cancelCallback()

    def finishParsing(self):
        self.parsing = False
        self.parser.destroy()

    def cleanup(self):
        super().cleanup()
        for i in self.indicators.values():
            i.hide()
            i.amountLabel.updateBackgroundColor("black")

    def changeStatus(self, text):
        self.itemconfigure(self.statusLabel,text=text)

