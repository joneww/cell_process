#!/usr/bin/env python
import openslide
import os
import patch_xml
import analy_anno
import numpy as np
import tensorflow as tf
import threading
import sys
my_lib_path ="/home1/zengwx/git_code/my_lib/"
sys.path.append(my_lib_path)
import log
import logging
import multiprocessing as mp

logger = logging.getLogger("lib_logger")
max_group_num = 6
group_name = ["asc-us", "lsil", "hsil", "scc", "ec", "mc"]

class train_cut_anno_conf():
    def __init__(self):
        self.centre_size = (128,128)
        self.patch_size = (299,299)
        self.step = 128
        self.tiff_start = 1
        self.tiff_num = 1
        self.patch_cut_flag = 1
        self.patch_stat_flag = 1
        self.json_flag = 0
        self.level0 = 40
        self.mask_level = 3 # should less than 7
        self.patch_extract_level = 0
        self.base = "/home1/zengwx/work_code/tct"
        self.file_base = 'test_traindata/kfb'
        self.xml_base = 'test_traindata/out_xml'
        self.out_patch_base = "/home1/zengwx/work_code/tct/test_traindata/out_patch/"
        self.cut_class_num = 7#asc-us/asc-h/lsil/hsil/scc/ncc(neck canal cells)/mc(metaplastic cells)



def dir_check():
    config = train_cut_anno_conf()

    #input train file path check
    # xml input path check
    file_input_dir = os.path.join(config.base, config.file_base)
    if(os.path.exists(file_input_dir)):
        print("file input dir check ok")
    else:
        print("file input dir not exists")
        return 1

    #patch output path check
    patch_out_dir = os.path.join(config.base, config.out_patch_base)
    if(os.path.exists(patch_out_dir)):
        print("patch output dir check ok")
    else:
        os.makedirs(patch_out_dir)
        print("patch output dir not exists, and create OK")
        return 1



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

def file_loop(thread_id, files):
    '''
    :file loop
    :return:
    '''
    logger.debug("thread:%d"%thread_id)
    config = train_cut_anno_conf()
    extract_level = config.patch_extract_level
    patch_size = config.patch_size
    centre_size = config.centre_size
    out_patch_base = config.out_patch_base
    out_xml_base = os.path.join(config.base, config.xml_base)

    file_path = os.path.join(config.base, config.file_base)

    pixel_top_off_max = (patch_size[0] - centre_size[0]) / 2
    pixel_bot_off_max = (patch_size[0] + centre_size[0]) / 2
    pixel_solid_off = (patch_size[0] - centre_size[0]) / 2
    pixel_center_off = centre_size[0] / 2

    all_patch_number = 0
    all_patch_omitted_number = 0
    slide_stat_number = 0

    for file in files:
        if(file.endswith(".kfb")):
            name = file
            out_xml = os.path.join(out_xml_base, "%s.xml" % name)
            # open slide
            logger.debug("thread:%d, slide %s" %(thread_id, os.path.join(file_path, file)))
            slide = slide_open(os.path.join(file_path, file))

            # analy annotation
            if(0 == config.json_flag):
                anno_xml = os.path.join(file_path, "%s.Ano"%name)
                annos_of_groups = analy_anno.analy_kfb_xml(anno_xml)
            else:
                json_file = os.path.join(file_path, "json_anno/%s/1.json"%name)
                annos_of_groups = analy_anno.analy_kfb_json(json_file)

            #cut patch with annos_of_groups
            print("\n===== Cutting all patches =====")
            dims_file = slide.level_dimensions[extract_level]
            ww = int(dims_file[0] / centre_size[0])
            hh = int(dims_file[1] / centre_size[1])
            print(dims_file)
            patch_coords = []

            for group_id in range(0, max_group_num):
                g_name = group_name[group_id]
                print("cut %s group:patch num:%s"%(g_name, len(annos_of_groups[group_id])))
                for cor_region in annos_of_groups[group_id]:
                    cor_left = cor_region[0]
                    cor_right = cor_region[1]
                    if config.patch_stat_flag:
                        x = int((cor_left[0] + cor_right[0])/2.0) - pixel_center_off
                        y = int((cor_left[1] + cor_right[1])/2.0) - pixel_center_off
                        if (x - pixel_top_off_max) < 0 or (x + pixel_bot_off_max) > dims_file[0]:
                            #print("[WARN1] patch with centre(%d,%d) cannot be cut by 299*299!" % (x, y))
                            all_patch_omitted_number += 1
                            continue
                        if (y - pixel_top_off_max) < 0 or (y + pixel_bot_off_max) > dims_file[1]:
                            #print("[WARN2] patch with centre(%d,%d) cannot be cut by 299*299!" % (x, y))
                            all_patch_omitted_number += 1
                            continue
                        slide_stat_number += 1
                        patch_coords.append((y, x))
                        if config.patch_cut_flag:
                            xx = x - pixel_solid_off
                            yy = y - pixel_solid_off
                            im_patch = slide.read_region((xx, yy), extract_level, patch_size)

                            out_name = out_patch_base + '%s/'%(g_name) + '%s_L00_X%06d_Y%06d_W%04d_H%04d.jpg' % (
                                name, x, y, ww, hh)
                            print(out_name)
                            im_patch = im_patch.convert('RGB')
                            im_patch.save(out_name)
                    else:
                        slide_stat_number += 1

            if config.patch_stat_flag:
                patch_xml.generate_xml_from_coords(patch_coords, out_xml, config.centre_size[0])
            all_patch_number += slide_stat_number

            print("===== all_patch_number: %d , ommited: %d=====" % (all_patch_number, all_patch_omitted_number))

