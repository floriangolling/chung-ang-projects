from PIL import Image
from datetime import datetime
from filters.change_image import apply_filter
import numpy as np


def fear(image_path):

    pixelToChange = []

    # Open image even grayscale and convert it to RGBA

    img = Image.open(image_path)
    rbgimg = Image.new("RGBA", img.size)
    rbgimg.paste(img)

    # Do your algorithm

    # This loop get all RGBA value for all pixel.

    gray_array = np.zeros([rbgimg.size[0], rbgimg.size[1]])
    for i in range(rbgimg.size[0]):
        for j in range(rbgimg.size[1]):
            r, g, b, a = rbgimg.getpixel((i, j))
            gray = int((r + g + b) / 3)
            gray_array[i, j] = gray

    # cooling

    originalValues = np.array([0, 50, 100, 150, 200, 255])

    redValues = np.array([0, 10, 40, 80, 130, 230])
    blueValues = np.array([0, 80, 190, 200, 220, 255])

    # create lookup table for red channel
    allValues = np.arange(0, 256)
    redLookupTable = np.interp(allValues, originalValues, redValues)

    # create lookup table for blue channel
    blueLookupTable = np.interp(allValues, originalValues, blueValues)

    for i in range(rbgimg.size[0]):
        for j in range(rbgimg.size[1]):
            r, g, b, a = rbgimg.getpixel((i, j))

            r = redLookupTable[r]
            b = blueLookupTable[b]
            # Example of adding to the list a new pixel that has to change
            # with its value.

            pixelToChange.append({"x": i, "y": j, "RGBA": (int(r), g, int(b), 255)})

    # Apply the changes

    for newPixel in pixelToChange:
        rbgimg.putpixel([newPixel["x"], newPixel["y"]], newPixel["RGBA"])
    # Save output.
    dateString = datetime.now().strftime("%m%d%Y%H-%M-%S")
    rbgimg.save("./outputs/output_fear" + dateString + ".png")
