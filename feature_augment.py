import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from skimage.filters import roberts, sobel
import matplotlib.image as mpimg
import cv2
from scipy import ndimage as nd
from PIL import ImageEnhance
from skimage import data, exposure, img_as_float

def feature_augment(image):

    #####judge contrast is low or not########
    result = exposure.is_low_contrast(image)
    print(result)

    #####enhance contrast##################
    imagenhancer_Contrast = ImageEnhance.Contrast(image)
    gam2 = imagenhancer_Contrast.enhance(2)

    # gam3 = exposure.adjust_log(image)

    # gam1.show()
    # gam2.show()

    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.set_title('orig')

    # fig, ax = plt.subplots()
    # ax.imshow(gam1)
    # ax.set_title('gam1')

    fig, ax = plt.subplots()
    ax.imshow(gam2)
    ax.set_title('gam2')
    #
    # fig, ax = plt.subplots()
    # ax.imshow(gam3)
    # ax.set_title('gam3')

    # plt.show()

    return gam2

if __name__ == "__main__":
    image_path = "./f.jpg"
    image = Image.open(image_path)

    feature_augment(image)