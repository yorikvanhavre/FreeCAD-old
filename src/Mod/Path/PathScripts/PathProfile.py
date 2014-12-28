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
import PathSelection,ConvGcode

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
        obj.addProperty("App::PropertyLinkSub","Edge1","Path",translate("Edge","First Selected Edge to help determine which geometry to make a toolpath around"))
#        obj.addProperty("Part::PropertyPartShape","Edge2","Path",translate("Edge","Second Selected Edge to help determine which geometry to make a toolpath around"))
        obj.addProperty("App::PropertyInteger","ToolNumber","Tool",translate("PathProfile","The tool number to use"))
        obj.addProperty("App::PropertyFloat", "ClearanceHeight", "Depth Parameters", translate("Clearance Height","The height needed to clear clamps and obstructions"))
        obj.addProperty("App::PropertyFloat", "StepDown", "Depth Parameters", translate("StepDown","Incremental Step Down of Tool"))
        obj.addProperty("App::PropertyFloat", "StartDepth", "Depth Parameters", translate("Start Depth","Starting Depth of Tool- first cut depth in Z"))
        obj.addProperty("App::PropertyFloat", "FinalDepth", "Depth Parameters", translate("Final Depth","Final Depth of Tool- lowest value in Z"))
        obj.addProperty("App::PropertyFloat", "RetractHeight", "Depth Parameters", translate("Retract Height","The height desired to retract tool when path is finished"))
        obj.addProperty("App::PropertyVector","StartPoint","Profile Parameters",translate("Start Point","The start point of this path"))
        obj.addProperty("App::PropertyBool","UseStartPoint","Profile Parameters",translate("Use Start Point","make True, if specifying a Start Point"))
        obj.addProperty("App::PropertyEnumeration", "Direction", "Profile Parameters",translate("Direction", "The direction that the toolpath should go around the part ClockWise CW or CounterClockWise CCW"))
        obj.Direction = ['CW','CCW']
        obj.addProperty("App::PropertyVector","EndPoint","Profile Parameters",translate("End Point","The end point of this path"))
        obj.addProperty("App::PropertyBool","UseEndPoint","Profile Parameters",translate("Use End Point","make True, if specifying an End Point"))
        obj.addProperty("App::PropertyEnumeration", "Side", "Profile Parameters", translate("Side","Side of edge that tool should cut"))
        obj.Side = ['Left','Right','On']
        obj.addProperty("App::PropertyFloat", "RollRadius", "Profile Parameters", translate("Roll Radius","Radius at start and end"))
        obj.addProperty("App::PropertyFloat", "OffsetExtra", "Profile Parameters",translate("OffsetExtra","Extra value to stay away from final profile- good for roughing toolpath"))
        obj.addProperty("App::PropertyFloat", "ExtendAtStart", "Profile Parameters", translate("extend at start", "extra length of tool path before start of part edge"))
        obj.addProperty("App::PropertyFloat", "ExtendAtEnd", "Profile Parameters", translate("extend at end","extra length of tool path after end of part edge"))
        obj.addProperty("App::PropertyFloat", "LeadInLineLen", "Profile Parameters", translate("lead in length","length of straight segment of toolpath that comes in at angle to first part edge"))
        obj.addProperty("App::PropertyFloat", "LeadOutLineLen", "Profile Parameters", translate("lead_out_line_len","length of straight segment of toolpath that comes in at angle to last part edge"))
        obj.Proxy = self


    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None
        
    def getTool(self,obj,number=0):
        "retrieves a tool from a hosting object with a tooltable, if any"
        for o in obj.InList:
            if hasattr(o,"Tooltable"):
                return o.Tooltable.getTool(number)
        # not found? search one level up
        for o in obj.InList:
            return self.getTool(o,number)
        return None

    def execute(self,obj):
        if obj.Base:
            tool = self.getTool(obj,obj.ToolNumber)
            if tool:
                radius = tool.Diameter/2
            else:
                # temporary value, to be taken from the properties later on
                radius = 1

            if obj.Base[0].Shape.ShapeType == "Wire": #a pure wire was picked
                wire = obj.Base[0].Shape
            else: #we are dealing with a face and it's wires or a wire
                if obj.Edge1:

                    e1 = FreeCAD.ActiveDocument.getObject(obj.Base[0].Name).Shape.Edges[eval(obj.Edge1[1][0].lstrip('Edge'))-1]
                    if e1.BoundBox.ZMax <> e1.BoundBox.ZMin:
                        FreeCAD.Console.PrintError('vertical edges not valid yet\n')
                        return

                    if obj.Base[0].Shape.ShapeType =='Wire':
                        wire = obj.Base[0].Shape

                    if obj.Base[0].Shape.ShapeType =='Solid':
                        shape = obj.Base[0].Shape
                        for fw in shape.Wires:
                            if (fw.BoundBox.ZMax == e1.BoundBox.ZMax) and (fw.BoundBox.ZMin == e1.BoundBox.ZMin):

                                for e in fw.Edges:
                                    if e.isSame(e1):
                                        FreeCAD.Console.PrintMessage('found the same objects\n')
                                        wire = fw

                else: # we are only dealing with a face
                    shape = getattr(obj.Base[0].Shape,obj.Base[1][0])
                    # we only consider the outer wire if this is a Face
                    wire = shape.OuterWire
            if obj.Direction == 'CCW':
                revpts=False
            else:
                revpts=True
            output = ""
            
            
            #ZMax = obj.Base[0].Shape.BoundBox.ZMax
            #ZCurrent = ZMax- obj.StepDown
            ZCurrent = obj.StartDepth
            while ZCurrent >= obj.FinalDepth:
                output += ConvGcode.convert(wire,obj.Side,obj.ToolNumber,radius,revpts,ZCurrent)
                ZCurrent = ZCurrent-obj.StepDown
            
            #ZCurrent = ZCurrent -obj.FinalDepth
            #output += ConvGcode.convert(wire,obj.Side,obj.ToolNumber,radius,revpts,obj.FinalDepth)
            path = Path.Path(output)
            obj.Path = path

