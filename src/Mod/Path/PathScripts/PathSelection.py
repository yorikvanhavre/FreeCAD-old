#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2014                                                    *
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
import FreeCAD
import FreeCADGui



def segments(poly):
    """A sequence of (x,y) numeric coordinates pairs """
    return zip(poly, poly[1:] + [poly[0]])

def check_clockwise(poly):
    '''
     a function for determining if the selected wire is clockwise or counter clockwise
     based on selecting two consecutive edges
     this will help place the tool path on the correct side of the wire
    '''
    clockwise = False
    if (sum(x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in segments(poly))) < 0:
        clockwise = not clockwise
    return clockwise

    '''
    # example useage:
    poly = [(2,2),(6,2),(6,6),(2,6)]
    check_clockwise(poly)
    False
    '''
    '''
    vlist = []
    for v in e.Vertexes:
        vlist.append((v.Point.x,v.Point.y))

    print vlist
    check_clockwise(vlist)
    '''


def multiSelect():
    '''
    A function for selecting elements of an object for CNC path operations.
    Select just a face, an edge, a vertex on the object, a point not on the object,
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
    for s in sel:
        if (s.Object.Shape.ShapeType=='Solid') or (s.Object.Shape.ShapeType=='Wire'):
            objname = s.ObjectName 
            selItems['objname']   =objname
#        if s.Object.Shape.ShapeType == 'Vertex':
#            ptlist.append((s.ObjectName,s.Object))
#            points = True
        for sub in s.SubObjects:
            if sub.ShapeType =='Face':
                face = sub
                selItems['face']     =face
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
        else:
            selItems['edgelist'] =edgelist

    if edges and (len(edgelist)>=2):
        vlist = []
        e0 = edgelist[0]
        e1=edgelist[1]
        a0 = e0.Vertexes[0]
        a1 = e0.Vertexes[1]
        b0 = e1.Vertexes[0]
        b1 = e1.Vertexes[1]
        # my crazy and crude comparison routine:
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

        if check_clockwise(vlist):
            selItems['clockwise']=True
        elif check_clockwise(vlist) == False:
            selItems['clockwise']=False

    if points:
        selItems['pointlist']  = ptlist
    if edges:
        selItems['edgenames']=edgenames

    return selItems

'''
# possible useage:
selection = multiSelect()
selection

for k in selection.keys():
    print k,", ", selection[k]
    
'''
