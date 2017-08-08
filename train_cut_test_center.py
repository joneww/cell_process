#!/usr/bin/env python
import pre_ext
import openslide
import os
import numpy as np
import math
import patch_xml
import patch_xml_kfb
from skimage import color, measure,io
from scipy.misc import imsave,imread
from scipy import ndimage as nd

class train_cut_test_conf():
    def __init__(self):
        self.centre_size = (128, 128)
        self.patch_size = (299, 299)
        self.step = 128
        self.tiff_start = 1
        self.tiff_num = 1
        self.patch_cut_flag = 1
        self.patch_stat_flag = 1
        self.mask_level = 3  # should less than 7,NOT USE
        self.patch_extract_level = 0
        self.base = "/home1/zengwx/work_code/tct"
        self.file_base = 'test_traindata/kfb'
        self.xml_base = 'test_traindata/out_xml'
        self.out_patch_base = "/home1/zengwx/work_code/tct/test_traindata/out_patch/"
        self.cut_class_num = 7  # asc-us/asc-h/lsil/hsil/scc/ncc(neck canal cells)/mc(metaplastic cells)


def slide_open(filename):
    '''
    :open slide file use file name
    :param filename:
    :return:slide class
    '''
    slide = openslide.open_slide(filename)
    print("filename is %s" % str(filename))
    print("shape of dimensions is %s" % str(slide.level_dimensions))
    print("level count is %s" % slide.level_count)
    print("spacingx = %s" % slide.properties[openslide.PROPERTY_NAME_MPP_X])
    print("spacingy = %s" % slide.properties[openslide.PROPERTY_NAME_MPP_Y])
    print("PROPERTY_NAME_VENDOR is %s" % slide.properties[openslide.PROPERTY_NAME_VENDOR])

    return slide


def file_loop():
    '''
    :file loop
    :return:
    '''
    config = train_cut_test_conf()
    mask_level = config.mask_level
    extract_level = config.patch_extract_level
    step = config.step
    patch_size = config.patch_size
    centre_size = config.centre_size
    out_patch_base = config.out_patch_base
    out_xml_base = os.path.join(config.base, config.xml_base)

    print("config:%s" % config.base)
    file_path = os.path.join(config.base, config.file_base)
    files = os.listdir(file_path)

    pixel_top_off_max = (patch_size[0] - centre_size[0]) / 2
    pixel_bot_off_max = (patch_size[0] + centre_size[0]) / 2
    pixel_solid_off = (patch_size[0] - centre_size[0]) / 2

    all_patch_number = 0
    all_patch_omitted_number = 0
    slide_stat_number = 0

    for file in files:
        if (file == "2017-07-26 10_19_08.kfb"):
            name = file
            # out_xml = os.path.join(out_xml_base, "%s.xml" % name)
            out_xml = os.path.join(out_xml_base, "%s.Ano" % name)
            # open slide
            slide = slide_open(os.path.join(file_path, file))
            mask_level = slide.level_count - 1 ###########mask_level
            print("mask_level:%d"%mask_level)
            multiple_size = math.pow(2, mask_level)
            mask_tile_level_size = int(step / multiple_size)

            # pre ground extract
            # slide_dat = slide.read_region((0, 0), mask_level, slide.level_dimensions[mask_level])
            slide_dat = slide.read_region((8000, 8000), mask_level, (500, 500))
            slide_dat = np.array(slide_dat)
            slide_dat = slide_dat[:, :, :3]
            imsave("region.bmp", slide_dat)
            slide_mask = pre_ext.gen_crop_mask(slide_dat)

            #label mask
            mask_label = measure.label(slide_mask)
            imsave("mask_label.bmp", mask_label)
            label_num = np.amax(mask_label)
            print("label_mun : %d"%(label_num))
            properties = measure.regionprops(mask_label)
            print("len:%d"%(len(properties)))

            print("\n===== Cutting all patches =====")

            dims_mask = slide.level_dimensions[mask_level]
            dims_file = slide.level_dimensions[extract_level]
            ww = int(dims_file[0] / centre_size[0])
            hh = int(dims_file[1] / centre_size[1])
            tissue_threshold = int(mask_tile_level_size * mask_tile_level_size)  # 255 or 1 #100% sum_t>=threshold
            patch_coords = []

            test_center = []

            for label in range(1,label_num):
                center = properties[label].centroid#local centroid is relevante to region
                center = [center[1],center[0]]
                test_center.append(center)
                area = properties[label].area
                print("area:%f" % area)

                xx_c = center[1] - 64 / multiple_size
                yy_c = center[0] - 64 / multiple_size
                print("center")
                print(xx_c, yy_c)

                if(area < 256):
                    xx_min = int(xx_c)
                    xx_max = int(xx_c)
                    yy_min = int(yy_c)
                    yy_max = int(yy_c)
                else:
                    box = properties[label].bbox
                    yy_min = box[0]
                    xx_min = box[1]
                    yy_max = box[2]
                    xx_max = box[3]
                    print("bbox")
                    print(xx_min, yy_min, xx_max, yy_max)

                for xx_t in range(xx_min, xx_max+1, mask_tile_level_size):
                    for yy_t in range(yy_min, yy_max+1, mask_tile_level_size):
                        temp = mask_label == (label+1)
                        # imsave("temp%s.bmp" % label, temp)
                        slide_mask_label = np.multiply(slide_mask, temp)
                        # imsave("slide_mask_label_%s.bmp"%label, slide_mask_label)
                        sum_t = slide_mask_label[yy_t:yy_t + mask_tile_level_size, xx_t:xx_t + mask_tile_level_size].sum()
                        print("sum_t:%d" % sum_t)
                        print("yy_t:%d"%yy_t)
                        if sum_t > 256:  # patch valid in tissue mask
                            if config.patch_stat_flag:
                                x = int(xx_t * multiple_size + 8000)
                                y = int(yy_t * multiple_size + 8000)
                                # print(x,y)
                                # if (x - pixel_top_off_max) < 0 or (x + pixel_bot_off_max) > dims_file[0]:
                                #     # print("[WARN1] patch with centre(%d,%d) cannot be cut by 299*299!" % (x, y))
                                #     all_patch_omitted_number += 1
                                #     continue
                                # if (y - pixel_top_off_max) < 0 or (y + pixel_bot_off_max) > dims_file[1]:
                                #     # print("[WARN2] patch with centre(%d,%d) cannot be cut by 299*299!" % (x, y))
                                #     all_patch_omitted_number += 1
                                #     continue
                                slide_stat_number += 1
                                patch_coords.append((x, y))
                                # if config.patch_cut_flag:
                                #     xx = x - pixel_solid_off
                                #     yy = y - pixel_solid_off
                                #     im_patch = slide.read_region((xx, yy), extract_level, patch_size)
                                #
                                #     out_name = out_patch_base + '%s_L00_X%06d_Y%06d_W%04d_H%04d.jpg' % (
                                #         name, x, y, ww, hh)
                                #     im_patch = im_patch.convert('RGB')
                                #     im_patch.save(out_name)
                            else:
                                slide_stat_number += 1

            pre_ext.draw_point_in_image("./mask_fill_re.bmp", test_center,"center_point.bmp")

            if config.patch_stat_flag:
                patch_xml_kfb.generate_xml_from_coords(patch_coords, out_xml, config.centre_size[0])
            all_patch_number += slide_stat_number

            print("===== all_patch_number: %d , ommited: %d=====" % (all_patch_number, all_patch_omitted_number))

if __name__ == "__main__":
    file_loop()