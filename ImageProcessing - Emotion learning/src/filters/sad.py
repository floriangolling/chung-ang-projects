from PIL import Image
from datetime import datetime
from filters.change_image import apply_filter
import numpy as np


def sad(image_path, x, y, h, w):

    pixelToChange = []

    # Open image even grayscale and convert it to RGBA

    img = Image.open(image_path)
    rbgimg = Image.new("RGBA", img.size)
    rbgimg.paste(img)
    mask_size = 6
    # Do your algorithm

    # Set grayscale to the picture.
    for i in range(rbgimg.size[0]):
        for j in range(rbgimg.size[1]):
            r, g, b, a = rbgimg.getpixel((i, j))
            grayscale = int((r + g + b) / 3)
            rbgimg.putpixel((i, j), (grayscale, grayscale, grayscale))
    for i in range(rbgimg.size[0]):
        for j in range(rbgimg.size[1]):
            if (
                i >= mask_size
                and i <= rbgimg.size[0] - mask_size
                and j >= mask_size
                and j <= rbgimg.size[1] - mask_size
            ):
                average = []
                for k in range(0, mask_size):
                    for z in range(0, mask_size):
                        r, g, b, a = rbgimg.getpixel((i + k, z + j))
                        average.append(r)
                average = int(np.average(average))
                if (i > x or i < x + w) and (j < y or j > y + h):
                    pixelToChange.append(
                        {"x": i, "y": j, "RGBA": (average, average, average, 255)}
                    )
                elif i < x or i > x + w:
                    pixelToChange.append(
                        {"x": i, "y": j, "RGBA": (average, average, average, 255)}
                    )
    apply_filter(pixelToChange, rbgimg)

    # Save output.
    dateString = datetime.now().strftime("%m%d%Y%H-%M-%S")
    rbgimg.save("./outputs/output_sad" + dateString + ".png")
