import numpy as np
from skimage import color, measure,io
from scipy import ndimage as nd
from scipy.misc import imsave,imread
from skimage import morphology
from PIL import Image, ImageDraw


def draw_point_in_image(image_name, points,new_image_name):
    image = Image.open(image_name)
    draw = ImageDraw.Draw(image)
    for n in range(len(points)):
        ####plot region box in orig image####
        draw.point(points[n], fill=0)
    image.save(new_image_name)


def gen_crop_mask(image):
    '''

    :param image:image dat in hsv space
    :return: mask dat for crop
    '''
    # #change color space
    # hsv_img_dat = color.rgb2hsv(image)
    # #plot pic relevance
    # imsave("h_space.bmp",hsv_img_dat[:,:,0])
    # imsave("s_space.bmp",hsv_img_dat[:,:,1])
    # imsave("v_space.bmp",hsv_img_dat[:,:,2])

    # #change color space
    # hsv_img_dat = color.rgb2hed(image)
    # #plot pic relevance
    # imsave("h_space.bmp",hsv_img_dat[:,:,0])
    # imsave("e_space.bmp",hsv_img_dat[:,:,1])
    # imsave("d_space.bmp",hsv_img_dat[:,:,2])

    #change color space
    xyz_img_dat = color.rgb2xyz(image)
    #plot pic relevance
    imsave("x_space.bmp",xyz_img_dat[:,:,0])
    imsave("y_space.bmp",xyz_img_dat[:,:,1])
    imsave("z_space.bmp",xyz_img_dat[:,:,2])

    np.save("xyz.npy", xyz_img_dat[:,:,2])

    mask = (xyz_img_dat[:,:,2] < 0.9)
    # mask = (hsv_img_dat[:, :, 1] > 0.2)

    mask = mask.astype(np.int32)

    ##get central of label#####
    imsave("mask1.bmp",mask)
    print(np.shape(mask))

    filled_image = nd.morphology.binary_fill_holes(mask)
    imsave("mask_fill.bmp", filled_image)

    filled_image_re = morphology.remove_small_objects(filled_image, min_size=50,connectivity=1)
    imsave("mask_fill_re.bmp", filled_image_re)

    # mask_label = measure.label(filled_image)
    # max_label = np.amax(mask_label)
    # print(max_label)
    #
    # mask_label = measure.label(filled_image_re)
    # max_label = np.amax(mask_label)
    #
    # print(max_label)

    #repet error
    # for i in range(0, max_label):
    #     region = (properties[i].centroid[0]*math.pow(2,3), properties[i].centroid[1]*math.pow(2,3))
    #     cor.append(region)
    #
    # patch_xml.generate_xml_from_coords(cor, "./a.xml", 128)

    return filled_image_re










