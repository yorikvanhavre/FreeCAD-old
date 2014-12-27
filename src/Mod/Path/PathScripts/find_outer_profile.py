#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2014                                              *  
#*   Daniel Falck <ddfalck@gmail.com>                                      *  
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************


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
