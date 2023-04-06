from PIL import Image
from datetime import datetime
from filters.change_image import apply_filter


def happy(image_path):

    pixelToChange = []

    # Open image even grayscale and convert it to RGBA

    img = Image.open(image_path)
    rbgimg = Image.new("RGBA", img.size)
    rbgimg.paste(img)

    pixelToAdd = []
    pixelAddBlue = []
    # Do your algorithm

    # This loop get all RGBA value for all pixel.
    for i in range(rbgimg.size[0] - 100):
        for j in range(rbgimg.size[1] - 100):
            r, g, b, a = rbgimg.getpixel((i, j))
            pixelToChange.append({"x": i + 100, "y": j + 100, "RGBA": (r, 0, 0, 255)})
    for i in range(100, rbgimg.size[0]):
        for j in range(100, rbgimg.size[1]):
            r, g, b, a = rbgimg.getpixel((i, j))
            pixelToAdd.append({"x": i - 100, "y": j - 100, "RGBA": (0, g, 0, 255)})
    for i in range(0, rbgimg.size[0]):
        for j in range(0, rbgimg.size[1]):
            r, g, b, a = rbgimg.getpixel((i, j))
            pixelAddBlue.append({"x": i, "y": j, "RGBA": (0, 0, b, 255)})
    # Apply the changes

    rbgimg = apply_filter(pixelToChange, rbgimg)

    for pixel in pixelToAdd:
        r, g, b, a = rbgimg.getpixel((pixel["x"], pixel["y"]))
        newG = g + pixel["RGBA"][1] if g + pixel["RGBA"][1] < 255 else 255
        rbgimg.putpixel([pixel["x"], pixel["y"]], (r, newG, b, a))

    for pixel in pixelAddBlue:
        r, g, b, a = rbgimg.getpixel((pixel["x"], pixel["y"]))
        newB = b + pixel["RGBA"][1] if g + pixel["RGBA"][2] < 255 else 255
        rbgimg.putpixel([pixel["x"], pixel["y"]], (r, g, newB, a))
    # Save output.
    for i in range(0, rbgimg.size[0]):
        for j in range(0, rbgimg.size[1]):
            r, g, b, a = rbgimg.getpixel((i, j))
            rbgimg.putpixel((i, j), (r + 20, g + 20, b + 20, a))
    dateString = datetime.now().strftime("%m%d%Y%H-%M-%S")
    rbgimg.save("./outputs/output_happy" + dateString + ".png")
