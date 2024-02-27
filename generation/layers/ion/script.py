import os
from PIL import Image

main = "charge"
mainList = ["accuracy", "base", "fire", "hull", "power"]
second = ["chain", "adapt"]

inputfold = "generation/layers/ion/existing/"
prefix = "modular_ion_"

for s in second:
    img = Image.open(inputfold + prefix + "base.png")
    addimg = Image.open("generation/layers/ion/" + s + ".png")
    img.paste(addimg, (0, 0), addimg)
    img.save(inputfold + "output/" + prefix + main + "_" + s + ".png")

#iterate through all the files in the input folder
for file in os.listdir(inputfold):
    if file != "output":
        img = Image.open(inputfold + file)
        for m in mainList:
            if file.endswith(m+".png"):
                for s in second:
                    imgcopy = img.copy()
                    addimg = Image.open("generation/layers/ion/" + s + ".png")
                    imgcopy.paste(addimg, (0, 0), addimg)
                    imgcopy.save(inputfold  + "output/" + file.replace(m, m + "_" + s))
            elif file.__contains__("base"):
                imgcopy = img.copy()
                addimg = Image.open("generation/layers/ion/" + main + ".png")
                imgcopy.paste(addimg, (0, 0), addimg)
                imgcopy.save(inputfold + "output/" + file.replace("base", main))


