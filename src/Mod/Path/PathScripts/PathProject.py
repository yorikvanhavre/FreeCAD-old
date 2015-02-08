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
        obj.addProperty("App::PropertyFile", "PostProcessor", "CodeOutput", translate("PostProcessor","Select the Post Processor file for this project"))
        obj.addProperty("App::PropertyFile", "OutputFile", "CodeOutput", translate("OutputFile","The NC output file for this project"))
        obj.addProperty("App::PropertyBool","Editor","CodeOutput",translate("Show Editor","Show G-Code in simple editor after posting code"))
        obj.addProperty("Path::PropertyTooltable","Tooltable",  "Path",translate("PathProject","The tooltable of this feature"))
        obj.addProperty("App::PropertyVector",    "CornerMin",  "Path",translate("PathProject","The lower left corner of the machine extents"))
        obj.addProperty("App::PropertyVector",    "CornerMax",  "Path",translate("PathProject","The upper right corner of the machine extents"))
        obj.addProperty("App::PropertyString",    "Description","Path",translate("PathProject","An optional description for this project"))
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

#    def onChanged(self,obj,prop):
#        pass

    def execute(self,obj):
        cmds = []
        for child in obj.Group:
            if child.isDerivedFrom("Path::Feature"):
                cmds.extend(child.Path.Commands)
        if cmds:
            path = Path.Path(cmds)
            obj.Path = path

class ViewProviderProject:
    
    
    def __init__(self,vobj):
        vobj.Proxy = self
        vobj.addProperty("App::PropertyBool","ShowExtents","Path",translate("PathProject","Switch the machine extents bounding box on/off"))

    def __getstate__(self): #mandatory
        return None

    def __setstate__(self,state): #mandatory
        return None

    def getIcon(self):
        return ":/icons/Path-Project.svg"
        
    def attach(self,vobj):
        from pivy import coin
        self.extentsBox = coin.SoSeparator()
        vobj.RootNode.addChild(self.extentsBox)
        
    def onChanged(self,vobj,prop):
        if prop == "ShowExtents":
            self.extentsBox.removeAllChildren()
            if vobj.ShowExtents and hasattr(vobj,"Object"):
                from pivy import coin
                parent = coin.SoType.fromName("SoSkipBoundingGroup").createInstance()
                self.extentsBox.addChild(parent)
                # set pattern
                pattern = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Part").GetInt("GridLinePattern",0x0f0f)
                defStyle = coin.SoDrawStyle()
                defStyle.lineWidth = 1
                defStyle.linePattern = pattern
                parent.addChild(defStyle)
                # set color
                c = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Path").GetUnsigned("DefaultExtentsColor",3418866943)
                r = float((c>>24)&0xFF)/255.0
                g = float((c>>16)&0xFF)/255.0
                b = float((c>>8)&0xFF)/255.0
                color = coin.SoBaseColor()
                parent.addChild(color)
                # set boundbox
                extents = coin.SoType.fromName("SoFCBoundingBox").createInstance()
                extents.coordsOn.setValue(False)
                extents.dimensionsOn.setValue(True)
                p1 = vobj.Object.CornerMin
                p2 = vobj.Object.CornerMax
                extents.minBounds.setValue(p1.x,p1.y,p1.z)
                extents.maxBounds.setValue(p2.x,p2.y,p2.z)
                parent.addChild(extents)
                

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
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()


if FreeCAD.GuiUp: 
    # register the FreeCAD command
    FreeCADGui.addCommand('Path_Project',CommandProject())

FreeCAD.Console.PrintLog("Loading PathProject... done\n")
