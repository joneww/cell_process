import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)

    return rough_string


def generate_xml_from_coords(coords, out_xml, tile_size):
    root = ET.Element("Slide")
    Annotations = ET.SubElement(root, "Annotations")
    Regions = ET.SubElement(Annotations, "Regions")

    end = tile_size-1
    for i in range(len(coords)):
        region = ET.SubElement(Regions,
                                 "Region",
                                 Guid="Ellipse20170728150121",
                                 Name="ASC-US",
                                 Detail="ASC-US",
                                 FontSize="12",
                                 FontItalic="False",
                                 FontBold="False",
                                 Size="2",
                                 FigureType="Ellipse",
                                 Hidden="Visible",
                                 Zoom="20.0",
                                 Visible="Collapsed",
                                 MsVisble="False",
                                 Color="4278190335",
                                 PinType="images/pin_1.png")
        x0,y0 = coords[i]
        x1,y1 = x0+end,y0+end
        Vertices = ET.SubElement(region, "Vertices")
        ET.SubElement(Vertices, "Vertice", X=str(x0/20), Y=str(y0/20))
        ET.SubElement(Vertices, "Vertice", X=str(x1/20), Y=str(y1/20))

    f = open(out_xml, "w")
    f.write(prettify(root))
    f.close()