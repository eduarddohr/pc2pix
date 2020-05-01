from PIL import Image
import sys
import os

chair_folders = open("data/chair_folders.txt", "r")
folder_count = 0
RES = 64

os.mkdir(str(RES) + "_images/")
for folder in chair_folders:
    folder_count += 1
    print("folder: ", folder_count)

    os.mkdir(str(RES) + "_images/" + folder.rstrip('\n'))
    for i in range(20):
        img = Image.open("data/shapenet_release/renders/03001627/" + folder.rstrip('\n') + "/render_" + str(i) + ".png")
        img = img.resize((RES, RES), Image.ANTIALIAS)
        img.save(str(RES) + "_images/" + folder.rstrip('\n') + "/render_" + str(i) + "_" + str(RES) + ".png")
