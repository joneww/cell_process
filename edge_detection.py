import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from skimage.filters import roberts, sobel
import matplotlib.image as mpimg
import cv2
from scipy import ndimage as nd
from skimage import measure
import feature_augment as f_aug

cor = []

def crop_patch(image):
    '''

    :param image: Image class
    :return:
    '''

    for n in range(len(cor)):
        ####crop patch and save##############
        crop_img = image.crop(tuple(cor[n]))
        crop_img.save("./%d.jpg" % (n))
        slide.read_region((xx, yy), extract_level, patch_size)

    draw = ImageDraw.Draw(image)
    for n in range(len(cor)):
        ####plot region box in orig image####
        draw.rectangle(cor[n], fill=None, outline="black")
    image.save("./edge_detectionA/a.jpg")





def edge_det(image):
    '''

    :param image: gray np array
    :return:
    '''
    # edge_roberts = roberts(image_gray)
    edge_sobel = sobel(image_gray)
    retval, edge_sobel_thre = cv2.threshold(edge_sobel, 0.15, 1, cv2.THRESH_BINARY)

    reverse = 1 - edge_sobel_thre
    distance = nd.distance_transform_edt(reverse)
    binary = distance < 20
    filled_image = nd.morphology.binary_fill_holes(binary)

    return filled_image, edge_sobel_thre

def find_cellcor_from_edge(edge_image):
    '''

    :param edge_image: the fina binary image of detect cell
    :return: add cell cor to cor[]
    '''
    ##get central of label#####
    mask_label = measure.label(edge_image)
    properties = measure.regionprops(mask_label)
    max_label = np.amax(mask_label)
    print(max_label)

    for i in range(0, max_label):
        cor_1 = properties[i].centroid[0] - 60
        cor_2 = properties[i].centroid[0] + 60
        cor_3 = properties[i].centroid[1] - 60
        cor_4 = properties[i].centroid[1] + 60
        region = [cor_3, cor_1, cor_4, cor_2]
        if ((cor_1 < 0) | (cor_2 < 0) | (cor_3 < 0) | (cor_4 < 0)
                | (cor_3 > image.size[0]) | (cor_4 > image.size[0]) | (cor_1 > image.size[1]) | (
            cor_2 > image.size[1])):
            continue
        cor.append(region)

if __name__ == "__main__":
    #image path
    image_path = "./a.jpg"

    #open image
    image = Image.open(image_path)

    #feature augment
    #image = f_aug.feature_augment(image)

    #convert to gray image for edge detect
    image_gray = image.convert("L")

    #edge_det
    edge_image, orig_edge_image = edge_det(image_gray)

    find_cellcor_from_edge(edge_image)

    #plot pic relevance
    fig, ax = plt.subplots()
    ax.imshow(image_gray, cmap=plt.cm.gray)
    ax.set_title('image_gray')

    fig, ax = plt.subplots()
    ax.imshow(orig_edge_image, cmap=plt.cm.gray)
    ax.set_title('orig edge image')

    fig, ax = plt.subplots()
    ax.imshow(edge_image, cmap=plt.cm.gray)
    ax.set_title('filled_image')

    crop_patch(image)
    plt.show()
