from tkinter import *

from Splashscreen import Splashscreen
from concurrent.futures import ThreadPoolExecutor
from time import sleep

window = Tk()
window.wm_state("withdrawn")
window.iconbitmap("rock.ico")

loadscreen = Splashscreen(window)
loadScreenText = None
def awaitResult(function):
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(function)

        while not future.done():
            loadscreen.updateAnimation()
            if loadScreenText is not None:
                loadscreen.updateLabel(loadScreenText)
            sleep(0.01)
        return future.result()

def progressCallback(text, current, goal):
    global loadScreenText
    loadScreenText = f"{text}... ({current}/{goal})"

loadscreen.updateLabel("Loading Libraries...")


GUI = None
exceptHook = CONFIG = MATERIALS = None
downloadGamedata = downloadEntityLists = None
loadOperators = loadMaterials = None
def doImports():
    global GUI
    global exceptHook, CONFIG, MATERIALS
    global downloadGamedata, downloadEntityLists
    global loadOperators, loadMaterials
    from GUI import GUI
    from util import exceptHook, CONFIG, MATERIALS
    from gameDataReader import downloadGamedata, downloadEntityLists
    from database import loadOperators, loadMaterials
awaitResult(lambda: doImports())

awaitResult(lambda: downloadGamedata(lambda current, goal: progressCallback("Downloading Gamedata", current, goal)))
awaitResult(lambda: downloadEntityLists(lambda current, goal: progressCallback("Downloading Entity Lists", current, goal)))

materialPageSize = awaitResult(lambda: loadMaterials(lambda current, goal: progressCallback("Downloading Material Images", current, goal)))

awaitResult(lambda: loadOperators(lambda current, goal: progressCallback("Downloading Operator Images", current, goal)))

loadscreen.updateLabel("Preprocessing Images...")

for m in MATERIALS.values():
    m.getPhotoImage(CONFIG.uiScale)
    m.getPhotoImage(CONFIG.uiScale, transparency=0.5)
    loadscreen.updateAnimation()

backgroundImage = None
if CONFIG.backgroundImage is not None:
    from PIL import Image, ImageTk
    i = Image.open(CONFIG.backgroundImage)
    loadscreen.updateAnimation()
    i.thumbnail((CONFIG.uiScale*materialPageSize, CONFIG.uiScale*materialPageSize))
    loadscreen.updateAnimation()
    backgroundImage = ImageTk.PhotoImage(i)
    loadscreen.updateAnimation()

loadscreen.updateLabel("Rendering Interface...")

def update():
    loadscreen.updateAnimation()
    loadscreen.after(1, update)
update()

GUI(window, materialPageSize, backgroundImage)
window.report_callback_exception=exceptHook

loadscreen.destroy()
window.attributes('-topmost', 'false')
window.wm_state("normal")

window.mainloop()
