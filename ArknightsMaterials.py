from GUI import GUI
from util import exceptHook

window = GUI().window
# Set Icon after window init since that would force a draw when the window isn't fully rendered yet
window.iconbitmap("rock.ico")
window.report_callback_exception=exceptHook
window.mainloop()
