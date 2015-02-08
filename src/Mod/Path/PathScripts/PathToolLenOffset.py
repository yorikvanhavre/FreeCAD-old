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
''' Used for CNC machine Tool Length Offsets ie G43H2'''

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

class ToolLenOffset:
    def __init__(self,obj):
        obj.addProperty("App::PropertyInteger", "HeightNumber","HeightOffset", translate( "Height Offset Number",  "The Height offset number of the active tool"))
        obj.addProperty("App::PropertyFloat", "Height", "HeightOffset", translate("Height","The first height value in Z, to rapid to, before making a feed move in Z"))
        obj.addProperty("App::PropertyBool","Active","HeightOffset",translate("Active","Make False, to prevent operation from generating code"))
        obj.Proxy = self


    def execute(self,obj):

        command = 'G43H'+str(obj.HeightNumber)+'G0Z'+str(obj.Height)
        obj.Path = Path.Path(command)
        obj.Label = "Height"+str(obj.HeightNumber)
        if obj.Active:
            obj.Path = Path.Path(command)
            obj.ViewObject.Visibility = True
        else:
            obj.Path = Path.Path("(inactive operation)")
            obj.ViewObject.Visibility = False

class _ViewProviderTLO:
    def __init__(self,obj): #mandatory
        obj.Proxy = self

    def __getstate__(self): #mandatory
        return None

    def __setstate__(self,state): #mandatory
        return None

    def getIcon(self): #optional
        return ":/icons/Path-LengthOffset.svg"

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


class CommandPathToolLenOffset:
    def GetResources(self):
        return {'Pixmap'  : 'Path-LengthOffset',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PathToolLenOffset","Tool Length Offset"),
                'Accel': "P, T",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PathToolLenOffset","Create a Tool Length Offset object")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction(translate("PathPlane","Create a Selection Plane object"))
        FreeCADGui.addModule("PathScripts.PathToolLenOffset")
        snippet = '''
import Path
import PathScripts
from PathScripts import PathProject
prjexists = False
obj = FreeCAD.ActiveDocument.addObject("Path::FeaturePython","HeightOffset")
PathScripts.PathToolLenOffset.ToolLenOffset(obj)
obj.Active = True
PathScripts.PathToolLenOffset._ViewProviderTLO(obj.ViewObject)
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
    FreeCADGui.addCommand('Path_ToolLenOffset', CommandPathToolLenOffset())
    
FreeCAD.Console.PrintLog("Loading PathToolLenOffset... done\n")




