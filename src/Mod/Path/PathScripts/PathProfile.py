# -*- coding: utf-8 -*-

#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2014 Yorik van Havre <yorik@uncreated.net>              *
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

import FreeCAD,FreeCADGui,Path,PathGui
from PySide import QtCore,QtGui
from PathScripts import PathUtils,PathSelection,PathProject

"""Path Profile object and FreeCAD command"""

# Qt tanslation handling
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig)


class ObjectProfile:

    def __init__(self,obj):
        obj.addProperty("App::PropertyLinkSub","Base","Path",translate("Parent Object","The base geometry of this toolpath"))
        #obj.addProperty("App::PropertyString", "ObjName", "Path",translate("Part Name", "The name of the part being processed"))
        obj.addProperty("App::PropertyLinkSub","Face1","Path",translate("Face1","First Selected Face to help determine where final depth of tool path is"))
        obj.addProperty("App::PropertyLinkSub","Face2","Path",translate("Face2","Second Selected Face to help determine where the upper level of tool path is"))
        obj.addProperty("App::PropertyBool","PathClosed","Path",translate("Path Closed","If the toolpath is a closed polyline this is True"))
        obj.addProperty("App::PropertyLinkSub","Edge1","Path",translate("Edge 1","First Selected Edge to help determine which geometry to make a toolpath around"))
        obj.addProperty("App::PropertyLinkSub","Edge2","Path",translate("Edge 2","Second Selected Edge to help determine which geometry to make a toolpath around"))
        obj.addProperty("App::PropertyBool","Active","Path",translate("Active","Make False, to prevent operation from generating code"))
    

        obj.addProperty("App::PropertyIntegerConstraint","ToolNum","Tool",translate("PathProfile","The tool number in use"))
        obj.ToolNum = (0,0,1000,1)
#        obj.addProperty("App::PropertyFloat", "SpindleSpeed", "Tool", translate("Spindle Speed","The speed of the cutting spindle in RPM"))
#        obj.addProperty("App::PropertyEnumeration", "SpindleDir", "Tool", translate("Spindle Dir","Direction of spindle rotation"))
#        obj.SpindleDir = ['Forward','Reverse']

        #Depth Properties
        obj.addProperty("App::PropertyDistance", "ClearanceHeight", "Depth", translate("Clearance Height","The height needed to clear clamps and obstructions"))
        obj.addProperty("App::PropertyLength", "StepDown", "Depth", translate("StepDown","Incremental Step Down of Tool"))
        obj.addProperty("App::PropertyBool","UseStartDepth","Depth",translate("Use Start Depth","make True, if manually specifying a Start Start Depth"))
        obj.addProperty("App::PropertyDistance", "StartDepth", "Depth", translate("Start Depth","Starting Depth of Tool- first cut depth in Z"))
        obj.addProperty("App::PropertyDistance", "FinalDepth", "Depth", translate("Final Depth","Final Depth of Tool- lowest value in Z"))
        obj.addProperty("App::PropertyDistance", "RetractHeight", "Depth", translate("Retract Height","The height desired to retract tool when path is finished"))
        obj.addProperty("App::PropertyString","Comment","Path",translate("PathProject","An optional comment for this profile"))
        obj.addProperty("App::PropertyEnumeration", "Direction", "Profile",translate("Direction", "The direction that the toolpath should go around the part ClockWise CW or CounterClockWise CCW"))
        obj.Direction = ['CW','CCW']

        #Feed Properties
        obj.addProperty("App::PropertySpeed", "VertFeed", "Feed",translate("Vert Feed","Feed rate for vertical moves in Z"))
        obj.addProperty("App::PropertySpeed", "HorizFeed", "Feed",translate("Horiz Feed","Feed rate for horizontal moves"))
       
        #Start Point Properties
        obj.addProperty("App::PropertyVector","StartPoint","Start Point",translate("Start Point","The start point of this path"))
        obj.addProperty("App::PropertyBool","UseStartPoint","Start Point",translate("Use Start Point","make True, if specifying a Start Point"))
        obj.addProperty("App::PropertyLength", "ExtendAtStart", "Start Point", translate("extend at start", "extra length of tool path before start of part edge"))
        obj.addProperty("App::PropertyLength", "LeadInLineLen", "Start Point", translate("lead in length","length of straight segment of toolpath that comes in at angle to first part edge"))


        #End Point Properties
        obj.addProperty("App::PropertyBool","UseEndPoint","End Point",translate("Use End Point","make True, if specifying an End Point"))
        obj.addProperty("App::PropertyLength", "ExtendAtEnd", "End Point", translate("extend at end","extra length of tool path after end of part edge"))
        obj.addProperty("App::PropertyLength", "LeadOutLineLen", "End Point", translate("lead_out_line_len","length of straight segment of toolpath that comes in at angle to last part edge"))
        obj.addProperty("App::PropertyVector","EndPoint","End Point",translate("End Point","The end point of this path"))

        #Profile Properties
        obj.addProperty("App::PropertyEnumeration", "Side", "Profile", translate("Side","Side of edge that tool should cut"))
        obj.Side = ['Left','Right','On']

        obj.addProperty("App::PropertyDistance", "RollRadius", "Profile", translate("Roll Radius","Radius at start and end"))
        obj.addProperty("App::PropertyDistance", "OffsetExtra", "Profile",translate("OffsetExtra","Extra value to stay away from final profile- good for roughing toolpath"))
        obj.addProperty("App::PropertyLength", "SegLen", "Profile",translate("Seg Len","Tesselation  value for tool paths made from beziers, bsplines, and ellipses"))

        obj.Proxy = self
