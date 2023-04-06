# How to use outside docker and outside Visual Studio

## Environnement

Install python

```
pip install -r requirements.txt
```

## Training

```
python ./src/main.py --train
```

## Emotion detection

```
python ./src/main.py [filepath]
```

# How to use inside visual studio.

## /!\ Important

You must create a python env in visual studio, and install its requirements in the env
Visual studio will show you how to do it once you open the project.

## Training

Right click on properties of the opened python project on visual studio.

Go to Debugger

In script arguments, remove everything and add --train

## Usage

Right click on properties of the opened python project on visual studio.

Go to Debugger

Write down the relative path of the picture you want to process coming from the root of the project.
ex: ./tests_images/surprise.png

# How to use inside docker

Not working because cuda using GPU into docker and docker does not allow using GPU if you don't configure it for it.

If you have allowed your GPU inside docker, just build the container

```
docker-compose build --no-cache
```

and launch it, it will by default try to open the file named 'test.png' at root.

```
docker-compose up
```
