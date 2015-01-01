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
import Part
from FreeCAD import Vector
import FreeCADGui
import math
import DraftGeomUtils
import DraftVecUtils

def isSameEdge(e1,e2):
    """isSameEdge(e1,e2): return True if the 2 edges are both lines or arcs/circles and have the same
    points - inspired by Yorik's function isSameLine"""
    if not (isinstance(e1.Curve,Part.Line) or isinstance(e1.Curve,Part.Circle)):
        return False
    if not (isinstance(e2.Curve,Part.Line) or isinstance(e2.Curve,Part.Circle)):
        return False
    if type(e1.Curve) <> type(e2.Curve):
        return False
    if isinstance(e1.Curve,Part.Line):
        if (DraftVecUtils.equals(e1.Vertexes[0].Point,e2.Vertexes[0].Point)) and \
           (DraftVecUtils.equals(e1.Vertexes[-1].Point,e2.Vertexes[-1].Point)):
            return True
        elif (DraftVecUtils.equals(e1.Vertexes[-1].Point,e2.Vertexes[0].Point)) and \
           (DraftVecUtils.equals(e1.Vertexes[0].Point,e2.Vertexes[-1].Point)):
            return True
    if isinstance(e1.Curve,Part.Circle):
        center = False; radius= False; endpts=False
        if e1.Curve.Center == e2.Curve.Center:
            center = True
        if e1.Curve.Radius == e2.Curve.Radius:
            radius = True
        if (DraftVecUtils.equals(e1.Vertexes[0].Point,e2.Vertexes[0].Point)) and \
           (DraftVecUtils.equals(e1.Vertexes[-1].Point,e2.Vertexes[-1].Point)):
            endpts = True
        elif (DraftVecUtils.equals(e1.Vertexes[-1].Point,e2.Vertexes[0].Point)) and \
           (DraftVecUtils.equals(e1.Vertexes[0].Point,e2.Vertexes[-1].Point)):
            endpts = True
        if (center and radius and endpts):
            return True
    return False


def segments(poly):
    ''' A sequence of (x,y) numeric coordinates pairs '''
    return zip(poly, poly[1:] + [poly[0]])

def check_clockwise(poly):
    '''
     check_clockwise(poly) a function for returning a boolean if the selected wire is clockwise or counter clockwise
     based on point order. poly = [(x1,y1),(x2,y2),(x3,y3)]
    '''
    clockwise = False
    if (sum(x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in segments(poly))) < 0:
        clockwise = not clockwise
    return clockwise

def Sort2Edges(edgelist=[]):
    '''Sort2Edges(edgelist=[]) simple function to reorder the start and end pts of two edges based on their selection order. Returns the list, the start point, and their common point, => edgelist, vertex, vertex'''
    if len(edgelist)>=2:
        vlist = []
        e0 = edgelist[0]
        e1=edgelist[1]
        a0 = e0.Vertexes[0]
        a1 = e0.Vertexes[1]
        b0 = e1.Vertexes[0]
        b1 = e1.Vertexes[1]
        # comparison routine to order two edges:
        if a1.isSame(b0):
            vlist.append((a0.Point.x,a0.Point.y))
            vlist.append((a1.Point.x,a1.Point.y))
            vlist.append((b1.Point.x,b1.Point.y))

        elif a0.isSame(b0):
            vlist.append((a1.Point.x,a1.Point.y))
            vlist.append((a0.Point.x,a0.Point.y))
            vlist.append((b1.Point.x,b1.Point.y))

        elif a0.isSame(b1):
            vlist.append((a1.Point.x,a1.Point.y))
            vlist.append((a0.Point.x,a0.Point.y))
            vlist.append((b0.Point.x,b0.Point.y))

        elif a1.isSame(b1):
            vlist.append((a0.Point.x,a0.Point.y))
            vlist.append((a1.Point.x,a1.Point.y))
            vlist.append((b0.Point.x,b0.Point.y))

        edgestart = Vector(vlist[0][0],vlist[0][1],e0.Vertexes[1].Z)
        edgecommon = Vector(vlist[1][0],vlist[1][1],e0.Vertexes[1].Z)

    return vlist,edgestart,edgecommon

