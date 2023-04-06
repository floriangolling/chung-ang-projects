from PIL import Image
from datetime import datetime
from filters.change_image import apply_filter
import numpy as np


def angry(image_path):

    pixelToChange = []

    # Open image even grayscale and convert it to RGBA

    img = Image.open(image_path)
    rbgimg = Image.new("RGBA", img.size)
    rbgimg.paste(img)
    saveImage = Image.new("RGBA", img.size)
    saveImage.paste(img)
    # Do your algorithm

    # This loop get all RGBA value for all pixel.
    gray_array = np.zeros([rbgimg.size[0], rbgimg.size[1]])
    Gx = np.array([[1.0, 0.0, -1.0], [2.0, 0.0, -2.0], [1.0, 0.0, -1.0]])
    Gy = np.array([[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]])
    sobel_filters = np.zeros(shape=(img.size[0], img.size[1]))
    for i in range(rbgimg.size[0]):
        for j in range(rbgimg.size[1]):
            r, g, b, a = rbgimg.getpixel((i, j))
            gray = int((r + g + b) / 3)
            gray_array[i, j] = gray
    for i in range(rbgimg.size[0] - 2):
        for j in range(rbgimg.size[1] - 2):
            gx = np.sum(
                np.multiply(Gx, gray_array[i : i + 3, j : j + 3])
            )  # x direction
            gy = np.sum(
                np.multiply(Gy, gray_array[i : i + 3, j : j + 3])
            )  # y direction
            color = int(np.sqrt(gx**2 + gy**2))
            rbgimg.putpixel((i + 1, j + 1), (color, color, color, 255))
    for i in range(saveImage.size[0]):
        for j in range(saveImage.size[1]):
            r, g, b, a = saveImage.getpixel((i, j))
            r1, g1, b1, a1 = rbgimg.getpixel((i, j))
            if r1 > 90:
                saveImage.putpixel((i, j), (r % 255 + 70, g - 20, b - 20, a))
    for i in range(saveImage.size[0]):
        for j in range(saveImage.size[1]):
            r, g, b, a = saveImage.getpixel((i, j))
            saveImage.putpixel((i, j), (r - 60, g - 60, b - 60, a))
    mask_size = 2
    for i in range(saveImage.size[0]):
        for j in range(saveImage.size[1]):
            if (
                i >= mask_size
                and i <= saveImage.size[0] - mask_size
                and j >= mask_size
                and j <= saveImage.size[1] - mask_size
            ):
                averageR = []
                averageB = []
                averageG = []
                for k in range(0, mask_size):
                    for z in range(0, mask_size):
                        r, g, b, a = saveImage.getpixel((i + k, z + j))
                        averageB.append(b)
                        averageG.append(g)
                        averageR.append(r)
                averageB = int(np.average(averageB))
                averageG = int(np.average(averageG))
                averageR = int(np.average(averageR))
                pixelToChange.append(
                    {"x": i, "y": j, "RGBA": (averageR, averageG, averageB, 255)}
                )
    apply_filter(pixelToChange, saveImage)
    for i in range(saveImage.size[0]):
        for j in range(saveImage.size[1]):
            if (
                i >= mask_size
                and i <= saveImage.size[0] - mask_size
                and j >= mask_size
                and j <= saveImage.size[1] - mask_size
            ):
                averageR = []
                averageB = []
                averageG = []
                for k in range(0, mask_size):
                    for z in range(0, mask_size):
                        r, g, b, a = saveImage.getpixel((i + k, z + j))
                        averageB.append(b)
                        averageG.append(g)
                        averageR.append(r)
                averageB = int(np.average(averageB))
                averageG = int(np.average(averageG))
                averageR = int(np.average(averageR))
                pixelToChange.append(
                    {"x": i, "y": j, "RGBA": (averageR, averageG, averageB, 255)}
                )
    apply_filter(pixelToChange, saveImage)
    for i in range(saveImage.size[0]):
        for j in range(saveImage.size[1]):
            r, g, b, a = saveImage.getpixel((i, j))
            saveImage.putpixel((i, j), (r + 10, g + 5, b + 5, a))
    dateString = datetime.now().strftime("%m%d%Y%H-%M-%S")
    saveImage.save("./outputs/output_angry" + dateString + ".png")
