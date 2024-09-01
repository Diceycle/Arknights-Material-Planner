import threading
import time
import shutil

from PIL import Image

from utilImport import *
from database import DEPOT_ORDER
from WindowHandler import resolveHandler
from imageRecognizing import matchMasked
from ocr import readImage, prepareImage

SCREENSHOT_SIZE = (1641, 923)
WINDOW_BORDER = CONFIG.arknightsWindowBorder

DEPOT_CHECKS = [
    ((1425, 40), (50, 50, 50)),
    ((1420, 55), (50, 50, 50)),
    ((1440, 55), (50, 50, 50)),
    ((1430, 54), None)
]

DEPOT_FILTER_CHECKS = [
    ((1425, 40), (255, 255, 255)),
    ((1420, 55), (255, 255, 255)),
    ((1440, 55), (255, 255, 255)),
    ((1433, 47), None)
]

MAIN_MENU_CHECKS = [
    ((60, 35), (255, 255, 255)),
    ((170, 70), (255, 255, 255)),
    ((220, 70), (255, 255, 255)),
    ((30, 450), (50, 50, 50))
]
MAIN_MENU_DEPOT_BUTTON = (1530, 830)

DEPOT_BUTTON_SIZE = 250

FIRST_MATERIAL_CENTER = (160, 240)
FIRST_MATERIAL_CENTER_END = (269, 240)
MATERIAL_DISTANCE = (199, 243)
BOX_RADIUS = 120
BOXES_ON_SCREEN = (7, 3)

SCROLL_LINE_START = (1425 + CONFIG.depotScanScrollOffset, 360)
SCROLL_LINE_END = (25, 360)

DEPOT_END_CHECKS = [
    (1560, 160),
    (1560, 210),
    (1560, 250),
    (1560, 290),
    (1560, 330)
]

AMOUNT_CROP_BOX = (118, 157, 181, 192)
AMOUNT_CROP_BOX_SLIM = (123, 163, 176, 188)

def matchesColor(c1, c2, leniency = 3):
    return (abs(c1[0] - c2[0]) <= leniency and
            abs(c1[1] - c2[1]) <= leniency and
            abs(c1[2] - c2[2]) <= leniency)

def resizeArknights(windowHandler):
    windowHandler.resize((int(round(SCREENSHOT_SIZE[0] / CONFIG.displayScale)) + WINDOW_BORDER[0] + WINDOW_BORDER[2],
                          int(round(SCREENSHOT_SIZE[1] / CONFIG.displayScale)) + WINDOW_BORDER[1] + WINDOW_BORDER[3]))

def takeScreenshot(windowHandler):
    windowHandler.activate()
    resizeArknights(windowHandler)

    screenshot = windowHandler.takeScreenshot().crop((
        int(round(WINDOW_BORDER[0] * CONFIG.displayScale)),
        int(round(WINDOW_BORDER[1] * CONFIG.displayScale)),
        SCREENSHOT_SIZE[0] + int(round(WINDOW_BORDER[0] * CONFIG.displayScale)),
        SCREENSHOT_SIZE[1] + int(round(WINDOW_BORDER[1] * CONFIG.displayScale))))
    return screenshot.convert("RGB")

def scrollArknights(windowHandler):
    windowHandler.dragLine(SCROLL_LINE_START, SCROLL_LINE_END, CONFIG.depotScanScrollDelay)
    # Give Arknights time to snap back in case of overscroll
    time.sleep(0.5)

def checkEndOfDepot(image):
    for p in DEPOT_END_CHECKS:
        pix = image.getpixel(p)
        if pix[0] < 200 or pix[1] < 200 or pix[2] < 200:
            return False

    return True