def multiSelect():
    '''
    A function for selecting elements of an object for CNC path operations.
    Select just a face, an edge,or two edges to indicate direction, a vertex on the object, a point not on the object,
    or some combination. Returns a dictionary.
    '''
    sel = FreeCADGui.Selection.getSelectionEx()
    numobjs = len([selobj.Object for selobj in sel])
    if numobjs == 0:
        FreeCAD.Console.PrintError('Please select some objects and try again.\n')
        return
    goodselect = False
    for s in sel:
        for i in s.SubObjects:
            if i.ShapeType == 'Face':
                goodselect = True
            if i.ShapeType == 'Edge':
                goodselect = True

    if not goodselect:
        FreeCAD.Console.PrintError('Please select a face and/or edges along with points (optional) and try again.\n')
        return

    selItems = {}
    selItems['objname']=None #the parent object name - a 3D solid
    selItems['pointlist']=None #start and end points
    selItems['facename']=None # the selected face name
    selItems['face']=None # the actual face shape
    selItems['facelist']=None #list of faces selected
    selItems['edgelist']=None #some edges that could be selected along with points and faces
    selItems['edgenames']=None
    selItems['pathwire']=None #the whole wire around edges of the face
    selItems['clockwise']=None
    edgelist =[]
    edgenames=[]
    ptlist=[]
    face = False
    edges = False
    points = False
    wireobj = False
    facelist= []
    for s in sel:
        if s.Object.Shape.ShapeType in ['Solid','Compound','Wire','Vertex']:
            if not (s.Object.Shape.ShapeType =='Vertex'):
                objname = s.ObjectName 
                selItems['objname']   =objname
            if s.Object.Shape.ShapeType == 'Wire':
                wireobj = True
            if s.Object.Shape.ShapeType == 'Vertex':
                #ptlist.append((s.ObjectName,s.Object))
                ptlist.append(s.Object)
                points = True
        for sub in s.SubObjects:
            if sub.ShapeType =='Face':
                #face = sub
                #selItems['face']=face
                facelist.append(sub)
            if sub.ShapeType =='Edge':
                edge = sub
                edgelist.append(edge)
                edges = True
            if sub.ShapeType =='Vertex':
                ptlist.append(sub)
                points = True

        for sub in s.SubElementNames:
            if 'Face' in sub:
                facename = sub
                selItems['facename']  =facename  ; 
            if 'Edge' in sub:
                edgenames.append(sub)
# now indicate which wire is going to be processed, based on which edges are selected
    if facelist:
        selItems['facelist']=facelist

    if edges:
        if face:
            selItems['edgelist'] =edgelist
            for fw in face.Wires:
                for e in  fw.Edges:
                    if e.isSame(edge):
                        pathwire = fw
                        selItems['pathwire']  =pathwire
        elif wireobj:
            selItems['pathwire'] =s.Object.Shape
            selItems['edgelist'] =edgelist
        else:
            for w in s.Object.Shape.Wires:
                for e in  w.Edges:
                    if e.BoundBox.ZMax == e.BoundBox.ZMin: #if they are on same plane in Z as sel edge
                        if e.isSame(edge):
                            pathwire = w
                            selItems['pathwire']  =pathwire
            selItems['edgelist'] =edgelist

    if not edges:
        if face:
            selItems['pathwire']  =face.OuterWire


    if edges and (len(edgelist)>=2):
        vlist,edgestart,edgecommon=Sort2Edges(edgelist)
        edgepts ={}
        edgepts['vlist'] = vlist
        edgepts['edgestart']=edgestart # start point of edges selected
        edgepts['edgecommon']=edgecommon # point where two edges join- will be last point in in first gcode line
        selItems['edgepts']=edgepts

        if check_clockwise(vlist):
            selItems['clockwise']=True
        elif check_clockwise(vlist) == False:
            selItems['clockwise']=False

    if points:
        selItems['pointlist']  = ptlist
    if edges:
        selItems['edgenames']=edgenames

    return selItems

def fmt(val): return format(val, '.4f') #set at 4 decimal places for testing

