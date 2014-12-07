import DraftGeomUtils 
import Draft
from FreeCAD import Vector,Base

def findOutsideWire(wires):
    samediagonal = []
    if len(wires)>1:
        outside = wires[0]
        biggest = wires[0].BoundBox.DiagonalLength
        #wires.remove(outside)
        for w in wires:

            if (w.BoundBox.DiagonalLength >= biggest) and (w.Length < outside.Length) :

#                if (w.BoundBox.DiagonalLength == biggest):
#                    samediagonal.append(outside)
#                    samediagonal.append(w)

                biggest = w.BoundBox.DiagonalLength
                outside = w
        wires.remove(outside)
        return outside, wires, samediagonal
    else:
        return wires

def openFilter(wires):
    #filter out open wires
    wirelist = []
    for w in wires:
        if w.isClosed():
            wirelist.append(w)
    return wirelist

def edgelist(obj):
    #make a list of all edges in an object
    edges = []
    for e in obj.Shape.Edges:
        edges.append(e)
    return edges

def horizontal(edges):
    #find all horizontal edges and discard the rest
    edgelist = []
    for e in edges:
        if e.BoundBox.ZMin == e.BoundBox.ZMax:
            edgelist.append(e)
    return edgelist

def sameDiagonals(wir):
    wlist = []
    first = wir[0]
    for w in wir:
        if (w.BoundBox.DiagonalLength == first.BoundBox.DiagonalLength):
            print 'pair'
            wlist.append(w)
        wir.remove(first)
        first = wir[0]
    return wlist


testing = '''

sel = FreeCADGui.Selection.getSelection()[0]
obj = sel
el = edgelist(obj)
hl = horizontal(el)
connected = DraftGeomUtils.findWires(hl)
goodwires = openFilter(connected)

outerwires ,innerwires, same = findOutsideWire(goodwires)
#get distance from outerwires Z to bottom of part
zdiff = obj.Shape.BoundBox.ZMin- outerwires.BoundBox.ZMax
outerwires.Placement.move(Vector(0,0,zdiff))
Part.show(outerwires)

zupperouter = outerwires
zupperouter.Placement.move(Vector(0,0,obj.Shape.BoundBox.ZMax))
Part.show(zupperouter)

'''