def splitScreenshot(screenshot, firstBoxPosition):
    boxes = []
    for x in range(BOXES_ON_SCREEN[0]):
        for y in range(BOXES_ON_SCREEN[1]):
            posX = firstBoxPosition[0] + x * MATERIAL_DISTANCE[0]
            posY = firstBoxPosition[1] + y * MATERIAL_DISTANCE[1]
            boxes.append(screenshot.crop((posX - BOX_RADIUS, posY - BOX_RADIUS,
                                          posX + BOX_RADIUS, posY + BOX_RADIUS)))

    return boxes

def readAmount(box, fileName = None):
    crop = box.crop(AMOUNT_CROP_BOX)
    if CONFIG.debug:
        safeSave(crop, "debug/numbers/{}.png".format(fileName))
    ocrCrop = prepareImage(crop)
    ocrResult = readImage(ocrCrop)
    if CONFIG.debug:
        safeSave(ocrCrop, "debug/numbers_processed/{}_{}.png".format(fileName, ocrResult))
    return ocrResult

def validateMenu(handler):
    image = takeScreenshot(handler)
    if CONFIG.debug:
        safeSave(image, "debug/menu.png")

    filterPreselected = True
    for p in DEPOT_FILTER_CHECKS:
        if (p[1] is not None and not matchesColor(image.getpixel(p[0]), p[1], leniency=CONFIG.colorLeniency) or
            p[1] is None and matchesColor(image.getpixel(p[0]), DEPOT_FILTER_CHECKS[0][1], leniency=min(3, 256 - CONFIG.colorLeniency))):
            filterPreselected = False
            break

    if filterPreselected:
        handler.click((DEPOT_CHECKS[0][0][0] - DEPOT_BUTTON_SIZE, DEPOT_CHECKS[0][0][1]), delay=0.5)
        handler.click(DEPOT_CHECKS[0][0], delay=0.5)
        LOGGER.debug("Scan: I'm in the depot with the Growth Material filter is preselected")
        return takeScreenshot(handler)

    mainMenu = True
    for p in MAIN_MENU_CHECKS:
        if not matchesColor(image.getpixel(p[0]), p[1], leniency=CONFIG.colorLeniency):
            mainMenu = False
            break

    if mainMenu:
        handler.click(MAIN_MENU_DEPOT_BUTTON, delay=1)
        handler.click(DEPOT_CHECKS[0][0], delay=0.5)
        LOGGER.debug("Scan: I'm in the main menu")
        return takeScreenshot(handler)

    inDepot = True
    for p in DEPOT_CHECKS:
        if (p[1] is not None and not matchesColor(image.getpixel(p[0]), p[1], leniency=CONFIG.colorLeniency) or
            p[1] is None and matchesColor(image.getpixel(p[0]), DEPOT_CHECKS[0][1], min(3, 256 - CONFIG.colorLeniency))):
            inDepot = False
            break

    if inDepot:
        handler.click(DEPOT_CHECKS[0][0], delay=0.5)
        LOGGER.debug("Scan: I'm in the depot")
        return takeScreenshot(handler)

    return None