def thread_test():#kfb read image .so not support
    config = train_cut_anno_conf()
    file_path = os.path.join(config.base, config.file_base)
    files = os.listdir(file_path)

    #create group for all slide patch
    for i in range(0, max_group_num):
        group_out_path = os.path.join(config.base, config.out_patch_base, group_name[i])
        if(os.path.exists(group_out_path)):
            print("group %s is exist"%group_name[i])
        else:
            os.makedirs(group_out_path)
            print("group %s is not exist,and creat ok"%group_name[i])

    files = [file for file in files if file.endswith(".kfb")]
    thread_num = 1
    space = np.linspace(0, len(files), thread_num + 1).astype(np.int)

    threads = []
    coord = tf.train.Coordinator()
    for thread_id in range(thread_num):
        f = files[space[thread_id]:space[thread_id + 1]]
        args = (thread_id, f)
        t = threading.Thread(target=file_loop, args=args)
        t.start()
        threads.append(t)

    # Wait for all the threads to terminate.
    coord.join(threads)

def process_test():
    config = train_cut_anno_conf()
    file_path = os.path.join(config.base, config.file_base)
    files = os.listdir(file_path)

    #create group for all slide patch
    for i in range(0, max_group_num):
        group_out_path = os.path.join(config.base, config.out_patch_base, group_name[i])
        if(os.path.exists(group_out_path)):
            print("group %s is exist"%group_name[i])
        else:
            os.makedirs(group_out_path)
            print("group %s is not exist,and creat ok"%group_name[i])

    files = [file for file in files if file.endswith(".kfb")]
    proc_num = 2
    space = np.linspace(0, len(files), proc_num + 1).astype(np.int)

    process = []
    coord = tf.train.Coordinator()
    for thread_id in range(proc_num):
        f = files[space[thread_id]:space[thread_id + 1]]
        args = (thread_id, f)
        t = mp.Process(target=file_loop, args=args)
        t.start()
        process.append(t)

    # Wait for all the threads to terminate.
    coord.join(process)

if __name__ == "__main__":
    dir_check()
    process_test()