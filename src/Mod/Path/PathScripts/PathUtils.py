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
import DraftGeomUtils,DraftVecUtils
import ArcDirection

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
                face = sub
                selItems['face']=face
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

def convert(wire,Side,radius,clockwise=False,Z=0.0):
    if Side == 'Left':
    # we use the OCC offset feature
        offset = wire.makeOffset(radius)
    elif Side == 'Right':
        offset = wire.makeOffset(-radius)
    else:
        offset = wire.makeOffset(0.0) #tool is on the original profile ie engraving

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
    last = None
    output = ""
    # create the path from the offset shape
    for edge in toolpath:
        if not last:
            #set the first point
            last = edge.Vertexes[0].Point
            FreeCAD.Console.PrintMessage("last pt= " + str(last)+ "\n")
            output += "G1 X" + str(fmt(last.x)) + " Y" + str(fmt(last.y)) + " Z" + str(fmt(Z)) + "\n"
        if isinstance(edge.Curve,Part.Circle):
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
            FreeCAD.Console.PrintMessage("arc  startpt= " + str(startpt)+ "\n")
            FreeCAD.Console.PrintMessage("arc  midpt= " + str(midpt)+ "\n")
            FreeCAD.Console.PrintMessage("arc  endpt= " + str(endpt)+ "\n")
            arc_cw = check_clockwise([(startpt.x,startpt.y),(midpt.x,midpt.y),(endpt.x,endpt.y)])
            FreeCAD.Console.PrintMessage("arc_cw="+ str(arc_cw)+"\n")
            if arc_cw:
                output += "G2"
            else:
                output += "G3"

            output += " X" + str(fmt(endpt.x)) + " Y" + str(fmt(endpt.y)) + " Z" + str(fmt(Z))
            output += " I" + str(fmt(relcenter.x)) + " J" + str(fmt(relcenter.y)) + " K" + str(fmt(relcenter.z))
            output += "\n"
            last = endpt
            FreeCAD.Console.PrintMessage("last pt arc= " + str(last)+ "\n")
        else:
            point = edge.Vertexes[-1].Point
            if DraftVecUtils.equals(point , last): # edges can come flipped
                point = edge.Vertexes[0].Point
            output += "G1 X" + str(fmt(point.x)) + " Y" + str(fmt(point.y)) + " Z" + str(fmt(Z)) + "\n"
            last = point
            FreeCAD.Console.PrintMessage("last pt line= " + str(last)+ "\n")

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
    while ZCurrent > ZFinalDepth:
        paths += convert(wire,Side,radius,clockwise,ZCurrent)
        ZCurrent = ZCurrent-abs(StepDown)
    paths += convert(wire,Side,radius,clockwise,ZFinalDepth)
    paths += "G0 Z" + str(ZClearance)
    return paths


