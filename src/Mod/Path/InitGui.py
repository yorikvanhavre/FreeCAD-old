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
        # load the module
        import Path
        import PathGui
    def GetClassName(self):
        return "PathGui::Workbench"

Gui.addWorkbench(PathWorkbench())