#        obj.Closed = True

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None
        
    def getTool(self,obj,number=0):
        "retrieves a tool from a hosting object with a tooltable, if any"
        for o in obj.InList:
            if o.TypeId == "Path::FeatureCompoundPython":
                for m in o.Group:
                    if hasattr(m,"Tooltable"):
                        return m.Tooltable.getTool(number)
        # not found? search one level up
        for o in obj.InList:
            return self.getTool(o,number)
        return None

    def execute(self,obj):
        if obj.Base:
            tool = self.getTool(obj,obj.ToolNum)
            if tool:
                radius = tool.Diameter/2
            else:
                # temporary value, to be taken from the properties later on
                radius = 0.001
            if obj.Base[0].Shape.ShapeType == "Wire": #a pure wire was picked
                wire = obj.Base[0].Shape
            else: #we are dealing with a face and it's edges or just a face
                if obj.Edge1:
                    e1 = FreeCAD.ActiveDocument.getObject(obj.Base[0].Name).Shape.Edges[eval(obj.Edge1[1][0].lstrip('Edge'))-1]
                    if e1.BoundBox.ZMax <> e1.BoundBox.ZMin:
                        FreeCAD.Console.PrintError('vertical edges not valid yet\n')
                        return
                    if obj.Base[0].Shape.ShapeType =='Wire':
                        wire = obj.Base[0].Shape
                    if obj.Base[0].Shape.ShapeType =='Solid' or obj.Base[0].Shape.ShapeType =='Compound':
                        shape = obj.Base[0].Shape
                        for fw in shape.Wires:
                            if (fw.BoundBox.ZMax == e1.BoundBox.ZMax) and (fw.BoundBox.ZMin == e1.BoundBox.ZMin):
                                for e in fw.Edges:
                                    if e.isSame(e1):
                                        #FreeCAD.Console.PrintMessage('found the same objects\n')
                                        wire = fw
                elif obj.Face1: # we are only dealing with a face or faces
                    f1 = FreeCAD.ActiveDocument.getObject(obj.Base[0].Name).Shape.Faces[eval(obj.Face1[1][0].lstrip('Face'))-1]
                    # make the side Left and direction CW for normal cnc milling
                    obj.Direction = 'CW'
                    obj.Side = "Left"
                    # we only consider the outer wire if this is a single Face
                    wire = f1.OuterWire

            if obj.Direction == 'CCW':
                clockwise=False
            else:
                clockwise=True
            output =""
            output += '('+ str(obj.Comment)+')\n'
#            output += "M6 T"
#            output += str(obj.ToolNum)+"\n"
#            output +="M"
#            if obj.SpindleDir =='Forward':
#                output +="3"
#            else:
#                output +="4"
#            output += " \n"
#            output +="S"+str(obj.SpindleSpeed) +"\n" #going to just use spindle forward for the moment

#            output += "\n"
            FirstEdge= None
            if obj.Edge1:
                ename = obj.Edge1[1][0]
                edgeNumber = int(ename[4:])-1
                FirstEdge = obj.Base[0].Shape.Edges[edgeNumber]
            ZMax = obj.Base[0].Shape.BoundBox.ZMax
            #ZCurrent = ZMax- obj.StepDown.Value
            ZCurrent = obj.ClearanceHeight.Value
            #while ZCurrent >= obj.FinalDepth.Value:
            #                   approach(wire,Side,radius,clockwise,ZClearance,StepDown,ZFinalDepth)
            if obj.UseStartDepth:
                output += PathUtils.SortPath(wire,obj.Side,radius,clockwise,obj.ClearanceHeight.Value,obj.StepDown.Value,obj.StartDepth.Value, obj.FinalDepth.Value,FirstEdge,obj.PathClosed,obj.SegLen.Value,obj.VertFeed.Value,obj.HorizFeed.Value)
            else:
                output += PathUtils.SortPath(wire,obj.Side,radius,clockwise,obj.ClearanceHeight.Value,obj.StepDown.Value,ZMax, obj.FinalDepth.Value,FirstEdge,obj.PathClosed,obj.SegLen.Value,obj.VertFeed.Value,obj.HorizFeed.Value)
                #ZCurrent = ZCurrent-abs(obj.StepDown.Value)

