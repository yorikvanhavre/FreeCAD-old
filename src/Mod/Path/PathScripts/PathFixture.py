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
''' Used to create CNC machine fixture offsets such as G54,G55, etc...'''

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

class Fixture():
    def __init__(self,obj):
        obj.addProperty("App::PropertyInteger", "Fixture", "Fixture Parameters", "Fixture Offset Number")
        obj.Fixture=1
        obj.Proxy = self

    def execute(self,obj):
        fixlist = ['G53','G54','G55','G56','G57','G58','G59','G59.1', 'G59.2', 'G59.3', 'G59.4', 'G59.5','G59.6','G59.7', 'G59.8', 'G59.9']
        fixture=fixlist[int(obj.Fixture)]
        obj.Path = Path.Path(fixture)
        obj.Label = "Fixture"+str(obj.Fixture)
        for o in FreeCAD.ActiveDocument.Objects:
            if "Proxy" in o.PropertiesList:
                if isinstance(o.Proxy,PathProject.ObjectPathProject):
                    g = o.Group
                    g.append(obj)
                    o.Group = g

class _ViewProviderFixture:

    def __init__(self,obj): #mandatory
#        obj.addProperty("App::PropertyFloat","SomePropertyName","PropertyGroup","Description of this property")
        obj.Proxy = self

    def __getstate__(self): #mandatory
        return None

    def __setstate__(self,state): #mandatory
        return None

    def getIcon(self): #optional
        return ":/icons/Path-Datums.svg"

#    def attach(self): #optional
#        # this is executed on object creation and object load from file
#        pass

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


class CommandPathFixture:
    def GetResources(self):
        return {'Pixmap'  : 'Path-Datums',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PathFixture","Fixture"),
                'Accel': "P, F",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PathFixture","Creates a Fixture Offset object")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction(translate("PathFixture","Create a Fixture Offset"))
        FreeCADGui.addModule("PathScripts.PathFixture")
        FreeCADGui.doCommand('obj = FreeCAD.ActiveDocument.addObject("Path::FeaturePython","Fixture")')
        FreeCADGui.doCommand('PathScripts.PathFixture.Fixture(obj)')
        FreeCADGui.doCommand('PathScripts.PathFixture._ViewProviderFixture(obj.ViewObject)')
#        FreeCADGui.doCommand('obj.ViewObject.Proxy = 0')
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()

if FreeCAD.GuiUp: 
    # register the FreeCAD command
    FreeCADGui.addCommand('Path_Fixture',CommandPathFixture())


FreeCAD.Console.PrintLog("Loading PathFixture... done\n")
