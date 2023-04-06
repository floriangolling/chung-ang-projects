from PIL import Image


def apply_filter(pixels_infos, img):
    for newPixel in pixels_infos:
        img.putpixel([newPixel["x"], newPixel["y"]], newPixel["RGBA"])
    return img
