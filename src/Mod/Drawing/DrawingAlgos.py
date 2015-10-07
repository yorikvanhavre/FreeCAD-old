import FreeCAD, Part, Drawing

startSVG = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
 
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ev="http://www.w3.org/2001/xml-events"
     version="1.1" baseProfile="full"
     width="297mm" height="420mm">
"""


def createSVG(Part):

	# projecting with HLR
	[Visibly,Hidden] = Drawing.project(Part)
	buffer = startSVG

	for i in Hidden.Edges:
		buffer += '<line x1="' +`i.Vertexes[0].X` +'" y1="' +`i.Vertexes[0].Y` +'" x2="'+ `i.Vertexes[1].X`+ '" y2="'+ `i.Vertexes[1].Y`+ '" stroke="#fff000" stroke-width="1px" />\n'
	for i in Visibly.Edges:
		buffer += '<line x1="' +`i.Vertexes[0].X` +'" y1="' +`i.Vertexes[0].Y` +'" x2="'+ `i.Vertexes[1].X`+ '" y2="'+ `i.Vertexes[1].Y`+ '" stroke="#000000" stroke-width="1px" />\n'
		
	buffer += '</svg>'

	return buffer
    
def centerView(view):
    "Centers a View on its page"
    if not view.isDerivedFrom("Drawing::FeatureViewPart"):
        FreeCAD.Console.PrintError("The given object is not a Drawing Part View\n")
        return
    page = None
    for o in view.InList:
        if o.isDerivedFrom("Drawing::FeaturePage"):
            page = o
            break
    if not page:
        FreeCAD.Console.PrintError("The given Drawing View is not inserted in any page\n")
        return
    # find page size
    tf = open(page.Template,"rb")
    temp = tf.read().replace("\n"," ")
    tf.close()
    import re
    width = re.findall("\<svg.*?width=\"(.*?)\"",temp)
    height = re.findall("\<svg.*?height=\"(.*?)\"",temp)
    if (len(height) != 1) or (len(width) != 1):
        FreeCAD.Console.PrintError("Couldn't determine page size\n")
        return
    width = float(width[0].strip("mm").strip("px"))
    height = float(height[0].strip("mm").strip("px"))
    # find center point
    if not view.Source:
        FreeCAD.Console.PrintError("The given Drawing View has no Source\n")
        return
    center = view.Source.Shape.BoundBox.Center
    import WorkingPlane
    p = WorkingPlane.plane()
    p.alignToPointAndAxis(FreeCAD.Vector(0,0,0),view.Direction)
    center = p.getLocalCoords(center)
    center.multiply(view.Scale)
    # calculate delta
    print "center of page: (",width/2,",",height/2,")"
    print "center of view: (",center.x,",",center.y,")"
    view.X = int(width/2 - center.x)
    view.Y = int(height/2 + center.y)
    FreeCAD.ActiveDocument.recompute()
    
