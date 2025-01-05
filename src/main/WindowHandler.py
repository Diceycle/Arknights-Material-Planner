import time
from ctypes import windll

import win32api
import win32con
import win32gui
import win32ui
from PIL import Image

from utilImport import LOGGER, CONFIG


def resolveHandler(windowName, childClass, advancedResolutionMode):
    handler = WindowHandler(windowName)
    children = listChildWindows(handler.hwnd)
    if advancedResolutionMode:
        for child in children.values():
            # HINT, BlueStacks and LDPlayer usually have one enabled child window that takes input for the app
            if child[1]:
                handler.hwndInput = child[0]
                LOGGER.debug("NEW HWND_INPUT: %s", child[0])
    else:
        if childClass is not None:
            for className, child in children.items():
                if className.lower() == childClass.lower():
                    handler.hwndInput = child[0]
                    LOGGER.debug("NEW HWND_INPUT: %s", child[0])
                    return 

    return handler

class WindowHandler:
    def __init__(self, windowName, childClassName = None, captureBorder=False):
        self.windowName = windowName
        self.childClassName = childClassName
        self.captureBorder = captureBorder

        self.hwnd = None
        self.hwndInput = None
        self.hwndDC = None
        self.mfcDC  = None
        self.saveDC = None

        self.bitmapBuffer = None

        self.initializeContext()

    def initializeContext(self):
        try:
            self.findWindowHandler()
            self.findDeviceContexts()
            self.updateBitmapBuffer()
            self.ready = True

            LOGGER.debug("HWND: %s", self.hwnd)
            LOGGER.debug("HWND_INPUT: %s", self.hwndInput)
            LOGGER.debug("HWND_DC: %s", self.hwndDC)
            LOGGER.debug("MFC_DC: %s", self.mfcDC)
            LOGGER.debug("SAVE_DC: %s", self.saveDC)

        except Exception as err:
            LOGGER.error("Failed to initialize Context: %s", err)
            self.cleanup()
            self.ready = False

    def findWindowHandler(self):
        self.hwnd = win32gui.FindWindow(None, self.windowName)
        if self.childClassName is not None:
            self.hwndInput = win32gui.FindWindowEx(self.hwnd, 0, self.childClassName, None)
        else:
            self.hwndInput = self.hwnd

        if self.hwnd == 0 or self.hwndInput == 0:
            raise Exception("Did not find Window with title: " + self.windowName)

    def findDeviceContexts(self):
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC  = win32ui.CreateDCFromHandle(self.hwndDC)
        self.saveDC = self.mfcDC.CreateCompatibleDC()

    def findWindowDimensions(self, includeBorder):
        if includeBorder:
            # GetWindowRect = Window + Border
            left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
        else:
            # GetClientRect = WindowContent - Top-Left is always (0,0)
            left, top, right, bot = win32gui.GetClientRect(self.hwnd)

        return left, top, right - left, bot - top

    def updateBitmapBuffer(self):
        left, top, width, height = self.findWindowDimensions(self.captureBorder)

        self.cleanBitmapBuffer()
        self.bitmapBuffer = win32ui.CreateBitmap()
        self.bitmapBuffer.CreateCompatibleBitmap(self.mfcDC, width, height)

        self.saveDC.SelectObject(self.bitmapBuffer)

    def activate(self):
        placement = win32gui.GetWindowPlacement(self.hwnd)
        if win32con.SW_SHOWMINIMIZED == placement[1]:
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWNOACTIVATE)
            time.sleep(0.5)

        win32gui.SendMessage(self.hwnd, win32con.WM_ACTIVATE, win32con.WA_CLICKACTIVE, 0)

    def resize(self, dimensions):
        # Establish consistent Window-Dimensions so pixel values always line up
        left, top, width, height = self.findWindowDimensions(includeBorder=True)
        win32gui.SetWindowPos(self.hwnd, None, left, top, dimensions[0], dimensions[1], win32con.SWP_NOACTIVATE + win32con.SWP_NOZORDER)

        self.updateBitmapBuffer()

    def click(self, position, delay = 0.001):
        encodedCoords = win32api.MAKELONG(position[0], position[1])

        win32gui.PostMessage(self.hwndInput, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, encodedCoords)
        win32gui.PostMessage(self.hwndInput, win32con.WM_LBUTTONUP, None, encodedCoords)

        time.sleep(delay)

    def dragLine(self, start, end, delayScale, interruptCheckCallback=None):
        def dragLineInternal(start, end, delayScale, mouseDown, drag, mouseUp):
            mouseDown(start)

            points = 50
            for i in range(points):
                if interruptCheckCallback is not None and interruptCheckCallback():
                    break
                time.sleep(.01 * delayScale)
                pos = (start[0] + int((end[0] - start[0]) / points * (i + 1)),
                       start[1] + int((end[1] - start[1]) / points * (i + 1)))
                drag(pos)
            time.sleep(.3)
            mouseUp(end)

        dragLineInternal(
            start, end, delayScale,
            lambda coords: win32gui.PostMessage(self.hwndInput, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(coords[0], coords[1])),
            lambda coords: win32gui.PostMessage(self.hwndInput, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, win32api.MAKELONG(coords[0], coords[1])),
            lambda coords: win32gui.PostMessage(self.hwndInput, win32con.WM_LBUTTONUP, None, win32api.MAKELONG(coords[0], coords[1])))

    def takeScreenshot(self):
        self.printWindowToBuffer()
        bmpinfo = self.bitmapBuffer.GetInfo()
        bmpstr = self.bitmapBuffer.GetBitmapBits(True)

        im = Image.frombuffer('RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        return im

    def printWindowToBuffer(self):
        borderFlag = 1
        if self.captureBorder:
            borderFlag = 0

        return windll.user32.PrintWindow(self.hwnd, self.saveDC.GetSafeHdc(), borderFlag)

    def cleanup(self):
        # Clean Device Contexts
        self.cleanBitmapBuffer()

        if self.saveDC is not None:
            self.saveDC.DeleteDC()
            self.saveDC = None

        if self.mfcDC is not None:
            try:
                self.mfcDC.DeleteDC()
            except win32ui.error as err:
                print("mfcDC delete failed:", err)
            finally:
                self.mfcDC = None

        if self.hwndDC is not None and self.hwnd is not None:
            win32gui.ReleaseDC(self.hwnd, self.hwndDC)
            self.hwndDC = None
            self.hwnd = None
            self.hwndInput = None

    def cleanBitmapBuffer(self):
        if self.bitmapBuffer is not None:
            win32gui.DeleteObject(self.bitmapBuffer.GetHandle())
            self.bitmapBuffer = None
        
    def __del__(self):
        self.cleanup()

def listWindows():
    import ctypes

    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible

    titles = []

    def foreach_window(hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            titles.append(buff.value)
        return True

    EnumWindows(EnumWindowsProc(foreach_window), 0)
    LOGGER.debug("Available Window Titles: %s", titles)

def listChildWindows(hwnd):
    childHandles = {}

    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            hwnds[win32gui.GetClassName(hwnd)] = (hwnd, win32gui.IsWindowEnabled(hwnd), win32gui.GetParent(hwnd))
        return True

    win32gui.EnumChildWindows(hwnd, callback, childHandles)

    return childHandles

if __name__ == "__main__":
    from util import CONFIG
    s = WindowHandler(CONFIG.arknightsWindowName, childClassName=CONFIG.arknightsInputWindowClass, captureBorder=False)
    if not s.ready:
        LOGGER.debug("Could not find Window with title '%s'", CONFIG.arknightsWindowName)
        listWindows()
    else:
        for k, v in listChildWindows(s.hwnd).items():
            LOGGER.debug("Child: %s, %s", k, v)
    input("Press Enter to close...")