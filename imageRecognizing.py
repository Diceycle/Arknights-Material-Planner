import cv2
import numpy as np
from PIL import Image, ImageDraw

def matchMasked(targetRGB, material):
    templateImage = material.renderImage().convert("RGB")
    mask = createMask(material, templateImage.size)

    return findMatch(targetRGB, templateImage, mask=mask)

def findMatch(image, template, mask=None):
    w, h = template.size
    redCircle = image.copy()

    res = cv2.matchTemplate(np.array(image), np.array(template), cv2.TM_CCOEFF_NORMED, mask=mask)
    # CCOEFF_NORMED sometimes outputs infinity instead of 0 filter those occurrences
    res[res == np.inf] = 0
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    loc = max_loc
    mask = Image.fromarray(np.uint8(mask), mode="L")
    draw = ImageDraw.Draw(redCircle)
    draw.rectangle((loc, (loc[0] + w, loc[1] + h)), outline = (255,), width = 2)

    return redCircle, max_val

def createMask(material, size):
    mask = centerTransparentImage(material.image, size)
    # Mask MUST be Float32 Type to assign weights to the pixels
    mask = np.array(mask.getchannel("A"), dtype=np.float32)
    # Increase significance of central area where the class icons are on the class chips
    mask /= 2
    mask[56:111, 68:123] *= 2

    return mask

def centerTransparentImage(image, size, color = (255, 255, 255, 0)):
    background = Image.new("RGBA", size, color)
    background.alpha_composite(image, dest=((background.width - image.width) // 2,
                                            (background.height - image.height) // 2))
    return background