class CommandPathProfile:
    def GetResources(self):
        return {'Pixmap'  : 'Path-Profile',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PathProfile","Profile"),
                'Accel': "P, P",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PathProfile","Creates a Path Profile object from selected faces")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None
        
    def Activated(self):
        # check that the selection contains exactly what we want
        selection = PathSelection.multiSelect()
        if not selection:
            return

        # if everything is ok, execute and register the transaction in the undo/redo stack
        FreeCAD.ActiveDocument.openTransaction(translate("PathProfile","Create Profile"))
        FreeCADGui.addModule("PathScripts.PathProfile")
        FreeCADGui.doCommand('obj = FreeCAD.ActiveDocument.addObject("Path::FeaturePython","Profile")')
        FreeCADGui.doCommand('PathScripts.PathProfile.ObjectProfile(obj)')

        if selection['edgenames']:
            FreeCAD.Console.PrintMessage('There are edges selected\n')
            FreeCADGui.doCommand('obj.Base = (FreeCAD.ActiveDocument.'+selection['objname']+',"'+selection['edgenames'][0]+'")')
            FreeCADGui.doCommand('obj.Edge1 =(FreeCAD.ActiveDocument.getObject("'+(selection['objname'])+'"),["'  +str(selection['edgenames'][0]+'"])'))

        else:
            FreeCADGui.doCommand('obj.Base = (FreeCAD.ActiveDocument.'+selection['objname']+',"'+selection['facename']+'")')

        if selection['pointlist']:
            # we should at least have a start point
            FreeCADGui.doCommand('from FreeCAD import Vector')
            stptX, stptY, stptZ = selection['pointlist'][0].X, selection['pointlist'][0].Y, selection['pointlist'][0].Z
            FreeCADGui.doCommand('obj.StartPoint = Vector('+str(stptX)+',' +str(stptY)+',' +str(stptZ)+')')
            if len(selection['pointlist'])>1: # we have more than one point so we have an end point
                endptX, endptY, endptZ = selection['pointlist'][-1].X, selection['pointlist'][-1].Y, selection['pointlist'][-1].Z
                FreeCADGui.doCommand('obj.EndPoint = Vector('+str(endptX)+',' +str(endptY)+',' +str(endptZ)+')')
        if selection['clockwise']:
            FreeCADGui.doCommand('obj.Side = "Left" ')
        elif selection['clockwise'] == False: 
            FreeCADGui.doCommand('obj.Side = "Right" ')
        FreeCADGui.doCommand('ZMax = obj.Base[0].Shape.BoundBox.ZMax')
        FreeCADGui.doCommand('obj.StepDown = 1.0')
        FreeCADGui.doCommand('obj.StartDepth = ZMax- obj.StepDown')
        FreeCADGui.doCommand('obj.FinalDepth = -10.0')
        FreeCADGui.doCommand('obj.ViewObject.Proxy = 0')
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()

if FreeCAD.GuiUp: 
    # register the FreeCAD command
    FreeCADGui.addCommand('Path_Profile',CommandPathProfile())

FreeCAD.Console.PrintLog("Loading PathProfile... done\n")
