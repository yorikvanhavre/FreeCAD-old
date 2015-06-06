# -*- coding: utf-8 -*-

#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2015 Dan Falck <ddfalck@gmail.com>                      *
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
'''PathKurveUtils - functions needed for using libarea (created by Dan Heeks) for making simple CNC profile paths '''
import FreeCAD
from FreeCAD import Vector
import FreeCADGui as Gui
import Part
import DraftGeomUtils
from DraftGeomUtils import geomType
import math
import area
import Path
from PathScripts import PathUtils


def makeAreaVertex(seg):
    if seg.ShapeType =='Edge':
        if isinstance(seg.Curve,Part.Circle):
            segtype = int(seg.Curve.Axis.z) #1=ccw arc,-1=cw arc
            vertex = area.Vertex(segtype, area.Point(seg.valueAt(seg.LastParameter)[0],seg.valueAt(seg.LastParameter)[1]), area.Point(seg.Curve.Center.x, seg.Curve.Center.y))
        elif isinstance(seg.Curve,Part.Line):
            point1 = seg.valueAt(seg.FirstParameter)[0],seg.valueAt(seg.FirstParameter)[1]
            point2 = seg.valueAt(seg.LastParameter)[0],seg.valueAt(seg.LastParameter)[1]
            segtype = 0 #0=line
            vertex = area.Point(seg.valueAt(seg.LastParameter)[0],seg.valueAt(seg.LastParameter)[1])
        else:
            pass
    return vertex

def makeAreaCurve(edges,direction,startpt=None,endpt=None):
    curveobj = area.Curve()
    cleanededges = PathUtils.cleanedges(edges, 0.01)
    edgelist = DraftGeomUtils.sortEdges(cleanededges) 
    seglist =[]
    if direction=='CW':
        edgelist.reverse()
        for e in edgelist:
            seglist.append(PathUtils.reverseEdge(e)) #swap end points on every segment
    else:
        for e in edgelist:
            seglist.append(e) 
                     
    firstedge= seglist[0]
    lastedge = seglist[-1]
    startptX = firstedge.valueAt(firstedge.FirstParameter)[0]
    startptY = firstedge.valueAt(firstedge.FirstParameter)[1]    
    curveobj.append(area.Point(startptX,startptY))
        
    for s in seglist:
        curveobj.append(makeAreaVertex(s))

    if startpt:
        # future nearest point code yet to be worked out -fixme
#         v1 = Vector(startpt.X,startpt.Y,startpt.Z)
#         perppoint1 = DraftGeomUtils.findPerpendicular(v1,firstedge)
#         perppoint1 = DraftGeomUtils.findDistance(v1,firstedge)
#         if  perppoint1:
#             curveobj.ChangeStart(area.Point(perppoint1[0].x,perppoint1[0].y))
#         else:
#             curveobj.ChangeStart(area.Point(startpt.X,startpt.Y))
        curveobj.ChangeStart(area.Point(startpt.X,startpt.Y))         
    if endpt:
        # future nearest point code yet to be worked out -fixme
#         v2 = Vector(endpt.X,endpt.Y,endpt.Z)
#         perppoint2 = DraftGeomUtils.findPerpendicular(v2,lastedge)
#         if perppoint2:
#             curveobj.ChangeEnd(area.Point(perppoint2[0].x,perppoint2[0].y))
#         else:
#             curveobj.ChangeEnd(area.Point(endpt.X,endpt.Y))
        curveobj.ChangeEnd(area.Point(endpt.X,endpt.Y))
           
    if direction == 'CW':
        curveobj.Reverse()

    return curveobj


