import os
import time
from tkinter import *
from PIL import Image, ImageTk

from util import MATERIALS
from random import choice

class Splashscreen(Toplevel):
    def __init__(self, parent):
        super().__init__()

        loadscreenWidth = 400
        loadscreenHeight = 300
        offsetX = parent.winfo_screenwidth() // 2 - loadscreenWidth // 2
        offsetY = parent.winfo_screenheight() // 2 - loadscreenHeight // 2

        self.geometry(f"{loadscreenWidth}x{loadscreenHeight}+{offsetX}+{offsetY}")
        self.configure(background="#444444")
        self.overrideredirect(True)
        self.attributes('-topmost', 'true')

        self.animationLabel = Label(self, bd=-2)
        self.animationLabel.place(x=0, y=0)

        self.label = Label(self, background="#444444", foreground="white", font=("Arial", 15))
        self.label.pack(anchor=S, side=BOTTOM)

        self.animationImageFolder = "img/ui/loadscreen/"
        self.animationFrameOrder = [
            ("Left1.png", 0.300),
            ("Left2.png", 0.300),
            ("Right1.png", 0.300),
            ("Right2.png", 0.300),
            ("Bottom1.png", 0.300),
            ("Bottom2.png", 0.300),
            ("Done1.png", 0.250),
            ("Done2.png", 0.600)
        ]
        self.animationFrames = {f: ImageTk.PhotoImage(Image.open(self.animationImageFolder + f)) for f in os.listdir(self.animationImageFolder)}
        initialFrame = self.animationFrameOrder[0]
        self.animationTime = time.time() + initialFrame[1]
        self.animationLabel.configure(image = self.animationFrames[initialFrame[0]])
        self.animationFrameCounter = 1

    def updateLabel(self, text):
        self.label.configure(text = text)
        self.update()

    def updateAnimation(self):
        frame = self.animationFrameOrder[self.animationFrameCounter % len(self.animationFrameOrder)]
        if time.time() >= self.animationTime:
            image = self.animationFrames[frame[0]]

            if frame[0].startswith("Done1"):
                self.createMaterialOverlay()

            if frame[0].startswith("Done"):
                    im = Image.open(self.animationImageFolder + frame[0]).convert("RGBA")
                    im.alpha_composite(self.currentMaterialOverlay,
                                       (180-self.currentMaterialOverlay.size[0] // 2,
                                        270-self.currentMaterialOverlay.size[1]))
                    self.currentFinishFrame = image = ImageTk.PhotoImage(im)

            self.animationLabel.configure(image = image)

            self.animationTime += frame[1]
            self.animationFrameCounter += 1

            self.update()

    def createMaterialOverlay(self):
        if len(MATERIALS) > 0:
            matImage = choice(list(MATERIALS.values())).image.copy()
        else:
            matImage = Image.open(self.animationImageFolder + "defaultMaterial.png")

        shadowHeight = 30

        transparencyMask = Image.eval(matImage.resize((matImage.size[0], shadowHeight)).getchannel("A"), lambda x: x // 2)
        shadow = Image.new("RGB", transparencyMask.size, (20, 20, 20))
        shadow.putalpha(transparencyMask)

        self.currentMaterialOverlay = Image.new("RGBA", matImage.size)
        self.currentMaterialOverlay.alpha_composite(shadow, (0, self.currentMaterialOverlay.size[1]-shadowHeight))
        self.currentMaterialOverlay.alpha_composite(matImage)