#            path = Path.Path(output)
#            obj.Path = path

            if obj.Active:
                path = Path.Path(output)
                obj.Path = path
                obj.ViewObject.Visibility = True
#                FreeCAD.Console.PrintMessage(output)
            else:
                path = Path.Path("(inactive operation)")
                obj.Path = path
                obj.ViewObject.Visibility = False


class CommandPathProfile:
    def GetResources(self):
        return {'Pixmap'  : 'Path-Profile',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PathProfile","Profile"),
                'Accel': "P, P",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PathProfile","Creates a Path Profile object from selected faces")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None
        
    def Activated(self):
        import Path
        from PathScripts import PathUtils,PathProfile,PathProject
        prjexists = False
        selection = PathSelection.multiSelect()

        if not selection:
            return

        # if everything is ok, execute and register the transaction in the undo/redo stack
        FreeCAD.ActiveDocument.openTransaction(translate("PathProfile","Create Profile"))
        FreeCADGui.addModule("PathScripts.PathProfile")

        obj = FreeCAD.ActiveDocument.addObject("Path::FeaturePython","Profile")
        PathProfile.ObjectProfile(obj)

        obj.Base = (FreeCAD.ActiveDocument.getObject(selection['objname']))

        if selection['facenames']:
            FreeCAD.Console.PrintMessage('There are edges selected\n')
            obj.Face1 = (FreeCAD.ActiveDocument.getObject(selection['objname']),selection['facenames'][0])
            if len(selection['facenames'])>1:
                obj.Face2 = (FreeCAD.ActiveDocument.getObject(selection['objname']),selection['facenames'][-1])

        if selection['edgenames']:
            FreeCAD.Console.PrintMessage('There are edges selected\n')
            
            obj.Edge1 =(FreeCAD.ActiveDocument.getObject(selection['objname']),(selection['edgenames'][0]))
            if len(selection['edgenames'])>1:
                obj.Edge2 =(FreeCAD.ActiveDocument.getObject(selection['objname']),(selection['edgenames'][-1]))

        if selection['pointlist']:
            FreeCADGui.doCommand('from FreeCAD import Vector')
            stptX, stptY, stptZ = selection['pointlist'][0].X, selection['pointlist'][0].Y, selection['pointlist'][0].Z
            obj.StartPoint = Vector((stptX),(stptY),(stptZ))
            if len(selection['pointlist'])>1: # we have more than one point so we have an end point
                endptX, endptY, endptZ = selection['pointlist'][-1].X, selection['pointlist'][-1].Y, selection['pointlist'][-1].Z
                obj.EndPoint = Vector(endptX,endptY,endptZ)
        if selection['pathwire'].isClosed():
            obj.PathClosed = True
            if selection['clockwise']:
                obj.Side = "Left"
                obj.Direction = "CW"
            elif selection['clockwise'] == False: 
                obj.Side = "Right"
                obj.Direction = "CCW"
        else:
            obj.Side = "On"
            obj.Direction = "CCW"
            obj.PathClosed = False

        ZMax = obj.Base[0].Shape.BoundBox.ZMax
        ZMin = obj.Base[0].Shape.BoundBox.ZMin
        obj.StepDown.Value = 1.0
        obj.StartDepth.Value = ZMax- obj.StepDown.Value
        obj.FinalDepth.Value = ZMin-1.0
        obj.ClearanceHeight.Value =  ZMax + 5.0
#        obj.SpindleDir = 'Forward'
#        obj.SpindleSpeed = 2000.00
        obj.SegLen.Value = 0.5
        obj.ViewObject.Proxy = 0
        obj.Active = True

        for o in FreeCAD.ActiveDocument.Objects:
            if "Proxy" in o.PropertiesList:
                if isinstance(o.Proxy,PathProject.ObjectPathProject):
                    project = o
                    g = o.Group
                    g.append(obj)
                    o.Group = g
                    prjexists = True

        if prjexists:
            pass
        else: #create a new path object
            project = FreeCAD.ActiveDocument.addObject("Path::FeatureCompoundPython","Project")
            PathProject.ObjectPathProject(project)
            PathProject.ViewProviderProject(project.ViewObject)
            g = project.Group
            g.append(obj)
            project.Group = g
        tl = PathUtils.changeTool(obj,project)
        if tl:
            obj.ToolNum = tl

        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()

if FreeCAD.GuiUp: 
    # register the FreeCAD command
    FreeCADGui.addCommand('Path_Profile',CommandPathProfile())

FreeCAD.Console.PrintLog("Loading PathProfile... done\n")
