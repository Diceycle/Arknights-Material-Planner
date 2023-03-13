from tkinter import *

from utilImport import *

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

    def registerCallback(self, parent, posX, posY, callback, centered = False):
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

        if centered:
            self.place(x = windowWidth // 2, y = windowHeight // 2, anchor=CENTER)
        else:
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
        width = 8*scale
        super().__init__(parent, "UpgradeSelection", width=width, height=4*scale, **kwargs)

        self.scale = scale
        self.upgrades = []

        self.totalSeparator = self.create_line(0, self.scale * 3, width, self.scale*3, fill=CONFIG.color)

        self.draw()

    def draw(self, operator = None):
        for up in self.upgrades:
            self.delete(up)

        upgrades = None
        if operator is not None:
            upgrades = operator.getCosts()

        x = 0
        if upgrades is None or UPGRADES["E1"] in upgrades:
            self.placeImage(x, 0, UPGRADES["E1"])
            if upgrades is None or UPGRADES["E2"] in upgrades:
                self.placeImage(x, 1, UPGRADES["E2"])
            x += 1

        if upgrades is None or UPGRADES["SK2"] in upgrades:
            self.placeImage(x, 0, UPGRADES["SK2"])
            self.placeImage(x, 1, UPGRADES["SK3"])
            self.placeImage(x, 2, UPGRADES["SK4"])
            self.placeImage(x, 3, UPGRADES["SK1-4"])
            x += 1
            self.placeImage(x, 0, UPGRADES["SK5"])
            self.placeImage(x, 1, UPGRADES["SK6"])
            self.placeImage(x, 2, UPGRADES["SK7"])
            self.placeImage(x, 3, UPGRADES["SK4-7"])
            x += 1

        if upgrades is None or UPGRADES["S1M1"] in upgrades:
            self.placeImage(x, 0, UPGRADES["S1M1"])
            self.placeImage(x, 1, UPGRADES["S1M2"])
            self.placeImage(x, 2, UPGRADES["S1M3"])
            self.placeImage(x, 3, UPGRADES["S1MX"])
            x += 1

        if upgrades is None or UPGRADES["S2M1"] in upgrades:
            self.placeImage(x, 0, UPGRADES["S2M1"])
            self.placeImage(x, 1, UPGRADES["S2M2"])
            self.placeImage(x, 2, UPGRADES["S2M3"])
            self.placeImage(x, 3, UPGRADES["S2MX"])
            x += 1
        if upgrades is None or UPGRADES["S3M1"] in upgrades:
            self.placeImage(x, 0, UPGRADES["S3M1"])
            self.placeImage(x, 1, UPGRADES["S3M2"])
            self.placeImage(x, 2, UPGRADES["S3M3"])
            self.placeImage(x, 3, UPGRADES["S3MX"])
            x += 1

        if upgrades is None or UPGRADES["MOD-X-1"] in upgrades:
            self.placeImage(x, 0, UPGRADES["MOD-X-1"], operator)
            self.placeImage(x, 1, UPGRADES["MOD-X-2"], operator)
            self.placeImage(x, 2, UPGRADES["MOD-X-3"], operator)
            self.placeImage(x, 3, UPGRADES["MOD-X-X"], operator)
            x += 1

        if upgrades is None or UPGRADES["MOD-Y-1"] in upgrades:
            self.placeImage(x, 0, UPGRADES["MOD-Y-1"], operator)
            self.placeImage(x, 1, UPGRADES["MOD-Y-2"], operator)
            self.placeImage(x, 2, UPGRADES["MOD-Y-3"], operator)
            self.placeImage(x, 3, UPGRADES["MOD-Y-X"], operator)
            x += 1

        self.config(width = self.scale * x)

    def placeImage(self, x, y, upgrade, operator = None):
        up = self.create_image(x*self.scale + self.scale // 2,
                               y*self.scale + self.scale // 2,
                               image = upgrade.getPhotoImage(self.scale, operator = operator), anchor = CENTER)
        self.upgrades.append(up)
        self.tag_bind(up, "<Button-1>", lambda e: self.notifyObserver(upgrade))

    def registerCallback(self, parent, posX, posY, callback, operator):
        self.draw(operator)
        super().registerCallback(parent, posX, posY, callback)

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

        matches = self.findMatches(self.query.get(), OPERATORS.keys(), self.rows * self.columns)
        for c in range(len(matches)):
            op = matches[c]
            if not op in self.ops:
                self.ops[op] = self.createImage(OPERATORS[op])
            self.itemconfigure(self.ops[op], state="normal")
            self.coords(self.ops[op], self.scale*(c%self.columns), self.entryOffset + self.scale*(c // self.columns))

    def findMatches(self, query, values, results):
        values = sorted(values)
        if self.query.get() == "":
            return values[:results]

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