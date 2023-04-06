import keras
import os
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import load_model


def get_model():
    model = None
    if os.path.exists("./model.h5"):
        model = load_model("model.h5")
    else:
        # First Layer
        model = Sequential()
        model.add(
            Conv2D(32, kernel_size=(3, 3), activation="relu", input_shape=(48, 48, 1))
        )
        model.add(Conv2D(64, kernel_size=(3, 3), activation="relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        # Second Layer
        model.add(Conv2D(128, kernel_size=(3, 3), activation="relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(128, kernel_size=(3, 3), activation="relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        # Third layer
        model.add(Flatten())
        model.add(Dense(1024, activation="relu"))
        model.add(Dropout(0.5))
        model.add(Dense(6, activation="softmax"))
    return model


def train():
    img_rows, img_cols = 48, 48
    batch_size = 128
    train_datagen = ImageDataGenerator(rescale=1.0 / 255)
    validation_datagen = ImageDataGenerator(rescale=1.0 / 255)
    train_generator = train_datagen.flow_from_directory(
        "./train_emotion",
        color_mode="grayscale",
        target_size=(img_rows, img_cols),
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=True,
    )

    validation_generator = validation_datagen.flow_from_directory(
        "./validation_emotion",
        color_mode="grayscale",
        target_size=(img_rows, img_cols),
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=True,
    )
    model = get_model()
    nb_train_samples = 24176
    nb_validation_samples = 3006
    epochs = 15
    model.compile(
        loss="categorical_crossentropy",
        optimizer=Adam(lr=0.0001, decay=1e-6),
        metrics=["accuracy"],
    )
    model_info = model.fit(
        train_generator,
        steps_per_epoch=nb_train_samples // batch_size,
        epochs=epochs,
        validation_data=validation_generator,
        validation_steps=nb_validation_samples // batch_size,
    )
    model.save("model.h5")
