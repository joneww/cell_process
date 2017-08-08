import xml.etree.ElementTree as ET
import numpy as np
import json
import string


multiple_size = 40

def get_groups_from_xml(xml_name):
    """
    :param xml_name:
    :return: poly_groups with format [[group_id0, [polygons]], ...]
    """
    ### parameter initialization
    max_group_num = 6
    polygons_of_groups = [ [] for i in range(max_group_num) ]
    poly_groups = []

    ### main work area
    tree = ET.parse(xml_name)
    top = tree.getroot()
    for child in top:
        if child.tag == 'Annotations':
            for Annotation in child:
                if Annotation.get("Type").lower() == 'polygon' and \
                Annotation.get("PartOfGroup").find("Annotation Group") >= 0:
                    #print "[] Annotation.attrib=", Annotation.attrib
                    for Coordinates in Annotation: # a "Coordinates" is a polygon
                        polygon = []
                        for coord in Coordinates:
                            x = coord.get("X")
                            y = coord.get("Y")
                            polygon.append(np.array([round(float(x)), round(float(y))], dtype=np.int))
                        # print ptlist
                        group_name = Annotation.get("PartOfGroup")
                        group_id = int(group_name[-1])
                        #print "[] group_id=", group_id
                        if group_id >= max_group_num:
                            raise ValueError("[ERR] Invalid group number: %d" % group_id)
                        polygons_of_groups[group_id].append(polygon)

    for groud_id in range(max_group_num):
        if len(polygons_of_groups[groud_id]) != 0:
            poly_groups.append([groud_id, polygons_of_groups[groud_id]])
        else:
            poly_groups.append([groud_id, []])

    return poly_groups


def analy_kfb_xml(xml_name):
    '''

    :param xml_name:
    :return:group and group cors
    '''
    max_group_num = 6
    group_name = ["asc-us", "lsil", "hsil", "scc", "ec", "mc"]
    annos_of_groups = [[] for i in range(max_group_num)]

    #modify string
    file_xml = open(xml_name,"r")
    xml_str = file_xml.read()
    xml_str = unicode(xml_str, encoding='gb2312').encode('utf - 8')
    xml_str = xml_str.replace('<?xml version="1.0" encoding="gb2312"?>', '<?xml version="1.0" encoding="utf-8"?>')
    file_xml.close()

    #modify xml file
    file_xml = open(xml_name, "w")
    file_xml.write(xml_str)
    file_xml.close()

    #xml tree
    tree = ET.parse(xml_name)
    top = tree.getroot()

    for slide in top:
        if(slide.tag == "Annotations"):
            for annotations in slide:
                if(annotations.tag == "Regions"):
                    for regions in annotations:
                        g_name = regions.get("Detail")
                        g_name_num = group_name.index(g_name.lower())
                        for vertices in regions: #region<<r>v<>>
                            cor_region = []
                            if(vertices.tag == "Vertices"):
                                for vertice in vertices:
                                    x = string.atof(vertice.get("X"))*multiple_size
                                    y = string.atof(vertice.get("Y"))*multiple_size
                                    cor = (x, y)
                                    cor_region.append(cor)
                            annos_of_groups[g_name_num].append(cor_region)
    print(annos_of_groups)
    return annos_of_groups

def analy_kfb_json(json_name):
    '''
    :analy json file of kfb annotation
    :param json_name:
    :return:
    '''
    max_group_num = 6
    group_name = ["asc-us", "lsil", "hsil", "scc", "ec", "mc"]
    annos_of_groups = [[] for i in range(max_group_num)]


    json_str = open(json_name,"r").read()
    parsed_json = json.loads(json_str)
    anno_num = len(parsed_json)
    for i in range(0,anno_num):
        anno = parsed_json[i]
        g_name = anno["description"]
        g_name_num = group_name.index(g_name.lower())
        x1 = anno["region"]['x']
        y1 = anno["region"]['y']
        h = anno["region"]['height']
        w = anno["region"]['width']
        x2 = x1 + w
        y2 = y1 + h
        cor_region = [(x1,y1),(x2,y2)]
        annos_of_groups[g_name_num].append(cor_region)
    return annos_of_groups



if __name__ == "__main__":
    # xml_name = "../test_traindata/kfb/2017-07-24 16_45_46.kfb.Ano"
    #
    # #modify string
    # file_xml = open(xml_name,"r")
    # xml_str = file_xml.read()
    # xml_str = unicode(xml_str, encoding='gb2312').encode('utf - 8')
    # xml_str = xml_str.replace('<?xml version="1.0" encoding="gb2312"?>', '<?xml version="1.0" encoding="utf-8"?>')
    # file_xml.close()
    #
    # #modify xml file
    # file_xml = open(xml_name, "w")
    # file_xml.write(xml_str)
    # file_xml.close()
    # analy_kfb_xml(xml_name)

    json_name = "../test_traindata/kfb/1.json"
    analy_kfb_json(json_name)

