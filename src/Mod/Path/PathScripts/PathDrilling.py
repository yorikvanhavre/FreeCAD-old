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

"""Path Drilling object and FreeCAD command"""

# Qt tanslation handling
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig)


class ObjectDrilling:
    

    def __init__(self,obj):
        #obj.addProperty("App::PropertyVector","StartPoint","Path",translate("PathProfile","The start position of the drilling"))

        obj.addProperty("App::PropertyLinkSub","Base","Path",translate("Parent Object","The base geometry of this toolpath"))
        obj.addProperty("App::PropertyVectorList","locations","Path","The drilling locations")

        obj.addProperty("App::PropertyFloatConstraint", "PeckDepth", "Drilling", translate("PeckDepth","Incremental Drill depth before retracting to clear chips"))
        obj.PeckDepth = (0,0,1000,1)
        obj.addProperty("App::PropertyFloat", "ClearanceHeight", "Drilling", translate("Clearance Height","The height needed to clear clamps and obstructions"))
        obj.addProperty("App::PropertyFloat", "FinalDepth", "Drilling", translate("Final Depth","Final Depth of Tool- lowest value in Z"))
        obj.addProperty("App::PropertyFloat", "RetractHeight", "Drilling", translate("Retract Height","The height where feed starts and height during retract tool when path is finished"))
        obj.addProperty("App::PropertyFloatConstraint", "VertFeed", "Feed",translate("Vert Feed","Feed rate for vertical moves in Z"))
        obj.VertFeed = (0,0,100000,1)

        obj.addProperty("App::PropertyFloatConstraint", "HorizFeed", "Feed",translate("Horiz Feed","Feed rate for horizontal moves"))
        obj.HorizFeed = (0,0,100000,1)

        obj.addProperty("App::PropertyString","Comment","Path",translate("PathProject","An optional comment for this profile"))
        obj.addProperty("App::PropertyBool","Active","Path",translate("Active","Make False, to prevent operation from generating code"))
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
        output = "G90 G98\n"
        output += "G0 Z" + str(obj.ClearanceHeight) + "\n"
        if obj.PeckDepth > 0:
            cmd = "G83"
            qword = " Q"+ str(obj.PeckDepth)
        else:
            cmd = "G81"
            qword = ""
            
        for p in obj.locations:
            output += cmd + " X" + str(p.x) + " Y" + str(p.y) + " Z" + str(obj.FinalDepth) + qword + " R" + str(obj.RetractHeight) + " F" + str(obj.VertFeed) + "\n"

        output += "G80\n"

        print output
        path = Path.Path(output)
        obj.Path = path


class CommandPathDrilling:


    def GetResources(self):
        return {'Pixmap'  : 'Path-Drilling',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PathDrilling","Drilling"),
                'Accel': "P, D",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PathDrilling","Creates a Path Drilling object")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None
        
    def Activated(self):
        import Path
        import Part

        from PathScripts import PathUtils,PathDrilling,PathProject
        prjexists = False
        selection = PathSelection.multiSelect()

        if not selection:
            return
        # if everything is ok, execute and register the transaction in the undo/redo stack
        FreeCAD.ActiveDocument.openTransaction(translate("PathDrilling","Create Drilling"))
        FreeCADGui.addModule("PathScripts.PathDrilling")
        
        obj = FreeCAD.ActiveDocument.addObject("Path::FeaturePython","Drilling")
        PathDrilling.ObjectDrilling(obj)

        if selection['pointlist']:
            myList = obj.locations
            for point in selection['pointlist']:
                if isinstance(point, Part.Vertex):
                    #vec = FreeCAD.Vector(point.X, point.Y, point.Z)
                    myList.append(FreeCAD.Vector(point.X, point.Y, point.Z))
            obj.locations = myList        
   



        obj.ViewObject.Proxy = 0
        obj.Active = False
       
        for o in FreeCAD.ActiveDocument.Objects:
            if "Proxy" in o.PropertiesList:
                if isinstance(o.Proxy,PathProject.ObjectPathProject):
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

        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()


if FreeCAD.GuiUp: 
    # register the FreeCAD command
    FreeCADGui.addCommand('Path_Drilling',CommandPathDrilling())

FreeCAD.Console.PrintLog("Loading PathDrilling... done\n")
