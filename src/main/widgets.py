from tkinter import *

from PIL import Image, ImageTk


class LockableCanvas(Canvas):
    def __init__(self, *args, width, height, **kwargs):
        super().__init__(*args, width = width, height = height, **kwargs)

        self.overlayImage = self.createOverlayImage(width, height)
        self.overlayPhotoImage = ImageTk.PhotoImage(self.overlayImage)
        self.inputLock = self.create_image(0, 0, anchor = NW, state = "hidden", image = self.overlayPhotoImage)
        self.tag_bind(self.inputLock, "<Button-1>", lambda e: self.notifyLockClicked())
        self.lockableChildren = []
        self.notifyCallback = None

    def createOverlayImage(self, width, height):
        return Image.new(size=(width, height), mode="RGBA", color=(0, 0, 0, 0))

    def addChildCanvas(self, child):
        self.lockableChildren.append(child)

    def removeChildCanvas(self, child):
        self.lockableChildren.remove(child)

    def disable(self, notifyCallback=None):
        self.notifyCallback = notifyCallback
        self.tag_raise(self.inputLock)
        self.itemconfigure(self.inputLock, state = "normal")

        for child in self.lockableChildren:
            child.disable(notifyCallback)

    def enable(self):
        self.itemconfigure(self.inputLock, state = "hidden")

        for child in self.lockableChildren:
            child.enable()

    def notifyLockClicked(self):
        if self.notifyCallback is not None:
            self.notifyCallback()

    def resize(self, width = None, height = None):
        if width is None:
            width = self.overlayImage.width
        if height is None:
            height = self.overlayImage.height

        if width == self.overlayImage.width and height == self.overlayImage.height:
            return

        self.config(width = width, height = height)

        self.overlayImage = self.createOverlayImage(width, height)
        self.overlayPhotoImage = ImageTk.PhotoImage(self.overlayImage)
        self.itemconfigure(self.inputLock, image = self.overlayPhotoImage)


class CanvasLabel:
    def __init__(self, parent, x, y, height, anchor = NW,
                 var = None, text = None,
                 textColor = "black", backgroundColor = "",
                 fontFamily ="Arial"):
        self.parent = parent

        self.var = var
        if self.var is None:
            self.var = StringVar(value=text)

        self.x = x
        self.y = y
        self.fontSize = int(height / 3 * 2)
        self.padding = height // 6

        if anchor == CENTER:
            pass
        elif "s" in anchor:
            self.y -= self.padding
        elif "n" in anchor:
            self.y += self.padding

        if anchor == CENTER:
            pass
        elif "e" in anchor:
            self.x -= self.padding
        elif "w" in anchor:
            self.x += self.padding

        self.background = self.parent.create_rectangle(0, 0, 0, 0, fill=backgroundColor, outline="")
        self.text = self.parent.create_text(self.x, self.y,
                                            anchor=anchor, fill=textColor,
                                            font=(fontFamily, self.fontSize), justify="center")
        self.var.trace("w", lambda *args: self.updateText())

        self.hidden = False
        self.updateText()

    def updateText(self):
        self.parent.itemconfigure(self.text, text = self.var.get())
        bbox = self.parent.bbox(self.text)

        if bbox is not None:
            self.parent.coords(self.background,
                               bbox[0] - self.padding, bbox[1] - self.padding,
                               bbox[2] + self.padding, bbox[3] + self.padding)

    def changeColor(self, color=None, fontColor=None):
        if color is not None:
            self.parent.itemconfigure(self.background, fill = color)
        if fontColor is not None:
            self.parent.itemconfigure(self.text, fill = fontColor)

    def hide(self):
        self.setHidden(True)

    def show(self):
        self.setHidden(False)

    def setHidden(self, hidden):
        if hidden == self.hidden:
            return

        if hidden:
            self.parent.itemconfigure(self.text, state="hidden")
            self.parent.itemconfigure(self.background, state="hidden")
        else:
            self.parent.itemconfigure(self.text, state="normal")
            self.parent.itemconfigure(self.background, state="normal")
            self.updateText()
        self.hidden = hidden


    def raiseWidgets(self):
        self.parent.tag_raise(self.background)
        self.parent.tag_raise(self.text)

    def bind(self, trigger, command):
        self.parent.tag_bind(self.text, trigger, command, add="+")
        self.parent.tag_bind(self.background, trigger, command, add="+")

    def delete(self):
        self.parent.delete(self.text)
        self.parent.delete(self.background)

class ImageCheckbutton:
    def __init__(self, parent, x, y, images, callback, anchor = NW):

        self.parent = parent
        self.images = images
        self.callback = callback
        self.state = 0
        self.button = self.parent.create_image(x, y, anchor = anchor, image = images[0])
        self.parent.tag_bind(self.button, "<Button-1>", lambda e: self.toggleState())

    def setState(self, state):
        self.state = state
        self.renderState()

    def toggleState(self):
        self.state = (self.state + 1) % len(self.images)
        self.renderState()

    def renderState(self):
        self.parent.itemconfigure(self.button, image = self.images[self.state])
        self.callback(self.state)