#***************************************************************************
#*   (c) Yorik van Havre (yorik@uncreated.net) 2014                        *
#*                                                                         *
#*   This file is part of the FreeCAD CAx development system.              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   FreeCAD is distributed in the hope that it will be useful,            *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        * 
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Lesser General Public License for more details.                   *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with FreeCAD; if not, write to the Free Software        * 
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************/


class PathWorkbench ( Workbench ):
    "Path workbench"
    Icon = """
            /* XPM */
            static char * Path_xpm[] = {
            "16 16 9 1",
            "   c None",
            ".  c #262623",
            "+  c #452F16",
            "@  c #525451",
            "#  c #7E5629",
            "$  c #838582",
            "%  c #BE823B",
            "&  c #989A97",
            "*  c #CFD1CE",
            "  .@@@@@@@@@@.  ",
            "  $**********$  ",
            "  @$$$&&&&$$$@  ",
            "    .$&&&&$.    ",
            "    @******.    ",
            "    @******.    ",
            "    ...@@...    ",
            "     .&&@.      ",
            "     .@. .      ",
            "       .&&.     ",
            "     .$*$.      ",
            "     .$. .      ",
            "+###+  .@&.+###+",
            "+%%%+ .$$. +%%%+",
            "+%%%%#.. .#%%%%+",
            ".++++++..++++++."};
            """
    MenuText = "Path"
    ToolTip = "Path workbench"

    def Initialize(self):
        # load the builtin modules
        import Path
        import PathGui
        # load python modules
        from PathScripts import PathProfile
        from PathScripts import PathPocket
        from PathScripts import PathDrilling
        from PathScripts import PathDressup
        from PathScripts import PathHop
        
        # build commands list
        commands = ["Path_Profile","Path_Pocket","Path_Drilling","Path_Dressup","Path_Hop","Path_Shape","Path_Compound","Path_Project"]
        
        # Add commands to menu and toolbar
        def QT_TRANSLATE_NOOP(scope, text): return text
        self.appendToolbar(QT_TRANSLATE_NOOP("PathWorkbench","Path"),commands)
        self.appendMenu(QT_TRANSLATE_NOOP("PathWorkbench","Path"),commands)
        Log ('Loading Path workbench... done\n')

    def GetClassName(self):
        return "Gui::PythonWorkbench"
        
    def Activated(self):
        Msg("Path workbench activated\n")
                
    def Deactivated(self):
        Msg("Path workbench deactivated\n")

Gui.addWorkbench(PathWorkbench())

FreeCAD.addImportType("GCode (*.nc *.gc *.ncc *.ngc *.cnc *.tap)","PathGui")
FreeCAD.addExportType("GCode (*.nc *.gc *.ncc *.ngc *.cnc *.tap)","PathGui")
