from GUI import GUI

window = GUI().window
# Set Icon after window init since that would force a draw when the window isn't fully rendered yet
window.iconbitmap("rock.ico")
window.mainloop()
