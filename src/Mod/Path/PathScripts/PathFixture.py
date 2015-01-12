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

import FreeCAD
import Path

class FixtureParams():
    def __init__(self,obj):

        obj.addProperty("App::PropertyEnumeration", "Fixture", "Fixture Parameters", "Fixture Mode")
        obj.Fixture = ['G54','G55','G56','G57','G58','G59']
        obj.Proxy = self

    def execute(self,obj):
        obj.Label = obj.Fixture

        output =""
        output += obj.Fixture
        output +="G91"
        output +="G0X0Y0Z0"
        output +="G90"
        path = Path.Path(output)
        obj.Path = path

class ViewProviderFixtureParams:
    def __init__(self, obj):
        "Set this object to the proxy object of the actual view provider"
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None


    def getIcon(self):
        return """
        /* XPM */
        static char * fixtures_xpm[] = {
        "16 16 14 1",
        " 	c None",
        ".	c #FF0000",
        "+	c #FE0000",
        "@	c #0000FF",
        "#	c #0000FE",
        "$	c #1900E5",
            "%	c #BE0040",
            "&	c #61009D",
            "*	c #A0005E",
            "=	c #F90005",
            "-	c #1400EA",
            ";	c #3400CA",
            ">	c #650099",
            ",	c #AD0051",
            "                ",
            "                ",
            "     ..         ",
            "                ",
            "    +  + ..     ",
            "        .       ",
            "   +    .  +    ",
            "                ",
            "  . @#$% &  .   ",
            " .    *   *     ",
            "      = @@-; .  ",
            ".    ... >,.  . ",
            "                ",
            "    ..  +..+....",
            "                ",
            "                "};
                        """
'''
f1 = FreeCAD.ActiveDocument.addObject("Path::FeaturePython","FixtureOffset")
FixtureParams(f1)
ViewProviderFixtureParams(f1.ViewObject)
App.activeDocument().recompute()
'''

def makeFixture():
    f1 = FreeCAD.ActiveDocument.addObject("Path::FeaturePython","FixtureOffset")
    FixtureParams(f1)
    ViewProviderFixtureParams(f1.ViewObject)
#    FreeCAD.activeDocument().recompute()
