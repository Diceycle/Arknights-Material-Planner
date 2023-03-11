from tkinter import *

from config import CONFIG
from widgets import CanvasLabel


class ItemIndicator:
    def __init__(self, parent, scale, material, x, y, labelHeight, var, editable = True, scrollable = False,
                 incrementMultiplier = 1, additionalLabels = []):

        self.parent = parent
        self.material = material
        self.scale = scale
        self.x = x
        self.y = y
        self.labelHeight = labelHeight
        self.amount = var
        self.incrementMultiplier = incrementMultiplier
        self.additionalLabels = additionalLabels

        self.editable = editable
        self.hidden = True

        self.image = self.parent.create_image(self.x, self.y, image=self.material.getPhotoImage(self.scale), anchor=NW)
        self.amountLabel = CanvasLabel(self.parent, self.x + self.scale - self.scale // 20, self.y + self.scale - self.scale // 20, labelHeight,
                                       anchor=SE, var=self.amount, backgroundColor=CONFIG.amountColor, textColor=CONFIG.amountColorFont)

        if editable:
            self.incrementLabel = CanvasLabel(self.parent, self.x + self.scale, self.y, labelHeight,
                                              anchor = NE, backgroundColor=CONFIG.amountColor, text = "+", textColor=CONFIG.amountColorFont)
            self.incrementLabel.bind("<Button-1>", lambda e: self.incrementAmount())

            self.decrementLabel = CanvasLabel(self.parent, self.x, self.y, labelHeight,
                                              anchor = NW, backgroundColor=CONFIG.amountColor, text = "-", textColor=CONFIG.amountColorFont)
            self.decrementLabel.bind("<Button-1>", lambda e: self.decrementAmount())

            self.bind("<Enter>", lambda e: self.showIncrementors())
            self.bind("<Leave>", lambda e: self.hideIncremetors())
            self.hideIncremetors()

        if scrollable:
            self.bind("<Enter>", lambda e: self.activateMouseWheelBinding())
            self.bind("<Leave>", lambda e: self.deactivateMouseWheelBinding())
        self.show()


    def showIncrementors(self):
        if not self.hidden:
            self.incrementLabel.show()
            self.decrementLabel.show()

    def hideIncremetors(self):
        self.incrementLabel.hide()
        self.decrementLabel.hide()

    def incrementAmount(self):
        if not self.hidden:
            self.amount.set(self.amount.get() + 1 * self.incrementMultiplier)

    def decrementAmount(self):
        if not self.hidden:
            if self.amount.get() > 0:
                self.amount.set(self.amount.get() - 1 * self.incrementMultiplier)

    def activateMouseWheelBinding(self):
        if not self.hidden:
            self.parent.bind_all("<MouseWheel>", lambda e: self.handleMouseWheel(e))

    def deactivateMouseWheelBinding(self):
        self.parent.unbind_all("<MouseWheel>")

    def handleMouseWheel(self, e):
        if e.delta > 0:
            self.incrementAmount()
        elif e.delta < 0:
            self.decrementAmount()

    def hide(self):
        self.hidden = True
        self.parent.itemconfigure(self.image, image = self.material.getPhotoImage(self.scale, 0.5))
        self.amountLabel.hide()
        if self.editable:
            self.hideIncremetors()

    def show(self):
        self.hidden = False
        self.parent.itemconfigure(self.image, image = self.material.getPhotoImage(self.scale))
        self.amountLabel.show()

    def delete(self):
        if self.editable:
            self.incrementLabel.delete()
            self.decrementLabel.delete()
        self.parent.delete(self.image)
        self.amountLabel.delete()

    def bind(self, trigger, command, incrementors=True):
        self.parent.tag_bind(self.image, trigger, command, add="+")
        self.amountLabel.bind(trigger, command)
        for label in self.additionalLabels:
            label.bind(trigger, command)
        if self.editable and incrementors:
            self.incrementLabel.bind(trigger, command)
            self.decrementLabel.bind(trigger, command)