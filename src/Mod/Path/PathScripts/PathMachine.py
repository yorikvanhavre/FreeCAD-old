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
''' A CNC machine object to define how code is posted '''

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

class Machine:
    def __init__(self,obj):

        obj.addProperty("App::PropertyString",    "MachineName","Machine",translate("Machine Name","Name of the Machine that will use the CNC program"))
        obj.addProperty("App::PropertyFile", "PostProcessor", "CodeOutput", translate("Post Processor","Select the Post Processor file for this machine"))
        obj.addProperty("App::PropertyEnumeration", "MachineUnits","Machine", translate( "Machine Units",  "Units that the machine works in, ie Metric or Inch"))
        obj.MachineUnits=['Metric', 'Inch']
        obj.addProperty("Path::PropertyTooltable","Tooltable",  "Machine",translate("Tool Table","The tooltable used for this CNC program")) #will implement later
        obj.addProperty("App::PropertyVector",    "CornerMin",  "Machine",translate("CornerMin","The lower left corner of the machine travel"))
        obj.addProperty("App::PropertyVector",    "CornerMax",  "Machine",translate("CornerMax","The upper right corner of the machine travel"))
        obj.addProperty("App::PropertyDistance", "XHomePos", "Machine", translate("X Home Position","Home position of machine, in X (mainly for visualization)"))
        obj.addProperty("App::PropertyDistance", "YHomePos", "Machine", translate("Y Home Position","Home position of machine, in Y (mainly for visualization)"))
        obj.addProperty("App::PropertyDistance", "ZHomePos", "Machine", translate("Z Home Position","Home position of machine, in Z (mainly for visualization)"))

        obj.Proxy = self
        mode = 2
        obj.setEditorMode('Placement',mode)

    def execute(self,obj):
        obj.Label = "Machine_"+str(obj.MachineName)
        gcode = 'G0 X'+str(obj.XHomePos.Value)+' Y'+str(obj.YHomePos.Value)+' Z'+str(obj.ZHomePos.Value)
        obj.Path = Path.Path(gcode)

    def onChanged(self,obj,prop):
        mode = 2
        obj.setEditorMode('Placement',mode)

class _ViewProviderMachine:
    def __init__(self,vobj):
        vobj.Proxy = self
        vobj.addProperty("App::PropertyBool","ShowMinMaxTravel","Machine",translate("ShowMinMaxTravel","Switch the machine max and minimum travel bounding box on/off"))
        mode = 2
        vobj.setEditorMode('LineWidth',mode)
        vobj.setEditorMode('MarkerColor',mode)
        vobj.setEditorMode('NormalColor',mode)
        vobj.setEditorMode('ShowFirstRapid',mode)
        vobj.setEditorMode('DisplayMode',mode)
        vobj.setEditorMode('BoundingBox',mode)
        vobj.setEditorMode('Selectable',mode)
        
        
    def __getstate__(self): #mandatory
        return None

    def __setstate__(self,state): #mandatory
        return None

    def getIcon(self): #optional
        return ":/icons/Path-Machine.svg"

    def attach(self,vobj):
        from pivy import coin
        self.extentsBox = coin.SoSeparator()
        vobj.RootNode.addChild(self.extentsBox)
        
    def onChanged(self,vobj,prop):
        if prop == "ShowMinMaxTravel":
            self.extentsBox.removeAllChildren()
            if vobj.ShowMinMaxTravel and hasattr(vobj,"Object"):
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
                extents.dimensionsOn.setValue(False)
                p1 = vobj.Object.CornerMin
                p2 = vobj.Object.CornerMax
                UnitParams = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Units")
                if UnitParams.GetInt('UserSchema') == 0:
                    extents.minBounds.setValue(p1.x,p1.y,p1.z)
                    extents.maxBounds.setValue(p2.x,p2.y,p2.z)
                else:
                    scale = 25.4
                    extents.minBounds.setValue(p1.x*scale,p1.y*scale,p1.z*scale)
                    extents.maxBounds.setValue(p2.x*scale,p2.y*scale,p2.z*scale)
                parent.addChild(extents)
        mode = 2
        vobj.setEditorMode('LineWidth',mode)
        vobj.setEditorMode('MarkerColor',mode)
        vobj.setEditorMode('NormalColor',mode)
        vobj.setEditorMode('ShowFirstRapid',mode)
        vobj.setEditorMode('DisplayMode',mode)
        vobj.setEditorMode('BoundingBox',mode)
        vobj.setEditorMode('Selectable',mode)


    def updateData(self,vobj,prop): #optional
        # this is executed when a property of the APP OBJECT changes
        pass

    def setEdit(self,vobj,mode): #optional
        # this is executed when the object is double-clicked in the tree
        pass

    def unsetEdit(self,vobj,mode): #optional
        # this is executed when the user cancels or terminates edit mode
        pass

class CommandPathMachine:
    def GetResources(self):
        return {'Pixmap'  : 'Path-Machine',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PathMachine","Machine Object"),
                'Accel': "P, M",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PathMachine","Create a Machine object")}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        FreeCAD.ActiveDocument.openTransaction(translate("PathMachine","Create a Machine object"))
        FreeCADGui.addModule("PathScripts.PathMachine")
        snippet = '''
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

        FreeCADGui.doCommand(snippet)
        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()

if FreeCAD.GuiUp: 
    # register the FreeCAD command
    FreeCADGui.addCommand('Path_Machine',CommandPathMachine())


FreeCAD.Console.PrintLog("Loading PathMachine... done\n")


