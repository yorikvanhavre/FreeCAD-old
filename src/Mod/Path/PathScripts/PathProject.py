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

"""Path Project object and FreeCAD command"""

# Qt tanslation handling
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def translate(context, text, disambig=None):
        return QtGui.QApplication.translate(context, text, disambig)


class ObjectPathProject:
    

    def __init__(self,obj):
#        obj.addProperty("App::PropertyFile", "PostProcessor", "CodeOutput", translate("PostProcessor","Select the Post Processor file for this project"))
        obj.addProperty("App::PropertyFile", "OutputFile", "CodeOutput", translate("OutputFile","The NC output file for this project"))
        obj.addProperty("App::PropertyBool","Editor","CodeOutput",translate("Show Editor","Show G-Code in simple editor after posting code"))
#        obj.addProperty("Path::PropertyTooltable","Tooltable",  "Path",translate("PathProject","The tooltable of this feature"))
        obj.addProperty("App::PropertyString",    "Description","Path",translate("PathProject","An optional description for this project"))
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

    def onChanged(self,obj,prop):
        pass

    def execute(self,obj):
        cmds = []
        for child in obj.Group:
            if child.isDerivedFrom("Path::Feature"):
                cmds.extend(child.Path.Commands)
        if cmds:
            path = Path.Path(cmds)
            #obj.Path = path

class ViewProviderProject:

    def __init__(self,vobj):
        vobj.Proxy = self
        mode = 2
        vobj.setEditorMode('LineWidth',mode)
        vobj.setEditorMode('MarkerColor',mode)
        vobj.setEditorMode('NormalColor',mode)
        vobj.setEditorMode('ShowFirstRapid',mode)
        vobj.setEditorMode('BoundingBox',mode)
        vobj.setEditorMode('DisplayMode',mode)
        vobj.setEditorMode('Selectable',mode)
        vobj.setEditorMode('ShapeColor',mode)
        vobj.setEditorMode('Transparency',mode)
        vobj.setEditorMode('Visibility',mode)

    def __getstate__(self): #mandatory
        return None

    def __setstate__(self,state): #mandatory
        return None

    def getIcon(self):
        return ":/icons/Path-Project.svg"


class CommandProject:


    def GetResources(self):
        return {'Pixmap'  : 'Path-Project',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PathProject","Project"),
                'Accel': "P, P",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PathProject","Creates a Path Project object")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None
        
    def Activated(self):
        incl = []
        sel = FreeCADGui.Selection.getSelection()
        for obj in sel:
            if obj.isDerivedFrom("Path::Feature"):
                incl.append(obj)
        FreeCAD.ActiveDocument.openTransaction(translate("PathProject","Create Project"))
        FreeCADGui.addModule("PathScripts.PathProject")
        FreeCADGui.doCommand('obj = FreeCAD.ActiveDocument.addObject("Path::FeatureCompoundPython","Project")')
        FreeCADGui.doCommand('PathScripts.PathProject.ObjectPathProject(obj)')
        if incl:
            FreeCADGui.doCommand('children = []')
            for obj in incl:
                FreeCADGui.doCommand('children.append(FreeCAD.ActiveDocument.'+obj.Name+')')
            FreeCADGui.doCommand('obj.Group = children')
        FreeCADGui.doCommand('PathScripts.PathProject.ViewProviderProject(obj.ViewObject)')

        addmachine = '''
import Path
import PathScripts
from PathScripts import PathProject
prjexists = False
obj = FreeCAD.ActiveDocument.addObject("Path::FeaturePython","Machine")
PathScripts.PathMachine.Machine(obj)

PathScripts.PathMachine._ViewProviderMachine(obj.ViewObject)
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
UnitParams = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units")
if UnitParams.GetInt('UserSchema') == 0:
    obj.MachineUnits = 'Metric'
     #metric mode
else:
    obj.MachineUnits = 'Inch'

'''

        FreeCADGui.doCommand(addmachine)

        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()


if FreeCAD.GuiUp: 
    # register the FreeCAD command
    FreeCADGui.addCommand('Path_Project',CommandProject())

FreeCAD.Console.PrintLog("Loading PathProject... done\n")