class DepotParser:
    def __init__(self, image = None, confidenceThreshold = 0.95, debug = False):
        if not image:
            self.handler = resolveHandler(CONFIG.arknightsWindowName,
                                          childClass=CONFIG.arknightsInputWindowClass,
                                          advancedResolutionMode=CONFIG.usesBlueStacks() or CONFIG.usesLDPlayer())
            self.image = None
        else:
            self.handler = None
            self.image = image

        self.debug = debug
        self.confidenceThreshold = confidenceThreshold
        self.scrollThread = None


    def startParsing(self, statusCallback, materialCallback, finishCallback):
        if self.image is None and not self.handler.ready:
            statusCallback("Arknights is not running or cannot be found. Check your Arknights Window configuration.", error = True)
            finishCallback(False)
            return

        if CONFIG.tesseractExeLocation is None:
            statusCallback("Tesseract Exe needs to be configured", error = True)
            finishCallback(False)
            return

        self.materialIndex = 0
        self.finalPage = False
        self.interrupted = False

        if CONFIG.debug:
            shutil.rmtree("debug", ignore_errors=True)

        if self.handler is not None:
            screenshot = validateMenu(self.handler)
        else:
            screenshot = Image.open(self.image).convert("RGB")

        if screenshot is None:
            statusCallback("Can not scan depot from here, please navigate to the main menu or the depot.", error = True)
            finishCallback(False)
            return

        self.loadNextPage(screenshot, firstPage=True)
        threading.Thread(target=lambda : self.parse(statusCallback, materialCallback, finishCallback)).start()


    def loadNextPage(self, screenshot, firstPage = False):
        if checkEndOfDepot(screenshot):
            self.finalPage = True
            self.boxes = splitScreenshot(screenshot, FIRST_MATERIAL_CENTER_END)
            if not firstPage:
                self.boxIndex = self.findFirstUnknownBox()
            else:
                self.boxIndex = 0
        else:
            self.boxes = splitScreenshot(screenshot, FIRST_MATERIAL_CENTER)
            self.boxIndex = 0
            self.scrollThread = threading.Thread(target=lambda : scrollArknights(self.handler))
            self.scrollThread.start()
        self.lastTopRow = [None for i in range(BOXES_ON_SCREEN[0])]

    def findFirstUnknownBox(self):
        c = 0
        for m in self.lastTopRow:
            if matchMasked(self.boxes[0], m)[1] > self.confidenceThreshold:
                return (BOXES_ON_SCREEN[0] - c) * BOXES_ON_SCREEN[1]
            c += 1
        return 0

    def parse(self, statusCallback, materialCallback, finishCallback):
        threads = []
        statusCallback("Scanning...")
        while self.materialIndex < len(DEPOT_ORDER) and not self.interrupted:
            if self.boxIndex >= len(self.boxes):
                if self.handler is not None and not self.finalPage:
                    if self.scrollThread.is_alive():
                        statusCallback("Waiting for scroll to finish...")
                    self.scrollThread.join()
                    statusCallback("Scanning...")
                    self.loadNextPage(takeScreenshot(self.handler))

            thread = self.parseMaterialAmount(materialCallback, statusCallback)
            if thread is not None:
                threads.append(thread)
            self.materialIndex += 1

        for t in threads:
            t.join()

        finishCallback(self.materialIndex >= len(DEPOT_ORDER))

    def parseMaterialAmount(self, materialCallback, statusCallback):
        material = MATERIALS[DEPOT_ORDER[self.materialIndex]]
        box = self.boxes[self.boxIndex]

        result, confidence = matchMasked(box, material)
        if CONFIG.debug:
            safeSave(result, "debug/boxes/{}_{:.3}.png".format(self.materialIndex, confidence))
        if confidence > self.confidenceThreshold:
            if self.boxIndex % BOXES_ON_SCREEN[1] == 0:
                self.lastTopRow[self.boxIndex // BOXES_ON_SCREEN[1]] = material
            self.boxIndex += 1
            return self.readAmountAsync(box, self.materialIndex, material, materialCallback, statusCallback)
        else:
            materialCallback(material, self.convertAmount(None))
            return None

    def readAmountAsync(self, box, materialIndex, material, materialCallback, statusCallback):
        def readAndNotifyAmount():
            try:
                amount = readAmount(box, fileName=materialIndex)
                materialCallback(material, self.convertAmount(amount))
            except Exception as e:
                self.interrupted = True
                statusCallback("Error encountered during scanning of depot: " + str(e), error = True)
                LOGGER.exception("Scanning Error: ")

        thread = threading.Thread(target=readAndNotifyAmount)
        thread.start()
        return thread

    def convertAmount(self, amount):
        if amount is None:
            amount = 0
        else:
            try:
                amount = int(amount)
            except Exception as e:
                LOGGER.debug("Could not read amount. Was '%s'", amount)
                amount = None

        return amount

    def stop(self):
        self.interrupted = True

    def destroy(self):
        if self.handler is not None:
            self.handler.cleanup()