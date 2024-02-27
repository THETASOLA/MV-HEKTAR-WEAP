#turns out beam is pure nightmare fuel so I use a different method

import os
from PIL import Image

main = "charge"
mainList = ["accuracy", "base", "fire", "hull", "power"]
second = ["chain", "adapt"]

inputfold = "generation/layers/beam/existing/"

#iterate through all the files in the input folder
for file in os.listdir(inputfold):
    if file != "output":
        img = Image.open(inputfold + file)
        for m in mainList:
            if file.endswith(m+".png"):
                for s in second:
                    imgcopy = img.copy()
                    addimg = Image.open("generation/layers/beam/" + s + ".png")
                    imgcopy.paste(addimg, (0, 0), addimg)
                    imgcopy.save(inputfold  + "output/" + file.replace(m, m + "_" + s))
