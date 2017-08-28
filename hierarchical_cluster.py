#!/usr/bin/env python
#
# -*- coding: utf-8 -*- 


from numpy import *

# 读取文件
def readfile(fileName):
    lines = [line for line in open(fileName)]
    
    colNames = lines[0].strip().split('\t')[1:]
    rowNames = []
    
    for line in lines[1:]:
        p = line.strip().split('\t')
        
        rowNames.append(p[0])
        data.append([float(x) for x in p[1:]])
        
    return rowNames, colNames, data


# 紧密度——皮尔逊相关系数
from math import sqrt
def pearson(v1, v2):
    sum1 = sum(v1)
    sum2 = sum(v2)

    sum1Sq = sum([pow(v, 2) for v in v1])
    sum2Sq = sum([pow(v, 2) for v in v2])

    pSum = sum([v1[i] * v2[i] for i in range(len(v1))])

    num = pSum - ((sum1 * sum2) / len(v1))
    den = sqrt((sum1Sq - pow(sum1, 2) / len(v1)) * (sum2Sq - pow(sum2, 2) / len(v1)))

    if den == 0:
        return 0.0
    return 1.0 - num / den


# 新建一个类，代表聚类这一类型
class bicluster:
    u'''
        vec           代表建立新聚类的集合
        left,right    是建立新聚类的左右两个旧聚类
        distance      是这个聚类的距离，也即是两个旧聚类的皮尔逊相关系数
        id            用以代表这是一个分支还是叶节点
    '''
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.vec = vec
        self.right = right
        self.distance = distance
        self.id = id


# 聚类
def hcluster(rows, distance=pearson):
    distances = {}
    currentclustid = -1
    lowestpair = None

    # 最开始的聚类就是数据集中的行
    clusts = [bicluster(rows[i], id = i) for i in range(len(rows))]

    while len(clusts) > 1:
        closest = distance(clusts[0].vec, clusts[1].vec)
        # 遍历每一个配对，寻找最小距离
        for i in range(len(clusts) - 1):
            for j in range(i+1, len(clusts)):
                # 用distances来缓存距离的计算值
                if distances.get((clusts[i].id, clusts[j].id)) is None:
                    distances[(clusts[i].id, clusts[j].id)] = distance(clusts[i].vec, clusts[j].vec)
                d = distances[(clusts[i].id, clusts[j].id)]
                # 寻找最相似的两个群组
                if d < closest:
                    closest = d
                    lowestpair = (i, j)
        bic1, bic2 = lowestpair
        # 计算两个聚类的平均值
        mergevec = [((clusts[bic1].vec[i] + clusts[bic2].vec[i]) / 2.0) for i
                    in range(len(clusts[bic1].vec))]
        # 建立新的聚类
        newcluster = bicluster(mergevec, left=clusts[bic1], right=clusts[bic2], distance=closest,
                               id=currentclustid)
        # 不在原始集合中的聚类，其id为负数
        currentclustid -= 1
        del clusts[bic2]
        del clusts[bic1]
        clusts.append(newcluster)
    return clusts[0]

# 返回给定聚类的总体高度    
def getheight(clust):
    # 这是一个叶节点吗？若是，则高度为1
    if clust.left is None and clust.right is None:
        return 1
    # 否则，高度为每个分支的高度之和
    return getheight(clust.left)+getheight(clust.right)

# 根节点的总体误差
def getdepth(clust):
    # 一个叶节点的距离是0.0
    if clust.left is None and clust.right is None:
        return 0
    # 一个枝节点的距离等于左右两侧分支中距离较大者，加上该枝节点自身的距离
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance


# 绘制树状图, 根据聚类的大小创建一个高度为20像素、宽度固定的图片，其中缩放因子是由固定宽度除以总的深度值得到的
def drawdendprogram(clust, labels, jpeg='cluster.jpg'):
    # 高度和宽度
    h = getheight(clust) * 20
    w = 1200
    depth = getdepth(clust)

    # 由于宽度是固定的，因此我们需要对距离值做相应的调整
    scaling = float(w - 150) / depth

    # 新建一个白色背景的图片
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, h/2, 10, h/2), fill=(255, 0, 0))

    # 画第一个节点
    drawnode(draw, clust, 10, (h/2), scaling, labels)
    img.save(jpeg, 'JPEG')


# 开始绘制节点了，水平线的长度是有聚类中的误差情况觉决定的。线条越长代表合并在一起的两个聚类差别很大，线条越短则表明两个聚类相似度很高。
def drawnode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        # 线的长度
        l1 = clust.distance * scaling
        # 聚类到其子节点的垂直线
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))

        # 连接左侧节点的水平线
        draw.line((x, top + h1 / 2, x + l1, top + h1 / 2), fill=(255, 0, 0))

        # 连接右侧节点的水平线
        draw.line((x, bottom - h2 / 2, x + l1, bottom - h2 / 2), fill=(255, 0, 0))

        # 调用函数绘制左右节点
        drawnode(draw, clust.left, x + l1, top + h1 / 2, scaling, labels)
        drawnode(draw, clust.right, x + l1, bottom - h2 / 2, scaling, labels)
    else:
        # 如果这是一个叶节点，则绘制节点的标签
        draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))

 