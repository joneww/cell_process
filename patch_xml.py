import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def write_one_group_xml(Annotations, patches, name_head, color, tile_size):
    end = tile_size-1
    for i in range(len(patches)):
        x0,y0 = patches[i]
        x1,y1 = x0+end,y0+end
        anno = ET.SubElement(Annotations, "Annotation",Name=name_head+str(i),\
                        Type="Polygon",PartOfGroup=name_head, Color=color)
        coors = ET.SubElement(anno, "Coordinates")
        ET.SubElement(coors, "Coordinate",Order="0", X=str(x0), Y=str(y0))
        ET.SubElement(coors, "Coordinate",Order="1", X=str(x1), Y=str(y0))
        ET.SubElement(coors, "Coordinate",Order="2", X=str(x1), Y=str(y1))
        ET.SubElement(coors, "Coordinate",Order="3", X=str(x0), Y=str(y1))


def generate_xml_from_coords(coords, out_xml, tile_size, group_id=None):
    root = ET.Element("ASAP_Annotations")
    annos = ET.SubElement(root, "Annotations")
    annogrps = ET.SubElement(root, "AnnotationGroups")

    color = "#00aa00"
    if group_id == None:
        grp_name = 'patches'
    else:
        grp_name = 'Group %d' % group_id
    prob_grp = ET.SubElement(annogrps, "Group", Name=grp_name, PartOfGroup="None", Color=color)
    write_one_group_xml(annos, coords, prob_grp.get("Name"), prob_grp.get("Color"), tile_size)

    f = open(out_xml, "w")
    f.write(prettify(root))
    f.close()