def convert(toolpath,Side,radius,clockwise=False,Z=0.0,firstedge=None):
    '''converts lines and arcs to G1,G2,G3 moves'''
    last = None
    output = ""
    # create the path from the offset shape
    for edge in toolpath:
        if not last:
            #set the first point
            last = edge.Vertexes[0].Point
            #FreeCAD.Console.PrintMessage("last pt= " + str(last)+ "\n")
            output += "G1 X" + str(fmt(last.x)) + " Y" + str(fmt(last.y)) + " Z" + str(fmt(Z)) + "\n"
        if isinstance(edge.Curve,Part.Circle):
            #FreeCAD.Console.PrintMessage("arc\n")
            arcstartpt = edge.valueAt(edge.FirstParameter)
            midpt = edge.valueAt((edge.FirstParameter+edge.LastParameter)*0.5)
            arcendpt = edge.valueAt(edge.LastParameter)
            arcchkpt=edge.valueAt(edge.LastParameter*.99)

            if DraftVecUtils.equals(last,arcstartpt):
                startpt = arcstartpt
                endpt = arcendpt
            else:
                startpt = arcendpt
                endpt = arcstartpt
            center = edge.Curve.Center
            relcenter = center.sub(last)
            #FreeCAD.Console.PrintMessage("arc  startpt= " + str(startpt)+ "\n")
            #FreeCAD.Console.PrintMessage("arc  midpt= " + str(midpt)+ "\n")
            #FreeCAD.Console.PrintMessage("arc  endpt= " + str(endpt)+ "\n")
            arc_cw = check_clockwise([(startpt.x,startpt.y),(midpt.x,midpt.y),(endpt.x,endpt.y)])
            #FreeCAD.Console.PrintMessage("arc_cw="+ str(arc_cw)+"\n")
            if arc_cw:
                output += "G2"
            else:
                output += "G3"

            output += " X" + str(fmt(endpt.x)) + " Y" + str(fmt(endpt.y)) + " Z" + str(fmt(Z))
            output += " I" + str(fmt(relcenter.x)) + " J" + str(fmt(relcenter.y)) + " K" + str(fmt(relcenter.z))
            output += "\n"
            last = endpt
            #FreeCAD.Console.PrintMessage("last pt arc= " + str(last)+ "\n")
        else:
            point = edge.Vertexes[-1].Point
            if DraftVecUtils.equals(point , last): # edges can come flipped
                point = edge.Vertexes[0].Point
            output += "G1 X" + str(fmt(point.x)) + " Y" + str(fmt(point.y)) + " Z" + str(fmt(Z)) + "\n"
            last = point
            #FreeCAD.Console.PrintMessage("line\n")
            #FreeCAD.Console.PrintMessage("last pt line= " + str(last)+ "\n")

    return output


def SortPath(wire,Side,radius,clockwise,ZClearance,StepDown,ZStart, ZFinalDepth,firstedge=None):
    edgelist =[]
    for edge in wire.Edges:
        edgelist.append(edge)

    elindex = None
    n=0
    for e in edgelist:
        if isSameEdge(e,firstedge):
            FreeCAD.Console.PrintMessage('found first edge\n')
            elindex = n
        n+=1

    l1 = edgelist[:elindex]
    l2 = edgelist[elindex:]
    newedgelist = l2+l1
    nlist = DraftGeomUtils.sortEdgesOld(newedgelist)
    newwire = Part.Wire(nlist)
    
    '''sorts the wire path for forward/reverse (CW/CCW) and start of path '''
    if Side == 'Left':
    # we use the OCC offset feature
        offset = newwire.makeOffset(radius)#tool is outside line
    elif Side == 'Right':
        offset = newwire.makeOffset(-radius)#tool is inside line
    else:
        offset = newwire.makeOffset(0.0) #tool is on the original profile ie engraving
    # resort the edges in the wire


#    nlist = DraftGeomUtils.sortEdgesOld(edgelist)
#    offset = Part.Wire(nlist)

    if clockwise:
        revlist = []
        for edge in offset.Edges:
            revlist.append(edge)
        revlist.reverse()
        toolpath = DraftGeomUtils.sortEdgesOld(revlist)

    else:
        newlist =[]
        for edge in offset.Edges:
            newlist.append(edge)
        FreeCAD.Console.PrintMessage('counter clockwise toolpath\n')
        toolpath = newlist

    paths =""
    first = toolpath[0].Vertexes[0].Point
    paths += "G0 X"+str(fmt(first.x))+"Y"+str(fmt(first.y))+"\n"
    ZCurrent = ZStart- StepDown
    while ZCurrent > ZFinalDepth:
        paths += convert(toolpath,Side,radius,clockwise,ZCurrent,firstedge)
        ZCurrent = ZCurrent-abs(StepDown)
    paths += convert(toolpath,Side,radius,clockwise,ZFinalDepth,firstedge)
    paths += "G0 Z" + str(ZClearance)
    return paths


