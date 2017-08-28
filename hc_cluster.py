#!/usr/bin/env python
import os
from PIL import Image, ImageDraw
import cluster
# create a list of images
from matplotlib.pyplot import *
from numpy import *
import time

time1 = time.time()
path = '../test_traindata/test_cluster'
imlist = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]
# extract feature vector (8 bins per color channel)
features = zeros([len(imlist), 512])
for i, f in enumerate(imlist):
    im = array(Image.open(f))
    # multi-dimensional histogram
    h, edges = histogramdd(im.reshape(-1, 3), 8, normed=True, range=[(0, 255), (0, 255), (0, 255)])
    features[i] = h.flatten()
time2 = time.time()
feature_time = time2 - time1
print("feature time:%ss"%feature_time)
tree = cluster.hcluster(features)
time3 = time.time()
tree_time = time3 - time2
print("tree time:%ss"%tree_time)
# visualize clusters with some (arbitrary) threshold
clusters = tree.extract_clusters(tree.distance)
print(len(clusters))
time4 = time.time()
extract_cluster_time = time4 - time3
print("extract cluster time:%ss"%extract_cluster_time)
# plot images for clusters with more than 3 elements
c_id = 0
for c in clusters:
    path_cluster = "../test_traindata/test_cluster/%s/"%c_id
    if(not os.path.exists(path_cluster)):
        os.makedirs(path_cluster)
    c_id = c_id + 1
    elements = c.get_cluster_elements()
    nbr_elements = len(elements)
    if nbr_elements > 0:
        # figure()
        # for p in range(nbr_elements):
        #     subplot(8, (nbr_elements/8)+1, p + 1)
        #     im = array(Image.open(imlist[elements[p]]))
        #     imshow(im)
        #     axis('off')
        #mv image to cluster
        for p in range(nbr_elements):
            # cmd = "mv %s %s"%(imlist[elements[p]], path_cluster)
            # print(cmd)
            # break
            os.system("mv %s %s"%(imlist[elements[p]], path_cluster))
    # break
time5 = time.time()
mv_time = time5 - time4
print("mv time:%ss"%mv_time)