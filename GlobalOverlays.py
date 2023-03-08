from tkinter import *

from config import CONFIG
from database import *

OVERLAYS = {}

def cancelCallbacks():
    for c in OVERLAYS.values():
        c.cleanup()

class GlobalSelection(Canvas):
    def __init__(self, parent, name, width, height, disableCallback = None, enableCallback = None):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=2, bg=CONFIG.colorDark, bd=0,
                         highlightbackground=CONFIG.highlightColor, highlightcolor=CONFIG.highlightColor)

        self.disableCallback = disableCallback
        self.enableCallback = enableCallback

        OVERLAYS[name] = self
        self.bind("<Button-3>", lambda e: self.cancelCallback())

    def registerCallback(self, parent, posX, posY, callback):
        cancelCallbacks()
        if self.disableCallback is not None:
            self.callDisableCallback()

        windowWidth = self.winfo_toplevel().winfo_width()
        windowHeight = self.winfo_toplevel().winfo_height()
        width = self.winfo_width()
        height = self.winfo_height()
        if width == 1 or height == 1:
            # Force a first render to get real size
            self.place(x=0, y=0)
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()

        self.place(x = min(windowWidth - width, parent.winfo_x() + posX),
                   y = min(windowHeight - height, parent.winfo_y() + posY))
        self.tk.call('raise', self._w)
        self.callback = callback

    def cancelCallback(self):
        self.cleanup()
        if self.enableCallback is not None:
            self.enableCallback()

    def notifyObserver(self, selection):
        self.callback(selection)
        self.cancelCallback()

    def cleanup(self):
        self.place_forget()

    def callDisableCallback(self):
        self.disableCallback()


class UpgradeSelection(GlobalSelection):
    def __init__(self, parent, scale, **kwargs):
        super().__init__(parent, "UpgradeSelection", width=3*scale, height=4*scale, **kwargs)

        self.scale = scale

        self.placeImage(0, 0, UPGRADES["E1"])
        self.placeImage(1, 0, UPGRADES["E2"])
        self.placeImage(2, 0, UPGRADES["SK7"])
        self.placeImage(0, 1, UPGRADES["S1M1"])
        self.placeImage(1, 1, UPGRADES["S1M2"])
        self.placeImage(2, 1, UPGRADES["S1M3"])
        self.placeImage(0, 2, UPGRADES["S2M1"])
        self.placeImage(1, 2, UPGRADES["S2M2"])
        self.placeImage(2, 2, UPGRADES["S2M3"])
        self.placeImage(0, 3, UPGRADES["S3M1"])
        self.placeImage(1, 3, UPGRADES["S3M2"])
        self.placeImage(2, 3, UPGRADES["S3M3"])

    def placeImage(self, x, y, upgrade):
        up = self.create_image(x*self.scale + self.scale // 2,
                               y*self.scale + self.scale // 2,
                               image = upgrade.getPhotoImage(self.scale), anchor = CENTER)
        self.tag_bind(up, "<Button-1>", lambda e: self.notifyObserver(upgrade))

    def callDisableCallback(self):
        self.disableCallback(self.cancelCallback)

class MaterialSelection(GlobalSelection):
    def __init__(self, parent, scale, **kwargs):
        super().__init__(parent, "MaterialSelection", width=14*scale, height=5*scale, **kwargs)

        self.scale = scale

        for m in MATERIALS.values():
            y, x = m.getPosition()
            self.placeImage(x, y, m)

    def placeImage(self, x, y, material):
        mat = self.create_image(x*self.scale, y*self.scale, image = material.getPhotoImage(self.scale), anchor = NW)
        self.tag_bind(mat, "<Button-1>", lambda e: self.notifyObserver(material))

    def callDisableCallback(self):
        self.disableCallback(self.cancelCallback)

class OperatorSelection(GlobalSelection):
    def __init__(self, parent, scale, **kwargs):
        self.columns = 5
        self.rows = 5
        super().__init__(parent, "OperatorSelection", width=self.columns*scale, height=self.rows*scale, **kwargs)

        self.scale = scale

        self.query = StringVar(value="")
        self.query.trace("w", lambda *args: self.draw())
        self.ops = {}

        self.entry = Entry(self, width=10, textvariable=self.query, relief=FLAT, font = ("Arial", self.scale // 6),
                           background=CONFIG.color, foreground=CONFIG.highlightColor)
        self.entry.place(x=10, y = scale // 4, anchor=W)
        self.entryOffset = self.scale // 2

        for op in sorted(OPERATORS.keys()):
            self.ops[op] = self.createImage(OPERATORS[op])

        self.draw()

    def callDisableCallback(self):
        self.disableCallback(self.cancelCallback)

    def registerCallback(self, parent, posX, posY, callback):
        super().registerCallback(parent, posX, posY, callback)
        self.entry.focus_set()

    def createImage(self, operator):
        op = self.create_image(0, 0, image = operator.getPhotoImage(self.scale), anchor = NW)
        self.tag_bind(op, "<Button-1>", lambda e: self.notifyObserver(operator))
        return op

    def draw(self):
        for op in self.ops.keys():
            self.itemconfigure(self.ops[op], state="hidden")

        matches = self.findMatches(self.query.get(), self.ops.keys(), self.rows * self.columns)
        for c in range(len(matches)):
            op = matches[c]
            self.itemconfigure(self.ops[op], state="normal")
            self.coords(self.ops[op], self.scale*(c%self.columns), self.entryOffset + self.scale*(c // self.columns))

    def findMatches(self, query, values, results):
        if self.query.get() == "":
            return list(values)[:results]

        query = query.lower()

        result = []
        for v in values:
            if v.lower().startswith(query) or (" " + query) in v.lower():
                result.append(v)

        for v in values:
            if query in v.lower() and not v in result:
                result.append(v)

        return result[:results]

    def cleanup(self):
        self.query.set("")
        super().cleanup()