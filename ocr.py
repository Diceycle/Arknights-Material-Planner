import os
import time
import pytesseract
from PIL import ImageOps, Image

from config import CONFIG
from database import safeSave

pytesseract.pytesseract.tesseract_cmd = CONFIG.tesseractExeLocation

CHARACTER_WHITELIST = "-c tessedit_char_whitelist=0123456789"
READ_MODE = "--psm 10"

def readImage(image):
    return pytesseract.image_to_string(image, config=READ_MODE + " " + CHARACTER_WHITELIST)

def getAdjacent(coords):
    return ((coords[0] - 1, coords[1]), (coords[0] + 1, coords[1]),
            (coords[0], coords[1] - 1), (coords[0], coords[1] + 1))

def filterNoise(imageRGB, saturationThreshold, valueThreshold):
    hsv = imageRGB.convert("HSV")
    for x in range(imageRGB.width):
        for y in range(imageRGB.height):
            p = hsv.getpixel((x, y))
            if p[1] > saturationThreshold or p[2] < valueThreshold:
                imageRGB.putpixel((x, y), (0, 0, 0))
            else:
                imageRGB.putpixel((x, y), (255, 255, 255))

def trimBorders(image):
    borders = []
    for x in range(image.width):
        borders.append((x, 0))
        borders.append((x, image.height - 1))
    for y in range(image.height):
        borders.append((0, y))
        borders.append((image.width - 1, y))

    c = 0
    while c < len(borders):
        pix = borders[c]
        if pix[0] < 0 or pix[0] >= image.width or pix[1] < 0 or pix[1] >= image.height:
            c += 1
            continue
        if image.getpixel(pix) != 255:
            image.putpixel(pix, 255)
            borders.extend(getAdjacent(pix))
        c += 1

def getCroppedSides(image, scanline, allowedWhitespace, maxWhitespaceStreak):
    lastX = image.width
    whiteSpaceStreak = 0
    for x in range(image.width - 1, 0, -1):
        if image.getpixel((x, scanline)) == 0 and whiteSpaceStreak < maxWhitespaceStreak:
            whiteSpaceStreak = 0
            lastX = x
        else:
            if lastX != image.width:
                whiteSpaceStreak += 1

    image = image.crop((max(0, lastX - allowedWhitespace), 0, image.width, image.height))

    lastX = 0
    for x in range(image.width):
        if image.getpixel((x, scanline)) == 0:
            lastX = x
    image = image.crop((0, 0, min(lastX + allowedWhitespace, image.width), image.height))

    return image

def applyDilation(image, radius = 1):
    for i in range(radius):
        character = []
        for x in range(image.width):
            for y in range(image.height):
                if image.getpixel((x,y)) == (255,255,255):
                    character.extend(getAdjacent((x,y)))

        for pix in character:
            if not (pix[0] < 0 or pix[0] >= image.width or pix[1] < 0 or pix[1] >= image.height):
                image.putpixel(pix, (255,255,255))

def prepareImage(image):
    # Scale up image to work more precisely
    image = image.resize((int(image.width*4), int(image.height*4)), Image.BICUBIC)

    # Filter anything that is either too colorful or too dark to be white font
    filterNoise(image, saturationThreshold=30, valueThreshold=120)

    # Convert to grayscale and invert as Tesseract likes dark text on white background
    image = ImageOps.invert(image.convert("L"))

    # Remove any non-white artifact that is touching the edges
    trimBorders(image)

    # Scale down the image to get some anti-alias back and hit the tesseract font size sweetspot of ~32px
    image = image.resize((image.width // 5 * 2, image.height // 5 * 2))

    # Scan along the middle and remove any excessive whitespace left or right of the text
    image = getCroppedSides(image, scanline=image.height // 2, allowedWhitespace=20, maxWhitespaceStreak=20)
    # Trim again in case the cropping exposed more artifacts to the edges
    trimBorders(image)

    # Literally just stretch that boi and shrink him down again to add more anti-alias in the y-axis, I think?
    # Why? Idk it worked on the single 9s (those bitches)
    image = image.resize((image.width, image.height * 10)).resize((image.width, image.height))

    # Finally, stretch that boi on the x-axis because apparently tesseract likes absolute units
    # Arknights' Font seems too slim in general but this really helped with the trailing 1s
    return image.resize((int(image.width * 1.5), image.height))

def readFile(folder, file, processedFolder = None, reprocess = True):
    if reprocess:
        image = Image.open(folder + "/" + file).convert("RGB")
        image = prepareImage(image)
    else:
        image = Image.open(processedFolder + "/" + file).convert("RGB")
    return readImage(image), image

if __name__ == "__main__":
    start = time.time()
    fails = 0
    c = 0
    testFolder = "img/tests"
    for f in os.listdir(testFolder):
        number = f[:f.index(".")]
        expectedResult = expectedResults_new[number]
        result, inputImage = readFile(testFolder, f, processedFolder="img/processed", reprocess=True)
        if expectedResult != result:
            print("Failed {}: {} != {}".format(f, expectedResult, result))
            fails += 1
        c += 1
        safeSave(inputImage, "img/processed/" + f)
    print("Error Rate: {}/{} = {:.2f}%".format(fails, c, fails/c * 100))
    print("Took:", time.time() - start)

