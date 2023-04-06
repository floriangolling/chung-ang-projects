from PIL import Image
from datetime import datetime
import numpy as np

# This function get the average R, G, B values of the given img_array
# and modifies the existing image using these values.


def median(img, img_arr):
    r = np.mean(img_arr[:, 0])
    g = np.mean(img_arr[:, 1])
    b = np.mean(img_arr[:, 2])

    # data[3 / 4] are x, y positions from the flattened array created
    # with 5 channels.
    for data in img_arr:
        img[data[3]][data[4]] = [r, g, b]


# This function find the most predominant colors recursively according
# to the depth, and will find the closest colors and modify it according
# to an average.


def buckets(pillow_image, five_channel, depth):
    # The pictures has no size or at the end.
    if len(five_channel) == 0:
        return

    # The number of depth search is done, you can apply the filter with the medians.
    if depth == 0:
        median(pillow_image, five_channel)
        return

    # Find the difference between R, G, B value of the position
    # so we can find the color closer to our primary color.
    r = np.max(five_channel[:, 0]) - np.min(five_channel[:, 0])
    g = np.max(five_channel[:, 1]) - np.min(five_channel[:, 1])
    b = np.max(five_channel[:, 2]) - np.min(five_channel[:, 2])

    # Check what is the most predominant color
    range = 0
    if g >= r and g >= b:
        range = 1
    elif b >= r and b >= g:
        range = 2
    elif r >= b and r >= g:
        range = 0
    five_channel = five_channel[five_channel[:, range].argsort()]

    # Find the index of the color we have to apply and apply it.
    index = int((len(five_channel) + 1) / 2)
    buckets(pillow_image, five_channel[0:index], depth - 1)
    buckets(pillow_image, five_channel[index:], depth - 1)


def surprise(image_path):
    # Open image
    img = Image.open(image_path)
    rbgimg = Image.new("RGBA", img.size)
    rbgimg.paste(img)

    # Transform it to np.array using only 3 channels (R, G , B) => We dont need
    # The Alpha channel for this algorithm.
    rbgimg = np.array(rbgimg)
    rbgimg = rbgimg[:, :, :3]
    five_channel_img = []

    # flatten the image.
    for x, image_row in enumerate(rbgimg):
        for y, color in enumerate(image_row):
            five_channel_img.append([color[0], color[1], color[2], x, y])

    # get 5 channel np array using R, G, B, and positions.
    five_channel_img = np.array(five_channel_img)

    # Applies the algorithm recursively (the number is the depth of algorithm)
    buckets(rbgimg, five_channel_img, 4)

    # Transform the array into Pillow image and save it.
    rbgimg = Image.fromarray(rbgimg)
    dateString = datetime.now().strftime("%m%d%Y%H-%M-%S")
    rbgimg.save("./outputs/output_surprise" + dateString + ".png")
