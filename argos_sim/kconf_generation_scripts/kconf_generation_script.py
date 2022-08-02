from datetime import datetime
import numpy as np
import cv2 as cv

# TODO Parameters to choose
conf_file_name = 'aggregation_arena'  # name of the generated config file
image_name = "empty_half.png"  # name of the image file

im = cv.imread(image_name)

gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
gray = gray.transpose()
gray = np.fliplr(gray)
gray = np.rot90(gray, 2)

print(gray)

# TODO change values according to your image
gray[gray == 96] = 1 #red
gray[gray == 158] = 2 #grey
gray[gray == 0] = 3 #white
gray[gray == 255] = 4 #black
print(gray)

with open(conf_file_name + '.kconf', 'w') as f:
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print('# Experiment: ', conf_file_name, file=f)
    print('# Generation Time: ', dt_string, file=f)
    print('\n', file=f)

    # writing for each module
    for x in range(10):
        for y in range(20):
            # print header
            print('address', file=f)
            print('module:' + str(x) + '-' + str(y) + '\n', file=f)
            print('data', file=f)
            # fill with values ..
            print(hex(gray[x * 2, y * 2 + 1]), file=f)
            print(hex(gray[x * 2 + 1, y * 2 + 1]), file=f)
            print(hex(gray[x * 2, y * 2]), file=f)
            print(hex(gray[x * 2 + 1, y * 2]), file=f)
            # needed for structure
            print('', file=f)
