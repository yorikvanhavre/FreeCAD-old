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


from DraftGeomUtils import sortEdges, findMidpoint,findWires, isReallyClosed, isClockwise
from FreeCAD import Vector,Base
import Part
import FreeCADGui
import FreeCAD
import FreeCAD as App
import FreeCADGui as Gui
#from PyQt4 import QtGui,QtCore
from PySide import QtGui,QtCore

def getGeom(g):

    geom = g.Group
    name = g.Label
    
    objs = []
    item = "# ***** "+name+" *****\n"
    edges=[]
    points = []
    for s in geom:
        if s.Shape.ShapeType =='Vertex':
            points.append(s)
        elif s.Shape.ShapeType =='Wire':
            edges.extend(s.Shape.Edges)
        elif s.Shape.ShapeType =='Face':
            edges.extend(s.Shape.OuterWire.Edges)
        else:
        #objs.append(s.Object)
            edges.append(s.Shape)
        
    sorted_edges = []
    sorted_edges = sortEdges(edges)
    wire1 = findWires(sorted_edges)


    start=sorted_edges[0]
    end=sorted_edges[-1]
    startingZ = start.Vertexes[0].Z
    #set starting depth to same Z as starting curve element
    #self.form.lineEditStartDepth.setText(str(start.Vertexes[0].Z))
    item += name+" = area.Curve()\n"
    
    if isReallyClosed(wire1[0]):
        item += '#closed path\n'
        path = 'closedpath'
    else:
        item += '#open path\n'
        path = 'openpath'
    
#    if isSameVertex(start.Vertexes[0],end.Vertexes[1]) :
#        item += '#closed path\n'
#        path = 'closedpath'
#    else:
#        item += '#open path\n'
#        path = 'openpath'

    #if path ==  'openpath' :
    item += name+".append(area.Point(" + str(start.Vertexes[0].X) + "," + str(start.Vertexes[0].Y)+ "))\n"

    for s in sorted_edges:
        #edges.append(s)
        if (isinstance(s.Curve,Part.Circle)):
            mp = findMidpoint(s)
            ce = s.Curve.Center
#            tang1 = s.Curve.tangent(s.ParameterRange[0]) ; tang2 = s.Curve.tangent(s.ParameterRange[1])
#            cross1 = Vector.cross(Base.Vector(tang1[0][0],tang1[0][1],tang1[0][2]),Base.Vector(tang2[0][0],tang2[0][1],tang2[0][2]))
            #look at isClockwise in DraftGeomUtils.py
#            if cross1[2] > 0:
            if isClockwise(s):
                direct = '1 ' #we seem to be working in a rh system in FreeCAD 
            else:
                direct = '-1 ' 
            item += name+".append(area.Vertex("+str(direct)+ ", area.Point( "+ str(s.Vertexes[-1].Point[0])+", "+str(s.Vertexes[-1].Point[1])+ "), area.Point("+str(s.Curve.Center [0])+ ", " + str(s.Curve.Center[1])+ ")))\n"

        elif (isinstance(s.Curve,Part.Line)):
            item += name+".append(area.Point( "+str(s.Vertexes[-1].Point[0])+", " +str(s.Vertexes[-1].Point[1])+ "))\n"
        else:
            pass

#    if path ==  'closedpath':
#        item += name+".append(area.Point(" + str(start.Vertexes[1].X) + "," + str(start.Vertexes[1].Y)+ "))\n"

    #item+= name+".Reverse()\n"
    #return item

    if points:
        item+= name+"_startparams = {'key':'value'}\n"
        item+= name+"_startparams['startpt'] = True\n"
        item+= name+"_startparams['startptX'] = "+str(points[0].X)+"\n"
        item+= name+"_startparams['startptY'] = "+str(points[0].Y)+"\n"
        #item+= "kurve_funcs.make_smaller( "+ name+ ", start = area.Point(" + str(points[0].X)+","+str(points[0].Y)+"))\n"
    else:
        item+= name+"_startparams = {'key':'value'}\n"
        item+= name+"_startparams['startpt'] = False\n"
       

#    item+="profileparams['side'] = 'left'\n"
#    item+="profile("+name+", profileparams,"+ name+"_startparams)\n"

    return item
#    clipboard = QtGui.QApplication.clipboard()
#    clipboard.setText(item)


def getcustom(d):
    item = ""
    for p in d.PropertiesList:
        if p=='Proxy':
            pass
        elif p=='Label':
            pass
        elif p=='CustomProps':
            for i in d.getPropertyByName(p):
                item += i
                
        else:
            if p == 'Side':
                item += (p +"="+ repr(d.getPropertyByName(p)))
            else:
                item += (p +"="+ str(d.getPropertyByName(p)))
            item +="\n"
    return item


def parseit():
    sel=Gui.Selection.getSelection()
    topgroup = sel[0]
    items = ""
    geomlist =[]
    for g in topgroup.Group:
        #geomlist.append(g.Label)
        if g.TypeId ==  'App::FeaturePython':
            #print 'FeaturePython\n'
            items+= getcustom(g)
            items+="\n"
        elif g.TypeId ==  'App::DocumentObjectGroup' :
            #print 'DocumentObjectGroup'
            #items+=  '#'+ g.Label
            geomlist.append(str(g.Label))
            items+=  getGeom(g)
            items+="\n"

        else:
            items+=  '# something else\n'
    #items+= str(geomlist)
    return items,geomlist

curves,geolist = parseit()
heeksitems =""
heeksitems+= curves
#heeksitems+= "geolist=" + str(geolist)
clipboard = QtGui.QApplication.clipboard()
clipboard.setText(heeksitems)

