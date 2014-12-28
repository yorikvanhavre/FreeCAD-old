# -*- coding: utf-8 -*-

#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2014 Dan Falck <ddfalck@gmail.com>                      *
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

import FreeCAD
from FreeCAD import Vector
import Part

''' used to split up wires and possibly reverse them to create toolpaths '''

def fmt(val): return format(val, '.4f') #set at 4 decimal places for testing

def filterEdges(wire,revpts=False):
    edgelist = []
    for e in wire.Edges:
        edgelist.append(e)
    if revpts:
        revlist = edgelist
        revlist.reverse()
        edgelist = revlist
    newlist = []
    for s in edgelist:
        if (isinstance(s.Curve,Part.Circle)):
            if revpts:
                newlist.append((("circle"),s.valueAt(s.LastParameter),s.Curve.Center,s.valueAt(s.FirstParameter)))
            else:
                newlist.append((("circle"),s.valueAt(s.FirstParameter),s.Curve.Center,s.valueAt(s.LastParameter)))
        if (isinstance(s.Curve,Part.Line)):
            if revpts:
                newlist.append((("line"), (s.Curve.EndPoint),(s.Curve.StartPoint)))
            else:
                newlist.append((("line"), (s.Curve.StartPoint),(s.Curve.EndPoint)))
    return newlist


def convert(wire,Side,ToolNumber,radius,revpts=False,Z=0.0):
    if Side == 'Left':
    # we use the OCC offset feature
        offset = wire.makeOffset(radius)
    elif Side == 'Right':
        #wire.reverse()
        offset = wire.makeOffset(-radius)
    else:
        offset = wire #tool is on the original profile ie engraving
    # we create the path from the offset shape

    edges = filterEdges(offset,revpts)

    last = None
    output = ""
    #output += "M06 T" + str(ToolNumber) + "\n"
    for edge in edges:
        if not last:
            # we set the base GO to our first point
            last = edge[1]
            output += "G1 X" + str(fmt(last.x)) + " Y" + str(fmt(last.y)) + " Z" + str(fmt(Z)) + "\n"
        if edge[0]=='circle':
            point = edge[-1]
            if point == last: # edges can come flipped
                point = edge[1]
            center = edge[2]
            relcenter = center.sub(last)
            v1 = last.sub(center)
            v2 = point.sub(center)
            if v1.cross(v2).z < 0:
                output += "G2"
            else:
                output += "G3"
            output += " X" + str(fmt(point.x)) + " Y" + str(fmt(point.y)) + " Z" + str(fmt(Z))
            output += " I" + str(fmt(relcenter.x)) + " J" + str(fmt(relcenter.y)) + " K" + str(fmt(relcenter.z))
            output += "\n"
            last = point
        else:
            point = edge[-1]
            if point == last: # edges can come flipped
                point = edge[1]
            output += "G1 X" + str(fmt(point.x)) + " Y" + str(fmt(point.y)) + " Z" + str(fmt(Z)) + "\n"
            last = point
    #print output
    return output






