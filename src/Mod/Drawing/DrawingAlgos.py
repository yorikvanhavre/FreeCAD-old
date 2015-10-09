import FreeCAD, Part, Drawing, math

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
        FreeCAD.Console.PrintError("The given object is not a Drawing View\n")
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
    fragment = view.ViewResult
    if not fragment:
        FreeCAD.Console.PrintError("The given Drawing View doesn't have any content\n")
        return
    import importSVG # this uses the Draft SVG parser
    points = importSVG.getpointslist(fragment)
    if not points:
        FreeCAD.Console.PrintError("Failed to parse the contents of this view\n")
        return
    center = Part.Compound([Part.Vertex(p) for p in points]).BoundBox.Center
    # calculate delta
    print "center of page: (",width/2,",",height/2,")"
    print "center of view: (",center.x,",",center.y,")"
    delta = FreeCAD.Vector(center.x,center.y,0).sub(FreeCAD.Vector(width/2,height/2,0))
    delta.multiply(view.Scale)
    rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,1),math.radians(view.Rotation))
    delta = rot.multVec(delta)
    print "delta:",delta
    view.X = view.X - delta.x
    view.Y = view.Y - delta.y
    FreeCAD.ActiveDocument.recompute()
    
