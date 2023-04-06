import sys
from train import train
from process_emotion import process_emotion
from apply_filter import apply_filter
import os


def main():
    relativePath = ""
    mode = True
    list = sys.argv
    for arg in list[1:]:
        if arg == "--train":
            mode = False
    if mode == False:
        return train()
    relativePath = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", list[1])
    )
    if len(list) == 1 or not os.path.exists(relativePath):
        return print("No argument given or the file is not found.")
    emotion, x, y, h, w = process_emotion(relativePath)
    print(f"Found emotion is {emotion}")
    apply_filter(emotion, relativePath, x, y, h, w)


main()
