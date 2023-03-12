import os

import cv2
import numpy as np
from PIL import Image

from utilImport import MATERIALS, safeSave


def findMatches(image, template, mask=None, threshold=None):
    w, h = template.shape[:-1]

    res = cv2.matchTemplate(image, template, cv2.TM_CCORR_NORMED, mask=mask)
    if threshold is not None:
        loc = np.where(res >= threshold)
    else:
        loc = np.where(res == res.max())
    maximum = np.where(res == res.max())

    result = image.copy()
    for pt in zip(*loc[::-1]):  # Switch columns and rows
        cv2.rectangle(result, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

    return result, res[maximum[0][0], maximum[1][0]]

def matchMasked(targetRGB, material, savePath=None, threshold=None, debug=False):
    targetImage = pilConversion(targetRGB)
    templateImage = material.renderImage()
    mask = getMaskMaterialFocus(material)

    alpha = pilToMask(mask)
    if debug:
        safeSave(mask, "img/masks/" + material.name + ".png")

    matchImage, confidence = findMatches(targetImage, pilConversion(templateImage.convert("RGB")), mask=alpha, threshold=threshold)
    if debug:
        fileName = savePath + material.name + "_" + str(int(confidence*100)) + ".png"
        print(fileName)
        cv2.imwrite(fileName, matchImage)

    return confidence

def getMaskMaterialFocus(material):
    templateImage = material.renderImage()
    materialMask = addBackgroundToRawMaterial(material).getchannel("A")
    borderMask = Image.eval(templateImage.getchannel("A"), lambda v : v // 2)

    return Image.fromarray(np.maximum(materialMask, borderMask), mode="L")

def addBackground(image, size = None, color = (255, 255, 255, 255)):
    if size is None:
        size = image.size
    background = Image.new("RGBA", size, color)
    background.alpha_composite(image, dest=((background.width - image.width) // 2,
                                            (background.height - image.height) // 2))

    return background

def addBackgroundToRawMaterial(material):
    templateImage = material.renderImage()
    return addBackground(material.image, color = (255, 255, 255, 0), size = templateImage.size)

def pilConversion(rgbPilImage):
    open_cv_image = np.array(rgbPilImage)
    # Convert RGB to BGR
    return open_cv_image[:, :, ::-1].copy()

def pilToMask(singleChannel):
    openCVMask = np.array(singleChannel)
    for x in range(singleChannel.width):
        for y in range(singleChannel.height):
            openCVMask[x][y] /= 255

    return openCVMask

def runFullImageRecognitionTest(cvImage, contents):
    for f in os.listdir("img/negatives"):
        os.remove("img/negatives/" + f)

    for f in os.listdir("img/positives"):
        os.remove("img/positives/" + f)

    confidence = 1
    for m in contents:
        con = matchMasked(cvImage, MATERIALS[m], savePath ="img/positives/", debug = True)
        if con < confidence:
            confidence = con

    print("\nMinimum Confidence:", confidence, "\n")
    negCon = 0
    for m in MATERIALS.keys():
        if not m in contents:
            con = matchMasked(cvImage, MATERIALS[m], savePath ="img/negatives/", threshold=confidence, debug = True)
            if con > confidence:
                print("False Positive!\n")
            if con > negCon:
                negCon = con
    print("\nBiggest Negative Confidence:", negCon)