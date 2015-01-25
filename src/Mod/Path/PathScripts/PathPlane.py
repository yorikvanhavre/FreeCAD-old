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
''' Used for CNC machine plane selection G17,G18,G19 '''

import FreeCAD,FreeCADGui,Path,PathGui
from PathScripts import PathProject
from PySide import QtCore,QtGui

# Qt tanslation handling
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig)

class Plane:
    def __init__(self,obj):
        obj.addProperty("App::PropertyEnumeration", "SelectionPlane","Plane", translate( "Selection Plane",  "Orientation plane of CNC path"))
        obj.SelectionPlane=['XY', 'XZ', 'YZ']
        obj.Proxy = self

    def execute(self,obj):
        clonelist = ['XY', 'XZ', 'YZ']
        cindx = clonelist.index(str(obj.SelectionPlane))
        pathlist = ['G17', 'G18', 'G19']
        obj.Path = Path.Path(pathlist[cindx])
        labelindx = clonelist.index(obj.SelectionPlane)+1
        obj.Label = "Plane"+str(labelindx)

class _ViewProviderPlane:
    def __init__(self,obj): #mandatory
        obj.Proxy = self

    def __getstate__(self): #mandatory
        return None

    def __setstate__(self,state): #mandatory
        return None

    def getIcon(self): #optional
        return ":/icons/Path-Plane.svg"

    def onChanged(self,obj,prop): #optional
        # this is executed when a property of the VIEW PROVIDER changes
        pass

    def updateData(self,obj,prop): #optional
        # this is executed when a property of the APP OBJECT changes
        pass

    def setEdit(self,vobj,mode): #optional
        # this is executed when the object is double-clicked in the tree
        pass

    def unsetEdit(self,vobj,mode): #optional
        # this is executed when the user cancels or terminates edit mode
        pass

class CommandPathPlane:
    def GetResources(self):
        return {'Pixmap'  : 'Path-Plane',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PathPlane","Selection Plane"),
                'Accel': "P, P",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PathPlane","Create a Selection Plane object")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction(translate("PathPlane","Create a Selection Plane object"))
        FreeCADGui.addModule("PathScripts.PathPlane")
        snippet = '''
import Path
import PathScripts
from PathScripts import PathProject
prjexists = False
obj = FreeCAD.ActiveDocument.addObject("Path::FeaturePython","Plane")
PathScripts.PathPlane.Plane(obj)
PathScripts.PathPlane._ViewProviderPlane(obj.ViewObject)
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


'''

        FreeCADGui.doCommand(snippet)
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()

if FreeCAD.GuiUp: 
    # register the FreeCAD command
    FreeCADGui.addCommand('Path_Plane',CommandPathPlane())


FreeCAD.Console.PrintLog("Loading PathPlane... done\n")


