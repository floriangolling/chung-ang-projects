from PIL import Image
from datetime import datetime
from filters.change_image import apply_filter


def neutral(image_path):

    pixelToChange = []

    # Open image even grayscale and convert it to RGBA

    img = Image.open(image_path)
    rbgimg = Image.new("RGBA", img.size)
    rbgimg.paste(img)
    RedminIntensity = 255
    RedmaxIntensity = 0
    GreenminIntensity = 255
    GreenmaxIntensity = 0
    BlueminIntensity = 255
    BluemaxIntensity = 0
    # Do your algorithm

    # This loop get all RGBA value for all pixel.
    for i in range(rbgimg.size[0]):
        for j in range(rbgimg.size[1]):
            r, g, b, a = rbgimg.getpixel((i, j))
            RedminIntensity = min(RedminIntensity, r)
            RedmaxIntensity = max(RedmaxIntensity, r)
            GreenminIntensity = min(GreenminIntensity, g)
            GreenmaxIntensity = max(GreenmaxIntensity, g)
            BlueminIntensity = min(BlueminIntensity, b)
            BluemaxIntensity = max(BluemaxIntensity, b)
            # Example of adding to the list a new pixel that has to change
            # with its value.

    for i in range(rbgimg.size[0]):
        for j in range(rbgimg.size[1]):
            r, g, b, a = rbgimg.getpixel((i, j))
            newR = 255 * ((r - RedminIntensity) / (RedmaxIntensity - RedminIntensity))
            newG = 255 * (
                (g - GreenminIntensity) / (GreenmaxIntensity - GreenminIntensity)
            )
            newB = 255 * (
                (b - BlueminIntensity) / (BluemaxIntensity - BlueminIntensity)
            )
            pixelToChange.append(
                {"x": i, "y": j, "RGBA": (int(newR), int(newG), int(newB), 255)}
            )
    # Apply the changes

    rbgimg = apply_filter(pixelToChange, rbgimg)

    # Save output.
    dateString = datetime.now().strftime("%m%d%Y%H-%M-%S")
    rbgimg.save("./outputs/output_neutral" + dateString + ".png")
