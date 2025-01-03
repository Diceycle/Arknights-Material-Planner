from PIL import Image

SCANLINE_HIGH = 58
SCANLINE_LOW = 91

def readImage(imageL):
    number = ""
    lastBlack = imageL.width

    for x in range(imageL.width - 1, 0, -1):
        whiteDetected = False
        for y in range(imageL.height):
            whiteDetected = whiteDetected or imageL.getpixel((x, y))
        if not whiteDetected:
            if lastBlack - 1 > x:
                numberImage = imageL.copy().crop((x, 0, lastBlack, imageL.height))
                number = readNumber(numberImage) + number
            lastBlack = x

    return number

def readNumber(imageL):
    high = []
    white = False
    for x in range(imageL.width):
        p = imageL.getpixel((x, SCANLINE_HIGH))
        if p and not white:
            high.append(x)
            white = True
        if not p and white:
            white = False

    low = []
    white = False
    for x in range(imageL.width):
        p = imageL.getpixel((x, SCANLINE_LOW))
        if p and not white:
            low.append(x)
            white = True
        if not p and white:
            white = False

    vertical = []
    white = False
    for y in range(imageL.height):
        p = imageL.getpixel((imageL.width // 2, y))
        if p and not white:
            vertical.append(y)
            white = True
        if not p and white:
            white = False

    if len(high) == 1 and len(low) == 1 and len(vertical) == 1:
        return '1'
    elif len(high) == 1 and len(low) == 1 and len(vertical) == 3 and high[0] - low[0] > 10:
        return '2'
    elif len(high) == 1 and len(low) == 1 and len(vertical) != 1 and abs(high[0] - low[0]) < 5:
        return '3'
    elif len(high) == 2 and len(low) == 1 and len(vertical) == 2:
        return '4'
    elif len(high) == 1 and len(low) == 1 and len(vertical) == 3 and high[0] - low[0] < -10:
        return '5'
    elif len(high) == 1 and len(low) == 2 and len(vertical) == 3:
        return '6'
    elif len(high) == 1 and len(low) == 1 and len(vertical) == 2 and high[0] - low[0] > 5:
        return '7'
    elif len(high) == 2 and len(low) == 2 and len(vertical) == 3:
        return '8'
    elif len(high) == 2 and len(low) == 1 and len(vertical) == 3:
        return '9'
    elif len(high) == 2 and len(low) == 2 and len(vertical) == 2:
        return '0'
    else:
        return ''

def detectOverlay(imageRGB):
    hsv = imageRGB.convert("HSV")

    lastValue = [0 for i in range(imageRGB.height)]

    for x in range(imageRGB.width):
        value = []
        for y in range(imageRGB.height):
            value.append(hsv.getpixel((x, y))[2])
        if sum(t[0] > t[1] for t in zip(lastValue, value)) >= len(value):
            return imageRGB.crop((x, 0, imageRGB.width, imageRGB.height))
        lastValue = value

    return imageRGB

def filterNoise(imageRGB, saturationThreshold, valueThreshold):
    hsv = imageRGB.convert("HSV")
    for x in range(imageRGB.width):
        for y in range(imageRGB.height):
            p = hsv.getpixel((x, y))
            if p[1] > saturationThreshold or p[2] < valueThreshold:
                imageRGB.putpixel((x, y), (0, 0, 0))
            else:
                imageRGB.putpixel((x, y), (255, 255, 255))

def prepareImage(image):
    # Scale up image to work more precisely
    image = image.resize((int(image.width*4), int(image.height*4)), Image.BICUBIC)

    # Try and crop the image at the start of the dark transparent overlay to reduce artifacts
    image = detectOverlay(image)

    # Filter anything that is either too colorful or too dark to be white font
    filterNoise(image, saturationThreshold=10, valueThreshold=210)

    # Convert to grayscale
    image = image.convert("L")

    return image




