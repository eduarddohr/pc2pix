from PIL import Image
import sys
import os

chair_folders = open("data/chair_folders.txt", "r")
folder_count = 0
RES = 128

# os.mkdir(str(RES) + "_images_3/")
for folder in chair_folders:
    folder_count += 1
    print("folder: ", folder_count)

    os.mkdir(str(RES) + "_images_3/03001627/" + folder.rstrip('\n'))
    for i in range(20):
        # img = Image.open("data/shapenet_release/renders/03001627/" + folder.rstrip('\n') + "/render_" + str(i) + ".png")
        # img = img.resize((RES, RES), Image.ANTIALIAS)

        png = Image.open("data/shapenet_release/renders/03001627/" + folder.rstrip('\n') + "/render_" + str(i) + "_" + str(RES) + ".png")
        png.load()  # required for png.split()

        background = Image.new("RGB", png.size, (255, 255, 255))
        background.paste(png, mask=png.split()[3])  # 3 is the alpha channel

        # background.save('real1/render_{}_64.png'.format(i), 'PNG', quality=80)

        background.save(str(RES) + "_images_3/03001627/" + folder.rstrip('\n') + "/render_" + str(i) + "_" + str(RES) + ".png", 'PNG')