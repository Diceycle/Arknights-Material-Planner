import os
import time
from tkinter import *
from PIL import Image, ImageTk

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

        self.animationLabel = Label(self)
        self.animationLabel.place(x=0, y=0)

        self.label = Label(self, background="#444444", foreground="white", font=("Arial", 15))
        self.label.pack(anchor=S, side=BOTTOM)

        animationFrameFolder = "img/ui/loadscreen/"
        self.animationFrameOrder = [
            ("1.png", 0.100),
            ("2.png", 0.100),
            ("3.png", 0.100),
        ]
        self.animationFrames = { f: ImageTk.PhotoImage(Image.open(animationFrameFolder + f)) for f in os.listdir(animationFrameFolder)}
        self.animationTime = time.time()
        self.animationLabel.configure(image = self.animationFrames[self.animationFrameOrder[0][0]])
        self.animationFrameCounter = 1

    def updateLabel(self, text):
        self.label.configure(text = text)
        self.update()

    def updateAnimation(self):
        frame = self.animationFrameOrder[self.animationFrameCounter % len(self.animationFrameOrder)]
        if time.time() >= frame[1] + self.animationTime:
            image = self.animationFrames[frame[0]]
            self.animationLabel.configure(image = image)
            self.update()

            self.animationTime += frame[1]
            self.animationFrameCounter += 1
