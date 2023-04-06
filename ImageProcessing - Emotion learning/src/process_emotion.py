from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import cv2
import os


def process_emotion(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if not os.path.exists("model.h5"):
        return "Model does not exist, you should train IA"
    classifier = load_model("model.h5")
    class_labels = ["Angry", "Fear", "Happy", "Neutral", "Sad", "Surprise"]
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = face_cascade.detectMultiScale(gray)
    foundFace = False
    for (x, y, w, h) in faces:
        foundFace = True
        roi_gray = gray[y : y + h, x : x + w]
        cropped_img = np.expand_dims(
            np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0
        )
        preds = classifier.predict(cropped_img)
        print(preds[0])
        t = np.argmax(preds[0])
        return class_labels[t], x, y, w, h
    if not foundFace:
        print("No face found, use Surprise filter as default.")
    return "Surprise"