# profile command,
# direction should be 'left' or 'right' or 'on'
def profile(curve,direction,radius=1.0,vertfeed=0.0,horizfeed=0.0,offset_extra=0.0, \
            rapid_safety_space=None,clearance=None,start_depth=None,stepdown=None, \
            final_depth=None,use_CRC=False,roll_start=False,roll_end=True,roll_radius=None, \
            roll_start_pt=None,roll_end_pt=None):

    output = ""
    offset_curve = area.Curve(curve)
    if offset_curve.getNumVertices() <= 1:
        raise Exception,"Sketch has no elements!"
    if direction == "on":
        use_CRC =False 

    elif (direction == "left") or (direction == "right"):
        # get tool radius plus little bit of extra offset, if needed to clean up profile a little more
        offset = radius + offset_extra
        if direction == 'left':
            offset_curve.Offset(offset)

        else:
            offset_curve.Offset(-offset)

        if offset_curve == False:
            raise Exception, "couldn't offset kurve " + str(offset_curve)
    else:
        raise Exception,"direction must be 'on', 'left', or 'right'"

    # do multiple depths
    layer_count = int((start_depth - final_depth) / stepdown)
    if layer_count * stepdown + 0.00001 < start_depth - final_depth:
        layer_count += 1
    current_start_depth = start_depth
    prev_depth = start_depth
    for i in range(1, layer_count+1):
        if i == layer_count:
            depth = final_depth
        else:
            depth = start_depth - i * stepdown
        mat_depth = prev_depth
        start_z = mat_depth
        #first move
        output += "G0 X"+str(PathUtils.fmt(offset_curve.GetFirstSpan().p.x))+\
        " Y"+str(PathUtils.fmt(offset_curve.GetFirstSpan().p.y))+\
        " Z"+str(PathUtils.fmt(mat_depth + rapid_safety_space))+"\n"
        # feed down to depth
        mat_depth = depth
        if start_z > mat_depth: 
            mat_depth = start_z
        # feed down in Z
        output += "G1 X"+str(PathUtils.fmt(offset_curve.GetFirstSpan().p.x))+\
        " Y"+str(PathUtils.fmt(offset_curve.GetFirstSpan().p.y))+" Z"+str(PathUtils.fmt(depth))+\
        " F"+str(PathUtils.fmt(vertfeed))+"\n"
        if use_CRC:
            if direction == 'left':
                output +="G41"+"\n"
            else:
                output +="G42"+"\n"
        # cut the main kurve
        current_perim = 0.0
        lastx=offset_curve.GetFirstSpan().p.x
        lasty=offset_curve.GetFirstSpan().p.y
        for span in offset_curve.GetSpans():
            current_perim += span.Length()
            if span.v.type == 0:#line
                #feed(span.v.p.x, span.v.p.y, ez)
                output +="G1 X"+str(PathUtils.fmt(span.v.p.x))+" Y"+str(PathUtils.fmt(span.v.p.y))+\
                " Z"+str(PathUtils.fmt(depth))+" F"+str(PathUtils.fmt(horizfeed))+"\n"
                lastx = span.v.p.x
                lasty = span.v.p.y
            elif (span.v.type == 1) or (span.v.type == -1):
                if span.v.type == 1:# anti-clockwise arc
                    command = 'G3'
                elif span.v.type == -1:#clockwise arc
                    command = 'G2'
                arc_I= span.v.c.x-lastx
                arc_J= span.v.c.y-lasty
                output +=command +"X"+str(PathUtils.fmt(span.v.p.x))+" Y"+ str(PathUtils.fmt(span.v.p.y))#+" Z"+ str(PathUtils.fmt(depth))
                output +=" I"+str(PathUtils.fmt(arc_I))+ " J"+str(PathUtils.fmt(arc_J))+" F"+str(PathUtils.fmt(horizfeed))+'\n'#" K"+str(PathUtils.fmt(depth)) +"\n"
                lastx = span.v.p.x
                lasty = span.v.p.y
            else:
                raise Exception, "valid geometry identifier needed"
        if use_CRC:
            #end_CRC()
            output +="G40"+"\n"
        # rapid up to the clearance height
        output +="G0 Z"+str(PathUtils.fmt(clearance))+"\n"

    del offset_curve

    return output

def makePath(edges,side,radius,vertfeed,horizfeed,offset_extra,rapid_safety_space,clearance,start_depth,step_down,final_depth,use_CRC,direction,startpt=None,endpt=None):

    curve = makeAreaCurve(edges,direction,startpt, endpt)
    if direction == 'CW':
        curve.Reverse()
    path = profile(curve,side,radius,vertfeed,horizfeed,offset_extra,rapid_safety_space,clearance,start_depth,step_down,final_depth,use_CRC)
    del curve
    return path




