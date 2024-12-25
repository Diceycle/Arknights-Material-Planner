from tkinter import *

window = Tk()
window.wm_state("withdrawn")
window.iconbitmap("rock.ico")

loadscreenWidth = 400
loadscreenHeight = 300
offsetX = window.winfo_screenwidth() // 2 - loadscreenWidth // 2
offsetY = window.winfo_screenheight() // 2 - loadscreenHeight // 2

loadscreen = Toplevel()
loadscreen.geometry(f"{loadscreenWidth}x{loadscreenHeight}+{offsetX}+{offsetY}")
loadscreen.configure(background="#444444")
loadscreen.overrideredirect(True)
loadscreen.attributes('-topmost', 'true')

l = Label(loadscreen, background="#444444", foreground="white", font=("Arial", 15))
l.pack(anchor=S, side=BOTTOM)

l.config(text="Loading Libraries...")
loadscreen.update()

from GUI import GUI
from util import exceptHook

from gameDataReader import downloadOperatorData
from database import loadOperators, loadMaterials

def progressCallback(text, current, goal):
    l.config(text=f"{text}... ({current}/{goal})")
    loadscreen.update()

downloadOperatorData(lambda current, goal: progressCallback("Downloading Operator Data", current, goal))

materialPageSize = loadMaterials(lambda current, goal: progressCallback("Downloading Material Images", current, goal))

loadOperators(lambda current, goal: progressCallback("Downloading Operator Images", current, goal))

l.config(text="Preprocessing Images...")
loadscreen.update()
GUI(window, materialPageSize)
window.report_callback_exception=exceptHook

loadscreen.destroy()
window.attributes('-topmost', 'false')
window.wm_state("normal")

window.mainloop()
