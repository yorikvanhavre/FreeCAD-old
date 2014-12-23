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
        obj.addProperty("App::PropertyInteger","ToolNumber","Path",translate("PathProfile","The tool number to use"))
        obj.addProperty("App::PropertyVector","StartPoint","Path",translate("PathProfile","The start position of the drilling"))
        obj.addProperty("App::PropertyLength","DrillingHeight","Path",translate("PathProfile","The Z position of the end of the drilling"))
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
        # absolute coords, millimeters, cancel offsets
        output = "G90\nG21\nG40\n"
        # save tool
        output += "M06 T" + str(obj.ToolNumber) + "\n"
        
        # rapid move to the start position
        output += "G0 X" + str(obj.StartPoint.x) + " Y" + str(obj.StartPoint.y) + " Z" + str(obj.StartPoint.z) + "\n"
        
        # feed rate move to the drilling Z position
        output += "G1 Z" + str(obj.DrillingHeight.Value) + "\n"
        
        # rapid move back to the start position
        output += "G0 Z" + str(obj.StartPoint.z) + "\n"
        
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
        FreeCAD.ActiveDocument.openTransaction(translate("PathDrilling","Create Drilling"))
        FreeCADGui.addModule("PathScripts.PathDrilling")
        FreeCADGui.doCommand('obj = FreeCAD.ActiveDocument.addObject("Path::FeaturePython","Drilling")')
        FreeCADGui.doCommand('PathScripts.PathDrilling.ObjectDrilling(obj)')
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()


if FreeCAD.GuiUp: 
    # register the FreeCAD command
    FreeCADGui.addCommand('Path_Drilling',CommandPathDrilling())

FreeCAD.Console.PrintLog("Loading PathDrilling... done\n")
