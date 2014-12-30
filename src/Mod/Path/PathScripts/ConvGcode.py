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
import DraftGeomUtils
import Part
import math
from PathSelection import check_clockwise

''' used to split up wires and possibly reverse them to create toolpaths '''

def fmt(val): return format(val, '.4f') #set at 4 decimal places for testing

def convert(wire,Side,radius,clockwise=False,Z=0.0):
    if Side == 'Left':
    # we use the OCC offset feature
        offset = wire.makeOffset(radius)
    elif Side == 'Right':
        #wire.reverse()
        offset = wire.makeOffset(-radius)
    else:
#        offset = wire.makeOffset(0.0) #tool is on the original profile ie engraving
        offset = wire

    if clockwise:
        revlist = []
        for edge in offset.Edges:
            revlist.append(edge)
        revlist.reverse()
        
        edgelist = []
        #newlist = []
        plast = offset.Edges[0].Vertexes[0].Point
        for edge in revlist:
            if isinstance(edge.Curve,Part.Circle):
                start = edge.valueAt(edge.FirstParameter)
                middle = edge.valueAt((edge.FirstParameter+edge.LastParameter)*0.5)
                end = edge.valueAt(edge.LastParameter)
                if start == plast:
                    arc = Part.ArcOfCircle(start,middle,end)
                else:
                    arc = Part.ArcOfCircle(end,middle,start)
                revedge=arc.toShape()
                edgelist.append(revedge)
                plast = end
            elif isinstance(edge.Curve,Part.Line):
                start = edge.Vertexes[0].Point
                print start
                end = edge.Vertexes[1].Point
                if start == plast:
                    revedge = Part.makeLine(start, end)
                else:
                    revedge = Part.makeLine(end, start)
                edgelist.append(revedge)
                plast = end

        toolpath = Part.Wire(edgelist)

    else:
        FreeCAD.Console.PrintMessage('counter clockwise toolpath\n')
        toolpath = offset.copy()
    last = None
    output = ""
    # we create the path from the offset shape
    for edge in toolpath.Edges:
        if not last:
            # we set the base GO to our first point
            last = edge.Vertexes[0].Point
            output += "G1 X" + str(fmt(last.x)) + " Y" + str(fmt(last.y)) + " Z" + str(fmt(Z)) + "\n"
        if isinstance(edge.Curve,Part.Circle):

            point = edge.Vertexes[-1].Point
            if point == last: # edges can come flipped
                point = edge.Vertexes[0].Point
            center = edge.Curve.Center
            relcenter = center.sub(last)
            # get the start,mid, and end pts
            startpt = edge.valueAt(edge.FirstParameter)
            midpt = edge.valueAt((edge.FirstParameter+edge.LastParameter)*0.5)
            endpt = edge.valueAt(edge.LastParameter)

#            v1 = last.sub(center)
#            v2 = point.sub(center)
#            if v1.cross(v2).z < 0:
#                output += "G2"
#            else:
#                output += "G3"

            arc_cw = check_clockwise([(startpt.x,startpt.y),(midpt.x,midpt.y),(endpt.x,endpt.y)])

            if arc_cw:
                output += "G2"
            else:
                output += "G3"

#            path_cw = clockwise
#            if (path_cw):
#                if arc_cw:
#                    output += "G2"
#                else:
#                    output += "G3"
#            else:
#                if arc_cw:
#                    output += "G3"
#                else:
#                    output += "G2"

            output += " X" + str(fmt(point.x)) + " Y" + str(fmt(point.y)) + " Z" + str(fmt(Z))
            output += " I" + str(fmt(relcenter.x)) + " J" + str(fmt(relcenter.y)) + " K" + str(fmt(relcenter.z))
            output += "\n"
            last = point
        else:
            point = edge.Vertexes[-1].Point
            if point == last: # edges can come flipped
                point = edge.Vertexes[0].Point
            output += "G1 X" + str(fmt(point.x)) + " Y" + str(fmt(point.y)) + " Z" + str(fmt(Z)) + "\n"
            last = point

    return output


def approach(wire,Side,radius,clockwise,ZClearance,StepDown,ZStart, ZFinalDepth):
    if Side == 'Left':
    # we use the OCC offset feature
        offset = wire.makeOffset(radius)
    elif Side == 'Right':
        #wire.reverse()
        offset = wire.makeOffset(-radius)
    else:
#        offset = wire.makeOffset(0.0) #tool is on the original profile ie engraving
        offset = wire

    paths =""
    first = offset.Edges[0].Vertexes[0].Point
    paths += "G0 X"+str(fmt(first.x))+"Y"+str(fmt(first.y))+"\n"
    ZCurrent = ZStart- StepDown
    while ZCurrent >= ZFinalDepth:
        paths += convert(wire,Side,radius,clockwise,ZCurrent)
        ZCurrent = ZCurrent-abs(StepDown)
    paths += "G0 Z" + str(ZClearance)
    return paths





